#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# Robust Python venv & Fast Dependency Check (Linux Aurora/Atomic)
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
VENV_DIR="$APP_DIR/venv"

mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR" "$HOME/.local/share/applications" "$HOME/Desktop" 2>/dev/null || true

# 1. Setup Virtual Environment (Venv) & Fast Check Dependency
echo "▶ [1/5] Memeriksa & Memasang Dependensi Python..."

# Buat venv jika belum ada
if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo "  -> Menyiapkan Virtual Environment Python mandiri..."
    python3 -m venv "$VENV_DIR" --system-site-packages 2>/dev/null || python3 -m venv "$VENV_DIR"
fi

PY_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

# Cek apakah modul sudah terpasang
MISSING_PKGS=""
for pkg in flask PIL reportlab qrcode; do
    if ! "$PY_BIN" -c "import $pkg" 2>/dev/null; then
        case "$pkg" in
            PIL) MISSING_PKGS="$MISSING_PKGS pillow" ;;
            *) MISSING_PKGS="$MISSING_PKGS $pkg" ;;
        esac
    fi
done

if [ -n "$MISSING_PKGS" ]; then
    echo "  -> Mengunduh dependensi yang belum ada:$MISSING_PKGS..."
    "$PIP_BIN" install --upgrade pip 2>/dev/null || true
    "$PIP_BIN" install $MISSING_PKGS
else
    echo "  -> Semua dependensi Python sudah lengkap! (Skip download)"
fi

# 2. Download / Update File Server & Template
echo "▶ [2/5] Memperbarui komponen aplikasi Aydin Print..."
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/server.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/database.py -o "$APP_DIR/database.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/pdf_generator.py -o "$APP_DIR/pdf_generator.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/hpp_engine.py -o "$APP_DIR/hpp_engine.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/generate_poster.py -o "$APP_DIR/generate_poster.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/index.html -o "$TEMPLATES_DIR/index.html"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/admin.html -o "$TEMPLATES_DIR/admin.html"

# 3. Setup Systemd Autostart Service menggunakan Python Venv
echo "▶ [3/5] Mengatur Autostart Web Server Systemd..."
mkdir -p "$HOME/.config/systemd/user"
cat << EOF > "$HOME/.config/systemd/user/printdrop.service"
[Unit]
Description=Aydin Print Kasir & Server Studio
After=network.target

[Service]
WorkingDirectory=$APP_DIR
ExecStart=$PY_BIN $APP_DIR/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable printdrop.service
systemctl --user restart printdrop.service

# 4. Setup PCIe QCA9377 Mode 5GHz & 2.4GHz
echo "▶ [4/5] Mengonfigurasi Wi-Fi Card Internal (QCA9377)..."

PCIE_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | grep -E '^wlp|^wlan' | head -n 1)
if [ -z "$PCIE_IFACE" ]; then
    PCIE_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)
fi

echo "  -> Interface Hotspot: $PCIE_IFACE"

nmcli con delete "AYDIN-PRINT-5G" 2>/dev/null || true
nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
nmcli con delete "Hotspot-Print" 2>/dev/null || true

# Profil 5GHz (AYDIN-PRINT-5G)
nmcli con add type wifi ifname "$PCIE_IFACE" con-name "AYDIN-PRINT-5G" autoconnect yes ssid "AYDIN-PRINT-5G" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT-5G" 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 36 2>/dev/null || true
nmcli con modify "AYDIN-PRINT-5G" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT-5G" ipv4.method shared ipv6.method ignore 2>/dev/null || true

# Profil 2.4GHz (AYDIN-PRINT)
nmcli con add type wifi ifname "$PCIE_IFACE" con-name "AYDIN-PRINT" autoconnect no ssid "AYDIN-PRINT" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap 802-11-wireless.band bg 802-11-wireless.channel 6 2>/dev/null || true
nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "aydinprint" 2>/dev/null || true
nmcli con modify "AYDIN-PRINT" ipv4.method shared ipv6.method ignore 2>/dev/null || true

if nmcli con up "AYDIN-PRINT-5G" 2>/dev/null; then
    echo "  -> Hotspot 5GHz 'AYDIN-PRINT-5G' (433 Mbps) AKTIF!"
else
    echo "  -> Mengaktifkan Hotspot 'AYDIN-PRINT'..."
    nmcli con up "AYDIN-PRINT" 2>/dev/null || true
fi

# 5. Generate Poster Meja & Shortcut Kasir
echo "▶ [5/5] Menghasilkan Poster Meja & Shortcut Aplikasi..."
"$PY_BIN" "$APP_DIR/generate_poster.py"

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
echo "📶 SSID Wi-Fi Hotspot     : AYDIN-PRINT-5G / AYDIN-PRINT"
echo "🔑 Password Wi-Fi (WPA2)  : aydinprint"
echo "📁 Folder File Masuk      : $RESULT_DIR"
echo "🖼️ Gambar Poster Meja     : $APP_DIR/POSTER_MEJA_AYDIN_PRINT.png"
echo "================================================================"
echo ""
