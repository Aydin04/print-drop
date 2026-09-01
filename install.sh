#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# Smart AP Hardware Detection (Pilih Card yang Dukung Mode AP)
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

mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR" "$HOME/.local/share/applications" "$HOME/Desktop" 2>/dev/null || true

# 1. Setup Virtual Environment & Fast Check Dependency
echo -e "${BOLD}${BLUE}▶ [1/5] Memeriksa & Menyiapkan Python Environment...${NC}"

if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo -e "  ${YELLOW}[i]${NC} Membuat Virtual Environment di $VENV_DIR..."
    python3 -m venv "$VENV_DIR" --system-site-packages 2>/dev/null || python3 -m venv "$VENV_DIR"
fi

PY_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

MISSING_PKGS=""
for pkg in flask PIL reportlab qrcode; do
    echo -n "  -> Memeriksa '$pkg'... "
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
fi

# 2. Download Komponen Aplikasi
echo ""
echo -e "${BOLD}${BLUE}▶ [2/5] Mengunduh Skrip & Template...${NC}"

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

systemctl --user daemon-reload
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

# 4. Deteksi Antarmuka Wi-Fi yang Benar-Benar Mendukung Mode AP (Access Point)
echo ""
echo -e "${BOLD}${BLUE}▶ [4/5] Memilih Perangkat Wi-Fi yang Mendukung Hotspot (AP)...${NC}"

rfkill unblock wifi 2>/dev/null || true

# Cari interface PCIe Qualcomm QCA9377 (biasanya wlp* tanpa USB 'u' flag, misal wlp2s0 atau wlan0)
ALL_WIFI=($(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d: -f1))
echo "  -> Semua Interface Wi-Fi: ${ALL_WIFI[*]}"

AP_DEVICE=""
for dev in "${ALL_WIFI[@]}"; do
    # Periksa apakah device ini mendukung mode AP (Access Point)
    echo -n "  -> Menguji kemampuan AP pada '$dev'... "
    PHY=$(iw dev "$dev" info 2>/dev/null | grep wiphy | awk '{print "phy"$2}')
    if [ -n "$PHY" ] && iw phy "$PHY" info 2>/dev/null | grep -E '* AP$' &>/dev/null; then
        echo -e "${GREEN}[MENDUKUNG AP]${NC}"
        AP_DEVICE="$dev"
        break
    else
        # Jika bukan wlp*u* (bukan USB dongle), beri prioritas
        if [[ "$dev" =~ ^wlp[0-9]+s[0-9]+$ ]] || [[ "$dev" =~ ^wlan[0-9]+$ ]]; then
            echo -e "${GREEN}[PCIe Card Terpilih]${NC}"
            AP_DEVICE="$dev"
            break
        else
            echo -e "${YELLOW}[Bukan AP Utama]${NC}"
        fi
    fi
done

# Jika belum terpilih, ambil yang PCIe (bukan USB 'u')
if [ -z "$AP_DEVICE" ]; then
    for dev in "${ALL_WIFI[@]}"; do
        if [[ ! "$dev" =~ u[0-9]+ ]]; then
            AP_DEVICE="$dev"
            break
        fi
    done
fi

if [ -z "$AP_DEVICE" ] && [ ${#ALL_WIFI[@]} -gt 0 ]; then
    AP_DEVICE="${ALL_WIFI[0]}"
fi

if [ -n "$AP_DEVICE" ]; then
    echo -e "  -> ${BOLD}${GREEN}Target Hotspot Wi-Fi Card: $AP_DEVICE${NC}"
    
    nmcli con delete "AYDIN-PRINT" 2>/dev/null || true
    nmcli con delete "AYDIN-PRINT-5G" 2>/dev/null || true
    nmcli con delete "Hotspot-Print" 2>/dev/null || true
    
    echo "  -> Mengaktifkan Hotspot 'AYDIN-PRINT' pada $AP_DEVICE..."
    nmcli con add type wifi ifname "$AP_DEVICE" con-name "AYDIN-PRINT" autoconnect yes ssid "AYDIN-PRINT"
    nmcli con modify "AYDIN-PRINT" 802-11-wireless.mode ap
    nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.key-mgmt wpa-psk
    nmcli con modify "AYDIN-PRINT" 802-11-wireless-security.psk "aydinprint"
    nmcli con modify "AYDIN-PRINT" ipv4.method shared
    
    if nmcli con up "AYDIN-PRINT"; then
        echo -e "  ${GREEN}[✓] Hotspot 'AYDIN-PRINT' BERHASIL MEMANCAR PADA $AP_DEVICE!${NC}"
    else
        echo -e "  ${YELLOW}[i] Mencoba dengan nmcli dev wifi hotspot...${NC}"
        nmcli dev wifi hotspot ifname "$AP_DEVICE" ssid "AYDIN-PRINT" password "aydinprint" con-name "AYDIN-PRINT" || true
    fi
else
    echo -e "  ${RED}[!] PERINGATAN: Wi-Fi Card PCIe tidak ditemukan.${NC}"
fi

# 5. Generate Poster Meja & Shortcut Aplikasi
echo ""
echo -e "${BOLD}${BLUE}▶ [5/5] Menghasilkan Poster Meja & Shortcut Aplikasi...${NC}"
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

# Test Koneksi Server
echo ""
echo -e "${BOLD}${BLUE}▶ [TEST KONEKSI SERVER]${NC}"
HTTP_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/ || echo "ERR")
if [ "$HTTP_TEST" = "200" ]; then
    echo -e "  ${GREEN}[✓] Web Server Berjalan Normal di http://127.0.0.1:5000 (HTTP 200 OK)${NC}"
else
    echo -e "  ${YELLOW}[i] Response Server: $HTTP_TEST${NC}"
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
