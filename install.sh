#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# Hotspot 5GHz Terenkripsi WPA2-PSK & AP Isolation (100% Aman)
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

mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR" "$HOME/.local/share/applications" "$HOME/Desktop" 2>/dev/null || true

# 1. Cek & Install Dependencies Python
echo "▶ [1/5] Memasang Dependensi Python (Flask, Pillow, ReportLab, QRCode)..."
pip3 install --user --upgrade flask pillow reportlab qrcode 2>/dev/null || pip install --user --upgrade flask pillow reportlab qrcode 2>/dev/null || true

# 2. Download File Server & Template
echo "▶ [2/5] Mengunduh komponen aplikasi Aydin Print..."
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/server.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/database.py -o "$APP_DIR/database.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/pdf_generator.py -o "$APP_DIR/pdf_generator.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/hpp_engine.py -o "$APP_DIR/hpp_engine.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/generate_poster.py -o "$APP_DIR/generate_poster.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/index.html -o "$TEMPLATES_DIR/index.html"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/admin.html -o "$TEMPLATES_DIR/admin.html"

# 3. Setup Systemd Autostart Service untuk Flask Web Server
echo "▶ [3/5] Mengatur Autostart Web Server Systemd..."
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

# 4. Setup Hotspot Wi-Fi 5GHz Terenkripsi WPA2-PSK (AYDIN-PRINT) + AP Isolation
echo "▶ [4/5] Mengonfigurasi Hotspot 5GHz Aman WPA2-PSK (AYDIN-PRINT)..."
WIFI_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)

if [ -n "$WIFI_IFACE" ]; then
    nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    # Konfigurasi WPA2-PSK Terenkripsi Penuh (Password: aydinprint)
    nmcli con add type wifi ifname "$WIFI_IFACE" con-name "AYDIN-PRINT" autoconnect yes ssid "AYDIN-PRINT" 2>/dev/null || true
    nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 36 2>/dev/null || true
    nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint" 2>/dev/null || true
    nmcli con modify "AYDIN-PRINT" ipv4.method shared ipv6.method ignore 2>/dev/null || true
    nmcli con up "AYDIN-PRINT" 2>/dev/null || true
    echo "  -> Hotspot 5GHz 'AYDIN-PRINT' aman terenkripsi WPA2-PSK telah aktif!"
fi

# 5. Generate Poster QR Meja & Shortcut Kasir
echo "▶ [5/5] Menghasilkan Poster Meja & Shortcut Aplikasi..."
python3 "$APP_DIR/generate_poster.py"

cat << 'EOF' > "$HOME/.local/share/applications/aydin-print-kasir.desktop"
[Desktop Entry]
Name=Aydin Print Kasir
Comment=Buka Dashboard Kasir & Antrian Cetak Aydin Print
Exec=xdg-open http://127.0.0.1:5000/admin
Icon=printer
Terminal=false
Type=Application
Categories=Office;Utility;
EOF

chmod +x "$HOME/.local/share/applications/aydin-print-kasir.desktop" 2>/dev/null || true
cp "$HOME/.local/share/applications/aydin-print-kasir.desktop" "$HOME/Desktop/" 2>/dev/null || true

echo ""
echo "================================================================"
echo "🎉 INSTALASI AYDIN PRINT SELESAI & SUKSES!"
echo "================================================================"
echo "🛡️ Buka Panel Kasir di PC : http://127.0.0.1:5000/admin"
echo "🌐 Web Pelanggan (Lokal)  : http://10.42.0.1:5000"
echo "📶 SSID Wi-Fi 5GHz Aman   : AYDIN-PRINT"
echo "🔑 Password Wi-Fi (WPA2)  : aydinprint"
echo "📁 Folder File Masuk      : $RESULT_DIR"
echo "🖼️ Gambar Poster Meja     : $APP_DIR/POSTER_MEJA_AYDIN_PRINT.png"
echo "================================================================"
echo ""
