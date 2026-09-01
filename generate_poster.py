import os
import qrcode
from PIL import Image, ImageDraw

def generate_poster():
    output_path = os.path.expanduser("~/PrintDrop/POSTER_MEJA_AYDIN_PRINT.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # QR: Auto Connect Wi-Fi (Triggers Auto Captive Portal Popup on phone)
    wifi_str = "WIFI:S:AYDIN-PRINT;T:WPA;P:aydinprint;;"
    qr_wifi = qrcode.QRCode(box_size=16, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_wifi.add_data(wifi_str)
    qr_wifi.make(fit=True)
    img_wifi = qr_wifi.make_image(fill_color="#0284c7", back_color="white").convert("RGBA")

    # Canvas Poster (High-Res 1200 x 1650 px)
    W, H = 1200, 1650
    poster = Image.new("RGB", (W, H), "#0b0f19")
    draw = ImageDraw.Draw(poster)

    # Top accent line
    draw.rectangle([(0, 0), (W, 16)], fill="#0284c7")

    # Card background
    card_m = 50
    draw.rounded_rectangle([(card_m, 50), (W - card_m, H - 50)], radius=30, fill="#1e293b", outline="#334155", width=4)

    # Header
    draw.text((W // 2, 120), "AYDIN PRINT", fill="#38bdf8", anchor="mm", font_size=64)
    draw.text((W // 2, 185), "LAYANAN CETAK MANDIRI & STUDIO PAS FOTO", fill="#94a3b8", anchor="mm", font_size=24)

    # Main Big QR Box (1x SCAN SAJA)
    box_y = 260
    box_h = 820
    draw.rounded_rectangle([(100, box_y), (W - 100, box_y + box_h)], radius=24, fill="#0f172a", outline="#0284c7", width=4)

    # Badge Heading
    draw.rounded_rectangle([(W // 2 - 320, box_y - 25), (W // 2 + 320, box_y + 35)], radius=16, fill="#0284c7")
    draw.text((W // 2, box_y + 5), "📷 CUKUP 1x SCAN DENGAN KAMERA HP", fill="#ffffff", anchor="mm", font_size=24)

    # Paste Big QR
    qr_size = 500
    img_resized = img_wifi.resize((qr_size, qr_size))
    poster.paste(img_resized, ((W - qr_size) // 2, box_y + 80), img_resized)

    # Instruction Steps Below QR
    draw.text((W // 2, box_y + 630), "1. Arahkan Kamera HP ke QR Code di atas", fill="#f8fafc", anchor="mm", font_size=28)
    draw.text((W // 2, box_y + 685), "2. Ketuk tombol 'Hubungkan ke Wi-Fi'", fill="#38bdf8", anchor="mm", font_size=26)
    draw.text((W // 2, box_y + 740), "3. Web Cetak otomatis terbuka di layar HP Anda!", fill="#22c55e", anchor="mm", font_size=26)

    # Features Banner
    draw.text((W // 2, 1170), "✨ Transfer Cepat 5GHz • Otomatis Crop Pas Foto • Tanpa Kuota Internet", fill="#cbd5e1", anchor="mm", font_size=23)

    # Fallback Info (Small Box)
    draw.rounded_rectangle([(140, 1230), (W - 140, 1420)], radius=16, fill="#0f172a", outline="#334155", width=2)
    draw.text((W // 2, 1275), "Jika web tidak otomatis terbuka:", fill="#94a3b8", anchor="mm", font_size=20)
    draw.text((W // 2, 1320), "Buka browser Google Chrome / Safari, lalu ketik:", fill="#94a3b8", anchor="mm", font_size=20)
    draw.text((W // 2, 1370), "🌐 http://10.42.0.1:5000", fill="#38bdf8", anchor="mm", font_size=28)

    # Footer
    draw.text((W // 2, 1490), "Setelah kirim file, silakan infokan nama Anda ke kasir.", fill="#64748b", anchor="mm", font_size=20)

    poster.save(output_path, "PNG")
    print(f"Poster 1-Scan tersimpan di: {output_path}")

if __name__ == "__main__":
    generate_poster()
