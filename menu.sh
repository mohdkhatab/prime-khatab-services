#!/bin/bash
# =====================================================
#             PRIME KHATAB SERVICES
#    VPS Multi-Tunnel Management Interactive CLI
#    Developed & Branded for: Prime Khatab
# =====================================================

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
NC='\033[0m'

clear_screen() {
    clear
}

show_header() {
    SERVER_IP=$(sudo /usr/local/bin/vpn-cli get-ip 2>/dev/null || curl -s4 --max-time 2 https://api.ipify.org 2>/dev/null || echo "127.0.0.1")
    echo -e "${CYAN}=====================================================${NC}"
    echo -e "${GREEN}               PRIME KHATAB SERVICES                 ${NC}"
    echo -e "${YELLOW}           Premium VPS & Multi-Tunnel CLI            ${NC}"
    echo -e "${BLUE}-----------------------------------------------------${NC}"
    echo -e " ${MAGENTA}Brand / Owner :${NC} Prime Khatab"
    echo -e " ${MAGENTA}Machine IP    :${NC} ${GREEN}${SERVER_IP}${NC} (Real Machine IPv4)"
    echo -e " ${MAGENTA}Optimization  :${NC} TCP BBR Active • Ultra Low Latency"
    echo -e "${CYAN}=====================================================${NC}"
}

while true; do
    clear_screen
    show_header
    echo -e " ${YELLOW}[1]${NC}  Create SSH Account ${GREEN}(WS / Dropbear / BadVPN)${NC}"
    echo -e " ${YELLOW}[2]${NC}  Create V2Ray / VMess Account ${GREEN}(Link & QR)${NC}"
    echo -e " ${YELLOW}[3]${NC}  Create VLESS Reality Account ${GREEN}(Ultra-Fast, No Domain)${NC}"
    echo -e " ${YELLOW}[4]${NC}  Create Trojan Account ${GREEN}(Link & QR)${NC}"
    echo -e " ${YELLOW}[5]${NC}  Create SOCKS5 Proxy ${GREEN}(Telegram 1-Click Link & QR)${NC}"
    echo -e "${BLUE}-----------------------------------------------------${NC}"
    echo -e " ${YELLOW}[6]${NC}  Show Account Link / QR Code ${CYAN}(Re-Generate Link)${NC}"
    echo -e " ${YELLOW}[7]${NC}  List All Active Accounts & Expiration"
    echo -e " ${YELLOW}[8]${NC}  Renew / Extend Account Expiry"
    echo -e " ${YELLOW}[9]${NC}  Delete Single Account"
    echo -e " ${YELLOW}[10]${NC} Auto-Clean All Expired Accounts ${RED}(Prune)${NC}"
    echo -e "${BLUE}-----------------------------------------------------${NC}"
    echo -e " ${YELLOW}[11]${NC} Live Online Users & Connection Statistics"
    echo -e " ${YELLOW}[12]${NC} VPS Dashboard & System Info ${GREEN}(RAM/CPU/Disk/BBR)${NC}"
    echo -e " ${YELLOW}[13]${NC} Speedtest Server Connection"
    echo -e " ${YELLOW}[14]${NC} Check Running Services Status"
    echo -e " ${YELLOW}[15]${NC} Restart All Tunnel Services"
    echo -e " ${YELLOW}[16]${NC} Backup Database & Configurations"
    echo -e " ${YELLOW}[17]${NC} Restore Database from Backup"
    echo -e " ${YELLOW}[18]${NC} Set Custom Domain / Bug Host"
    echo -e " ${YELLOW}[19]${NC} Custom WS HTTP Response ${GREEN}(AI Prompt & Code Setter)${NC}"
    echo -e " ${YELLOW}[0]${NC}  Exit Menu"
    echo -e "${CYAN}=====================================================${NC}"
    echo -e " ${GREEN}Prime Khatab Services${NC} • Fast, Secure & Anonymous"
    echo -e "${CYAN}=====================================================${NC}"
    read -rp " Select option [0-19]: " opt

    case "$opt" in
        1)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Create SSH Account ] ---${NC}"
            read -rp " Enter Username: " username
            read -rp " Enter Password: " password
            read -rp " Active Days [Default 30]: " days
            days=${days:-30}
            sudo /usr/local/bin/vpn-cli add-ssh "$username" "$password" "$days"
            read -rp " Press [Enter] to continue..."
            ;;
        2)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Create VMess Account ] ---${NC}"
            read -rp " Enter Username: " username
            read -rp " Active Days [Default 30]: " days
            days=${days:-30}
            sudo /usr/local/bin/vpn-cli add-vmess "$username" "$days"
            read -rp " Press [Enter] to continue..."
            ;;
        3)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Create VLESS Reality Account ] ---${NC}"
            read -rp " Enter Username: " username
            read -rp " Active Days [Default 30]: " days
            days=${days:-30}
            sudo /usr/local/bin/vpn-cli add-vless "$username" "$days"
            read -rp " Press [Enter] to continue..."
            ;;
        4)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Create Trojan Account ] ---${NC}"
            read -rp " Enter Username: " username
            read -rp " Enter Password: " password
            read -rp " Active Days [Default 30]: " days
            days=${days:-30}
            sudo /usr/local/bin/vpn-cli add-trojan "$username" "$password" "$days"
            read -rp " Press [Enter] to continue..."
            ;;
        5)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Create SOCKS5 Proxy ] ---${NC}"
            read -rp " Enter Username: " username
            read -rp " Enter Password: " password
            read -rp " Enter Port [Default 1080]: " port
            port=${port:-1080}
            read -rp " Active Days [Default 30]: " days
            days=${days:-30}
            sudo /usr/local/bin/vpn-cli add-socks "$username" "$password" "$days" "$port"
            read -rp " Press [Enter] to continue..."
            ;;
        6)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Show Account Link / QR ] ---${NC}"
            echo " Protocols: ssh | vless | vmess | trojan | socks"
            read -rp " Enter Protocol: " proto
            read -rp " Enter Username: " username
            sudo /usr/local/bin/vpn-cli show-user "$proto" "$username"
            read -rp " Press [Enter] to continue..."
            ;;
        7)
            echo ""
            sudo /usr/local/bin/vpn-cli list
            read -rp " Press [Enter] to continue..."
            ;;
        8)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Renew Account ] ---${NC}"
            echo " Protocols: ssh | vless | vmess | trojan | socks"
            read -rp " Enter Protocol: " proto
            read -rp " Enter Username: " username
            read -rp " Extend Days [e.g. 30]: " days
            days=${days:-30}
            sudo /usr/local/bin/vpn-cli renew "$proto" "$username" "$days"
            read -rp " Press [Enter] to continue..."
            ;;
        9)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Delete Account ] ---${NC}"
            echo " Protocols: ssh | vless | vmess | trojan | socks"
            read -rp " Enter Protocol: " proto
            read -rp " Enter Username to Delete: " username
            sudo /usr/local/bin/vpn-cli del "$proto" "$username"
            read -rp " Press [Enter] to continue..."
            ;;
        10)
            echo ""
            echo -e "${YELLOW}[*] Scanning and removing all expired accounts...${NC}"
            sudo /usr/local/bin/vpn-cli auto-clean
            read -rp " Press [Enter] to continue..."
            ;;
        11)
            echo ""
            sudo /usr/local/bin/vpn-cli live-users
            read -rp " Press [Enter] to continue..."
            ;;
        12)
            echo ""
            sudo /usr/local/bin/vpn-cli vps-info
            read -rp " Press [Enter] to continue..."
            ;;
        13)
            echo ""
            sudo /usr/local/bin/vpn-cli speedtest
            read -rp " Press [Enter] to continue..."
            ;;
        14)
            echo ""
            sudo /usr/local/bin/vpn-cli status
            read -rp " Press [Enter] to continue..."
            ;;
        15)
            echo ""
            echo -e "${YELLOW}[*] Restarting Prime Khatab Tunnel Services...${NC}"
            sudo systemctl restart dropbear ssh-ws badvpn xray
            echo -e "${GREEN}[✓] All Prime Khatab Services restarted successfully.${NC}"
            sudo /usr/local/bin/vpn-cli status
            read -rp " Press [Enter] to continue..."
            ;;
        16)
            echo ""
            sudo /usr/local/bin/vpn-cli backup
            read -rp " Press [Enter] to continue..."
            ;;
        17)
            echo ""
            read -rp " Enter Backup File Path [Default latest]: " bpath
            bpath=${bpath:-/home/ubuntu/prime_khatab_backup_latest.tar.gz}
            sudo /usr/local/bin/vpn-cli restore "$bpath"
            read -rp " Press [Enter] to continue..."
            ;;
        18)
            echo ""
            echo -e "${CYAN}--- [ Prime Khatab Services: Custom Domain / Bug Host ] ---${NC}"
            read -rp " Enter Domain (e.g., vpn.yourdomain.com): " domain
            sudo /usr/local/bin/vpn-cli set-domain "$domain"
            read -rp " Press [Enter] to continue..."
            ;;
        19)
            echo ""
            sudo /usr/local/bin/vpn-cli custom-response
            ;;
        0)
            echo ""
            echo -e "${GREEN}Thank you for using Prime Khatab Services! Have a great day!${NC}"
            echo ""
            break
            ;;
        *)
            echo -e "${RED} Invalid option!${NC}"
            sleep 1
            ;;
    esac
done
