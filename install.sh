#!/usr/bin/env bash
# =====================================================
#             PRIME KHATAB SERVICES
#    1-Click VPS Multi-Tunnel CLI Auto-Installer
#    Developed & Branded for: Prime Khatab
# =====================================================

set -e

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

echo -e "${CYAN}=====================================================${NC}"
echo -e "${GREEN}               PRIME KHATAB SERVICES                 ${NC}"
echo -e "${YELLOW}           VPS Multi-Tunnel CLI Installer            ${NC}"
echo -e "${CYAN}=====================================================${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run this installer as root or using sudo.${NC}"
  exit 1
fi

echo -e "${YELLOW}[*] Installing required packages...${NC}"
apt-get update -y
apt-get install -y python3 curl jq qrencode dropbear net-tools iptables

# Enable TCP BBR
echo -e "${YELLOW}[*] Optimizing network with TCP BBR...${NC}"
cat << 'EOF' > /etc/sysctl.d/99-bbr.conf
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
EOF
sysctl -p /etc/sysctl.d/99-bbr.conf > /dev/null 2>&1 || true

# Prepare Directories
mkdir -p /etc/vpn-manager
mkdir -p /usr/local/bin

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}[*] Installing Prime Khatab CLI binaries...${NC}"
cp "${SCRIPT_DIR}/vpn-cli.py" /usr/local/bin/vpn-cli.py
chmod +x /usr/local/bin/vpn-cli.py

cp "${SCRIPT_DIR}/menu.sh" /usr/local/bin/menu
chmod +x /usr/local/bin/menu

# Create Symlinks
ln -sf /usr/local/bin/vpn-cli.py /usr/local/bin/vpn-cli
ln -sf /usr/local/bin/vpn-cli.py /usr/local/bin/prime-cli
ln -sf /usr/local/bin/menu /usr/local/bin/prime
ln -sf /usr/local/bin/menu /usr/local/bin/prime-khatab

# Setup Daily Auto-Prune Cron Job
echo -e "${YELLOW}[*] Configuring daily auto-cleanup cron job...${NC}"
cat << 'EOF' > /etc/cron.daily/prime-khatab-prune
#!/bin/bash
/usr/local/bin/vpn-cli auto-clean >> /var/log/prime-khatab-prune.log 2>&1
EOF
chmod +x /etc/cron.daily/prime-khatab-prune

# Setup WebSocket multiplexer service if present
if [ -f "${SCRIPT_DIR}/services/ssh-ws.py" ]; then
  cp "${SCRIPT_DIR}/services/ssh-ws.py" /usr/local/bin/ssh-ws.py
  chmod +x /usr/local/bin/ssh-ws.py

  cat << 'EOF' > /etc/systemd/system/ssh-ws.service
[Unit]
Description=Prime Khatab Services WebSocket Proxy
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/ssh-ws.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable ssh-ws > /dev/null 2>&1 || true
  systemctl restart ssh-ws > /dev/null 2>&1 || true
fi

echo -e "${CYAN}=====================================================${NC}"
echo -e "${GREEN}[✓] PRIME KHATAB SERVICES INSTALLED SUCCESSFULLY!${NC}"
echo -e "${YELLOW}Launch the management interface anytime by running:${NC}"
echo -e "    ${GREEN}prime${NC}  or  ${GREEN}menu${NC}"
echo -e "${CYAN}=====================================================${NC}"
