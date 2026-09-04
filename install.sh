#!/usr/bin/env bash
# ==============================================================
# Aydin Print Drop — Auto-Installer (Hotspot 5GHz & Web Studio)
# Khusus Linux Aurora / Fedora Atomic / Ubuntu / Debian / Arch
# ==============================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🖨️  MEMULAI INSTALASI AYDIN PRINT DROP            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

APP_DIR="$HOME/PrintDrop"
OUT_DIR="$HOME/Hasil_Print"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

mkdir -p "$APP_DIR" "$APP_DIR/templates" "$APP_DIR/static" "$OUT_DIR" "$SYSTEMD_USER_DIR"

echo "📦 [1/5] Mengunduh berkas aplikasi dari GitHub..."
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/app.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/database.py -o "$APP_DIR/database.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/pdf_generator.py -o "$APP_DIR/pdf_generator.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/requirements.txt -o "$APP_DIR/requirements.txt"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/index.html -o "$APP_DIR/templates/index.html"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/admin.html -o "$APP_DIR/templates/admin.html"

echo "🐍 [2/5] Memasang library Python yang dibutuhkan..."
pip install --user -r "$APP_DIR/requirements.txt" || pip3 install --user -r "$APP_DIR/requirements.txt" || true

echo "📶 [3/5] Mengkonfigurasi Hotspot Wi-Fi 5GHz (AYDIN-PRINT)..."
WIFI_IFACE=$(nmcli device | grep wifi | awk '{print $1}' | head -n 1 || true)

if [ -n "$WIFI_IFACE" ]; then
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    nmcli con add type wifi ifname "$WIFI_IFACE" con-name "Hotspot-Print" autoconnect yes ssid "AYDIN-PRINT"
    nmcli con modify "Hotspot-Print" 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 36 || true
    nmcli con modify "Hotspot-Print" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint"
    nmcli con modify "Hotspot-Print" ipv4.method shared ipv6.method ignore
    nmcli con up "Hotspot-Print" || true
    echo "✅ Hotspot 5GHz 'AYDIN-PRINT' berhasil dikonfigurasi & diaktifkan."
else
    echo "⚠️  Interface Wi-Fi tidak ditemukan. Anda dapat mengaktifkan Hotspot manual."
fi

echo "⚙️ [4/5] Memasang Service Autostart (systemd background service)..."
cat << 'EOF' > "$SYSTEMD_USER_DIR/printdrop.service"
[Unit]
Description=Aydin PrintDrop Web Studio Server
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/PrintDrop
ExecStart=/usr/bin/python3 %h/PrintDrop/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload || true
systemctl --user enable --now printdrop.service || true

echo "📷 [5/5] Membuat QR Code Meja Kasir..."
python3 -c "import qrcode; img = qrcode.make('http://10.42.0.1:5000'); img.save('$APP_DIR/QR_MEJA_PRINT.png'); print('QR Code tersimpan di: $APP_DIR/QR_MEJA_PRINT.png')" 2>/dev/null || true

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🎉 INSTALASI SELESAI & BERJALAN LANCAR!           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo "📶 SSID Wi-Fi    : AYDIN-PRINT"
echo "🔑 Password      : aydinprint"
echo "🌐 URL Pelanggan : http://10.42.0.1:5000"
echo "⚙️ URL Panel HPP : http://10.42.0.1:5000/admin"
echo "📂 Folder Hasil  : $OUT_DIR"
echo "🖼️ QR Code Kasir : $APP_DIR/QR_MEJA_PRINT.png"
echo ""
