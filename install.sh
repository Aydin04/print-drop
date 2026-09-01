#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# Dengan VERBOSE LOGGING & Live Diagnostics Lengkap
# ==============================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🖨️  MEMULAI INSTALASI AYDIN PRINT STUDIO (VERBOSE)     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

APP_DIR="$HOME/PrintDrop"
RESULT_DIR="$HOME/Hasil_Print"
TEMPLATES_DIR="$APP_DIR/templates"
VENV_DIR="$APP_DIR/venv"

echo -e "${BLUE}[INFO]${NC} Menyiapkan direktori aplikasi..."
echo "  -> App Dir: $APP_DIR"
echo "  -> Result Dir: $RESULT_DIR"
mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR" "$HOME/.local/share/applications" "$HOME/Desktop" 2>/dev/null || true

# 1. Setup Virtual Environment & Fast Check Dependency
echo ""
echo -e "${BOLD}${BLUE}▶ [1/5] Memeriksa & Menyiapkan Python Environment...${NC}"

if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo -e "  ${YELLOW}[i]${NC} Membuat Python Virtual Environment baru di $VENV_DIR..."
    python3 -m venv "$VENV_DIR" --system-site-packages 2>/dev/null || python3 -m venv "$VENV_DIR"
    echo -e "  ${GREEN}[✓]${NC} Virtual environment berhasil dibuat."
else
    echo -e "  ${GREEN}[✓]${NC} Virtual environment sudah ada: $VENV_DIR"
fi

PY_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

echo "  -> Python Binary : $("$PY_BIN" --version 2>&1)"
echo "  -> Pip Binary    : $("$PIP_BIN" --version 2>&1)"

MISSING_PKGS=""
for pkg in flask PIL reportlab qrcode; do
    echo -n "  -> Memeriksa modul '$pkg'... "
    if "$PY_BIN" -c "import $pkg" 2>/dev/null; then
        echo -e "${GREEN}[TERPASANG]${NC}"
    else
        echo -e "${RED}[BELUM ADA]${NC}"
        case "$pkg" in
            PIL) MISSING_PKGS="$MISSING_PKGS pillow" ;;
            *) MISSING_PKGS="$MISSING_PKGS $pkg" ;;
        esac
    fi
done

if [ -n "$MISSING_PKGS" ]; then
    echo -e "  ${YELLOW}[i]${NC} Mengunduh modul yang kurang:${BOLD}$MISSING_PKGS${NC}..."
    "$PIP_BIN" install --upgrade pip 2>/dev/null || true
    "$PIP_BIN" install $MISSING_PKGS
    echo -e "  ${GREEN}[✓]${NC} Semua dependensi berhasil dipasang."
else
    echo -e "  ${GREEN}[✓]${NC} Semua dependensi Python sudah lengkap."
fi

# 2. Download Komponen Aplikasi
echo ""
echo -e "${BOLD}${BLUE}▶ [2/5] Mengunduh Skrip & Template Web Aydin Print...${NC}"

FILES_TO_DOWNLOAD=(
    "app.py:$APP_DIR/server.py"
    "database.py:$APP_DIR/database.py"
    "pdf_generator.py:$APP_DIR/pdf_generator.py"
    "hpp_engine.py:$APP_DIR/hpp_engine.py"
    "generate_poster.py:$APP_DIR/generate_poster.py"
    "templates/index.html:$TEMPLATES_DIR/index.html"
    "templates/admin.html:$TEMPLATES_DIR/admin.html"
)

for item in "${FILES_TO_DOWNLOAD[@]}"; do
    SRC="${item%%:*}"
    DST="${item##*:}"
    echo -n "  -> Mengunduh $SRC... "
    HTTP_CODE=$(curl -sSL -w "%{http_code}" "https://raw.githubusercontent.com/Aydin04/print-drop/main/$SRC" -o "$DST")
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}[OK $HTTP_CODE]${NC}"
    else
        echo -e "${RED}[FAILED $HTTP_CODE]${NC}"
    fi
done

# 3. Setup & Verify Systemd Autostart Service
echo ""
echo -e "${BOLD}${BLUE}▶ [3/5] Mengatur & Memverifikasi Systemd Service...${NC}"
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

echo "  -> Reload systemd daemon..."
systemctl --user daemon-reload
echo "  -> Enable & restart printdrop.service..."
systemctl --user enable printdrop.service
systemctl --user restart printdrop.service

sleep 2

SERVICE_STATUS=$(systemctl --user is-active printdrop.service 2>&1 || true)
if [ "$SERVICE_STATUS" = "active" ]; then
    echo -e "  ${GREEN}[✓] printdrop.service BERJALAN AKTIF (Status: $SERVICE_STATUS)${NC}"
