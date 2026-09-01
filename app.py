import os
import re
import json
import subprocess
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory
from database import load_db, save_db
from pdf_generator import generate_photo_layout_pdf
from hpp_engine import calculate_hpp, calculate_selling_price, round_to_nearest, calculate_cut_fits_per_page

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
def calculate_price_api():
    data = request.json or {}
    db = load_db()
    settings = db.get("settings", {})

    mode = data.get("mode", "document")  # "document" or "photo_custom"
    quantity = int(data.get("quantity", 1))
    paper_id = int(data.get("paper_id", 1))
    color_mode = data.get("color_mode", "COLOR")  # "COLOR" or "BW"
    duplex = bool(data.get("duplex", False))
    accessory_id = data.get("accessory_id", None)
    page_count = max(1, int(data.get("page_count", 1)))

    # Get Selected Paper
    paper = next((p for p in db.get("papers", []) if p["id"] == paper_id), db["papers"][0])

    # Get Default / Selected Printer
    printer = next((pr for pr in db.get("printers", []) if pr.get("is_default", False)), db["printers"][0] if db.get("printers") else {
        "purchase_price": 3200000.0, "page_capacity": 50000, "watt": 16.0
    })

    # Get Ink Data
    ink = db.get("inks", [{}])[0]
    avg_ink_price_per_ml = ink.get("avg_price_per_ml", 1200.0)

    # Accessory calculation
    accessory_price_total = 0
    accessory_cost_total = 0
    accessory_name = None
    if accessory_id:
        acc = next((a for a in db.get("accessories", []) if str(a["id"]) == str(accessory_id)), None)
        if acc:
            accessory_price_total = acc.get("selling_price", 0) * quantity
            accessory_cost_total = acc.get("unit_price", 0) * quantity
            accessory_name = acc["name"]

    cut_fits = 1
    total_sheets_needed = 1

    if mode == "photo_custom":
        preset_id = data.get("preset_id")
        preset = next((pr for pr in db.get("presets", []) if pr["id"] == preset_id), None)

        photo_w_mm = float(data.get("photo_w_mm", 28))
        photo_h_mm = float(data.get("photo_h_mm", 38))

        # Calculate fits per page
        cut_fits = calculate_cut_fits_per_page(
            master_w_cm=paper["width_mm"] / 10.0,
            master_h_cm=paper["height_mm"] / 10.0,
            cut_w_cm=photo_w_mm / 10.0,
            cut_h_cm=photo_h_mm / 10.0
        )
        total_sheets_needed = max(1, (quantity + cut_fits - 1) // cut_fits)

        # Check if preset has fixed price per pcs
        if preset and "price_per_pcs" in preset:
            selling_price_total = (preset["price_per_pcs"] * quantity) + accessory_price_total
            hpp_res = calculate_hpp(
                pack_price=paper["pack_price"],
                sheets_per_pack=paper["sheets_per_pack"],
                total_quantity_ordered=quantity,
                cut_fits_per_page=cut_fits,
                avg_ink_price_per_ml=avg_ink_price_per_ml,
                printer_watt=printer.get("watt", 16.0),
                electricity_rate_per_kwh=settings.get("electricity_kwh", 1500.0),
                printer_purchase_price=printer.get("purchase_price", 3200000.0),
                estimated_page_capacity=printer.get("page_capacity", 50000),
                accessory_cost_total=accessory_cost_total,
                duplex=False
            )
            profit_total = selling_price_total - hpp_res["hpp_total"]
            return jsonify({
                "total_price": round_to_nearest(selling_price_total, settings.get("round_price_to", 500)),
                "unit_price": round(selling_price_total / max(1, quantity), 2),
                "hpp_total": hpp_res["hpp_total"],
                "profit_total": round(profit_total, 2),
                "sheets_needed": total_sheets_needed,
                "cut_fits_per_page": cut_fits,
                "accessory_price_total": accessory_price_total,
                "accessory_name": accessory_name
            })
    else:
        # Document mode
        if duplex:
            total_sheets_needed = ((page_count + 1) // 2) * quantity
        else:
            total_sheets_needed = page_count * quantity

    # Full HPP & Selling price calculation
    ml_per_sheet = 0.5 if color_mode == "COLOR" else 0.15
    print_seconds = 15.0 if color_mode == "COLOR" else 6.0

    hpp_result = calculate_hpp(
        pack_price=paper["pack_price"],
        sheets_per_pack=paper["sheets_per_pack"],
        total_quantity_ordered=quantity if mode == "photo_custom" else (page_count * quantity),
        cut_fits_per_page=cut_fits,
        avg_ink_price_per_ml=avg_ink_price_per_ml,
        ml_ink_per_sheet=ml_per_sheet,
        printer_watt=printer.get("watt", 16.0),
        print_time_seconds_per_page=print_seconds,
        electricity_rate_per_kwh=settings.get("electricity_kwh", 1500.0),
        printer_purchase_price=printer.get("purchase_price", 3200000.0),
        estimated_page_capacity=printer.get("page_capacity", 50000),
        accessory_cost_total=accessory_cost_total,
        duplex=duplex
    )

    margin_pct = settings.get("default_margin_percent", 40.0)
    margin_type = settings.get("margin_type", "MARKUP")
    min_profit_per_sheet = settings.get("profit_per_sheet_min", 500.0)

    # If base selling prices defined on paper, use paper base if higher
    paper_base = paper.get("base_selling_price_color", 1000) if color_mode == "COLOR" else paper.get("base_selling_price_bw", 500)
    if duplex:
        paper_base = paper_base * (1.0 + (paper.get("duplex_extra_percent", 80) / 100.0))

    calc_sell = calculate_selling_price(
        hpp_total=hpp_result["hpp_total"],
        hpp_per_unit=hpp_result["hpp_per_unit"],
        quantity=quantity,
        margin_percent=margin_pct,
        margin_type=margin_type,
        min_profit_per_sheet=min_profit_per_sheet,
        total_sheets=total_sheets_needed
    )

    base_paper_total = (total_sheets_needed * paper_base) + accessory_price_total
    final_raw_total = max(calc_sell["selling_price_total"], base_paper_total)
    final_rounded_total = round_to_nearest(final_raw_total, settings.get("round_price_to", 500))

    return jsonify({
        "total_price": final_rounded_total,
        "unit_price": round(final_rounded_total / max(1, quantity), 2),
        "hpp_total": hpp_result["hpp_total"],
        "profit_total": round(final_rounded_total - hpp_result["hpp_total"], 2),
        "sheets_needed": total_sheets_needed,
        "cut_fits_per_page": cut_fits,
        "accessory_price_total": accessory_price_total,
        "accessory_name": accessory_name
    })

@app.route("/upload", methods=["POST"])
def upload():
    db = load_db()
    settings = db.get("settings", {})
    nama = request.form.get("nama", "").strip()
    if not nama:
        return jsonify({"error": "Nama pemesan tidak boleh kosong"}), 400

    clean_nama = re.sub(r'[/\:*?"<>|]', "", nama).strip() or "Pelanggan"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder_name = f"{timestamp}_{clean_nama}"
    order_dir = os.path.join(BASE_DIR, folder_name)
    os.makedirs(order_dir, exist_ok=True)

    mode = request.form.get("mode", "document")
    color_mode = request.form.get("color_mode", "COLOR")
    duplex = request.form.get("duplex", "false").lower() == "true"
    quantity = int(request.form.get("quantity", 1))
    paper_id = int(request.form.get("paper_id", 1))
    accessory_id = request.form.get("accessory_id", None)
    catatan = request.form.get("catatan", "")
    total_price = int(float(request.form.get("total_price", 0)))
    preset_name = request.form.get("preset_name", "")

    paper = next((p for p in db.get("papers", []) if p["id"] == paper_id), db["papers"][0])
    accessory = next((a for a in db.get("accessories", []) if str(a["id"]) == str(accessory_id)), None)

    saved_files = []
    generated_pdf = None

    uploaded_files = request.files.getlist("files")

    if mode == "photo_custom" and uploaded_files and uploaded_files[0].filename:
        file = uploaded_files[0]
        ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
        orig_img_path = os.path.join(order_dir, f"original_{clean_nama}{ext}")
        file.save(orig_img_path)
        saved_files.append(os.path.basename(orig_img_path))

        photo_w_mm = float(request.form.get("photo_w_mm", 28))
        photo_h_mm = float(request.form.get("photo_h_mm", 38))
        crop_json = request.form.get("crop_data", None)
        crop_data = json.loads(crop_json) if crop_json else None

        pdf_filename = f"CETAK_{int(photo_w_mm)}x{int(photo_h_mm)}mm_{quantity}pcs_{clean_nama}.pdf"
        out_pdf_path = os.path.join(order_dir, pdf_filename)

        generate_photo_layout_pdf(
            output_pdf_path=out_pdf_path,
            photo_image_path=orig_img_path,
            photo_w_mm=photo_w_mm,
            photo_h_mm=photo_h_mm,
            quantity=quantity,
            paper_size_key=paper.get("size", "A4"),
            cut_marks=True,
            customer_name=nama,
            accessory_name=accessory["name"] if accessory else None,
            crop_data=crop_data
        )
        generated_pdf = pdf_filename
    else:
        # Document mode
        for f in uploaded_files:
            if f.filename:
                safe_name = os.path.basename(f.filename)
                target_path = os.path.join(order_dir, safe_name)
                f.save(target_path)
                saved_files.append(safe_name)

    # Build STRUK_PESANAN.txt
    struk_content = f"""==================================================
              AYDIN PRINT — NOTA ORDER
==================================================
Waktu         : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Nama Pemesan  : {nama}
Mode Cetak    : {'Foto & Kustom Studio' if mode == 'photo_custom' else 'Dokumen / Fotocopy'}
Preset        : {preset_name if preset_name else '-'}
Jumlah / Qty  : {quantity} pcs/copy
Kertas        : {paper['name']}
Mode Warna    : {'Full Color' if color_mode == 'COLOR' else 'Hitam Putih (B/W)'}
Duplex (B-B)  : {'Ya (Bolak-Balik)' if duplex else 'Tidak (1 Sisi)'}
Aksesoris     : {accessory['name'] if accessory else '-'}
Catatan       : {catatan if catatan else '-'}
--------------------------------------------------
ESTIMASI TOTAL: Rp {total_price:,}
==================================================
File Pesanan:
"""
    for sf in saved_files:
        struk_content += f"- {sf}
"
    if generated_pdf:
        struk_content += f"- [⭐ SIAP CETAK PDF]: {generated_pdf}
"

    with open(os.path.join(order_dir, "STRUK_PESANAN.txt"), "w", encoding="utf-8") as f:
        f.write(struk_content)

    order_meta = {
        "id": timestamp,
        "nama": nama,
        "timestamp": timestamp,
        "created_at": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        "folder": folder_name,
        "mode": mode,
        "preset_name": preset_name,
        "quantity": quantity,
        "color_mode": color_mode,
        "duplex": duplex,
        "paper_name": paper['name'],
        "accessory_name": accessory['name'] if accessory else None,
        "catatan": catatan,
        "total_price": total_price,
        "status": "Pending",
        "files": saved_files,
        "generated_pdf": generated_pdf
    }

    with open(os.path.join(order_dir, "ORDER_DATA.json"), "w", encoding="utf-8") as f:
        json.dump(order_meta, f, indent=2)

    return jsonify({
        "status": "success",
        "folder": folder_name,
        "total_price": total_price,
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
                        orders.append(json.load(f))
                except Exception:
                    pass
    return jsonify(orders[:100])

@app.route("/api/order/status", methods=["POST"])
def update_order_status():
    data = request.json or {}
    folder = data.get("folder")
    new_status = data.get("status", "Pending")
    if folder:
        json_path = os.path.join(BASE_DIR, folder, "ORDER_DATA.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["status"] = new_status
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            return jsonify({"status": "success", "new_status": new_status})
    return jsonify({"status": "error"}), 400

@app.route("/api/order/delete", methods=["POST"])
def delete_order():
    data = request.json or {}
    folder = data.get("folder")
    if folder:
        fld_path = os.path.join(BASE_DIR, folder)
        if os.path.exists(fld_path):
            import shutil
            shutil.rmtree(fld_path, ignore_errors=True)
            return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route("/download/<path:folder>/<path:filename>")
def download_file(folder, filename):
    return send_from_directory(os.path.join(BASE_DIR, folder), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
