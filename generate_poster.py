import os
import qrcode
from PIL import Image, ImageDraw

def generate_posters():
    app_dir = os.path.expanduser("~/PrintDrop")
    os.makedirs(app_dir, exist_ok=True)

    # 1. QR Wi-Fi Universal
    wifi_str = "WIFI:S:AYDIN-PRINT;T:WPA;P:aydinprint;;"
    qr_w = qrcode.QRCode(box_size=12, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_w.add_data(wifi_str)
    qr_w.make(fit=True)
    img_wifi = qr_w.make_image(fill_color="#0284c7", back_color="white").convert("RGBA")

    # 2. QR Web
    url_str = "http://10.42.0.1:5000"
    qr_u = qrcode.QRCode(box_size=12, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_u.add_data(url_str)
    qr_u.make(fit=True)
    img_url = qr_u.make_image(fill_color="#0f172a", back_color="white").convert("RGBA")

    # Canvas
    W, H = 1200, 1600
    poster = Image.new("RGB", (W, H), "#0b0f19")
    draw = ImageDraw.Draw(poster)

    # Accent Border Top
    draw.rectangle([(0, 0), (W, 14)], fill="#0284c7")

    # Outer Frame
    draw.rounded_rectangle([(40, 40), (W - 40, H - 40)], radius=24, fill="#1e293b", outline="#334155", width=3)

    # Brand Title
    draw.text((W // 2, 110), "AYDIN PRINT", fill="#38bdf8", anchor="mm", font_size=58)
    draw.text((W // 2, 170), "PETUNJUK TRANSFER FILE & CETAK DARI HP", fill="#94a3b8", anchor="mm", font_size=22)

    # Box Step 1 (Wi-Fi)
    b1_y = 230
    b_h = 560
    draw.rounded_rectangle([(70, b1_y), (W - 70, b1_y + b_h)], radius=20, fill="#0f172a", outline="#0284c7", width=3)
    draw.rounded_rectangle([(100, b1_y - 20), (520, b1_y + 25)], radius=12, fill="#0284c7")
    draw.text((310, b1_y + 2), "LANGKAH 1: KONEK WI-FI", fill="#ffffff", anchor="mm", font_size=20)

    # Paste QR Wi-Fi
    qr_sz = 400
    img_w_resized = img_wifi.resize((qr_sz, qr_sz))
    poster.paste(img_w_resized, (110, b1_y + 75), img_w_resized)

    # Text Step 1
    t1_x = 550
    draw.text((t1_x, b1_y + 110), "1. Scan QR di samping", fill="#ffffff", font_size=30)
    draw.text((t1_x, b1_y + 165), "2. Ketuk 'Hubungkan Wi-Fi'", fill="#38bdf8", font_size=26)
    draw.text((t1_x, b1_y + 235), "Nama Wi-Fi : AYDIN-PRINT", fill="#38bdf8", font_size=24)
    draw.text((t1_x, b1_y + 275), "Password   : aydinprint", fill="#22c55e", font_size=24)
    draw.text((t1_x, b1_y + 340), "✨ Dukung Semua Tipe HP • Bebas Kuota", fill="#94a3b8", font_size=20)

    # Box Step 2 (Web Cetak)
    b2_y = 830
    draw.rounded_rectangle([(70, b2_y), (W - 70, b2_y + b_h)], radius=20, fill="#0f172a", outline="#22c55e", width=3)
    draw.rounded_rectangle([(100, b2_y - 20), (520, b2_y + 25)], radius=12, fill="#22c55e")
    draw.text((310, b2_y + 2), "LANGKAH 2: BUKA WEB CETAK", fill="#ffffff", anchor="mm", font_size=20)

    # Paste QR Web
    img_u_resized = img_url.resize((qr_sz, qr_sz))
    poster.paste(img_u_resized, (110, b2_y + 75), img_u_resized)

    # Text Step 2
    draw.text((t1_x, b2_y + 110), "1. Scan QR di samping", fill="#ffffff", font_size=30)
    draw.text((t1_x, b2_y + 165), "2. Masukkan Nama Pemesan", fill="#22c55e", font_size=24)
    draw.text((t1_x, b2_y + 215), "3. Upload Dokumen / Foto", fill="#22c55e", font_size=24)
    draw.text((t1_x, b2_y + 265), "4. Klik Kirim Pesanan", fill="#22c55e", font_size=24)
    draw.text((t1_x, b2_y + 340), "🌐 Alamat Web : 10.42.0.1:5000", fill="#94a3b8", font_size=22)

    # Footer
    draw.text((W // 2, 1480), "Setelah kirim file, silakan konfirmasi nama Anda ke kasir.", fill="#64748b", anchor="mm", font_size=20)

    poster_path = os.path.join(app_dir, "POSTER_MEJA_AYDIN_PRINT.png")
    poster.save(poster_path, "PNG")
    print(f"Poster Universal tersimpan di: {poster_path}")

if __name__ == "__main__":
    generate_posters()
