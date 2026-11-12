# 🚀 Prime Khatab Services - VPS Multi-Tunnel Management CLI

<p align="center">
  <img src="https://img.shields.io/badge/Prime%20Khatab-Services-00f2fe?style=for-the-badge&logo=wireguard&logoColor=white" alt="Prime Khatab Services">
  <img src="https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Debian-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/TCP%20BBR-Enabled-blueviolet?style=for-the-badge" alt="TCP BBR">
</p>

An all-in-one, enterprise-grade VPS management CLI and interactive terminal menu (TUI) designed for managing multi-protocol high-speed tunnels, proxies, and VPN accounts.

Developed and branded exclusively for **Prime Khatab**.

---

## 🌟 Key Features

- **Multi-Protocol Support:**
  - 🛡️ **SSH WebSocket / Dropbear / BadVPN:** OpenSSH (Port 22), Dropbear (Ports 109, 143), Multi-WS Proxy (Ports 80, 8080, 8880), UDPGW (Port 7300).
  - ⚡ **V2Ray / VMess (WebSocket):** CDN-friendly WebSocket tunneling with automated base64 client URI and QR codes.
  - 🚀 **VLESS Reality (XTLS Vision):** Ultra-fast, direct IP connection requiring **zero domain** and zero SSL certificates.
  - 🐎 **Trojan-WS:** Secure WebSocket tunneling for evasion of heavy DPI filters.
  - ✈️ **Telegram SOCKS5 Proxy:** Instant 1-click proxy generator (`tg://socks` & `https://t.me/socks`) with voice call UDP support.

- **Automated Lifecycle Management:**
  - ⏰ **Auto-Prune & Auto-Expiry:** Automatic removal of expired accounts daily via integrated background cron jobs.
  - 🔄 **Account Renewal:** 1-click extension of account validity for any protocol.
  - 🔍 **Account Link & QR Retrieval:** Re-generate connection URIs and ANSI terminal QR codes anytime.

- **System & Network Optimization:**
  - 🚀 **TCP BBR Congestion Control:** Automated kernel BBR activation for 2x–5x tunnel throughput and minimal packet loss.
  - 📊 **VPS Resource Dashboard:** Real-time CPU, RAM, Disk, Uptime, and account count statistics.
  - 👥 **Live Online Monitor:** Real-time detection of active SSH sessions and client connections across ports 22, 80, 443, 1080, and 7300.
  - ⚡ **Built-in Speedtest:** Fast latency and CDN download bandwidth measurement.
  - 💾 **1-Click Backup & Restore:** Safe backup of account databases and Xray configurations into compressed `.tar.gz` archives.

---

## 📋 Interactive Menu Overview

Launch the menu at any time by typing:
```bash
prime
# or
menu
```

```text
=====================================================
               PRIME KHATAB SERVICES                 
           Premium VPS & Multi-Tunnel CLI            
-----------------------------------------------------
 Brand / Owner : Prime Khatab
 Optimization  : TCP BBR Active • Ultra Low Latency
=====================================================
 [1]  Create SSH Account (WS / Dropbear / BadVPN)
 [2]  Create V2Ray / VMess Account (Link & QR)
 [3]  Create VLESS Reality Account (Ultra-Fast, No Domain)
 [4]  Create Trojan Account (Link & QR)
 [5]  Create SOCKS5 Proxy (Telegram 1-Click Link & QR)
-----------------------------------------------------
 [6]  Show Account Link / QR Code (Re-Generate Link)
 [7]  List All Active Accounts & Expiration
 [8]  Renew / Extend Account Expiry
 [9]  Delete Single Account
 [10] Auto-Clean All Expired Accounts (Prune)
-----------------------------------------------------
 [11] Live Online Users & Connection Statistics
 [12] VPS Dashboard & System Info (RAM/CPU/Disk/BBR)
 [13] Speedtest Server Connection
 [14] Check Running Services Status
 [15] Restart All Tunnel Services
 [16] Backup Database & Configurations
 [17] Restore Database from Backup
 [18] Set Custom Domain / Bug Host
 [0]  Exit Menu
=====================================================
 Prime Khatab Services • Fast, Secure & Anonymous
=====================================================
```

---

## ⚡ Quick 1-Click Installation

To install **Prime Khatab Services** on any fresh Ubuntu / Debian VPS:

```bash
git clone https://github.com/mohdkhatab/prime-khatab-services.git
cd prime-khatab-services
sudo chmod +x install.sh
sudo ./install.sh
```

---

## 🛠️ CLI Direct Commands

You can execute operations directly without opening the interactive menu:

| Task | Command |
| :--- | :--- |
| **Create SSH Account** | `sudo vpn-cli add-ssh <user> <pass> <days>` |
| **Create VMess Account** | `sudo vpn-cli add-vmess <user> <days>` |
| **Create VLESS Account** | `sudo vpn-cli add-vless <user> <days>` |
| **Create Trojan Account** | `sudo vpn-cli add-trojan <user> <pass> <days>` |
| **Create SOCKS5 Proxy** | `sudo vpn-cli add-socks <user> <pass> <days> [port]` |
| **Retrieve Link & QR** | `sudo vpn-cli show-user <protocol> <user>` |
| **List All Accounts** | `sudo vpn-cli list` |
| **Renew Account** | `sudo vpn-cli renew <protocol> <user> <days>` |
| **Delete Account** | `sudo vpn-cli del <protocol> <user>` |
| **Clean Expired Accounts**| `sudo vpn-cli auto-clean` |
| **Live Online Connections**| `sudo vpn-cli live-users` |
| **VPS Dashboard** | `sudo vpn-cli vps-info` |
| **Speedtest** | `sudo vpn-cli speedtest` |
| **Service Status** | `sudo vpn-cli status` |
| **Backup Configurations**| `sudo vpn-cli backup` |
| **Restore Configurations**| `sudo vpn-cli restore [file_path]` |

For full reference, see [COMMANDS.md](COMMANDS.md).

---

## 📁 Repository Structure

```text
prime-khatab-services/
├── menu.sh               # Colorful Interactive Terminal Menu (TUI)
├── vpn-cli.py            # Core Python Management Engine
├── install.sh            # Automated Setup & Dependency Installer
├── services/
│   └── ssh-ws.py         # Asynchronous WebSocket Multiplexer & Reverse Proxy
├── README.md             # Project Documentation
├── COMMANDS.md           # CLI Syntax and Usage Manual
├── INSTALLATION.md       # Prerequisite Ports, Firewall & Backend Architecture
├── LICENSE               # MIT License
└── .gitignore            # Git Ignore for databases, keys & backups
```

---

## 🔒 Security Best Practices

1. Default accounts are stored locally in `/etc/vpn-manager/database.json`.
2. Do not commit actual user credentials or private reality keys into version control.
3. Daily pruning ensures expired clients lose access instantly.

---

## 👤 Author & Credits

- **Author & Brand:** Mohd Khatab (Prime Khatab)
- **Website:** [codewithkhatab.in](https://codewithkhatab.in)
- **GitHub:** [@mohdkhatab](https://github.com/mohdkhatab)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
