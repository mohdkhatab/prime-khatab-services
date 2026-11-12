# 🛠️ Prime Khatab Services - Architecture & Installation Guide

This guide details port allocations, required daemon configurations, and backend system architecture.

---

## 🌐 Port Mapping & Services

| Service | Port(s) | Description |
| :--- | :--- | :--- |
| **OpenSSH** | `22` | Direct SSH Access |
| **Dropbear** | `109, 143` | Lightweight SSH Tunneling |
| **SSH-WS (Multiplexer)** | `80, 8080, 8880` | HTTP / WebSocket Reverse Proxy |
| **VLESS Reality** | `443` | Direct TLS Reality Tunnel (XTLS Vision) |
| **SOCKS5 Proxy** | `1080` | Telegram Proxy with UDP voice/video support |
| **BadVPN UDPGW** | `7300` | UDP Gateway for WhatsApp / Gaming tunneling |
| **VMess (Internal)** | `10086` | Internal inbound proxied via Port 80 /vmess |
| **Trojan (Internal)** | `10087` | Internal inbound proxied via Port 80 /trojan |

---

## 🧱 Firewall Requirements

Ensure the following ports are open in your VPS firewall / cloud security group (AWS, DigitalOcean, Linode, Hetzner, Vultr):

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 109/tcp
sudo ufw allow 143/tcp
sudo ufw allow 1080/tcp
sudo ufw allow 1080/udp
sudo ufw allow 7300/udp
sudo ufw allow 8080/tcp
sudo ufw allow 8880/tcp
sudo ufw reload
```

---

## ⚙️ Backend Architecture

1. **Multiplexer (`services/ssh-ws.py`):**
   - Listens on ports `80`, `8080`, and `8880`.
   - Inspects initial HTTP handshake headers.
   - If path matches `/vmess`, traffic is forwarded locally to Xray VMess inbound (`127.0.0.1:10086`).
   - If path matches `/trojan`, traffic is forwarded locally to Xray Trojan inbound (`127.0.0.1:10087`).
   - Standard SSH WebSocket `Upgrade: websocket` or `CONNECT` requests are routed to Dropbear (`127.0.0.1:109`).

2. **Xray Core (`/usr/local/etc/xray/config.json`):**
   - Handles `vless-reality` on Port `443`.
   - Handles `socks-tg` on Port `1080`.
   - Handles `vmess-ws` on `127.0.0.1:10086`.
   - Handles `trojan-ws` on `127.0.0.1:10087`.

3. **Database (`/etc/vpn-manager/database.json`):**
   - Stores user metadata:
     - Username
     - Password or UUID
     - Creation date
     - Expiry date
     - Protocol type

4. **Auto-Pruning Cron Job (`/etc/cron.daily/prime-khatab-prune`):**
   - Executes daily at 00:00 server time.
   - Automatically unlinks and removes expired users.
