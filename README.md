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

## ⚡ 1-Click Automated Installation (Zero Setup Needed)

Kisi bhi fresh **Ubuntu (20.04 / 22.04 / 24.04)** ya **Debian** VPS par bas **yeh 1 command** chalayein:

```bash
curl -fsSL https://raw.githubusercontent.com/mohdkhatab/prime-khatab-services/main/install.sh | sudo bash
```

*Alternative (agar git se clone karna ho):*
```bash
git clone https://github.com/mohdkhatab/prime-khatab-services.git
cd prime-khatab-services
chmod +x install.sh
sudo ./install.sh
```

---

## ⚡ Automatic Quick Shortcuts (Available Anywhere)

Jaise hi aap install karenge, ye saari short commands terminal me direct kaam karengi:

| Shortcut | Description / Action | Example |
| :--- | :--- | :--- |
| **`p`** | **1-Letter Single Key Shortcut!** Main Menu open karta hai | `p` |
| **`pk`** | **Prime Khatab** short command se Menu open karta hai | `pk` |
| **`prime`** | Full brand name se Menu open karta hai | `prime` |
| **`menu`** | Standard interactive menu launcher | `menu` |
| **`status`** | Direct sabhi tunnel services ka live status check karta hai | `status` |
| **`live`** | Real-time connected clients aur active users dikhata hai | `live` |
| **`speed`** | Instant ping aur 25MB CDN download speedtest run karta hai | `speed` |
| **`p-users`** | Sabhi active users, creation date aur expiry list karta hai | `p-users` |
| **`p-clean`** | Expired accounts ko automatically delete/prune karta hai | `p-clean` |
| **`p-info`** | VPS Dashboard (CPU, RAM, Disk, Uptime, BBR) dikhata hai | `p-info` |

---

## 📋 Interactive Terminal Menu (TUI)

Terminal me `p`, `pk`, `prime`, ya `menu` likhne par ye menu open hoga:

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

## 🛠️ Complete CLI Commands Reference (Direct Commands)

Aap bina menu khole direct terminal se bhi saari commands execute kar sakte hain.

### 1. Account Creation Commands

#### 🛡️ SSH Account (WebSocket / Dropbear / BadVPN UDPGW)
OpenSSH, Dropbear aur WebSocket proxy ke liye account create karta hai.
```bash
sudo vpn-cli add-ssh <username> <password> <days>
```
*Example:*
```bash
sudo vpn-cli add-ssh khatab pass123 30
```
- **Ports:** OpenSSH (22), Dropbear (109, 143), SSH-WS (80, 8080, 8880), BadVPN (7300).
- **HTTP Payload:** `GET / HTTP/1.1[crlf]Host: bug.com[crlf]Upgrade: websocket[crlf]Connection: Upgrade[crlf][crlf]`

---

#### ⚡ V2Ray / VMess (WebSocket CDN)
Xray VMess account create karta hai, UUID generate karta hai aur base64 `vmess://` link ke sath QR code deta hai.
```bash
sudo vpn-cli add-vmess <username> <days>
```
*Example:*
```bash
sudo vpn-cli add-vmess john 30
```
- **Port:** 80 (Also 8080, 8880)
- **Path:** `/vmess`
- **Network:** `ws` (WebSocket)

---

#### 🚀 VLESS Reality (XTLS Vision - No Domain Required)
Xray VLESS Reality account create karta hai bina kisi domain ya SSL certificate ke direct high-speed connection deta hai.
```bash
sudo vpn-cli add-vless <username> <days>
```
*Example:*
```bash
sudo vpn-cli add-vless alex 30
```
- **Port:** 443
- **Flow:** `xtls-rprx-vision`
- **Security:** `reality`
- **SNI:** `www.microsoft.com`

---

#### 🐎 Trojan-WS
Trojan WebSocket account create karta hai DPI filters aur censorship bypass ke liye.
```bash
sudo vpn-cli add-trojan <username> <password> <days>
```
*Example:*
```bash
sudo vpn-cli add-trojan david secret123 30
```
- **Port:** 80 (Also 8080, 8880)
- **Path:** `/trojan`

---

#### ✈️ Telegram SOCKS5 Proxy (With UDP Voice & Video Calls)
Telegram ke liye 1-Click proxy link (`tg://socks` aur `https://t.me/socks`) generate karta hai.
```bash
sudo vpn-cli add-socks <username> <password> <days> [port]
```
*Example (Default port 1080):*
```bash
sudo vpn-cli add-socks tguser tgpass 30 1080
```
- **Direct Telegram Link:** `https://t.me/socks?server=YOUR_IP&port=1080&user=tguser&pass=tgpass`
- **UDP:** Enabled for voice & video calling.

---

### 2. Querying & Display Commands

#### 🔍 Show Account Details / Re-generate Link & QR
Kisi bhi pehle se bane account ki link, config aur QR code dobara screen par dekhne ke liye:
```bash
sudo vpn-cli show-user <protocol> <username>
```
*Supported Protocols:* `ssh`, `vmess`, `vless`, `trojan`, `socks`
*Examples:*
```bash
sudo vpn-cli show-user vless alex
sudo vpn-cli show-user vmess john
sudo vpn-cli show-user socks tguser
sudo vpn-cli show-user ssh khatab
sudo vpn-cli show-user trojan david
```

