import os
import re
import json
import secrets
import subprocess
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory, session, redirect
from database import load_db, save_db
from pdf_generator import generate_photo_layout_pdf
from hpp_engine import calculate_hpp, calculate_selling_price, round_to_nearest, calculate_cut_fits_per_page

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))
BASE_DIR = os.path.expanduser("~/Hasil_Print")
os.makedirs(BASE_DIR, exist_ok=True)

def is_admin_authenticated():
    client_ip = request.remote_addr
    if client_ip in ["127.0.0.1", "::1", "localhost"]:
        return True
    return session.get("is_admin", False) is True

# ================= CAPTIVE PORTAL PROBE HANDLERS =================
@app.route("/generate_204")
@app.route("/gen_204")
@app.route("/ncsi.txt")
@app.route("/hotspot-detect.html")
@app.route("/canonical.html")
def captive_portal_probe():
    return redirect("http://10.42.0.1:5000/")

@app.route("/")
def index():
    db = load_db()
    return render_template("index.html", db=db)

@app.route("/admin")
def admin():
    db = load_db()
    is_auth = is_admin_authenticated()
    return render_template("admin.html", db=db, is_auth=is_auth)

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json or {}
    pin = str(data.get("pin", "")).strip()
    db = load_db()
    correct_pin = str(db.get("settings", {}).get("admin_pin", "1234")).strip()

    if pin == correct_pin:
        session["is_admin"] = True
        return jsonify({"status": "success", "message": "Autentikasi Berhasil"})
    return jsonify({"status": "error", "message": "PIN Kasir Salah"}), 401

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return jsonify({"status": "success"})

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_db())

@app.route("/api/config", methods=["POST"])
def update_config():
    if not is_admin_authenticated():
        return jsonify({"status": "error", "message": "Akses Ditolak: Khusus Admin"}), 403
    new_data = request.json
    if new_data:
        save_db(new_data)
        return jsonify({"status": "success", "message": "Konfigurasi berhasil disimpan!"})
    return jsonify({"status": "error", "message": "Data kosong"}), 400

# ================= MASTER DATA CRUD =================

@app.route("/api/admin/printer/save", methods=["POST"])
def save_printer():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    p_data = request.json or {}
    db = load_db()
    printers = db.get("printers", [])

    p_id = p_data.get("id")
    if p_id:
        for i, p in enumerate(printers):
            if p["id"] == p_id:
                printers[i] = p_data
                break
    else:
        new_id = max([p["id"] for p in printers] + [0]) + 1
        p_data["id"] = new_id
        printers.append(p_data)

    db["printers"] = printers
    save_db(db)
    return jsonify({"status": "success", "data": p_data})

@app.route("/api/admin/paper/save", methods=["POST"])
def save_paper():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    p_data = request.json or {}
    db = load_db()
    papers = db.get("papers", [])

    p_id = p_data.get("id")
    if p_id:
        for i, p in enumerate(papers):
            if p["id"] == p_id:
                papers[i] = p_data
                break
    else:
        new_id = max([p["id"] for p in papers] + [0]) + 1
        p_data["id"] = new_id
        papers.append(p_data)

    db["papers"] = papers
    save_db(db)
    return jsonify({"status": "success", "data": p_data})

@app.route("/api/admin/accessory/save", methods=["POST"])
def save_accessory():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    a_data = request.json or {}
    db = load_db()
    accessories = db.get("accessories", [])

    a_id = a_data.get("id")
    if a_id:
        for i, a in enumerate(accessories):
            if a["id"] == a_id:
                accessories[i] = a_data
                break
    else:
        new_id = max([a["id"] for a in accessories] + [0]) + 1
        a_data["id"] = new_id
        accessories.append(a_data)

    db["accessories"] = accessories
    save_db(db)
    return jsonify({"status": "success", "data": a_data})

@app.route("/api/admin/preset/save", methods=["POST"])
def save_preset():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    pr_data = request.json or {}
    db = load_db()
    presets = db.get("presets", [])

    pr_id = pr_data.get("id")
    if pr_id:
        for i, pr in enumerate(presets):
            if pr["id"] == pr_id:
                presets[i] = pr_data
                break
        else:
            presets.append(pr_data)
    else:
        pr_data["id"] = "preset_" + secrets.token_hex(4)
        presets.append(pr_data)

    db["presets"] = presets
    save_db(db)
    return jsonify({"status": "success", "data": pr_data})


