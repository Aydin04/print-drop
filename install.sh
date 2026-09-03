#!/usr/bin/env bash
# ==============================================================
# AYDIN PRINT — Self-Service Print & Studio Auto Installer
# FIX PERMANEN: Firewall Zone nm-shared & FedoraWorkstation (Port 5000)
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
echo -e "${CYAN}║         🖨️  MEMULAI KONFIGURASI AYDIN PRINT STUDIO         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

APP_DIR="$HOME/PrintDrop"
RESULT_DIR="$HOME/Hasil_Print"
TEMPLATES_DIR="$APP_DIR/templates"
VENV_DIR="$APP_DIR/venv"

mkdir -p "$APP_DIR" "$RESULT_DIR" "$TEMPLATES_DIR" "$HOME/.local/share/applications" "$HOME/Desktop" 2>/dev/null || true

# 1. Setup Virtual Environment
echo -e "${BOLD}${BLUE}▶ [1/4] Menyiapkan Python Server...${NC}"

PY_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

# 2. Download / Update Template & Server
echo -e "${BOLD}${BLUE}▶ [2/4] Sinkronisasi Skrip Web...${NC}"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/app.py -o "$APP_DIR/server.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/database.py -o "$APP_DIR/database.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/pdf_generator.py -o "$APP_DIR/pdf_generator.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/hpp_engine.py -o "$APP_DIR/hpp_engine.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/generate_poster.py -o "$APP_DIR/generate_poster.py"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/index.html -o "$TEMPLATES_DIR/index.html"
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/templates/admin.html -o "$TEMPLATES_DIR/admin.html"

# Restart printdrop.service
systemctl --user restart printdrop.service

# 3. BUKA FIREWALL DI SEMUA ZONE (nm-shared & FedoraWorkstation)
echo ""
echo -e "${BOLD}${BLUE}▶ [3/4] Mengizinkan Akses Port 5000 pada Firewall (nm-shared)...${NC}"

if command -v firewall-cmd &>/dev/null; then
    echo "  -> Menambahkan izin port 5000 ke zone nm-shared (Hotspot)..."
    sudo firewall-cmd --zone=nm-shared --add-port=5000/tcp --permanent 2>/dev/null || true
    sudo firewall-cmd --zone=nm-shared --add-port=5000/tcp 2>/dev/null || true
    
    sudo firewall-cmd --zone=FedoraWorkstation --add-port=5000/tcp --permanent 2>/dev/null || true
    sudo firewall-cmd --zone=FedoraWorkstation --add-port=5000/tcp 2>/dev/null || true
    
    sudo firewall-cmd --reload 2>/dev/null || true
    echo -e "  ${GREEN}[✓] Firewall zone 'nm-shared' & 'FedoraWorkstation' port 5000 SUDAH DIBUKA!${NC}"
fi

# 4. Generate Poster Meja
echo ""
echo -e "${BOLD}${BLUE}▶ [4/4] Memperbarui Poster Meja...${NC}"
"$PY_BIN" "$APP_DIR/generate_poster.py"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 AKSES WEB SELESAI DIBUKA LENGKAP!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e "📶 ${BOLD}Wi-Fi Hotspot Toko${NC}      : ${YELLOW}AYDIN-PRINT${NC} (Password: ${YELLOW}aydinprint${NC})"
echo -e "🌐 ${BOLD}Web Pelanggan (dari HP)${NC} : ${BOLD}${GREEN}http://10.42.0.1:5000${NC}"
echo -e "🛡️ ${BOLD}Panel Kasir (di PC)${NC}     : ${CYAN}http://127.0.0.1:5000/admin${NC}"
echo ""
