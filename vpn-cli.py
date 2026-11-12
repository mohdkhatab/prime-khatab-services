#!/usr/bin/env python3
# =====================================================
#             PRIME KHATAB SERVICES
#    VPS Multi-Tunnel Management CLI Backend
#    Branded & Developed for: Prime Khatab
# =====================================================

import sys
import os
import json
import uuid
import base64
import time
import subprocess
import ipaddress
from datetime import datetime, timedelta

CONFIG_DIR = "/etc/vpn-manager"
DB_FILE = os.path.join(CONFIG_DIR, "database.json")
CONF_FILE = os.path.join(CONFIG_DIR, "server.conf")
XRAY_CONF = "/usr/local/etc/xray/config.json"
REALITY_ENV = "/usr/local/etc/xray/reality.env"

os.makedirs(CONFIG_DIR, exist_ok=True)

def normalize_proto(proto):
    p = str(proto).lower().strip()
    if p in ["socks5", "socks"]:
        return "socks"
    return p

def is_valid_public_ip(ip_str):
    if not ip_str:
        return False
    try:
        ip = ipaddress.ip_address(str(ip_str).strip())
        return ip.version == 4 and ip.is_global and not (
            ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local
        )
    except Exception:
        return False

def save_detected_ip(ip):
    try:
        lines = []
        if os.path.exists(CONF_FILE):
            with open(CONF_FILE, "r") as f:
                for line in f:
                    if not line.startswith("DETECTED_IP="):
                        lines.append(line)
        lines.append(f"DETECTED_IP={ip}\n")
        with open(CONF_FILE, "w") as f:
            f.writelines(lines)
    except Exception:
        pass

def get_cached_ip():
    if os.path.exists(CONF_FILE):
        try:
            with open(CONF_FILE, "r") as f:
                for line in f:
                    if line.startswith("DETECTED_IP="):
                        val = line.strip().split("=", 1)[1].strip()
                        if val and is_valid_public_ip(val):
                            return val
        except Exception:
            pass
    return None

