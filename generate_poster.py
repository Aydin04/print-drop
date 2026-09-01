import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_poster():
    output_path = os.path.expanduser("~/PrintDrop/POSTER_MEJA_AYDIN_PRINT.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Generate QR Codes
    # QR 1: Auto Connect Wi-Fi
    wifi_str = "WIFI:S:AYDIN-PRINT;T:WPA;P:aydinprint;;"
    qr_wifi = qrcode.QRCode(box_size=12, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_wifi.add_data(wifi_str)
    qr_wifi.make(fit=True)
    img_wifi = qr_wifi.make_image(fill_color="#0284c7", back_color="white").convert("RGBA")

    # QR 2: Web URL
    url_str = "http://10.42.0.1:5000"
    qr_url = qrcode.QRCode(box_size=12, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_url.add_data(url_str)
    qr_url.make(fit=True)
    img_url = qr_url.make_image(fill_color="#0f172a", back_color="white").convert("RGBA")

    # 2. Canvas Poster (High-Res 1200 x 1700 px)
    W, H = 1200, 1750
    poster = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(poster)

    # Gradient Top Banner Accent
    draw.rectangle([(0, 0), (W, 16)], fill="#0284c7")

    # Brand Title
    # Draw nice rounded card container
    card_margin = 50
    draw.rounded_rectangle([(card_margin, 60), (W - card_margin, H - 60)], radius=30, fill="#1e293b", outline="#334155", width=4)

    # Title Banner
    draw.text((W // 2, 130), "AYDIN PRINT", fill="#38bdf8", anchor="mm", font_size=64)
    draw.text((W // 2, 200), "LAYANAN CETAK SELF-SERVICE & STUDIO PAS FOTO", fill="#94a3b8", anchor="mm", font_size=24)

    # Section 1: Scan Wi-Fi
    sec1_y = 300
    draw.rounded_rectangle([(100, sec1_y), (W - 100, sec1_y + 450)], radius=20, fill="#0f172a", outline="#0284c7", width=3)
    
    # Text badge
    draw.rounded_rectangle([(140, sec1_y - 20), (520, sec1_y + 25)], radius=12, fill="#0284c7")
    draw.text((330, sec1_y + 2), "LANGKAH 1: HUBUNGKAN WI-FI", fill="#ffffff", anchor="mm", font_size=20)

    # Place QR Wi-Fi
    qr_size = 340
    img_wifi_resized = img_wifi.resize((qr_size, qr_size))
    poster.paste(img_wifi_resized, (150, sec1_y + 60), img_wifi_resized)

    # Wi-Fi instructions on right side
    tx_x = 540
    draw.text((tx_x, sec1_y + 90), "Scan QR di samping:", fill="#f8fafc", font_size=28)
    draw.text((tx_x, sec1_y + 140), "HP Anda akan otomatis", fill="#94a3b8", font_size=22)
    draw.text((tx_x, sec1_y + 175), "terhubung ke Wi-Fi Toko.", fill="#94a3b8", font_size=22)

    draw.text((tx_x, sec1_y + 240), "Atau Sambungkan Manual:", fill="#cbd5e1", font_size=22)
    draw.text((tx_x, sec1_y + 280), "SSID : AYDIN-PRINT", fill="#38bdf8", font_size=24)
    draw.text((tx_x, sec1_y + 320), "Pass : aydinprint", fill="#38bdf8", font_size=24)

    # Section 2: Scan Web Upload
    sec2_y = 800
    draw.rounded_rectangle([(100, sec2_y), (W - 100, sec2_y + 450)], radius=20, fill="#0f172a", outline="#22c55e", width=3)

    # Text badge
    draw.rounded_rectangle([(140, sec2_y - 20), (520, sec2_y + 25)], radius=12, fill="#22c55e")
    draw.text((330, sec2_y + 2), "LANGKAH 2: BUKA WEB CETAK", fill="#ffffff", anchor="mm", font_size=20)

    # Place QR Web
    img_url_resized = img_url.resize((qr_size, qr_size))
    poster.paste(img_url_resized, (150, sec2_y + 60), img_url_resized)

    # Web instructions on right side
    draw.text((tx_x, sec2_y + 90), "Scan QR untuk Upload:", fill="#f8fafc", font_size=28)
    draw.text((tx_x, sec2_y + 140), "1. Masukkan Nama Pemesan", fill="#94a3b8", font_size=22)
    draw.text((tx_x, sec2_y + 180), "2. Pilih Dokumen / Pas Foto", fill="#94a3b8", font_size=22)
    draw.text((tx_x, sec2_y + 220), "3. Crop & Atur Rangkap", fill="#94a3b8", font_size=22)
    draw.text((tx_x, sec2_y + 260), "4. Klik Kirim Pesanan", fill="#94a3b8", font_size=22)
    draw.text((tx_x, sec2_y + 320), "🌐 http://10.42.0.1:5000", fill="#22c55e", font_size=24)

    # Footer Notes
    draw.text((W // 2, 1340), "⚡ Kecepatan Wi-Fi 5GHz • Tanpa Kuota Internet • Cepat & Aman", fill="#38bdf8", anchor="mm", font_size=24)
    draw.text((W // 2, 1390), "Setelah kirim, silakan konfirmasi ke kasir untuk proses cetak.", fill="#64748b", anchor="mm", font_size=20)

    poster.save(output_path, "PNG")
    print(f"Poster stand QR meja tersimpan di: {output_path}")

if __name__ == "__main__":
    generate_poster()
