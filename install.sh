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

# Create Core Binary Symlinks
ln -sf /usr/local/bin/vpn-cli.py /usr/local/bin/vpn-cli
ln -sf /usr/local/bin/vpn-cli.py /usr/local/bin/prime-cli
ln -sf /usr/local/bin/menu /usr/local/bin/prime
ln -sf /usr/local/bin/menu /usr/local/bin/prime-khatab

# Setup Ultra-Short Commands (p, pk, prime, menu, status, live, speed, etc.)
echo -e "${YELLOW}[*] Setting up automatic short commands (p, pk, prime, status, live)...${NC}"
ln -sf /usr/local/bin/menu /usr/local/bin/p
ln -sf /usr/local/bin/menu /usr/local/bin/pk

cat << 'EOF' > /usr/local/bin/status
#!/bin/bash
sudo /usr/local/bin/vpn-cli status
EOF

cat << 'EOF' > /usr/local/bin/live
#!/bin/bash
sudo /usr/local/bin/vpn-cli live-users
EOF

cat << 'EOF' > /usr/local/bin/speed
#!/bin/bash
sudo /usr/local/bin/vpn-cli speedtest
EOF

cat << 'EOF' > /usr/local/bin/p-users
#!/bin/bash
sudo /usr/local/bin/vpn-cli list
EOF

cat << 'EOF' > /usr/local/bin/p-clean
#!/bin/bash
sudo /usr/local/bin/vpn-cli auto-clean
EOF

cat << 'EOF' > /usr/local/bin/p-info
#!/bin/bash
sudo /usr/local/bin/vpn-cli vps-info
EOF

chmod +x /usr/local/bin/status /usr/local/bin/live /usr/local/bin/speed /usr/local/bin/p-users /usr/local/bin/p-clean /usr/local/bin/p-info

# Setup Global Profile & Welcome Banner
cat << 'EOF' > /etc/profile.d/prime-khatab.sh
# Prime Khatab Services Global Shortcuts & Profile
alias p='menu'
alias pk='menu'
alias prime='menu'
alias status='sudo /usr/local/bin/vpn-cli status'
alias live='sudo /usr/local/bin/vpn-cli live-users'
alias speed='sudo /usr/local/bin/vpn-cli speedtest'
alias p-users='sudo /usr/local/bin/vpn-cli list'
alias p-clean='sudo /usr/local/bin/vpn-cli auto-clean'
alias p-info='sudo /usr/local/bin/vpn-cli vps-info'

if [ -n "$PS1" ]; then
    echo -e "\033[1;36m=====================================================\033[0m"
    echo -e "\033[1;32m        WELCOME TO PRIME KHATAB SERVICES VPS        \033[0m"
    echo -e "\033[1;33m  Quick Commands:                                    \033[0m"
    echo -e "   • \033[1;32mp\033[0m / \033[1;32mpk\033[0m / \033[1;32mprime\033[0m / \033[1;32mmenu\033[0m  : Open Main Menu"
    echo -e "   • \033[1;32mstatus\033[0m                : Check Services"
    echo -e "   • \033[1;32mlive\033[0m                  : Online Users"
    echo -e "   • \033[1;32mspeed\033[0m                 : VPS Speedtest"
    echo -e "\033[1;36m=====================================================\033[0m"
fi
EOF
chmod +x /etc/profile.d/prime-khatab.sh

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
echo -e "${YELLOW}Quick Short Commands Available Immediately:${NC}"
echo -e "    ${GREEN}p${NC}  or  ${GREEN}pk${NC}  or  ${GREEN}prime${NC}  or  ${GREEN}menu${NC}  -> Open Main Menu"
echo -e "    ${GREEN}status${NC}                            -> Check All Tunnel Services"
echo -e "    ${GREEN}live${NC}                              -> View Live Client Connections"
echo -e "    ${GREEN}speed${NC}                             -> Run Bandwidth Speedtest"
echo -e "${CYAN}=====================================================${NC}"
