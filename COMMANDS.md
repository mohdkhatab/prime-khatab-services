# 📖 Prime Khatab Services - CLI Command Reference

This document provides complete syntax, flags, and examples for using the `vpn-cli` (or `prime-cli`) command-line tool.

---

## ⚡ Quick Global Short Commands

Once installed, you don't even need long command strings. Use these ultra-short commands from any directory:

| Shortcut | Description |
| :--- | :--- |
| **`p`** | Instant 1-letter shortcut to open Prime Khatab Services Menu |
| **`pk`** | "Prime Khatab" 2-letter menu shortcut |
| **`prime`** | Brand name menu launcher |
| **`menu`** | Standard menu launcher |
| **`status`** | Directly check all services status (OpenSSH, Dropbear, Xray, WS, BadVPN) |
| **`live`** | View live client connections per port in real-time |
| **`speed`** | Run instant ping & 25MB CDN download test |
| **`p-users`** | List all registered user accounts and remaining days |
| **`p-clean`** | Manually trigger auto-cleanup of expired accounts |
| **`p-info`** | View VPS hardware, RAM, Disk, Uptime, and BBR status |
| **`p-response`** / **`response`** | Open Custom HTTP WS Response & AI Prompt Wizard |

---

## Command Syntax

```bash
vpn-cli <command> [arguments...]
# or
prime-cli <command> [arguments...]
```

---

## 1. Account Management

### Add SSH Account
Creates an OpenSSH/Dropbear user, sets Linux account expiry date, and outputs connection configuration with HTTP Custom payload.
```bash
sudo vpn-cli add-ssh <username> <password> <days>
```
*Example:*
```bash
sudo vpn-cli add-ssh alex pass123 30
```

### Add V2Ray / VMess (WebSocket)
Generates a random UUID, adds the client to Xray inbound `vmess-ws`, reloads Xray, and outputs standard `vmess://` URI with QR code.
```bash
sudo vpn-cli add-vmess <username> <days>
```
*Example:*
```bash
sudo vpn-cli add-vmess john 30
```

### Add VLESS Reality
Generates a UUID, attaches it to XTLS-Vision flow under Xray inbound `vless-reality`, and outputs direct connection URI with public reality key.
```bash
sudo vpn-cli add-vless <username> <days>
```
*Example:*
```bash
sudo vpn-cli add-vless sam 30
```

### Add Trojan-WS
Creates a Trojan WebSocket credential under Xray `trojan-ws` inbound.
```bash
sudo vpn-cli add-trojan <username> <password> <days>
```
*Example:*
```bash
sudo vpn-cli add-trojan david secret123 30
```

### Add Telegram SOCKS5 Proxy
Creates authenticated SOCKS5 proxy credentials with UDP enabled for Telegram voice and video calls.
```bash
sudo vpn-cli add-socks <username> <password> <days> [port]
```
*Example:*
```bash
sudo vpn-cli add-socks teluser telpass 30 1080
```

---

## 2. Querying & Display

### Show Account Details / Re-generate Link & QR
Reconstructs and displays the connection URI and ANSI QR code for an existing user.
```bash
sudo vpn-cli show-user <protocol> <username>
```
*Valid protocols:* `ssh`, `vmess`, `vless`, `trojan`, `socks`
*Example:*
```bash
sudo vpn-cli show-user vless sam
```

### List All Accounts
Displays a tabulated list of all accounts across all protocols, with creation date, expiry date, and days left.
```bash
sudo vpn-cli list
```

---

## 3. Maintenance & Lifecycle

### Renew / Extend Account
Extends an account's expiry date by a specified number of days.
```bash
sudo vpn-cli renew <protocol> <username> <days_to_add>
```
*Example:*
```bash
sudo vpn-cli renew ssh alex 30
```

### Delete Account
Removes the account from the database and deregisters it from OpenSSH or Xray Core.
```bash
sudo vpn-cli del <protocol> <username>
```
*Example:*
```bash
sudo vpn-cli del vmess john
```

### Auto-Clean Expired Accounts
Scans all accounts across all protocols. If an account has passed its expiration date, it is automatically purged from the system.
```bash
sudo vpn-cli auto-clean
# or
sudo vpn-cli prune
```

---

## 4. System & Server Monitoring

### VPS Dashboard
Outputs CPU model, core count, RAM usage, disk space, uptime, TCP BBR status, and total active users.
```bash
sudo vpn-cli vps-info
```

### Live Online Users & Connection Monitor
Displays active terminal SSH sessions and count of established client connections across all tunnel ports.
```bash
sudo vpn-cli live-users
```

### Service Status Check
Verifies `systemctl` status for OpenSSH, Dropbear, WebSocket Proxy, BadVPN, and Xray Core.
```bash
sudo vpn-cli status
```

### Speedtest
Tests ping to Cloudflare DNS (`1.1.1.1`) and performs a 25MB CDN download speed test.
```bash
sudo vpn-cli speedtest
```

---

## 5. Backup & Recovery

### Backup Database & Configs
Archives `/etc/vpn-manager` and `/usr/local/etc/xray/config.json` into a timestamped `.tar.gz` archive.
```bash
sudo vpn-cli backup
```

### Restore Database
Restores configurations from an archive and restarts services.
```bash
sudo vpn-cli restore /path/to/backup.tar.gz
```

---

## 6. Custom HTTP Response & AI Prompt Manager

### Open Interactive Response Manager
Launches the full interactive wizard with preset options, AI prompt viewer, custom response setter, and reset options.
```bash
sudo vpn-cli custom-response
# or shortcut:
p-response
```

### Get Copy-Paste AI Agent Prompt
Displays a complete template to copy and send to ChatGPT, Claude, DeepSeek, or Gemini.
```bash
sudo vpn-cli get-prompt
```

### View Currently Active Responses
Checks whether you are using the default or a custom HTTP 101 / 200 response.
```bash
sudo vpn-cli view-response
```

### Set Custom HTTP 101 WebSocket Response
Directly paste or pass your custom HTTP 101 response block.
```bash
sudo vpn-cli set-response-101
```

### Set Custom HTTP 200 CONNECT Response
Directly paste or pass your custom HTTP 200 response block.
```bash
sudo vpn-cli set-response-200
```

### Reset to Default Response
Restores the default Prime Khatab Services HTTP 101 & 200 response and restarts `ssh-ws`.
```bash
sudo vpn-cli reset-response
```
