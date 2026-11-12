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

GITHUB_RAW="https://raw.githubusercontent.com/mohdkhatab/prime-khatab-services/main"

echo -e "${CYAN}=====================================================${NC}"
echo -e "${GREEN}               PRIME KHATAB SERVICES                 ${NC}"
echo -e "${YELLOW}       1-Click Automated VPS Installer & Setup       ${NC}"
echo -e "${CYAN}=====================================================${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run this installer as root or using sudo:${NC}"
  echo -e "    curl -fsSL ${GITHUB_RAW}/install.sh | sudo bash"
  exit 1
fi

echo -e "${YELLOW}[1/8] Installing core system packages...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y > /dev/null
apt-get install -y python3 curl jq qrencode dropbear net-tools iptables openssl ufw > /dev/null

# Enable TCP BBR
echo -e "${YELLOW}[2/8] Enabling TCP BBR Congestion Control for Ultra-Fast Tunnels...${NC}"
cat << 'EOF' > /etc/sysctl.d/99-bbr.conf
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
EOF
sysctl -p /etc/sysctl.d/99-bbr.conf > /dev/null 2>&1 || true

# Prepare Directories
mkdir -p /etc/vpn-manager
mkdir -p /usr/local/bin
mkdir -p /usr/local/etc/xray

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

echo -e "${YELLOW}[3/8] Fetching Prime Khatab CLI binaries...${NC}"
if [ -n "$SCRIPT_DIR" ] && [ -f "${SCRIPT_DIR}/vpn-cli.py" ]; then
    cp "${SCRIPT_DIR}/vpn-cli.py" /usr/local/bin/vpn-cli.py
    cp "${SCRIPT_DIR}/menu.sh" /usr/local/bin/menu
    [ -f "${SCRIPT_DIR}/services/ssh-ws.py" ] && cp "${SCRIPT_DIR}/services/ssh-ws.py" /usr/local/bin/ssh-ws.py
    [ -f "${SCRIPT_DIR}/bin/badvpn-udpgw" ] && cp "${SCRIPT_DIR}/bin/badvpn-udpgw" /usr/local/bin/badvpn-udpgw
else
    curl -fsSL "${GITHUB_RAW}/vpn-cli.py" -o /usr/local/bin/vpn-cli.py
    curl -fsSL "${GITHUB_RAW}/menu.sh" -o /usr/local/bin/menu
    curl -fsSL "${GITHUB_RAW}/services/ssh-ws.py" -o /usr/local/bin/ssh-ws.py
    curl -fsSL "${GITHUB_RAW}/bin/badvpn-udpgw" -o /usr/local/bin/badvpn-udpgw || true
fi

chmod +x /usr/local/bin/vpn-cli.py /usr/local/bin/menu /usr/local/bin/ssh-ws.py 2>/dev/null || true
[ -f /usr/local/bin/badvpn-udpgw ] && chmod +x /usr/local/bin/badvpn-udpgw

# If badvpn binary is missing, fetch prebuilt
if [ ! -f /usr/local/bin/badvpn-udpgw ]; then
    curl -fsSL "https://github.com/ambrop72/badvpn/releases/download/1.999.130/badvpn-1.999.130.tar.bz2" 2>/dev/null || true
fi

# Create Core Binary Symlinks
ln -sf /usr/local/bin/vpn-cli.py /usr/local/bin/vpn-cli
ln -sf /usr/local/bin/vpn-cli.py /usr/local/bin/prime-cli
ln -sf /usr/local/bin/menu /usr/local/bin/prime
ln -sf /usr/local/bin/menu /usr/local/bin/prime-khatab

# Setup Ultra-Short Commands (p, pk, prime, menu, status, live, speed, etc.)
echo -e "${YELLOW}[4/8] Configuring automatic short commands (p, pk, status, live, speed)...${NC}"
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

# Install Xray-Core if not installed
echo -e "${YELLOW}[5/8] Setting up Xray-Core engine...${NC}"
if ! command -v xray &>/dev/null; then
    bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install > /dev/null 2>&1 || true
fi

# Generate Initial Xray config & Reality keys if not exists
if [ ! -f /usr/local/etc/xray/config.json ]; then
    echo -e "${YELLOW}[*] Generating VLESS Reality Keys and Xray configuration...${NC}"
    if command -v xray &>/dev/null; then
        KEYS=$(xray x25519)
        PRIV=$(echo "$KEYS" | awk '/PrivateKey:/ {print $2}')
        PUB=$(echo "$KEYS" | awk '/(PublicKey):/ {print $3}')
    else
        PRIV="mFh_6Gfbf6i4a179IhGyd2MZKSWqGPebW5_Zi28Mu1w"
        PUB="9df9bO4HUb7IV8sljoAN6gHCNxe3U0NEZc7N9_Pcxic"
    fi
    SHORT_ID=$(openssl rand -hex 4)
    
    cat << EOF > /usr/local/etc/xray/reality.env
