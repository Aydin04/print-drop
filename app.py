import os
import re
import json
import time
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory
from database import load_db, save_db
from pdf_generator import generate_photo_layout_pdf

app = Flask(__name__)
BASE_DIR = os.path.expanduser("~/Hasil_Print")
os.makedirs(BASE_DIR, exist_ok=True)

@app.route("/")
def index():
    db = load_db()
    return render_template("index.html", db=db)

@app.route("/admin")
def admin():
    db = load_db()
    return render_template("admin.html", db=db)

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_db())

@app.route("/api/config", methods=["POST"])
def update_config():
    new_data = request.json
    if new_data:
        save_db(new_data)
        return jsonify({"status": "success", "message": "Konfigurasi berhasil disimpan!"})
    return jsonify({"status": "error", "message": "Data kosong"}), 400

@app.route("/api/calculate-price", methods=["POST"])
def calculate_price():
    data = request.json
    db = load_db()
    
    mode = data.get("mode", "document") # document or photo_custom
    quantity = int(data.get("quantity", 1))
    paper_id = int(data.get("paper_id", 1))
    color_mode = data.get("color_mode", "COLOR") # COLOR or BW
    duplex = bool(data.get("duplex", False))
    accessory_id = data.get("accessory_id")
    
    # Find paper
    paper = next((p for p in db.get("papers", []) if p["id"] == paper_id), None)
    if not paper:
        paper = db["papers"][0]
        
    base_price = paper["base_selling_price_color"] if color_mode == "COLOR" else paper["base_selling_price_bw"]
    
    # Duplex multiplier
    if duplex:
        multiplier = 1.0 + (paper.get("duplex_extra_percent", 80) / 100.0)
        unit_print_price = base_price * multiplier
    else:
        unit_print_price = base_price
        
    accessory_price_total = 0
    accessory_name = ""
    if accessory_id:
        acc = next((a for a in db.get("accessories", []) if a["id"] == int(accessory_id)), None)
        if acc:
            accessory_price_total = acc.get("selling_price", 0) * quantity
            accessory_name = acc["name"]

    # Calculate total based on mode
    if mode == "photo_custom":
        preset_id = data.get("preset_id")
        preset = next((pr for pr in db.get("presets", []) if pr["id"] == preset_id), None)
        
        if preset and "price_per_pcs" in preset:
            print_cost_total = preset["price_per_pcs"] * quantity
        elif preset and "suggested_price" in preset:
            print_cost_total = preset["suggested_price"] * quantity
        else:
            # Custom mm calculation
            photo_w = float(data.get("photo_w_mm", 28))
            photo_h = float(data.get("photo_h_mm", 38))
            # how many fit on paper
            cols = max(1, int(paper["width_mm"] / (photo_w + 3)))
            rows = max(1, int(paper["height_mm"] / (photo_h + 3)))
            fits = cols * rows
            sheets_needed = max(1, int(quantity + fits - 1) // fits)
            print_cost_total = sheets_needed * unit_print_price
    else:
        # Document mode
        page_count = int(data.get("page_count", 1))
        sheets_needed = page_count * quantity
        if duplex:
            sheets_needed = int((page_count + 1) // 2) * quantity
        print_cost_total = sheets_needed * unit_print_price

    total_price = print_cost_total + accessory_price_total
    
    # Rounding
    round_to = db.get("settings", {}).get("round_price_to", 500)
    if round_to > 0:
        total_price = int((total_price + round_to - 1) // round_to * round_to)

    return jsonify({
        "total_price": total_price,
        "print_cost_total": print_cost_total,
        "accessory_price_total": accessory_price_total,
        "accessory_name": accessory_name,
        "sheets_needed": locals().get("sheets_needed", 1)
    })

@app.route("/upload", methods=["POST"])
def upload():
    db = load_db()
    nama = request.form.get("nama", "").strip()
    if not nama:
        return jsonify({"error": "Nama tidak boleh kosong"}), 400

    clean_nama = re.sub(r'[/\\:*?"<>|]', "", nama).strip() or "Pelanggan"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder_name = f"{timestamp}_{clean_nama}"
    order_dir = os.path.join(BASE_DIR, folder_name)
    os.makedirs(order_dir, exist_ok=True)

    mode = request.form.get("mode", "document")
    color_mode = request.form.get("color_mode", "COLOR")
    duplex = request.form.get("duplex", "false") == "true"
    quantity = int(request.form.get("quantity", 1))
    paper_id = int(request.form.get("paper_id", 1))
    accessory_id = request.form.get("accessory_id", None)
    catatan = request.form.get("catatan", "")
    total_price = request.form.get("total_price", "0")

    paper = next((p for p in db.get("papers", []) if p["id"] == paper_id), db["papers"][0])
    accessory = next((a for a in db.get("accessories", []) if str(a["id"]) == str(accessory_id)), None)

    saved_files = []
    generated_pdf = None

    uploaded_files = request.files.getlist("files")

    if mode == "photo_custom" and uploaded_files and uploaded_files[0].filename:
        file = uploaded_files[0]
        ext = os.path.splitext(file.filename)[1]
        orig_img_path = os.path.join(order_dir, f"original_photo{ext}")
        file.save(orig_img_path)
        saved_files.append(os.path.basename(orig_img_path))

        photo_w_mm = float(request.form.get("photo_w_mm", 28))
        photo_h_mm = float(request.form.get("photo_h_mm", 38))
        crop_json = request.form.get("crop_data", None)
        crop_data = json.loads(crop_json) if crop_json else None

        pdf_name = f"TEMPLATE_PRINT_{int(photo_w_mm)}x{int(photo_h_mm)}_{quantity}pcs.pdf"
        out_pdf_path = os.path.join(order_dir, pdf_name)
        
        acc_name = accessory["name"] if accessory else None
        generate_photo_layout_pdf(
            output_pdf_path=out_pdf_path,
            photo_image_path=orig_img_path,
            photo_w_mm=photo_w_mm,
            photo_h_mm=photo_h_mm,
            quantity=quantity,
            paper_size_key=paper.get("size", "A4"),
            cut_marks=True,
            accessory_name=acc_name,
            crop_data=crop_data
        )
        generated_pdf = pdf_name
    else:
        # Document mode
        for f in uploaded_files:
            if f.filename:
                safe_name = os.path.basename(f.filename)
                target_path = os.path.join(order_dir, safe_name)
                f.save(target_path)
                saved_files.append(safe_name)

    # Generate STRUK_PESANAN.txt
    struk_content = f"""==================================================
              AYDIN PRINT — NOTA ORDER
==================================================
Waktu         : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Nama Pemesan  : {nama}
Mode Cetak    : {'Foto / Template Kustom' if mode == 'photo_custom' else 'Dokumen / Fotocopy'}
Jumlah / Qty  : {quantity} pcs/copy
Kertas        : {paper['name']}
Mode Warna    : {color_mode}
Duplex (B-B)  : {'Ya (Bolak-Balik)' if duplex else 'Tidak (1 Sisi)'}
Aksesoris     : {accessory['name'] if accessory else '-'}
Catatan       : {catatan if catatan else '-'}
--------------------------------------------------
ESTIMASI TOTAL: Rp {int(float(total_price)):,}
==================================================
File Pelanggan:
"""
    for sf in saved_files:
        struk_content += f"- {sf}\n"
    if generated_pdf:
        struk_content += f"- [SIAP CETAK]: {generated_pdf}\n"

    with open(os.path.join(order_dir, "STRUK_PESANAN.txt"), "w", encoding="utf-8") as f:
        f.write(struk_content)

    order_meta = {
        "nama": nama,
        "timestamp": timestamp,
        "folder": folder_name,
        "mode": mode,
        "quantity": quantity,
        "color_mode": color_mode,
        "duplex": duplex,
        "paper_name": paper['name'],
        "accessory_name": accessory['name'] if accessory else None,
        "catatan": catatan,
        "total_price": int(float(total_price)),
        "files": saved_files,
        "generated_pdf": generated_pdf
    }

    with open(os.path.join(order_dir, "ORDER_DATA.json"), "w", encoding="utf-8") as f:
        json.dump(order_meta, f, indent=2)

    return jsonify({
        "status": "success",
        "folder": folder_name,
        "total_price": int(float(total_price)),
        "files_count": len(saved_files),
        "generated_pdf": generated_pdf
    })

@app.route("/api/orders", methods=["GET"])
def get_orders():
    orders = []
    if os.path.exists(BASE_DIR):
        for fld in sorted(os.listdir(BASE_DIR), reverse=True):
            fld_path = os.path.join(BASE_DIR, fld)
            json_path = os.path.join(fld_path, "ORDER_DATA.json")
            if os.path.isdir(fld_path) and os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        orders.append(data)
                except Exception:
                    pass
    return jsonify(orders[:50])

@app.route("/download/<path:folder>/<path:filename>")
def download_file(folder, filename):
    return send_from_directory(os.path.join(BASE_DIR, folder), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
