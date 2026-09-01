#!/usr/bin/env bash
echo "=== [1] STATUS NETWORK INTERFACES ==="
ip -br addr
echo ""
echo "=== [2] STATUS NMCLI CONNECTIONS ==="
nmcli con show --active
echo ""
echo "=== [3] STATUS PORT LISTENING (5000) ==="
ss -tulpn | grep 5000 || netstat -tulpn | grep 5000 || echo "Port 5000 TIDAK LISTENING!"
echo ""
echo "=== [4] STATUS FIREWALL ZONES ==="
if command -v firewall-cmd &>/dev/null; then
    firewall-cmd --get-active-zones
    firewall-cmd --list-all
fi
echo ""
echo "=== [5] TEST CURL LOCALHOST ==="
curl -I http://127.0.0.1:5000/ || echo "Gagal konek 127.0.0.1"
echo ""
echo "=== [6] TEST CURL SEMUA IP LOKAL ==="
for ip_addr in $(ip -4 -o addr show | awk '{print $4}' | cut -d/ -f1); do
    echo -n "Testing $ip_addr:5000 ... "
    curl -s -o /dev/null -w "%{http_code}\n" "http://$ip_addr:5000/" --connect-timeout 2 || echo "TIMEOUT/REFUSED"
done