---

#### 📋 List All Active Accounts & Expiration
Sabhi accounts ki table jisme Protocol, Username, Created Date, Expiry Date aur Days Left aate hain:
```bash
sudo vpn-cli list
# ya shortcut:
p-users
```

---

### 3. Lifecycle & Maintenance Commands

#### 🔄 Renew / Extend Account Expiry
Account ki expiry date ko aage badhane (extend karne) ke liye:
```bash
sudo vpn-cli renew <protocol> <username> <days_to_add>
```
*Examples:*
```bash
sudo vpn-cli renew vless alex 30
sudo vpn-cli renew ssh khatab 15
sudo vpn-cli renew socks tguser 60
```

---

#### ❌ Delete Single Account
Kisi account ko database aur Xray/Linux se completely delete karne ke liye:
```bash
sudo vpn-cli del <protocol> <username>
```
*Examples:*
```bash
sudo vpn-cli del vless alex
sudo vpn-cli del ssh khatab
sudo vpn-cli del socks tguser
```

---

#### 🧹 Auto-Clean Expired Accounts (Prune)
Jo accounts expire ho chuke hain unhe 1 command me system se scan aur remove karne ke liye:
```bash
sudo vpn-cli auto-clean
# ya
sudo vpn-cli prune
# ya shortcut:
p-clean
```
*(Note: Daily raat 12:00 baje cron job ise automatically bhi run karti hai).*

---

### 4. Server & Monitoring Commands

#### 👥 Live Online Users & Connection Monitor
Real-time active SSH sessions aur har port par connected live clients check karne ke liye:
```bash
sudo vpn-cli live-users
# ya shortcut:
live
```

---

#### 📊 VPS Resource Dashboard
CPU Model, Cores, RAM Usage, Disk Space, Uptime, BBR Status aur Total Active Accounts summary dekhne ke liye:
```bash
sudo vpn-cli vps-info
# ya shortcut:
p-info
```

---

#### ⚡ Built-in Speedtest
Cloudflare DNS latency ping aur 25MB CDN high-speed download test:
```bash
sudo vpn-cli speedtest
# ya shortcut:
speed
```

---

#### 🚦 Service Status Check
Sabhi 5 tunnel services ka status check karne ke liye:
```bash
sudo vpn-cli status
# ya shortcut:
status
```

---

#### 🌐 Set Custom Domain / Bug Host
Agar aap Cloudflare CDN ya custom domain use kar rahe hain:
```bash
sudo vpn-cli set-domain vpn.yourdomain.com
```

---

### 5. Backup & Restore Commands

#### 💾 Backup Configurations & Database
Saare accounts aur Xray configuration ka compressed `.tar.gz` archive create karne ke liye:
```bash
sudo vpn-cli backup
```
*Backup file location:* `/home/ubuntu/prime_khatab_backup_latest.tar.gz`

---

#### 🔄 Restore Configurations from Backup
Backup se accounts aur configs ko 1-click restore karne ke liye:
```bash
sudo vpn-cli restore /home/ubuntu/prime_khatab_backup_latest.tar.gz
```

---

## 🧱 Ports & Firewall Configuration (UFW)

Agar aap AWS, DigitalOcean, Hetzner, ya Linode use kar rahe hain, to firewall me ye ports open honi chahiye:

```bash
sudo ufw allow 22/tcp    # OpenSSH
sudo ufw allow 80/tcp    # SSH-WS, VMess-WS, Trojan-WS
sudo ufw allow 443/tcp   # VLESS Reality
sudo ufw allow 109/tcp   # Dropbear SSH
sudo ufw allow 143/tcp   # Dropbear SSH
sudo ufw allow 1080/tcp  # SOCKS5 Proxy
sudo ufw allow 1080/udp  # SOCKS5 UDP Voice/Video Calls
sudo ufw allow 7300/udp  # BadVPN UDPGW (Gaming/Calls)
sudo ufw allow 8080/tcp  # Alternative HTTP Proxy
sudo ufw allow 8880/tcp  # Alternative HTTP Proxy
sudo ufw reload
```

---

## 🔄 System Service Controls (Manual Restart)

Agar kabhi kisi service ko manually restart ya check karna ho:

```bash
# Sabhi tunnel services ek sath restart karne ke liye:
sudo systemctl restart dropbear ssh-ws badvpn xray

# Individual services status:
sudo systemctl status xray
sudo systemctl status ssh-ws
sudo systemctl status dropbear
sudo systemctl status badvpn
```

---

## 📱 Recommended Client Apps

- **Android:** v2rayNG, NapsternetV, SagerNet, HTTP Custom, OpenTunnel, Telegram.
- **iOS:** Streisand, V2Box, Shadowrocket, NapsternetV, Telegram.
- **Windows:** v2rayN, Nekoray, OpenTunnel, Telegram Desktop.

---

## 👤 Author & Brand

- **Author & Owner:** Mohd Khatab (Prime Khatab)
- **Website:** [codewithkhatab.in](https://codewithkhatab.in)
- **GitHub:** [@mohdkhatab](https://github.com/mohdkhatab)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
