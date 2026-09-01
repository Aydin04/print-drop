#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# Hotspot Wi-Fi 5GHz (QCA9377) & Web Server Autostart
# Khusus Linux Aurora / Fedora Atomic / Ubuntu / Arch
# ==============================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🖨️  MEMULAI INSTALASI AYDIN PRINT STUDIO         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

APP_DIR="$HOME/PrintDrop"
RESULT_DIR="$HOME/Hasil_Print"
TEMPLATES_DIR="$APP_DIR/templates"

mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR"

# 1. Cek & Install Dependencies Python
echo "▶ [1/5] Memasang Dependensi Python (Flask, Pillow, ReportLab, QRCode)..."
pip3 install --user --upgrade flask pillow reportlab qrcode 2>/dev/null || pip install --user --upgrade flask pillow reportlab qrcode 2>/dev/null || true

# 2. Download File Server & Template
echo "▶ [2/5] Mengunduh komponen aplikasi Aydin Print..."
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/server.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/database.py -o "$APP_DIR/database.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/pdf_generator.py -o "$APP_DIR/pdf_generator.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/hpp_engine.py -o "$APP_DIR/hpp_engine.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/index.html -o "$TEMPLATES_DIR/index.html"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/admin.html -o "$TEMPLATES_DIR/admin.html"

# 3. Setup Systemd Autostart Service
echo "▶ [3/5] Mengatur Autostart Systemd..."
mkdir -p "$HOME/.config/systemd/user"
cat << 'EOF' > "$HOME/.config/systemd/user/printdrop.service"
[Unit]
Description=Aydin Print Kasir & Server Studio
After=network.target

[Service]
WorkingDirectory=%h/PrintDrop
ExecStart=/usr/bin/python3 %h/PrintDrop/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable printdrop.service
systemctl --user restart printdrop.service

# 4. Setup Hotspot 5GHz via NetworkManager (SSID: AYDIN-PRINT)
echo "▶ [4/5] Mengonfigurasi Hotspot 5GHz (AYDIN-PRINT)..."
WIFI_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)

if [ -n "$WIFI_IFACE" ]; then
    nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    nmcli con add type wifi ifname "$WIFI_IFACE" con-name "AYDIN-PRINT" autoconnect yes ssid "AYDIN-PRINT" 2>/dev/null || true
    nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 36 2>/dev/null || true
    nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint" 2>/dev/null || true
    nmcli con modify "AYDIN-PRINT" ipv4.method shared ipv6.method ignore 2>/dev/null || true
    nmcli con up "AYDIN-PRINT" 2>/dev/null || true
    echo "  -> Hotspot 5GHz 'AYDIN-PRINT' berhasil diaktifkan!"
else
    echo "  [!] Interface WiFi tidak ditemukan atau sedang dinonaktifkan."
fi

# 5. Generate QR Code Image untuk Meja Kasir
echo "▶ [5/5] Menghasilkan QR Code Meja Kasir..."
python3 - << 'EOF'
import qrcode
import os

url = "http://10.42.0.1:5000"
img = qrcode.make(url)
img.save(os.path.expanduser("~/PrintDrop/QR_AYDIN_PRINT.png"))
EOF

echo ""
echo "================================================================"
echo "🎉 INSTALASI AYDIN PRINT SELESAI & SUKSES!"
echo "================================================================"
echo "📶 SSID Wi-Fi Hotspot : AYDIN-PRINT"
echo "🔑 Password Wi-Fi     : aydinprint"
echo "🌐 Web Pelanggan      : http://10.42.0.1:5000"
echo "🛡️ Panel Kasir / Admin : http://10.42.0.1:5000/admin"
echo "📁 Folder File Masuk  : $RESULT_DIR"
echo "🖼️ Gambar QR Meja     : $APP_DIR/QR_AYDIN_PRINT.png"
echo "================================================================"
echo ""