@app.route("/api/admin/printer/delete", methods=["POST"])
def delete_printer():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    p_id = (request.json or {}).get("id")
    db = load_db()
    db["printers"] = [p for p in db.get("printers", []) if p["id"] != p_id]
    save_db(db)
    return jsonify({"status": "success"})

@app.route("/api/admin/paper/delete", methods=["POST"])
def delete_paper():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    p_id = (request.json or {}).get("id")
    db = load_db()
    db["papers"] = [p for p in db.get("papers", []) if p["id"] != p_id]
    save_db(db)
    return jsonify({"status": "success"})

@app.route("/api/admin/accessory/delete", methods=["POST"])
def delete_accessory():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    a_id = (request.json or {}).get("id")
    db = load_db()
    db["accessories"] = [a for a in db.get("accessories", []) if a["id"] != a_id]
    save_db(db)
    return jsonify({"status": "success"})

@app.route("/api/admin/preset/delete", methods=["POST"])
def delete_preset():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    pr_id = str((request.json or {}).get("id"))
    db = load_db()
    db["presets"] = [pr for pr in db.get("presets", []) if str(pr["id"]) != pr_id]
    save_db(db)
    return jsonify({"status": "success"})

# ================= PRICE CALCULATION =================

@app.route("/api/calculate-price", methods=["POST"])
def calculate_price_api():
    data = request.json or {}
    db = load_db()
    settings = db.get("settings", {})

    mode = data.get("mode", "document")
    quantity = int(data.get("quantity", 1))
    paper_id = int(data.get("paper_id", 1))
    color_mode = data.get("color_mode", "COLOR")
    duplex = bool(data.get("duplex", False))
    accessory_id = data.get("accessory_id", None)
    page_count = max(1, int(data.get("page_count", 1)))

    paper = next((p for p in db.get("papers", []) if p["id"] == paper_id), db["papers"][0])
    printer = next((pr for pr in db.get("printers", []) if pr.get("is_default", False)), db["printers"][0] if db.get("printers") else {
        "purchase_price": 3200000.0, "page_capacity": 50000, "watt": 16.0
    })

    ink = db.get("inks", [{}])[0]
    avg_ink_price_per_ml = ink.get("avg_price_per_ml", 1200.0)

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
        is_keychain = (preset_id == "goci_akrilik") or ("Gantungan Kunci" in (preset.get("name", "") if preset else ""))

        photo_w_mm = float(data.get("photo_w_mm", 28))
        photo_h_mm = float(data.get("photo_h_mm", 38))

        cut_fits = calculate_cut_fits_per_page(
            master_w_cm=paper["width_mm"] / 10.0,
            master_h_cm=paper["height_mm"] / 10.0,
            cut_w_cm=photo_w_mm / 10.0,
            cut_h_cm=photo_h_mm / 10.0
        )
        effective_slots = quantity * 2 if is_keychain else quantity
        total_sheets_needed = max(1, (effective_slots + cut_fits - 1) // cut_fits)

        if preset and "price_per_pcs" in preset:
            selling_price_total = (preset["price_per_pcs"] * quantity) + accessory_price_total
            hpp_res = calculate_hpp(
                pack_price=paper["pack_price"],
                sheets_per_pack=paper["sheets_per_pack"],
                total_quantity_ordered=effective_slots,
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
        if duplex:
            total_sheets_needed = ((page_count + 1) // 2) * quantity
        else:
            total_sheets_needed = page_count * quantity

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

# ================= UPLOAD ORDER =================

@app.route("/upload", methods=["POST"])
def upload():
    db = load_db()
    nama = request.form.get("nama", "").strip()
    if not nama:
        return jsonify({"error": "Nama pemesan tidak boleh kosong"}), 400

    clean_nama = re.sub(r'[/\:*?"<>|]', "", nama).strip() or "Pelanggan"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder_name = timestamp + "_" + clean_nama
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
        orig_img_path = os.path.join(order_dir, "original_" + clean_nama + ext)
        file.save(orig_img_path)
        saved_files.append(os.path.basename(orig_img_path))

        photo_w_mm = float(request.form.get("photo_w_mm", 28))
        photo_h_mm = float(request.form.get("photo_h_mm", 38))
        crop_json = request.form.get("crop_data", None)
        crop_data = json.loads(crop_json) if crop_json else None
        is_keychain = (preset_name == "goci_akrilik") or ("Gantungan Kunci" in preset_name)

        pdf_filename = "CETAK_" + str(int(photo_w_mm)) + "x" + str(int(photo_h_mm)) + "mm_" + str(quantity) + "pcs_" + clean_nama + ".pdf"
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
            crop_data=crop_data,
            is_keychain_mode=is_keychain
        )
        generated_pdf = pdf_filename
    else:
        for f in uploaded_files:
            if f.filename:
                safe_name = os.path.basename(f.filename)
                target_path = os.path.join(order_dir, safe_name)
                f.save(target_path)
                saved_files.append(safe_name)

    # Build STRUK_PESANAN.txt safely
    struk_lines = [
        "==================================================",
        "              AYDIN PRINT — NOTA ORDER            ",
        "==================================================",
        "Waktu         : " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        "Nama Pemesan  : " + nama,
        "Mode Cetak    : " + ("Foto & Kustom Studio" if mode == "photo_custom" else "Dokumen / Fotocopy"),
        "Preset        : " + (preset_name if preset_name else "-"),
        "Jumlah / Qty  : " + str(quantity) + " pcs/copy",
        "Kertas        : " + paper['name'],
        "Mode Warna    : " + ("Full Color" if color_mode == "COLOR" else "Hitam Putih (B/W)"),
        "Duplex (B-B)  : " + ("Ya (Bolak-Balik)" if duplex else "Tidak (1 Sisi)"),
        "Aksesoris     : " + (accessory['name'] if accessory else "-"),
        "Catatan       : " + (catatan if catatan else "-"),
        "--------------------------------------------------",
        "ESTIMASI TOTAL: Rp " + format(total_price, ","),
        "==================================================",
        "File Pesanan:"
    ]
    for sf in saved_files:
        struk_lines.append("- " + sf)
    if generated_pdf:
        struk_lines.append("- [SIAP CETAK PDF]: " + str(generated_pdf))

    with open(os.path.join(order_dir, "STRUK_PESANAN.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(struk_lines) + "\n")

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
    if not is_admin_authenticated():
        return jsonify([]), 403
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
    if not is_admin_authenticated():
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403
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
    if not is_admin_authenticated():
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403
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

# ================= 1-CLICK WI-FI MODE SWITCHER =================

@app.route("/api/admin/wifi/status", methods=["GET"])
def get_wifi_status():
    if not is_admin_authenticated():
        return jsonify({"status": "error"}), 403
    try:
        res = subprocess.run(["nmcli", "-t", "-f", "NAME,STATE", "connection", "show", "--active"], capture_output=True, text=True)
        active_lines = res.stdout.strip().split("\n")
        is_5g = any("AYDIN-PRINT-5G:activated" in line for line in active_lines)
        is_2g = any("AYDIN-PRINT:activated" in line for line in active_lines)
        current_mode = "5G" if is_5g else ("2G" if is_2g else "Unknown")
        return jsonify({"status": "success", "mode": current_mode, "ssid": "AYDIN-PRINT-5G" if is_5g else "AYDIN-PRINT"})
    except Exception as e:
        return jsonify({"status": "success", "mode": "5G", "ssid": "AYDIN-PRINT-5G"})

@app.route("/api/admin/wifi/switch", methods=["POST"])
def switch_wifi_mode():
    if not is_admin_authenticated():
        return jsonify({"status": "error", "message": "Akses Ditolak"}), 403
    data = request.json or {}
    target_mode = data.get("mode", "5G").upper()

    try:
        if target_mode == "5G":
            subprocess.run(["nmcli", "con", "down", "AYDIN-PRINT"], capture_output=True)
            res = subprocess.run(["nmcli", "con", "up", "AYDIN-PRINT-5G"], capture_output=True, text=True)
            return jsonify({"status": "success", "mode": "5G", "ssid": "AYDIN-PRINT-5G", "message": "Berhasil beralih ke Mode 5GHz (433 Mbps)"})
        else:
            subprocess.run(["nmcli", "con", "down", "AYDIN-PRINT-5G"], capture_output=True)
            res = subprocess.run(["nmcli", "con", "up", "AYDIN-PRINT"], capture_output=True, text=True)
            return jsonify({"status": "success", "mode": "2G", "ssid": "AYDIN-PRINT", "message": "Berhasil beralih ke Mode 2.4GHz (Kompatibel Semua HP)"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
