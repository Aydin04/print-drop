#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# Solusi Pasti: Deteksi Wi-Fi Card, Hotspot ON, Firewall, & Web
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
VENV_DIR="$APP_DIR/venv"

mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR" "$HOME/.local/share/applications" "$HOME/Desktop" 2>/dev/null || true

# 1. Setup Virtual Environment (Venv) & Fast Check Dependency
echo "▶ [1/5] Memeriksa & Memasang Dependensi Python..."

if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo "  -> Menyiapkan Virtual Environment Python..."
    python3 -m venv "$VENV_DIR" --system-site-packages 2>/dev/null || python3 -m venv "$VENV_DIR"
fi

PY_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

# Install dependensi yang belum ada
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
    echo "  -> Mengunduh modul:$MISSING_PKGS..."
    "$PIP_BIN" install --upgrade pip 2>/dev/null || true
    "$PIP_BIN" install $MISSING_PKGS
else
    echo "  -> Semua dependensi Python sudah siap!"
fi

# 2. Download Komponen Aplikasi
echo "▶ [2/5] Mengunduh skrip & template..."
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/server.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/database.py -o "$APP_DIR/database.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/pdf_generator.py -o "$APP_DIR/pdf_generator.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/hpp_engine.py -o "$APP_DIR/hpp_engine.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/generate_poster.py -o "$APP_DIR/generate_poster.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/index.html -o "$TEMPLATES_DIR/index.html"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/admin.html -o "$TEMPLATES_DIR/admin.html"

# 3. Setup Systemd Autostart Service
echo "▶ [3/5] Menjalankan Server Web & Autostart..."
mkdir -p "$HOME/.config/systemd/user"
cat << EOF > "$HOME/.config/systemd/user/printdrop.service"
[Unit]
Description=Aydin Print Kasir & Server Studio
After=network.target

[Service]
WorkingDirectory=$APP_DIR
ExecStart=$PY_BIN $APP_DIR/server.py
Restart=always
RestartSec=2
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable printdrop.service
systemctl --user restart printdrop.service

# 4. Deteksi Antarmuka Wi-Fi & Buat Hotspot Standar Teruji
echo "▶ [4/5] Mengaktifkan Hotspot Wi-Fi..."

# Unblock wifi jika ter-softblock oleh rfkill
rfkill unblock wifi 2>/dev/null || true

# Cari antarmuka Wi-Fi fisik
WIFI_DEV=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)

if [ -n "$WIFI_DEV" ]; then
    echo "  -> Menggunakan perangkat Wi-Fi: $WIFI_DEV"
    
    # Hapus profil lama
    nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
    nmcli con delete "AYDIN-PRINT-5G" 2>/dev/null || true
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    
    # Buat Hotspot Menggunakan Perintah Standar NetworkManager
    echo "  -> Menyalakan Hotspot 'AYDIN-PRINT'..."
    nmcli dev wifi hotspot ifname "$WIFI_DEV" ssid "AYDIN-PRINT" password "aydinprint" con-name "AYDIN-PRINT" || {
        # Fallback jika dev wifi hotspot butuh format koneksi manual
        nmcli con add type wifi ifname "$WIFI_DEV" con-name "AYDIN-PRINT" autoconnect yes ssid "AYDIN-PRINT"
        nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap
        nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk
        nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.psk "aydinprint"
        nmcli con modify "AYDIN-PRINT" ipv4.method shared
        nmcli con up "AYDIN-PRINT"
    }
    
    echo "  -> ✅ Hotspot 'AYDIN-PRINT' BERHASIL MEMANCAR!"
else
    echo "  [!] PERINGATAN: Perangkat Wi-Fi tidak ditemukan. Pastikan Wi-Fi Card aktif."
fi

# 5. Generate Poster Meja & Shortcut Aplikasi
echo "▶ [5/5] Membuat Poster Meja & Shortcut Kasir..."
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
echo "🎉 INSTALASI BERHASIL & SELESAI!"
echo "================================================================"
echo "📶 Wi-Fi Hotspot       : AYDIN-PRINT"
echo "🔑 Password Wi-Fi      : aydinprint"
echo "🛡️ Buka Panel Kasir PC : http://127.0.0.1:5000/admin"
echo "🌐 Web Pelanggan       : http://10.42.0.1:5000"
echo "📁 Folder File Masuk   : $RESULT_DIR"
echo "🖼️ Gambar Poster Meja  : $APP_DIR/POSTER_MEJA_AYDIN_PRINT.png"
echo "================================================================"
echo ""