else
    echo -e "  ${RED}[!] printdrop.service GAGAL AKTIF (Status: $SERVICE_STATUS)${NC}"
    echo -e "${YELLOW}--- LOG ERROR SERVICE ---${NC}"
    journalctl --user-unit printdrop.service -n 15 --no-pager || true
    echo -e "${YELLOW}-------------------------${NC}"
fi

# 4. Deteksi Antarmuka Wi-Fi & Buat Hotspot
echo ""
echo -e "${BOLD}${BLUE}▶ [4/5] Mengonfigurasi & Menyalakan Hotspot Wi-Fi...${NC}"

rfkill unblock wifi 2>/dev/null || true

echo "  -> Daftar Interface Wi-Fi yang Terdeteksi:"
nmcli device status | grep wifi || echo "  [!] Tidak ada device bertipe wifi pada nmcli"

WIFI_DEV=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1 | head -n 1)

if [ -n "$WIFI_DEV" ]; then
    echo -e "  -> Perangkat Wi-Fi yang Dipilih: ${CYAN}$WIFI_DEV${NC}"
    
    echo "  -> Membersihkan koneksi lama (jika ada)..."
    nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
    nmcli con delete "AYDIN-PRINT-5G" 2>/dev/null || true
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    
    echo "  -> Menyalakan Hotspot 'AYDIN-PRINT'..."
    if nmcli dev wifi hotspot ifname "$WIFI_DEV" ssid "AYDIN-PRINT" password "aydinprint" con-name "AYDIN-PRINT"; then
        echo -e "  ${GREEN}[✓] Hotspot 'AYDIN-PRINT' BERHASIL MEMANCAR!${NC}"
    else
        echo -e "  ${YELLOW}[i] Mencoba metode koneksi alternatif...${NC}"
        nmcli con add type wifi ifname "$WIFI_DEV" con-name "AYDIN-PRINT" autoconnect yes ssid "AYDIN-PRINT"
        nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap
        nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk
        nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.psk "aydinprint"
        nmcli con modify "AYDIN-PRINT" ipv4.method shared
        nmcli con up "AYDIN-PRINT"
        echo -e "  ${GREEN}[✓] Hotspot 'AYDIN-PRINT' BERHASIL DIAKTIFKAN!${NC}"
    fi
    
    HOTSPOT_IP=$(nmcli -t -f IP4.ADDRESS dev show "$WIFI_DEV" 2>/dev/null | cut -d: -f2 | cut -d/ -f1 | head -n 1)
    echo -e "  -> IP Gateway Hotspot PC: ${GREEN}${HOTSPOT_IP:-10.42.0.1}${NC}"
else
    echo -e "  ${RED}[!] PERINGATAN: Perangkat Wi-Fi tidak ditemukan. Periksa saklar Wi-Fi atau driver.${NC}"
fi

# 5. Generate Poster Meja & Shortcut Aplikasi
echo ""
echo -e "${BOLD}${BLUE}▶ [5/5] Menghasilkan Poster Meja & Shortcut Aplikasi...${NC}"
echo -n "  -> Menjalankan generate_poster.py... "
if "$PY_BIN" "$APP_DIR/generate_poster.py"; then
    echo -e "${GREEN}[BERHASIL]${NC}"
else
    echo -e "${RED}[GAGAL]${NC}"
fi

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

# Test Konektivitas Server Lokal
echo ""
echo -e "${BOLD}${BLUE}▶ [TEST KONEKSI SERVER]${NC}"
HTTP_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/ || echo "ERR")
if [ "$HTTP_TEST" = "200" ]; then
    echo -e "  ${GREEN}[✓] Web Server Berjalan Normal di http://127.0.0.1:5000 (HTTP 200 OK)${NC}"
else
    echo -e "  ${YELLOW}[i] Response Server Lokal: $HTTP_TEST${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 INSTALASI SELESAI & SUKSES LENGKAP!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e "🛡️ ${BOLD}Buka Panel Kasir PC${NC} : ${CYAN}http://127.0.0.1:5000/admin${NC}"
echo -e "🌐 ${BOLD}Web Pelanggan (Lokal)${NC} : ${CYAN}http://10.42.0.1:5000${NC}"
echo -e "📶 ${BOLD}Wi-Fi Hotspot Toko${NC}   : ${YELLOW}AYDIN-PRINT${NC} (Password: ${YELLOW}aydinprint${NC})"
echo -e "📁 ${BOLD}Folder File Masuk${NC}    : $RESULT_DIR"
echo -e "🖼️ ${BOLD}Gambar Poster Meja${NC}   : $APP_DIR/POSTER_MEJA_AYDIN_PRINT.png"
echo ""
