#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOR_UNKNOWN Enterprise - Single-file edition
Tor connection manager for lawful privacy testing.

Important:
- This tool only routes its own HTTP(S) requests through Tor.
- NEWNYM does not guarantee a different exit IP.
- DNS test verifies SOCKS5h remote resolution for this app only.
"""

import argparse
import csv
import json
import os
import random
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from stem import Signal
from stem.control import Controller
from colorama import init, Fore, Style

init(autoreset=True)

# ------------------------- CONFIGURATION -------------------------

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_CONFIG = {
    "socks_host": "127.0.0.1",
    "socks_port": 9050,
    "control_host": "127.0.0.1",
    "control_port": 9051,
    "cookie_path": "/run/tor/control.authcookie",
    "log_file": "logs/tor_unknown.jsonl",
    "csv_file": "logs/tor_unknown.csv",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "request_timeout": 15,
    "check_url": "https://check.torproject.org/api/ip"
}

class TorError(RuntimeError):
    pass

def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        print(Fore.YELLOW + f"[!] Created config file: {CONFIG_PATH}")
        print("[!] Review cookie_path and optional Telegram settings, then run again.")
        raise SystemExit(0)
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid config.json: {exc}")

# ------------------------- TOR ENGINE -------------------------

class TorManager:
    def __init__(self, config):
        self.cfg = config
        self.session = requests.Session()
        self.session.trust_env = False
        proxy = f"socks5h://{config['socks_host']}:{config['socks_port']}"
        self.session.proxies.update({"http": proxy, "https": proxy})

    def controller(self):
        c = Controller.from_port(
            address=self.cfg["control_host"],
            port=int(self.cfg["control_port"])
        )
        try:
            cookie_path = Path(self.cfg["cookie_path"])
            if cookie_path.is_file():
                try:
                    c.authenticate(cookie_path=str(cookie_path))
                except Exception:
                    with cookie_path.open("rb") as cookie:
                        c.authenticate(cookie=cookie.read())
            else:
                c.authenticate()
            return c
        except Exception:
            c.close()
            raise

    def status(self):
        try:
            with self.controller() as c:
                return {
                    "control_connected": True,
                    "tor_version": str(c.get_version()),
                    "bootstrap": c.get_info("status/bootstrap-phase", "unknown")
                }
        except Exception as exc:
            return {"control_connected": False, "error": str(exc)}

    def fetch_identity(self):
        try:
            response = self.session.get(
                self.cfg["check_url"],
                timeout=int(self.cfg["request_timeout"])
            )
            response.raise_for_status()
            data = response.json()
            ip = data.get("IP") or data.get("ip")
            if not ip:
                raise TorError("IP-check service returned no IP.")
            return {
                "ip": ip,
                "is_tor": data.get("IsTor", data.get("is_tor")),
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
        except requests.RequestException as exc:
            raise TorError(f"Tor proxy request failed: {exc}") from exc

    def new_identity(self):
        try:
            with self.controller() as c:
                if not c.is_newnym_available():
                    return False, "NEWNYM is rate-limited; wait before retrying."
                c.signal(Signal.NEWNYM)
            return True, "NEWNYM requested; a different exit IP is not guaranteed."
        except Exception as exc:
            return False, f"Tor ControlPort error: {exc}"

    def dns_proxy_check(self):
        # socks5h sends hostname resolution through the Tor SOCKS proxy.
        try:
            identity = self.fetch_identity()
            return {
                "ok": True,
                "method": "SOCKS5h remote DNS resolution",
                "exit_ip": identity["ip"],
                "scope": "This application's proxied request only; not a system-wide DNS audit."
            }
        except TorError as exc:
            return {"ok": False, "error": str(exc)}

# ------------------------- LOGGING -------------------------

class Logger:
    def __init__(self, jsonl_path, csv_path):
        self.jsonl_path = Path(jsonl_path)
        self.csv_path = Path(csv_path)
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event, **fields):
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields
        }
        with self.jsonl_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False) + "\\n")

        exists = self.csv_path.exists()
        with self.csv_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(row.keys()))
            if not exists:
                writer.writeheader()
            writer.writerow(row)
        return row

# ------------------------- TELEGRAM -------------------------

class Telegram:
    def __init__(self, token="", chat_id=""):
        self.token = token
        self.chat_id = chat_id

    def send(self, message):
        if not self.token or not self.chat_id:
            return False, "Telegram is not configured."
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            response = requests.post(
                url,
                json={"chat_id": self.chat_id, "text": message},
                timeout=10
            )
            response.raise_for_status()
            if not response.json().get("ok"):
                return False, "Telegram API rejected the message."
            return True, "Telegram notification sent."
        except requests.RequestException as exc:
            return False, str(exc)

# ------------------------- APPLICATION -------------------------

def service_check():
    if sys.platform.startswith("linux"):
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", "tor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    return None

def build_services():
    cfg = load_config()
    return (
        cfg,
        TorManager(cfg),
        Logger(cfg["log_file"], cfg["csv_file"]),
        Telegram(cfg.get("telegram_bot_token", ""), cfg.get("telegram_chat_id", ""))
    )

def banner():
    print(Fore.CYAN + r"""
