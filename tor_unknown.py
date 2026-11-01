#!/usr/bin/env python3
import time
import sys
import os
import random
import json
import requests
from stem import Signal
from stem.control import Controller
from colorama import init, Fore

# تهيئة الألوان
init(autoreset=True)

# ملف السجلات بصيغة JSON
LOG_FILE = "tor_unknown.json"

def banner():
    print(Fore.CYAN + """
    ████████╗ ██████╗ ██████╗     ██╗   ██╗███╗   ██╗██╗  ██╗███╗   ██╗ ██████╗ ███╗   ██╗
    ╚══██╔══╝██╔═══██╗██╔══██╗    ██║   ██║████╗  ██║██║ ██╔╝████╗  ██║██╔═══██╗████╗  ██║
       ██║   ██║   ██║██████╔╝    ██║   ██║██╔██╗ ██║█████╔╝ ██╔██╗ ██║██║   ██║██╔██╗ ██║
       ██║   ██║   ██║██╔══██╗    ██║   ██║██║╚██╗██║██╔═██╗ ██║╚██╗██║██║   ██║██║╚██╗██║
       ██║   ╚██████╔╝██║  ██║    ╚██████╔╝██║ ╚████║██║  ██╗██║ ╚████║╚██████╔╝██║ ╚████║
       ╚═╝    ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═══╝
         [ Tool Name: TOR_UNKNOWN | Advanced Pro Edition with Leak Shield & JSON Logs ]
    """ + Fore.RESET)

def check_tor_service():
    """التحقق مما إذا كانت خدمة تور تعمل"""
    response = os.system("systemctl is-active --quiet tor")
    if response != 0:
        print(Fore.RED + "[!] Error: Tor service is not running. Start it using: sudo systemctl start tor" + Fore.RESET)
        sys.exit(1)

def check_ip_leak():
    """التحقق من عدم تسرب الـ IP الحقيقي قبل بدء الأداة"""
    print(Fore.YELLOW + "[*] Checking for IP/DNS leaks..." + Fore.RESET)
    
    real_ip = None
    try:
        # محاولة جلب الـ IP الحقيقي بدون بروكسي لفحصه
        real_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
    except:
        pass

    try:
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        tor_res = requests.get('http://ip-api.com/json/', proxies=proxies, timeout=10).json()
        tor_ip = tor_res.get('query')
    except:
        tor_ip = None

    if not tor_ip:
        print(Fore.RED + "[!] Error: Cannot connect through Tor SOCKS proxy (127.0.0.1:9050). Check Tor service." + Fore.RESET)
        sys.exit(1)

    if real_ip and real_ip == tor_ip:
        print(Fore.RED + "[!] CRITICAL WARNING: IP Leak Detected! Tor IP matches your real IP address!" + Fore.RESET)
        sys.exit(1)
    else:
        print(Fore.GREEN + f"[+] Leak Check Passed! Secure Tor IP detected: {tor_ip}\n" + Fore.RESET)

def change_ip():
    """طلب هوية جديدة من شبكة تور"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            return True
    except Exception as e:
        print(Fore.RED + f"[!] ControlPort Error: {e}" + Fore.RESET)
        return False

def get_ip_info():
    """جلب عنوان الـ IP الحالي مع معلومات الدولة والمنطقة عبر بروكسي تور"""
    try:
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        response = requests.get('http://ip-api.com/json/', proxies=proxies, timeout=10)
        data = response.json()
        
        if data.get('status') == 'success':
            ip = data.get('query')
            country = data.get('country', 'Unknown')
            city = data.get('city', 'Unknown')
            isp = data.get('isp', 'Unknown')
            return ip, country, city, isp
        else:
            return None, "Unknown", "Unknown", "Unknown"
    except:
        return None, "Connection Failed", "Connection Failed", "Connection Failed"

def log_ip(ip_address, country, city, isp, timestamp):
    """حفظ الـ IP ومعلوماته في ملف السجلات بصيغة JSON Lines"""
    log_entry = {
        "timestamp": timestamp,
        "ip": ip_address,
        "country": country,
        "city": city,
        "isp": isp
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(Fore.YELLOW + f"[!] Warning: Could not write to log file: {e}" + Fore.RESET)

def main():
    banner()
    check_tor_service()
    check_ip_leak()

    print(Fore.YELLOW + "[?] Select Rotation Mode:" + Fore.RESET)
    print(Fore.WHITE + "    1. Fixed Interval (Constant time between changes)")
    print(Fore.WHITE + "    2. Random Interval (Dynamic time range for better stealth)\n")
    
    try:
        mode = input(Fore.YELLOW + "[?] Choose mode (1 or 2): " + Fore.RESET).strip()
        if mode == "2":
            min_t = int(input(Fore.YELLOW + "[?] Enter MIN seconds (e.g., 20): " + Fore.RESET))
            max_t = int(input(Fore.YELLOW + "[?] Enter MAX seconds (e.g., 60): " + Fore.RESET))
            is_random = True
        else:
            interval = int(input(Fore.YELLOW + "[?] Enter rotation interval in seconds (e.g., 30): " + Fore.RESET))
            is_random = False
    except ValueError:
        print(Fore.RED + "[!] Invalid input. Defaulting to fixed 30 seconds." + Fore.RESET)
        interval = 30
        is_random = False

    print(Fore.GREEN + "\n[*] Starting TOR_UNKNOWN Advanced Engine..." + Fore.RESET)
    print(Fore.CYAN + f"[*] JSON logs are being saved automatically to: {os.path.abspath(LOG_FILE)}" + Fore.RESET)
    print(Fore.CYAN + "[*] Press Ctrl+C to stop the tool safely.\n" + Fore.RESET)

    counter = 1
    try:
        while True:
            print(Fore.YELLOW + f"[-] Cycle #{counter}: Requesting new identity & masking ISP..." + Fore.RESET)
            if change_ip():
                time.sleep(3)  # مهلة لبناء المسار الجديد
                ip, country, city, isp = get_ip_info()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                if ip:
                    print(Fore.GREEN + f"[+] [{timestamp}] New Identity Secured!")
                    print(Fore.WHITE + f"    ├── IP Address : {ip}")
                    print(Fore.WHITE + f"    ├── Country    : {country}")
                    print(Fore.WHITE + f"    ├── City       : {city}")
                    print(Fore.WHITE + f"    └── Exit ISP   : {isp}" + Fore.RESET)
                    log_ip(ip, country, city, isp, timestamp)
                else:
                    print(Fore.RED + "[!] Failed to fetch IP details through Tor proxy." + Fore.RESET)
            else:
                print(Fore.RED + "[!] Failed to change IP in this cycle." + Fore.RESET)
            
            counter += 1
            print(Fore.LIGHTBLACK_EX + "-" * 70 + Fore.RESET)
            
            if is_random:
                sleep_time = random.randint(min_t, max_t)
                print(Fore.CYAN + f"[*] Waiting {sleep_time} seconds (Random Mode)..." + Fore.RESET)
            else:
                sleep_time = interval
                
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print(Fore.CYAN + "\n\n[!] Tool stopped by user. JSON Log file saved successfully. Stay safe!" + Fore.RESET)
        sys.exit(0)

if __name__ == "__main__":
    main()