PRIV=${PRIV}
PUB=${PUB}
SHORT_ID=${SHORT_ID}
SERVER_NAME=www.microsoft.com
EOF

    cat << EOF > /usr/local/etc/xray/config.json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "tag": "vless-reality",
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.microsoft.com:443",
          "xver": 0,
          "serverNames": [
            "www.microsoft.com",
            "microsoft.com"
          ],
          "privateKey": "${PRIV}",
          "shortIds": [
            "${SHORT_ID}"
          ]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    },
    {
      "tag": "vmess-ws",
      "listen": "127.0.0.1",
      "port": 10086,
      "protocol": "vmess",
      "settings": {
        "clients": []
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/vmess"
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    },
    {
      "tag": "trojan-ws",
      "listen": "127.0.0.1",
      "port": 10087,
      "protocol": "trojan",
      "settings": {
        "clients": []
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/trojan"
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    },
    {
      "tag": "socks-tg",
      "port": 1080,
      "listen": "0.0.0.0",
      "protocol": "socks",
      "settings": {
        "auth": "password",
        "accounts": [],
        "udp": true
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "tag": "direct"
    },
    {
      "protocol": "blackhole",
      "tag": "blocked"
    }
  ]
}
EOF
fi

# Configure Dropbear SSH
echo -e "${YELLOW}[6/8] Configuring Dropbear SSH (Ports 109, 143)...${NC}"
cat << 'EOF' > /etc/default/dropbear
NO_START=0
DROPBEAR_PORT=109
DROPBEAR_EXTRA_ARGS="-p 143 -b /etc/issue.net"
DROPBEAR_BANNER="/etc/issue.net"
DROPBEAR_RECEIVE_WINDOW=65536
EOF

echo -e "\033[1;36m=====================================================\033[0m\n\033[1;32m       PRIME KHATAB SERVICES - PREMIUM TUNNEL       \033[0m\n\033[1;36m=====================================================\033[0m" > /etc/issue.net
systemctl restart dropbear >/dev/null 2>&1 || true

# Setup Services: BadVPN & SSH-WS
echo -e "${YELLOW}[7/8] Configuring BadVPN & WebSocket Services...${NC}"
cat << 'EOF' > /etc/systemd/system/badvpn.service
[Unit]
Description=BadVPN UDP Gateway (Prime Khatab Services)
After=network.target

[Service]
ExecStart=/usr/local/bin/badvpn-udpgw --listen-addr 127.0.0.1:7300 --max-clients 500 --max-connections-for-client 20
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

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
systemctl enable badvpn ssh-ws xray >/dev/null 2>&1 || true
systemctl restart badvpn ssh-ws xray >/dev/null 2>&1 || true

# Initialize database if not exists
if [ ! -f /etc/vpn-manager/database.json ]; then
    cat << 'EOF' > /etc/vpn-manager/database.json
{
  "ssh": {},
  "vmess": {},
  "vless": {},
  "trojan": {},
  "socks": {}
}
EOF
fi

# Setup Global Profile & Welcome Banner
echo -e "${YELLOW}[8/8] Finalizing Profile Shortcuts & Cron Jobs...${NC}"
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
cat << 'EOF' > /etc/cron.daily/prime-khatab-prune
#!/bin/bash
/usr/local/bin/vpn-cli auto-clean >> /var/log/prime-khatab-prune.log 2>&1
EOF
chmod +x /etc/cron.daily/prime-khatab-prune

echo ""
echo -e "${CYAN}=====================================================${NC}"
echo -e "${GREEN}  ✓ PRIME KHATAB SERVICES INSTALLED & FULLY CONFIGURED!${NC}"
echo -e "${CYAN}=====================================================${NC}"
echo -e "  All services (SSH, Xray, BadVPN, Dropbear) are now ${GREEN}ACTIVE${NC}."
echo -e "  Instant Shortcuts:"
echo -e "    ${YELLOW}p${NC}      -> Launch Menu"
echo -e "    ${YELLOW}status${NC} -> Check Service Status"
echo -e "    ${YELLOW}live${NC}   -> Live Connected Clients"
echo -e "${CYAN}=====================================================${NC}"
echo ""

# Launch menu immediately if running in an interactive terminal
if [ -t 0 ]; then
    /usr/local/bin/menu
fi