╔══════════════════════════════════════════════════════╗
║                  TOR_UNKNOWN                          ║
║              ENTERPRISE EDITION                       ║
║            Single-file build | V1.1                   ║
╚══════════════════════════════════════════════════════╝
""")

def cli():
    cfg, tor, logger, telegram = build_services()
    banner()
    print(Fore.WHITE + "1) Check Tor status and exit IP")
    print("2) Request a new Tor circuit (NEWNYM)")
    print("3) DNS / SOCKS5h proxy-path check")
    print("4) Continuous monitor")
    print("5) Send Telegram test")
    print("6) Exit")

    choice = input(Fore.YELLOW + "\nSelect: ").strip()

    if choice == "1":
        print("Tor service:", "active" if service_check() else "inactive/unknown")
        print("Control:", tor.status())
        try:
            identity = tor.fetch_identity()
            print(Fore.GREEN + f"Exit IP: {identity['ip']}")
            print("Tor flag:", identity.get("is_tor"))
            logger.write("identity_check", **identity)
        except TorError as exc:
            print(Fore.RED + str(exc))
            logger.write("error", detail=str(exc))

    elif choice == "2":
        ok, message = tor.new_identity()
        print(message)
        logger.write("newnym", success=ok, detail=message)
        if ok:
            time.sleep(5)
            try:
                identity = tor.fetch_identity()
                print(Fore.GREEN + f"Exit IP: {identity['ip']}")
                logger.write("identity_after_newnym", **identity)
                telegram.send(f"TOR_UNKNOWN: Tor exit IP check: {identity['ip']}")
            except TorError as exc:
                print(Fore.RED + str(exc))
                logger.write("error_after_newnym", detail=str(exc))

    elif choice == "3":
        result = tor.dns_proxy_check()
        print(result)
        logger.write("dns_proxy_check", **result)

    elif choice == "4":
        try:
            interval = int(input("Monitor interval in seconds (minimum 60): "))
            if interval < 60:
                print(Fore.RED + "Minimum interval is 60 seconds.")
                return
            print(Fore.CYAN + "Monitoring started. Press Ctrl+C to stop.")
            while True:
                ok, message = tor.new_identity()
                time.sleep(5 if ok else 1)
                try:
                    identity = tor.fetch_identity()
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), identity)
                    logger.write("monitor", newnym=ok, detail=message, **identity)
                    if not ok:
                        telegram.send(f"TOR_UNKNOWN monitor: {message}")
                except TorError as exc:
                    print(Fore.RED + str(exc))
                    logger.write("monitor_error", detail=str(exc))
                    telegram.send(f"TOR_UNKNOWN connection check failed: {exc}")
                time.sleep(interval)
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
        except KeyboardInterrupt:
            print("\\nMonitor stopped.")

    elif choice == "5":
        ok, message = telegram.send("TOR_UNKNOWN Telegram test: notification channel is working.")
        print(message)

    else:
        print("Goodbye.")

def gui():
    import tkinter as tk
    from tkinter import ttk
    cfg, tor, logger, telegram = build_services()

    root = tk.Tk()
    root.title("TOR_UNKNOWN Enterprise")
    root.geometry("780x520")
    root.configure(bg="#101820")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#101820")
    style.configure("TLabel", background="#101820", foreground="#e8f1f2")
    style.configure("TButton", padding=8)

    ttk.Label(
        root, text="TOR_UNKNOWN | Enterprise Dashboard",
        font=("DejaVu Sans", 17, "bold")
    ).pack(pady=16)

    status_text = tk.StringVar(value="Ready")
    ip_text = tk.StringVar(value="Exit IP: not checked")
    ttk.Label(root, textvariable=status_text).pack(pady=4)
    ttk.Label(root, textvariable=ip_text, font=("DejaVu Sans", 14, "bold")).pack(pady=8)

    output = tk.Text(
        root, height=16, bg="#071018", fg="#7CFFB2",
        insertbackground="white", wrap="word"
    )
    output.pack(fill="both", expand=True, padx=18, pady=10)

    def run_async(function):
        status_text.set("Working...")
        def worker():
            try:
                result = function()
                def show():
                    output.insert("end", str(result) + "\\n")
                    output.see("end")
                    status_text.set("Operation completed")
                root.after(0, show)
            except Exception as exc:
                def show_error():
                    output.insert("end", "ERROR: " + str(exc) + "\\n")
                    output.see("end")
                    status_text.set("Operation failed")
                root.after(0, show_error)
        threading.Thread(target=worker, daemon=True).start()

    def check_identity():
        identity = tor.fetch_identity()
        ip_text.set("Exit IP: " + identity["ip"])
        logger.write("gui_identity_check", **identity)
        return identity

    def rotate_identity():
        ok, message = tor.new_identity()
        logger.write("gui_newnym", success=ok, detail=message)
        if not ok:
            return message
        time.sleep(5)
        identity = check_identity()
        telegram.send(f"TOR_UNKNOWN: New identity check: {identity['ip']}")
        return {"message": message, **identity}

    def check_dns():
        result = tor.dns_proxy_check()
        logger.write("gui_dns_proxy_check", **result)
        return result

    def check_status():
        result = tor.status()
        logger.write("gui_tor_status", **result)
        return result

    buttons = ttk.Frame(root)
    buttons.pack(pady=10)
    ttk.Button(buttons, text="Check Tor / IP", command=lambda: run_async(check_identity)).grid(row=0, column=0, padx=5)
    ttk.Button(buttons, text="New identity", command=lambda: run_async(rotate_identity)).grid(row=0, column=1, padx=5)
    ttk.Button(buttons, text="DNS / proxy test", command=lambda: run_async(check_dns)).grid(row=0, column=2, padx=5)
    ttk.Button(buttons, text="Tor status", command=lambda: run_async(check_status)).grid(row=0, column=3, padx=5)
    ttk.Button(buttons, text="Telegram test", command=lambda: run_async(
        lambda: telegram.send("TOR_UNKNOWN GUI test notification.")
    )).grid(row=0, column=4, padx=5)

    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="TOR_UNKNOWN Enterprise single-file edition")
    parser.add_argument("--gui", action="store_true", help="Launch graphical interface")
    args = parser.parse_args()
    if args.gui:
        gui()
    else:
        cli()

if __name__ == "__main__":
    main()
