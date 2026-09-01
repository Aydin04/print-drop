import json
import os

DB_FILE = os.path.expanduser("~/PrintDrop/store_data.json")

DEFAULT_DATA = {
    "settings": {
        "store_name": "Aydin Print",
        "tagline": "Percetakan, Fotocopy & Studio Pas Foto",
        "electricity_kwh": 1500.0,
        "default_margin_percent": 40.0,
        "margin_type": "MARKUP",
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
            "supports_duplex": True,
            "is_default": True
        },
        {
            "id": 2,
            "name": "Epson L800 / L805 (6 Warna Photo)",
            "purchase_price": 4500000.0,
            "page_capacity": 30000,
            "watt": 13.0,
            "supports_duplex": False,
            "is_default": False
        }
    ],
    "inks": [
        {
            "id": 1,
            "name": "Tinta Brother BTD60BK / BT5000 CMYK",
            "bottle_price": 95000.0,
            "bottle_ml": 108.0,
            "avg_price_per_ml": 880.0
        },
        {
            "id": 2,
            "name": "Tinta Epson 673 6-Color Photo",
            "bottle_price": 125000.0,
            "bottle_ml": 70.0,
            "avg_price_per_ml": 1785.0
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
            "base_selling_price_bw": 3000,
            "base_selling_price_color": 5000,
            "duplex_extra_percent": 0
        },
        {
            "id": 4,
            "name": "Glossy Photo Paper 4R (10.2 x 15.2 cm)",
            "size": "4R",
            "width_mm": 102,
            "height_mm": 152,
            "pack_price": 25000,
            "sheets_per_pack": 50,
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
            "base_selling_price_bw": 4000,
            "base_selling_price_color": 6000,
            "duplex_extra_percent": 0
        },
        {
            "id": 6,
            "name": "Art Paper / Ivory 210/260 gsm (A4)",
            "size": "A4",
            "width_mm": 210,
            "height_mm": 297,
            "pack_price": 48000,
            "sheets_per_pack": 50,
            "base_selling_price_bw": 2500,
            "base_selling_price_color": 4000,
            "duplex_extra_percent": 60
        }
    ],
    "accessories": [
        {
            "id": 1,
            "name": "Gantungan Kunci Akrilik Insert Foto Kotak (40x55mm)",
            "unit_price": 2500,
            "selling_price": 6000,
            "stock_note": "Termasuk ring putar rantai"
        },
        {
            "id": 2,
            "name": "Gantungan Kunci Akrilik Bulat (Diameter 45mm)",
            "unit_price": 2500,
            "selling_price": 6000,
            "stock_note": "Termasuk ring putar rantai"
        },
        {
            "id": 3,
            "name": "Plastik ID Card / Tali Lanyard (B2 / KTP)",
            "unit_price": 1500,
            "selling_price": 4000,
            "stock_note": "Bahan tebal transparan"
        },
        {
            "id": 4,
            "name": "Laminasi Panas Glossy / Doff (A4)",
            "unit_price": 800,
            "selling_price": 2000,
            "stock_note": "Plastik laminating 100 mic"
        },
        {
            "id": 5,
            "name": "Jilid Lakban Mika Bening + Buffalo",
            "unit_price": 1000,
            "selling_price": 3000,
            "stock_note": "Mika Depan & Buffalo Belakang"
        },
        {
            "id": 6,
            "name": "Jilid Spiral Kawat (A4)",
            "unit_price": 3000,
            "selling_price": 8000,
            "stock_note": "Spiral kawat putih/hitam"
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
            "profit_per_unit": 3500,
            "suggested_price": 8000,
            "description": "Cetak 2 sisi foto + Casing Akrilik Gantungan Kunci"
        },
        {
            "id": "pasfoto_2x3",
            "name": "Pas Foto 2x3 cm",
            "category": "Pas Foto",
            "photo_width_mm": 20,
            "photo_height_mm": 30,
            "paper_id": 3,
            "accessory_id": None,
            "profit_per_unit": 700,
            "price_per_pcs": 1000,
            "description": "Standar Ijazah / Dokumen Resmi"
        },
        {
            "id": "pasfoto_3x4",
            "name": "Pas Foto 3x4 cm",
            "category": "Pas Foto",
            "photo_width_mm": 28,
            "photo_height_mm": 38,
            "paper_id": 3,
            "accessory_id": None,
            "profit_per_unit": 800,
            "price_per_pcs": 1250,
            "description": "Standar Ijazah, KUA, CPNS, Kedinasan"
        },
        {
            "id": "pasfoto_4x6",
            "name": "Pas Foto 4x6 cm",
            "category": "Pas Foto",
            "photo_width_mm": 38,
            "photo_height_mm": 56,
            "paper_id": 3,
            "accessory_id": None,
            "profit_per_unit": 900,
            "price_per_pcs": 1500,
            "description": "Standar Paspor, SKCK, Visa"
        },
        {
            "id": "foto_2r",
            "name": "Cetak Foto 2R (6 x 9 cm)",
            "category": "Cetak Foto",
            "photo_width_mm": 60,
            "photo_height_mm": 90,
            "paper_id": 3,
            "accessory_id": None,
            "profit_per_unit": 1000,
            "price_per_pcs": 2000,
            "description": "Ukuran Dompet / Mini Album"
        },
        {
            "id": "foto_3r",
            "name": "Cetak Foto 3R (8.9 x 12.7 cm)",
            "category": "Cetak Foto",
            "photo_width_mm": 89,
            "photo_height_mm": 127,
            "paper_id": 3,
            "accessory_id": None,
            "profit_per_unit": 1200,
            "price_per_pcs": 2500,
            "description": "Ukuran Standar Foto Cetak 3R"
        },
        {
            "id": "foto_4r",
            "name": "Cetak Foto 4R (10.2 x 15.2 cm)",
            "category": "Cetak Foto",
            "photo_width_mm": 102,
            "photo_height_mm": 152,
            "paper_id": 4,
            "accessory_id": None,
            "profit_per_unit": 1500,
            "price_per_pcs": 3000,
            "description": "Ukuran Standar Pigura / Album 4R"
        },
        {
            "id": "foto_polaroid",
            "name": "Foto Polaroid Mini (5.4 x 8.6 cm)",
            "category": "Cetak Foto",
            "photo_width_mm": 54,
            "photo_height_mm": 86,
            "paper_id": 3,
            "accessory_id": None,
            "profit_per_unit": 800,
            "price_per_pcs": 1500,
            "description": "Foto Gaya Polaroid Mini Estetik"
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
            # Ensure all root keys exist
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
