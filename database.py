import json
import os

DB_FILE = os.path.expanduser("~/PrintDrop/store_data.json")

DEFAULT_DATA = {
    "settings": {
        "store_name": "Aydin Print",
        "electricity_kwh": 1500.0,
        "default_margin_percent": 40.0,
        "margin_type": "MARKUP",  # MARKUP or GROSS_MARGIN
        "profit_per_sheet_min": 500.0,
        "round_price_to": 500
    },
    "printers": [
        {
            "id": 1,
            "name": "Brother DCP-T720DW",
            "purchase_price": 3200000.0,
            "page_capacity": 50000,
            "watt": 16.0,
            "is_default": True
        },
        {
            "id": 2,
            "name": "Epson L800 / L805 (6 Warna Photo)",
            "purchase_price": 4500000.0,
            "page_capacity": 30000,
            "watt": 13.0,
            "is_default": False
        }
    ],
    "inks": [
        {
            "id": 1,
            "printer_id": 1,
            "name": "Brother BTD60BK (Black)",
            "bottle_price": 95000,
            "volume_ml": 108.0,
            "cost_per_ml": 879.6,
            "note": "Kapasitas cetak ~6.500 hal"
        },
        {
            "id": 2,
            "printer_id": 1,
            "name": "Brother BT5000C (Cyan)",
            "bottle_price": 85000,
            "volume_ml": 48.8,
            "cost_per_ml": 1741.8,
            "note": "Kapasitas cetak ~5.000 hal"
        },
        {
            "id": 3,
            "printer_id": 1,
            "name": "Brother BT5000M (Magenta)",
            "bottle_price": 85000,
            "volume_ml": 48.8,
            "cost_per_ml": 1741.8,
            "note": "Kapasitas cetak ~5.000 hal"
        },
        {
            "id": 4,
            "printer_id": 1,
            "name": "Brother BT5000Y (Yellow)",
            "bottle_price": 85000,
            "volume_ml": 48.8,
            "cost_per_ml": 1741.8,
            "note": "Kapasitas cetak ~5.000 hal"
        },
        {
            "id": 5,
            "printer_id": 2,
            "name": "Epson 6-Color Photo Ink Set (T673)",
            "bottle_price": 135000,
            "volume_ml": 70.0,
            "cost_per_ml": 1928.5,
            "note": "70ml per botol (C,M,Y,K,LC,LM)"
        }
    ],
    "papers": [
        {
            "id": 1,
            "name": "HVS 70/75 gsm (A4)",
            "size": "A4",
            "width_mm": 210,
            "height_mm": 297,
            "pack_price": 45000,
            "sheets_per_pack": 500,
            "cost_per_sheet": 90,
            "base_selling_price_bw": 500,
            "base_selling_price_color": 1000,
            "duplex_extra_percent": 80
        },
        {
            "id": 2,
            "name": "HVS 75/80 gsm (F4 / Folio)",
            "size": "F4",
            "width_mm": 215,
            "height_mm": 330,
            "pack_price": 52000,
            "sheets_per_pack": 500,
            "cost_per_sheet": 104,
            "base_selling_price_bw": 500,
            "base_selling_price_color": 1000,
            "duplex_extra_percent": 80
        },
        {
            "id": 3,
            "name": "Glossy Photo Paper 200/230 gsm (A4)",
            "size": "A4",
            "width_mm": 210,
            "height_mm": 297,
            "pack_price": 35000,
            "sheets_per_pack": 20,
            "cost_per_sheet": 1750,
            "base_selling_price_bw": 3000,
            "base_selling_price_color": 5000,
            "duplex_extra_percent": 0
        },
        {
            "id": 4,
            "name": "Glossy Photo Paper 4R",
            "size": "4R",
            "width_mm": 102,
            "height_mm": 152,
            "pack_price": 25000,
            "sheets_per_pack": 50,
            "cost_per_sheet": 500,
            "base_selling_price_bw": 1500,
            "base_selling_price_color": 2500,
            "duplex_extra_percent": 0
        },
        {
            "id": 5,
            "name": "Stiker Glossy / Vinyl (A4)",
            "size": "A4",
            "width_mm": 210,
            "height_mm": 297,
            "pack_price": 40000,
            "sheets_per_pack": 20,
            "cost_per_sheet": 2000,
            "base_selling_price_bw": 4000,
            "base_selling_price_color": 6000,
            "duplex_extra_percent": 0
        }
    ],
    "accessories": [
        {
            "id": 1,
            "name": "Gantungan Kunci Akrilik Insert Foto (Kotak/Bulat)",
            "pack_price": 125000,
            "pack_quantity": 50,
            "unit_price": 2500,
            "selling_price": 6000,
            "stock_note": "Termasuk ring gantungan"
        },
        {
            "id": 2,
            "name": "Plastik ID Card / Tali Lanyard",
            "pack_price": 150000,
            "pack_quantity": 100,
            "unit_price": 1500,
            "selling_price": 4000,
            "stock_note": "Ukuran KTP / B2"
        },
        {
            "id": 3,
            "name": "Jilid Mika / Lakban Biasa",
            "pack_price": 100000,
            "pack_quantity": 100,
            "unit_price": 1000,
            "selling_price": 3000,
            "stock_note": "Mika Depan & Belakang Buffalo"
        },
        {
            "id": 4,
            "name": "Laminasi Panas Glossy / Doff (A4)",
            "pack_price": 80000,
            "pack_quantity": 100,
            "unit_price": 800,
            "selling_price": 2000,
            "stock_note": "Plastik Laminating 100 mic"
        }
    ],
    "presets": [
        {
            "id": "goci_akrilik",
            "name": "Paket Gantungan Kunci Akrilik Foto (2 Sisi)",
            "category": "Aksesoris",
            "photo_width_mm": 40,
            "photo_height_mm": 55,
            "paper_id": 3,
            "accessory_id": 1,
            "suggested_price": 8000,
            "description": "Cetak 2 foto bolak-balik + Casing Akrilik Gantungan Kunci"
        },
        {
            "id": "pasfoto_2x3",
            "name": "Pas Foto 2x3 cm",
            "category": "Pas Foto",
            "photo_width_mm": 20,
            "photo_height_mm": 30,
            "paper_id": 3,
            "price_per_pcs": 1000,
            "description": "Standar Ijazah / Dokumen Resmi (2.0 x 3.0 cm)"
        },
        {
            "id": "pasfoto_3x4",
            "name": "Pas Foto 3x4 cm",
            "category": "Pas Foto",
            "photo_width_mm": 28,
            "photo_height_mm": 38,
            "paper_id": 3,
            "price_per_pcs": 1250,
            "description": "Standar Ijazah, KUA, CPNS (2.8 x 3.8 cm)"
        },
        {
            "id": "pasfoto_4x6",
            "name": "Pas Foto 4x6 cm",
            "category": "Pas Foto",
            "photo_width_mm": 38,
            "photo_height_mm": 56,
            "paper_id": 3,
            "price_per_pcs": 1500,
            "description": "Standar Paspor, SKCK (3.8 x 5.6 cm)"
        },
        {
            "id": "foto_2r",
            "name": "Cetak Foto 2R (6 x 9 cm)",
            "category": "Cetak Foto",
            "photo_width_mm": 60,
            "photo_height_mm": 90,
            "paper_id": 3,
            "price_per_pcs": 2000,
            "description": "Ukuran Dompet / Polaroid Mini"
        },
        {
            "id": "foto_4r",
            "name": "Cetak Foto 4R (10 x 15 cm)",
            "category": "Cetak Foto",
            "photo_width_mm": 102,
            "photo_height_mm": 152,
            "paper_id": 4,
            "price_per_pcs": 3000,
            "description": "Ukuran Standar Pigura / Album Foto"
        }
    ]
}

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DATA)
        return DEFAULT_DATA
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure keys exist
            for k, v in DEFAULT_DATA.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return DEFAULT_DATA

def save_db(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
