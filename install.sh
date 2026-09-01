#!/usr/bin/env bash
# ==============================================================
# PrintDrop Auto-Installer (Hotspot 5GHz & Auto Web Print Server)
# Khusus Linux Aurora / Fedora Atomic / Ubuntu / Arch
# ==============================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🖨️  MEMULAI INSTALASI PRINTDROP OTOMATIS          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

APP_DIR="$HOME/PrintDrop"
RESULT_DIR="$HOME/Hasil_Print"
mkdir -p "$APP_DIR" "$RESULT_DIR"

# 1. Cek & Install Dependencies
echo "▶ [1/4] Memasang Python Flask & QRCode Generator..."
pip3 install --user --upgrade flask qrcode pillow 2>/dev/null || pip install --user --upgrade flask qrcode pillow 2>/dev/null || true

# 2. Download File server.py
echo "▶ [2/4] Mengunduh server backend PrintDrop..."
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/server.py"

# 3. Setup Systemd Autostart Service
echo "▶ [3/4] Mengatur Autostart Systemd..."
mkdir -p "$HOME/.config/systemd/user"
cat << 'EOF' > "$HOME/.config/systemd/user/printdrop.service"
[Unit]
Description=PrintDrop Server Kasir
After=network.target

[Service]
ExecStart=/usr/bin/python3 %h/PrintDrop/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable printdrop.service
systemctl --user restart printdrop.service

# 4. Setup Hotspot 5GHz via NetworkManager (QCA9377)
echo "▶ [4/4] Mengonfigurasi Hotspot 5GHz..."
WIFI_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)

if [ -n "$WIFI_IFACE" ]; then
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    nmcli con add type wifi ifname "$WIFI_IFACE" con-name "Hotspot-Print" autoconnect yes ssid "PRINT-GRATIS" 2>/dev/null || true
    nmcli con modify "Hotspot-Print" 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 36 2>/dev/null || true
    nmcli con modify "Hotspot-Print" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "printgratis" 2>/dev/null || true
    nmcli con modify "Hotspot-Print" ipv4.method shared ipv6.method ignore 2>/dev/null || true
    nmcli con up "Hotspot-Print" 2>/dev/null || true
    echo "  -> Hotspot 5GHz 'PRINT-GRATIS' berhasil diaktifkan!"
else
    echo "  [!] Interface WiFi tidak ditemukan atau sedang dinonaktifkan."
fi

# 5. Generate QR Code Image
python3 - << 'EOF'
import qrcode
import os

url = "http://10.42.0.1:5000"
img = qrcode.make(url)
img.save(os.path.expanduser("~/PrintDrop/QR_MEJA_PRINT.png"))
EOF

echo ""
echo "================================================================"
echo "🎉 INSTALASI SELESAI & SUKSES!"
echo "================================================================"
echo "📶 SSID WiFi Hotspot : PRINT-GRATIS"
echo "🔑 Password WiFi     : printgratis"
echo "🌐 URL Web Print     : http://10.42.0.1:5000"
echo "📁 Folder File Masuk : $RESULT_DIR"
echo "🖼️ Gambar QR Meja    : $APP_DIR/QR_MEJA_PRINT.png"
echo "================================================================"
echo ""
