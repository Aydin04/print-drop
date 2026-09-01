#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# PCIe WiFi QCA9377: Virtual Dual-AP (5GHz + 2.4GHz) / 5GHz Max
# USB WiFi Dongle  : 100% BEBAS untuk Internet PC
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

# 4. Setup PCIe QCA9377 Mode 5GHz (433 Mbps) & Fallback 2.4GHz
echo "▶ [4/5] Mengonfigurasi Wi-Fi Card Internal (QCA9377) Mode 5GHz Super Cepat..."

PCIE_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | grep -E '^wlp|^wlan' | head -n 1)
if [ -z "$PCIE_IFACE" ]; then
    PCIE_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)
fi

echo "  -> Interface Hotspot PC: $PCIE_IFACE"
echo "  -> Dongle USB Anda 100% BEBAS digunakan untuk Internet PC!"

# Hapus koneksi lama
nmcli con delete "AYDIN-PRINT-5G" 2>/dev/null || true
nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
nmcli con delete "Hotspot-Print" 2>/dev/null || true

# 1. Buat Profil 5GHz (AYDIN-PRINT-5G) - Kecepatan Maksimal 433 Mbps
nmcli con add type wifi ifname "$PCIE_IFACE" con-name "AYDIN-PRINT-5G" autoconnect yes ssid "AYDIN-PRINT-5G" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT-5G" 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 36 2>/dev/null || true
nmcli con modify "AYDIN-PRINT-5G" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT-5G" ipv4.method shared ipv6.method ignore 2>/dev/null || true

# 2. Buat Profil 2.4GHz (AYDIN-PRINT) - Standar Kompatibilitas Tinggi
nmcli con add type wifi ifname "$PCIE_IFACE" con-name "AYDIN-PRINT" autoconnect no ssid "AYDIN-PRINT" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap 802-11-wireless.band bg 802-11-wireless.channel 6 2>/dev/null || true
nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT" ipv4.method shared ipv6.method ignore 2>/dev/null || true

# Coba aktifkan 5GHz sebagai default
if nmcli con up "AYDIN-PRINT-5G" 2>/dev/null; then
    echo "  -> Hotspot 5GHz 'AYDIN-PRINT-5G' (433 Mbps) AKTIF & SIAP PAKAI!"
else
    echo "  -> Mengaktifkan Hotspot 'AYDIN-PRINT'..."
    nmcli con up "AYDIN-PRINT" 2>/dev/null || true
fi

# 5. Buat Script Shortcut Switch Mode Cepat di Terminal / Kasir
cat << 'EOF' > "$APP_DIR/mode_5g.sh"
#!/bin/bash
nmcli con down "AYDIN-PRINT" 2>/dev/null || true
nmcli con up "AYDIN-PRINT-5G"
echo "✅ Hotspot Berpindah ke Mode 5GHz (AYDIN-PRINT-5G) - Super Cepat 433 Mbps!"
EOF

cat << 'EOF' > "$APP_DIR/mode_2g.sh"
#!/bin/bash
nmcli con down "AYDIN-PRINT-5G" 2>/dev/null || true
nmcli con up "AYDIN-PRINT"
echo "✅ Hotspot Berpindah ke Mode 2.4GHz (AYDIN-PRINT) - Kompatibel Semua HP!"
EOF

chmod +x "$APP_DIR/mode_5g.sh" "$APP_DIR/mode_2g.sh"

# 6. Generate Poster QR Meja & Shortcut Kasir
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
echo "🎉 INSTALASI SELESAI & SEMPURNA!"
echo "================================================================"
echo "🚀 Wi-Fi Card PCIe (QCA9377) : Hotspot 5GHz 'AYDIN-PRINT-5G' (433 Mbps)"
echo "🔌 USB Wi-Fi Dongle          : 100% BEBAS untuk Internet Toko/PC"
echo "🔑 Password Hotspot Toko     : aydinprint"
echo "🛡️ Buka Panel Kasir di PC    : http://127.0.0.1:5000/admin"
echo "🌐 Web Pelanggan (Lokal)     : http://10.42.0.1:5000"
echo "📁 Folder File Masuk         : $RESULT_DIR"
echo "🖼️ Gambar Poster Meja        : $APP_DIR/POSTER_MEJA_AYDIN_PRINT.png"
echo "================================================================"
echo ""