def get_server_ip():
    # 1. Custom Domain if explicitly configured
    if os.path.exists(CONF_FILE):
        try:
            with open(CONF_FILE, "r") as f:
                for line in f:
                    if line.startswith("DOMAIN="):
                        val = line.strip().split("=", 1)[1].strip()
                        if val:
                            return val
        except Exception:
            pass

    # 2. Dynamic Real Public IP Resolution (Multiple Global High-Speed Endpoints)
    endpoints = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "http://checkip.amazonaws.com",
        "https://ifconfig.me/ip",
        "https://ipinfo.io/ip",
        "https://ip.sb"
    ]
    for url in endpoints:
        try:
            res = subprocess.check_output(
                ["curl", "-s4", "--max-time", "2", url],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if is_valid_public_ip(res):
                save_detected_ip(res)
                return res
        except Exception:
            continue

    # 3. Cloud Provider Metadata Service (AWS EC2, Google Cloud)
    cloud_queries = [
        ["curl", "-s4", "--max-time", "2", "http://169.254.169.254/latest/meta-data/public-ipv4"],
        ["curl", "-s4", "--max-time", "2", "-H", "Metadata-Flavor: Google", "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"]
    ]
    for cmd in cloud_queries:
        try:
            res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            if is_valid_public_ip(res):
                save_detected_ip(res)
                return res
        except Exception:
            continue

    # 4. Check cached verified public IP
    cached = get_cached_ip()
    if cached and is_valid_public_ip(cached):
        return cached

    # 5. Local physical network interfaces (for Hetzner/OVH/Bare Metal with direct public IPv4)
    try:
        raw_ips = subprocess.check_output(["hostname", "-I"], stderr=subprocess.DEVNULL).decode().split()
        for rip in raw_ips:
            if is_valid_public_ip(rip):
                save_detected_ip(rip)
                return rip
    except Exception:
        pass

    return "127.0.0.1"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                data.setdefault("ssh", {})
                data.setdefault("vmess", {})
                data.setdefault("vless", {})
                data.setdefault("trojan", {})
                data.setdefault("socks", {})
                return data
        except Exception:
            pass
    return {"ssh": {}, "vmess": {}, "vless": {}, "trojan": {}, "socks": {}}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def load_xray_config():
    with open(XRAY_CONF, "r") as f:
        return json.load(f)

def save_xray_config(data):
    with open(XRAY_CONF, "w") as f:
        json.dump(data, f, indent=2)
    subprocess.run(["systemctl", "restart", "xray"], check=True)

def print_qr(text):
    try:
        p = subprocess.Popen(["qrencode", "-t", "ANSIUTF8"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode())
    except Exception:
        pass

def add_ssh(user, password, days):
    db = load_db()
    if user in db.get("ssh", {}):
        print(f"\033[1;31m[!] Error: SSH User {user} already exists!\033[0m")
        return False
    
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    cmd = ["useradd", "-e", exp_date, "-s", "/bin/false", "-M", user]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        subprocess.run(["usermod", "-e", exp_date, "-s", "/bin/false", user])
    
    p = subprocess.Popen(["chpasswd"], stdin=subprocess.PIPE)
    p.communicate(input=f"{user}:{password}\n".encode())
    
    db["ssh"][user] = {
        "password": password,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "expired_at": exp_date,
        "days": days
    }
    save_db(db)
    
    ip = get_server_ip()
    print("\n" + "="*54)
    print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
    print("\033[1;32m         SSH VPN ACCOUNT CREATED SUCCESSFULLY\033[0m")
    print("="*54)
    print(f" \033[1;33mUsername       :\033[0m {user}")
    print(f" \033[1;33mPassword       :\033[0m {password}")
    print(f" \033[1;33mHost / IP      :\033[0m {ip}")
    print(f" \033[1;33mOpenSSH Port   :\033[0m 22")
    print(f" \033[1;33mDropbear Port  :\033[0m 109, 143")
    print(f" \033[1;33mSSH WS Port    :\033[0m 80, 8080, 8880 (HTTP / CDN)")
    print(f" \033[1;33mBadVPN (UDPGW) :\033[0m 7300 (Gaming / Calls)")
    print(f" \033[1;33mActive Days    :\033[0m {days} Days")
    print(f" \033[1;33mExpired Date   :\033[0m {exp_date}")
    print("="*54)
    print("\033[1;36mPayload (HTTP Custom / Injector / OpenTunnel):\033[0m")
    print("GET / HTTP/1.1[crlf]Host: bug.com[crlf]Upgrade: websocket[crlf]Connection: Upgrade[crlf][crlf]")
    print("="*54)
    print("\033[1;32m      Powered & Managed by Prime Khatab Services\033[0m")
    print("="*54 + "\n")
    return True

def add_vmess(user, days):
    db = load_db()
    if user in db.get("vmess", {}):
        print(f"\033[1;31m[!] Error: VMess User {user} already exists!\033[0m")
        return False
    
    u_id = str(uuid.uuid4())
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    xcfg = load_xray_config()
    for inbound in xcfg.get("inbounds", []):
        if inbound.get("tag") == "vmess-ws":
            inbound["settings"]["clients"].append({
                "id": u_id,
                "alterId": 0,
                "email": f"{user}@primekhatab"
            })
            break
    save_xray_config(xcfg)
    
    db["vmess"][user] = {
        "id": u_id,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "expired_at": exp_date,
        "days": days
    }
    save_db(db)
    
    ip = get_server_ip()
    v_raw = {
        "v": "2",
        "ps": f"PrimeKhatab-VMess-{user}",
        "add": ip,
        "port": "80",
        "id": u_id,
        "aid": "0",
        "scy": "auto",
        "net": "ws",
        "type": "none",
        "host": ip,
        "path": "/vmess",
        "tls": ""
    }
    v_link = "vmess://" + base64.b64encode(json.dumps(v_raw).encode()).decode()
    
    print("\n" + "="*54)
    print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
    print("\033[1;32m        V2RAY / VMESS ACCOUNT CREATED\033[0m")
    print("="*54)
    print(f" \033[1;33mUsername    :\033[0m {user}")
    print(f" \033[1;33mHost / IP   :\033[0m {ip}")
    print(f" \033[1;33mPort        :\033[0m 80 (Also 8080, 8880)")
    print(f" \033[1;33mUUID        :\033[0m {u_id}")
    print(f" \033[1;33mNetwork     :\033[0m ws (WebSocket)")
    print(f" \033[1;33mPath        :\033[0m /vmess")
    print(f" \033[1;33mActive Days :\033[0m {days} Days")
    print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
    print("="*54)
    print("\033[1;36mVMess Link (Copy into v2rayNG / NapsternetV / v2rayN):\033[0m")
    print(v_link)
    print("="*54)
    print("\033[1;35mQR Code:\033[0m")
    print_qr(v_link)
    print("="*54)
    print("\033[1;32m      Powered & Managed by Prime Khatab Services\033[0m")
    print("="*54 + "\n")
    return True

def add_vless(user, days):
    db = load_db()
    if user in db.get("vless", {}):
        print(f"\033[1;31m[!] Error: VLESS User {user} already exists!\033[0m")
        return False
    
    u_id = str(uuid.uuid4())
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    xcfg = load_xray_config()
    for inbound in xcfg.get("inbounds", []):
        if inbound.get("tag") == "vless-reality":
            inbound["settings"]["clients"].append({
                "id": u_id,
                "flow": "xtls-rprx-vision",
                "email": f"{user}@primekhatab"
            })
            break
    save_xray_config(xcfg)
    
    db["vless"][user] = {
        "id": u_id,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "expired_at": exp_date,
        "days": days
    }
    save_db(db)
    
    pub_key = "9df9bO4HUb7IV8sljoAN6gHCNxe3U0NEZc7N9_Pcxic"
    short_id = "0a1d835a"
    server_name = "www.microsoft.com"
    if os.path.exists(REALITY_ENV):
        with open(REALITY_ENV) as f:
            for l in f:
                if l.startswith("PUB="):
                    pub_key = l.strip().split("=")[1]
                elif l.startswith("SHORT_ID="):
                    short_id = l.strip().split("=")[1]
                elif l.startswith("SERVER_NAME="):
                    server_name = l.strip().split("=")[1]
                    
    ip = get_server_ip()
    vless_link = f"vless://{u_id}@{ip}:443?security=reality&encryption=none&pbk={pub_key}&headerType=none&fp=chrome&spx=%2F&type=tcp&sni={server_name}&sid={short_id}&flow=xtls-rprx-vision#PrimeKhatab-VLESS-{user}"
    
    print("\n" + "="*54)
    print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
    print("\033[1;32m      VLESS REALITY ACCOUNT CREATED (NO DOMAIN)\033[0m")
    print("="*54)
    print(f" \033[1;33mUsername    :\033[0m {user}")
    print(f" \033[1;33mHost / IP   :\033[0m {ip}")
    print(f" \033[1;33mPort        :\033[0m 443")
    print(f" \033[1;33mUUID        :\033[0m {u_id}")
    print(f" \033[1;33mFlow        :\033[0m xtls-rprx-vision")
    print(f" \033[1;33mSecurity    :\033[0m reality (TLS)")
    print(f" \033[1;33mSNI         :\033[0m {server_name}")
    print(f" \033[1;33mPublic Key  :\033[0m {pub_key}")
    print(f" \033[1;33mShortId     :\033[0m {short_id}")
    print(f" \033[1;33mActive Days :\033[0m {days} Days")
    print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
    print("="*54)
    print("\033[1;36mVLESS Link (v2rayNG / NapsternetV / Streisand):\033[0m")
    print(vless_link)
    print("="*54)
    print("\033[1;35mQR Code:\033[0m")
    print_qr(vless_link)
    print("="*54)
    print("\033[1;32m      Powered & Managed by Prime Khatab Services\033[0m")
    print("="*54 + "\n")
    return True

def add_trojan(user, password, days):
    db = load_db()
    if user in db.get("trojan", {}):
        print(f"\033[1;31m[!] Error: Trojan User {user} already exists!\033[0m")
        return False
    
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    xcfg = load_xray_config()
    for inbound in xcfg.get("inbounds", []):
        if inbound.get("tag") == "trojan-ws":
            inbound["settings"]["clients"].append({
                "password": password,
                "email": f"{user}@primekhatab"
            })
            break
    save_xray_config(xcfg)
    
    db["trojan"][user] = {
        "password": password,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "expired_at": exp_date,
        "days": days
    }
    save_db(db)
    
    ip = get_server_ip()
    trojan_link = f"trojan://{password}@{ip}:80?path=%2Ftrojan&security=none&type=ws#PrimeKhatab-Trojan-{user}"
    
    print("\n" + "="*54)
    print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
    print("\033[1;32m           TROJAN-WS ACCOUNT CREATED\033[0m")
    print("="*54)
    print(f" \033[1;33mUsername    :\033[0m {user}")
    print(f" \033[1;33mPassword    :\033[0m {password}")
    print(f" \033[1;33mHost / IP   :\033[0m {ip}")
    print(f" \033[1;33mPort        :\033[0m 80 (Also 8080, 8880)")
    print(f" \033[1;33mPath        :\033[0m /trojan")
    print(f" \033[1;33mActive Days :\033[0m {days} Days")
    print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
    print("="*54)
    print("\033[1;36mTrojan Link:\033[0m")
    print(trojan_link)
    print("="*54)
    print("\033[1;35mQR Code:\033[0m")
    print_qr(trojan_link)
    print("="*54)
    print("\033[1;32m      Powered & Managed by Prime Khatab Services\033[0m")
    print("="*54 + "\n")
    return True

def add_socks(user, password, days, port=1080):
    db = load_db()
    if user in db.get("socks", {}):
        print(f"\033[1;31m[!] Error: SOCKS5 User {user} already exists!\033[0m")
        return False
    
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    xcfg = load_xray_config()
    socks_inbound = None
    for inbound in xcfg.get("inbounds", []):
        if inbound.get("tag") == "socks-tg":
            socks_inbound = inbound
            break
            
    if socks_inbound is None:
        socks_inbound = {
            "tag": "socks-tg",
            "port": port,
            "listen": "0.0.0.0",
            "protocol": "socks",
            "settings": {
                "auth": "password",
                "accounts": [],
                "udp": True
            }
        }
        xcfg["inbounds"].append(socks_inbound)
    else:
        port = socks_inbound.get("port", port)
        
    socks_inbound["settings"]["accounts"].append({
        "user": user,
        "pass": password
    })
    save_xray_config(xcfg)
    
    db["socks"][user] = {
        "password": password,
        "port": port,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "expired_at": exp_date,
        "days": days
    }
    save_db(db)
    
    ip = get_server_ip()
    tg_direct = f"tg://socks?server={ip}&port={port}&user={user}&pass={password}"
    tg_link = f"https://t.me/socks?server={ip}&port={port}&user={user}&pass={password}"
    
    print("\n" + "="*54)
    print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
    print("\033[1;32m       TELEGRAM SOCKS5 PROXY CREATED\033[0m")
    print("="*54)
    print(f" \033[1;33mUsername       :\033[0m {user}")
    print(f" \033[1;33mPassword       :\033[0m {password}")
    print(f" \033[1;33mHost / IP      :\033[0m {ip}")
    print(f" \033[1;33mPort           :\033[0m {port}")
    print(f" \033[1;33mUDP / Voice    :\033[0m Enabled (Voice & Video Calls)")
    print(f" \033[1;33mActive Days    :\033[0m {days} Days")
    print(f" \033[1;33mExpired Date   :\033[0m {exp_date}")
    print("="*54)
    print("\033[1;36mTelegram 1-Click Link (Mobile & Desktop):\033[0m")
    print(tg_link)
    print(f"\033[1;36mDirect URI     :\033[0m {tg_direct}")
    print("="*54)
    print("\033[1;35mQR Code:\033[0m")
    print_qr(tg_link)
    print("="*54)
    print("\033[1;32m      Powered & Managed by Prime Khatab Services\033[0m")
    print("="*54 + "\n")
    return True

def show_user(proto, user):
    proto = normalize_proto(proto)
    db = load_db()
    if proto not in db or user not in db[proto]:
        print(f"\033[1;31m[!] User {user} not found in {proto.upper()} database!\033[0m")
        return False
    
    info = db[proto][user]
    ip = get_server_ip()
    exp_date = info.get("expired_at", "N/A")
    created = info.get("created_at", "N/A")
    days = info.get("days", 30)
    
    if proto == "ssh":
        password = info.get("password", "")
        print("\n" + "="*54)
        print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
        print("\033[1;32m              SSH ACCOUNT DETAILS\033[0m")
        print("="*54)
        print(f" \033[1;33mUsername       :\033[0m {user}")
        print(f" \033[1;33mPassword       :\033[0m {password}")
        print(f" \033[1;33mHost / IP      :\033[0m {ip}")
        print(f" \033[1;33mOpenSSH Port   :\033[0m 22")
        print(f" \033[1;33mDropbear Port  :\033[0m 109, 143")
        print(f" \033[1;33mSSH WS Port    :\033[0m 80, 8080, 8880")
        print(f" \033[1;33mBadVPN (UDPGW) :\033[0m 7300")
        print(f" \033[1;33mCreated Date   :\033[0m {created}")
        print(f" \033[1;33mExpired Date   :\033[0m {exp_date}")
        print("="*54)
        print("\033[1;36mPayload:\033[0m")
        print("GET / HTTP/1.1[crlf]Host: bug.com[crlf]Upgrade: websocket[crlf]Connection: Upgrade[crlf][crlf]")
        print("="*54 + "\n")
    elif proto == "vmess":
        u_id = info.get("id", "")
        v_raw = {
            "v": "2", "ps": f"PrimeKhatab-VMess-{user}", "add": ip, "port": "80",
            "id": u_id, "aid": "0", "scy": "auto", "net": "ws", "type": "none",
            "host": ip, "path": "/vmess", "tls": ""
        }
        v_link = "vmess://" + base64.b64encode(json.dumps(v_raw).encode()).decode()
        print("\n" + "="*54)
        print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
        print("\033[1;32m             VMESS ACCOUNT DETAILS\033[0m")
        print("="*54)
        print(f" \033[1;33mUsername    :\033[0m {user}")
        print(f" \033[1;33mHost / IP   :\033[0m {ip}")
        print(f" \033[1;33mPort        :\033[0m 80, 8080, 8880")
        print(f" \033[1;33mUUID        :\033[0m {u_id}")
        print(f" \033[1;33mCreated     :\033[0m {created}")
        print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
        print("="*54)
        print("\033[1;36mVMess Link:\033[0m")
        print(v_link)
        print("="*54)
        print("\033[1;35mQR Code:\033[0m")
        print_qr(v_link)
        print("="*54 + "\n")
    elif proto == "vless":
        u_id = info.get("id", "")
        pub_key = "9df9bO4HUb7IV8sljoAN6gHCNxe3U0NEZc7N9_Pcxic"
        short_id = "0a1d835a"
        server_name = "www.microsoft.com"
        if os.path.exists(REALITY_ENV):
            with open(REALITY_ENV) as f:
                for l in f:
                    if l.startswith("PUB="): pub_key = l.strip().split("=")[1]
                    elif l.startswith("SHORT_ID="): short_id = l.strip().split("=")[1]
                    elif l.startswith("SERVER_NAME="): server_name = l.strip().split("=")[1]
        vless_link = f"vless://{u_id}@{ip}:443?security=reality&encryption=none&pbk={pub_key}&headerType=none&fp=chrome&spx=%2F&type=tcp&sni={server_name}&sid={short_id}&flow=xtls-rprx-vision#PrimeKhatab-VLESS-{user}"
        print("\n" + "="*54)
        print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
        print("\033[1;32m          VLESS REALITY ACCOUNT DETAILS\033[0m")
        print("="*54)
        print(f" \033[1;33mUsername    :\033[0m {user}")
        print(f" \033[1;33mHost / IP   :\033[0m {ip}:443")
        print(f" \033[1;33mUUID        :\033[0m {u_id}")
        print(f" \033[1;33mSNI         :\033[0m {server_name}")
        print(f" \033[1;33mCreated     :\033[0m {created}")
        print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
        print("="*54)
        print("\033[1;36mVLESS Link:\033[0m")
        print(vless_link)
        print("="*54)
        print("\033[1;35mQR Code:\033[0m")
        print_qr(vless_link)
        print("="*54 + "\n")
    elif proto == "trojan":
        password = info.get("password", "")
        trojan_link = f"trojan://{password}@{ip}:80?path=%2Ftrojan&security=none&type=ws#PrimeKhatab-Trojan-{user}"
        print("\n" + "="*54)
        print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
        print("\033[1;32m            TROJAN ACCOUNT DETAILS\033[0m")
        print("="*54)
        print(f" \033[1;33mUsername    :\033[0m {user}")
        print(f" \033[1;33mPassword    :\033[0m {password}")
        print(f" \033[1;33mPort        :\033[0m 80, 8080, 8880")
        print(f" \033[1;33mCreated     :\033[0m {created}")
        print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
        print("="*54)
        print("\033[1;36mTrojan Link:\033[0m")
        print(trojan_link)
        print("="*54)
        print("\033[1;35mQR Code:\033[0m")
        print_qr(trojan_link)
        print("="*54 + "\n")
    elif proto == "socks":
        password = info.get("password", "")
        port = info.get("port", 1080)
        tg_direct = f"tg://socks?server={ip}&port={port}&user={user}&pass={password}"
        tg_link = f"https://t.me/socks?server={ip}&port={port}&user={user}&pass={password}"
        print("\n" + "="*54)
        print("\033[1;36m               PRIME KHATAB SERVICES\033[0m")
        print("\033[1;32m            SOCKS5 PROXY DETAILS\033[0m")
        print("="*54)
        print(f" \033[1;33mUsername    :\033[0m {user}")
        print(f" \033[1;33mPassword    :\033[0m {password}")
        print(f" \033[1;33mPort        :\033[0m {port}")
        print(f" \033[1;33mCreated     :\033[0m {created}")
        print(f" \033[1;33mExpired Date:\033[0m {exp_date}")
        print("="*54)
        print("\033[1;36mTelegram 1-Click Link:\033[0m")
        print(tg_link)
        print(f"\033[1;36mDirect URI           :\033[0m {tg_direct}")
        print("="*54)
        print("\033[1;35mQR Code:\033[0m")
        print_qr(tg_link)
        print("="*54 + "\n")
    return True

def auto_clean_expired():
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    expired_list = []
    
    for proto in ["ssh", "vless", "vmess", "trojan", "socks"]:
        for user, info in list(db.get(proto, {}).items()):
            exp_s = info.get("expired_at", "")
            if exp_s and exp_s < today:
                expired_list.append((proto, user, exp_s))
                
    if not expired_list:
        print("\n\033[1;32m[✓] No expired accounts found. All accounts are currently active.\033[0m\n")
        return True
        
    print(f"\n\033[1;33m[*] Found {len(expired_list)} expired account(s). Cleaning up...\033[0m")
    for proto, user, exp_s in expired_list:
        print(f" - Cleaning expired {proto.upper()} user: {user} (Expired on: {exp_s})")
        del_user(proto, user)
        
    print(f"\033[1;32m[✓] Successfully pruned and removed {len(expired_list)} expired account(s).\033[0m\n")
    return True

def del_user(proto, user):
    proto = normalize_proto(proto)
    db = load_db()
    if proto not in db or user not in db[proto]:
        print(f"\033[1;31m[!] User {user} not found in {proto}!\033[0m")
        return False
    
    del db[proto][user]
    save_db(db)
    
    if proto == "ssh":
        subprocess.run(["userdel", "-f", user], stderr=subprocess.DEVNULL)
        print(f"\033[1;32m[✓] SSH user {user} deleted successfully from Prime Khatab Services.\033[0m")
    elif proto == "socks":
        xcfg = load_xray_config()
        for inbound in xcfg.get("inbounds", []):
            if inbound.get("tag") == "socks-tg":
                inbound["settings"]["accounts"] = [
                    a for a in inbound["settings"].get("accounts", [])
                    if a.get("user") != user
                ]
                break
        save_xray_config(xcfg)
        print(f"\033[1;32m[✓] SOCKS5 user {user} deleted successfully from Prime Khatab Services.\033[0m")
    else:
        xcfg = load_xray_config()
        tag = f"{proto}-reality" if proto == "vless" else f"{proto}-ws"
        for inbound in xcfg.get("inbounds", []):
            if inbound.get("tag") == tag:
                inbound["settings"]["clients"] = [
                    c for c in inbound["settings"]["clients"]
                    if c.get("email") not in [f"{user}@primekhatab", f"{user}@vpn"]
                ]
                break
        save_xray_config(xcfg)
        print(f"\033[1;32m[✓] {proto.upper()} user {user} deleted successfully from Prime Khatab Services.\033[0m")
    return True

def renew_user(proto, user, days):
    proto = normalize_proto(proto)
    db = load_db()
    if proto not in db or user not in db[proto]:
        print(f"\033[1;31m[!] User {user} not found in {proto}!\033[0m")
        return False
    
    current_exp = db[proto][user].get("expired_at", "")
    try:
        cur_date = datetime.strptime(current_exp, "%Y-%m-%d")
        if cur_date < datetime.now():
            cur_date = datetime.now()
    except Exception:
        cur_date = datetime.now()
        
    new_exp = (cur_date + timedelta(days=days)).strftime("%Y-%m-%d")
    db[proto][user]["expired_at"] = new_exp
    save_db(db)
    
    if proto == "ssh":
        subprocess.run(["usermod", "-e", new_exp, user])
    
    print(f"\033[1;32m[✓] User {user} ({proto.upper()}) renewed by {days} days. New Expiry: {new_exp}\033[0m")
    return True

def list_users():
    db = load_db()
    print("\n" + "="*68)
    print("\033[1;36m               PRIME KHATAB SERVICES - USER ACCOUNTS\033[0m")
    print("="*68)
    print(f" \033[1;33m{'PROTOCOL':<10} {'USERNAME':<16} {'CREATED':<12} {'EXPIRES':<12} {'DAYS LEFT':<10}\033[0m")
    print("="*68)
    total = 0
    now = datetime.now().date()
    for proto in ["ssh", "vless", "vmess", "trojan", "socks"]:
        users = db.get(proto, {})
        for u, info in users.items():
            total += 1
            exp_s = info.get("expired_at", "-")
            days_left = "-"
            try:
                exp_d = datetime.strptime(exp_s, "%Y-%m-%d").date()
                diff = (exp_d - now).days
                days_left = f"{diff}d" if diff >= 0 else "\033[1;31mEXPIRED\033[0m"
            except Exception:
                pass
            created = info.get("created_at", "-")
            print(f" {proto.upper():<10} {u:<16} {created:<12} {exp_s:<12} {days_left:<10}")
    if total == 0:
        print("  \033[1;33mNo accounts found. Use the menu to create one.\033[0m")
    print("="*68)
    print("\033[1;32m       Prime Khatab Services - All Rights Reserved\033[0m")
    print("="*68 + "\n")

def vps_info():
    uptime = "N/A"
    try:
        with open("/proc/uptime", "r") as f:
            total_seconds = float(f.readline().split()[0])
            days = int(total_seconds // 86400)
            hours = int((total_seconds % 86400) // 3600)
            minutes = int((total_seconds % 3600) // 60)
            uptime = f"{days}d {hours}h {minutes}m"
    except Exception:
        pass

    ram_info = "N/A"
    try:
        with open("/proc/meminfo", "r") as f:
            mem = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    mem[parts[0].strip()] = int(parts[1].split()[0])
            total = mem.get("MemTotal", 0) // 1024
            avail = mem.get("MemAvailable", 0) // 1024
            used = total - avail
            pct = int((used / total) * 100) if total else 0
            ram_info = f"{used}MB / {total}MB ({pct}%)"
    except Exception:
        pass

    disk_info = "N/A"
    try:
        st = os.statvfs("/")
        total_g = (st.f_blocks * st.f_frsize) / (1024**3)
        free_g = (st.f_bavail * st.f_frsize) / (1024**3)
        used_g = total_g - free_g
        pct = int((used_g / total_g) * 100) if total_g else 0
        disk_info = f"{used_g:.1f}GB / {total_g:.1f}GB ({pct}%)"
    except Exception:
        pass

    cpu_model = "N/A"
    cpu_cores = os.cpu_count() or 1
    try:
        with open("/proc/cpuinfo") as f:
            for l in f:
                if "model name" in l:
                    cpu_model = l.split(":", 1)[1].strip()
                    break
    except Exception:
        pass

    bbr_status = "Disabled"
    try:
        cc = subprocess.check_output(["sysctl", "-n", "net.ipv4.tcp_congestion_control"]).decode().strip()
        if cc == "bbr":
            bbr_status = "\033[1;32mEnabled (TCP BBR Active)\033[0m"
        else:
            bbr_status = f"\033[1;33m{cc}\033[0m"
    except Exception:
        pass

    db = load_db()
    total_acc = sum(len(db.get(p, {})) for p in ["ssh", "vless", "vmess", "trojan", "socks"])
    ip = get_server_ip()

    print("\n" + "="*58)
    print("\033[1;36m           PRIME KHATAB SERVICES - VPS DASHBOARD\033[0m")
    print("="*58)
    print(f" \033[1;33mBrand / Owner   :\033[0m Prime Khatab")
    print(f" \033[1;33mServer Host/IP  :\033[0m {ip}")
    print(f" \033[1;33mCPU Model       :\033[0m {cpu_model} ({cpu_cores} Cores)")
    print(f" \033[1;33mRAM Usage       :\033[0m {ram_info}")
    print(f" \033[1;33mDisk Usage      :\033[0m {disk_info}")
    print(f" \033[1;33mServer Uptime   :\033[0m {uptime}")
    print(f" \033[1;33mTCP Congestion  :\033[0m {bbr_status}")
    print(f" \033[1;33mTotal Accounts  :\033[0m {total_acc} Users")
    print("="*58)
    print("\033[1;32m      Prime Khatab Services • High Speed Tunnel VPS\033[0m")
    print("="*58 + "\n")

def live_users():
    print("\n" + "="*58)
    print("\033[1;36m          PRIME KHATAB SERVICES - LIVE CONNECTIONS\033[0m")
    print("="*58)
    
    print("\033[1;33m[ Active SSH / Terminal Sessions ]:\033[0m")
    try:
        who_out = subprocess.check_output(["who"]).decode().strip()
        if who_out:
            for line in who_out.splitlines():
                print(f"  • {line}")
        else:
            print("  (No direct terminal SSH sessions)")
    except Exception:
        print("  (Unable to check who)")

    ports_map = [
        ("SSH OpenSSH", "22"),
        ("Dropbear SSH", "109,143"),
        ("SSH & Multi-WS Proxy", "80,8080,8880"),
        ("VLESS Reality", "443"),
        ("SOCKS5 Proxy", "1080"),
        ("BadVPN UDPGW", "7300")
    ]
    
    print("\n\033[1;33m[ Active Client Connections By Tunnel Service ]:\033[0m")
    try:
        ss_out = subprocess.check_output(["ss", "-ant"]).decode()
        for label, port_str in ports_map:
            p_list = [p.strip() for p in port_str.split(",")]
            count = 0
            for line in ss_out.splitlines():
                if "ESTAB" in line:
                    for p in p_list:
                        if f":{p} " in line or f":{p}\t" in line:
                            count += 1
                            break
            print(f"  {label:<24} (Port {port_str:<12}) : \033[1;32m{count} active connection(s)\033[0m")
    except Exception as e:
        print(f"  Error reading sockets: {e}")

    print("="*58 + "\n")

def speedtest():
    print("\n" + "="*56)
    print("\033[1;36m         PRIME KHATAB SERVICES - SPEEDTEST\033[0m")
    print("="*56)
    print(" [*] Testing ping and latency...")
    try:
        ping_res = subprocess.check_output(["ping", "-c", "4", "1.1.1.1"]).decode()
        avg_line = [l for l in ping_res.splitlines() if "min/avg/max" in l or "rtt" in l]
        if avg_line:
            rtt = avg_line[0].split("=")[1].strip().split("/")[1]
            print(f" \033[1;33mAverage Ping (1.1.1.1) :\033[0m \033[1;32m{rtt} ms\033[0m")
    except Exception:
        print(" [!] Ping test skipped.")

    print(" [*] Testing download speed via CDN (25MB payload)...")
    try:
        cmd = ["curl", "-s", "-w", "%{speed_download} %{time_total}", "-o", "/dev/null", "https://speed.cloudflare.com/__down?bytes=25000000"]
        out = subprocess.check_output(cmd, timeout=15).decode().strip().split()
        if len(out) >= 2:
            speed_bps = float(out[0])
            time_tot = float(out[1])
            speed_mbps = (speed_bps * 8) / (1024 * 1024)
            speed_mb_s = speed_bps / (1024 * 1024)
            print(f" \033[1;33mDownload Speed         :\033[0m \033[1;32m{speed_mbps:.2f} Mbps\033[0m ({speed_mb_s:.2f} MB/s)")
            print(f" \033[1;33mDuration               :\033[0m {time_tot:.2f}s")
    except Exception as e:
        print(f" [!] Speed test failed or timed out: {e}")

    print("="*56 + "\n")

def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/home/ubuntu/prime_khatab_backup_{timestamp}.tar.gz"
    
    items = []
    if os.path.exists(CONFIG_DIR): items.append(CONFIG_DIR)
    if os.path.exists(XRAY_CONF): items.append(XRAY_CONF)
    if os.path.exists(REALITY_ENV): items.append(REALITY_ENV)
    
    cmd = ["tar", "-czf", backup_file] + items
    res = subprocess.run(cmd)
    if res.returncode == 0:
        subprocess.run(["ln", "-sf", backup_file, "/home/ubuntu/prime_khatab_backup_latest.tar.gz"])
        print("\n" + "="*56)
        print(f"\033[1;32m[✓] Backup created successfully!\033[0m")
        print(f" File Location : {backup_file}")
        print(f" Latest Link   : /home/ubuntu/prime_khatab_backup_latest.tar.gz")
        print("="*56 + "\n")
        return True
    else:
        print("\033[1;31m[!] Failed to create backup!\033[0m")
        return False

def restore_db(tar_path="/home/ubuntu/prime_khatab_backup_latest.tar.gz"):
    if not os.path.exists(tar_path):
        print(f"\033[1;31m[!] Backup file not found: {tar_path}\033[0m")
        return False
    res = subprocess.run(["tar", "-xzf", tar_path, "-C", "/"])
    if res.returncode == 0:
        subprocess.run(["systemctl", "restart", "xray", "ssh-ws", "dropbear"], check=False)
        print("\n" + "="*56)
        print(f"\033[1;32m[✓] Database & Configurations restored successfully!\033[0m")
        print(" All tunnel services have been restarted.")
        print("="*56 + "\n")
        return True
    else:
        print("\033[1;31m[!] Failed to extract backup!\033[0m")
        return False

def status():
    services = [
        ("OpenSSH (Port 22)", "ssh"),
        ("Dropbear SSH (Port 109, 143)", "dropbear"),
        ("SSH & Multi-WS Proxy (Port 80, 8080, 8880)", "ssh-ws"),
        ("BadVPN UDPGW (Port 7300)", "badvpn"),
        ("Xray Core (VLESS, VMess, Trojan, SOCKS5)", "xray")
    ]
    print("\n" + "="*56)
    print("\033[1;36m          PRIME KHATAB SERVICES - SYSTEM STATUS\033[0m")
    print("="*56)
    for name, srv in services:
        r = subprocess.run(["systemctl", "is-active", "--quiet", srv])
        if r.returncode == 0:
            st = "\033[1;32m[ RUNNING ]\033[0m"
        else:
            st = "\033[1;31m[ STOPPED ]\033[0m"
        print(f" {name:<42} {st}")
    print("="*56)
    print("\033[1;32m               Prime Khatab Tunnel Core\033[0m")
    print("="*56 + "\n")

def set_domain(domain):
    with open(CONF_FILE, "w") as f:
        f.write(f"DOMAIN={domain}\n")
    print(f"\033[1;32m[✓] Server domain set to: {domain}\033[0m")

def print_help():
    print("""
=======================================================
               PRIME KHATAB SERVICES
          VPS Multi-Tunnel Management CLI
=======================================================
 Usage:
   vpn-cli add-ssh <user> <pass> <days>
   vpn-cli add-vmess <user> <days>
   vpn-cli add-vless <user> <days>
   vpn-cli add-trojan <user> <pass> <days>
   vpn-cli add-socks <user> <pass> <days> [port]
   vpn-cli show-user <proto> <user>
   vpn-cli renew <proto> <user> <days>
   vpn-cli del <proto> <user>
   vpn-cli auto-clean
   vpn-cli list
   vpn-cli status
   vpn-cli vps-info
   vpn-cli live-users
   vpn-cli speedtest
   vpn-cli backup
   vpn-cli restore [file]
   vpn-cli set-domain <domain>

 Interactive Menu:
   Type 'menu' or 'prime' to launch interactive interface.
=======================================================
""")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print_help()
        sys.exit(0)
        
    cmd = sys.argv[1].lower()
    try:
        if cmd == "add-ssh":
            add_ssh(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        elif cmd == "add-vmess":
            add_vmess(sys.argv[2], int(sys.argv[3]))
        elif cmd == "add-vless":
            add_vless(sys.argv[2], int(sys.argv[3]))
        elif cmd == "add-trojan":
            add_trojan(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        elif cmd in ["add-socks", "add-socks5"]:
            port = int(sys.argv[5]) if len(sys.argv) > 5 else 1080
            add_socks(sys.argv[2], sys.argv[3], int(sys.argv[4]), port)
        elif cmd == "show-user":
            show_user(sys.argv[2], sys.argv[3])
        elif cmd == "del":
            del_user(sys.argv[2], sys.argv[3])
        elif cmd == "renew":
            renew_user(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        elif cmd in ["auto-clean", "prune"]:
            auto_clean_expired()
        elif cmd == "list":
            list_users()
        elif cmd == "status":
            status()
        elif cmd in ["vps-info", "dashboard", "info"]:
            vps_info()
        elif cmd in ["live-users", "live", "online"]:
            live_users()
        elif cmd == "speedtest":
            speedtest()
        elif cmd == "backup":
            backup_db()
        elif cmd == "restore":
            path = sys.argv[2] if len(sys.argv) > 2 else "/home/ubuntu/prime_khatab_backup_latest.tar.gz"
            restore_db(path)
        elif cmd == "set-domain":
            set_domain(sys.argv[2])
        elif cmd in ["get-ip", "ip", "my-ip"]:
            print(get_server_ip())
        else:
            print_help()
    except IndexError:
        print(f"\033[1;31m[!] Missing required arguments for command '{cmd}'.\033[0m")
        print_help()
