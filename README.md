TOR_UNKNOWN Enterprise

Advanced Tor Connection Manager & Privacy Monitoring Tool

Version: 1.1
Platform: Kali Linux / Debian Linux
Language: Python 3
Interface: CLI + GUI

---

1. Overview

TOR_UNKNOWN Enterprise is a Python-based Tor connection management tool designed for privacy testing and network monitoring.

It provides a terminal interface and a graphical interface for managing Tor connections, checking exit IP addresses, requesting new Tor circuits, monitoring connectivity, and recording connection events.

2. Features

- Tor Connection Management
  
  - Check Tor service status.
  - Test SOCKS5 proxy connectivity.
  - Request new Tor circuits using NEWNYM.
  - Display current Tor exit IP.

- Privacy Monitoring
  
  - SOCKS5h remote DNS resolution.
  - Tor connection verification.
  - Connection failure notifications.

- Logging System
  
  - Automatic JSONL logging.
  - CSV log export.
  - UTC timestamps.
  - Connection event history.

- Telegram Integration
  
  - Optional Telegram Bot notifications.
  - Connection status alerts.
  - Test notification support.

- User Interface
  
  - Interactive CLI.
  - Graphical desktop interface (GUI).
  - Background operations.

3. Requirements

- Kali Linux or Debian-based Linux.
- Python 3.
- Tor service.
- Internet connection.
- Python packages:
  - requests
  - stem
  - colorama
  - PySocks
  - tkinter (GUI)

4. Installation

Install system dependencies:

sudo apt update
sudo apt install tor python3 python3-pip python3-venv python3-tk -y

Create a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install Python packages:

pip install requests[socks] stem colorama

5. Tor Configuration

Edit the Tor configuration:

sudo nano /etc/tor/torrc

Ensure the following settings exist:

SocksPort 127.0.0.1:9050
ControlPort 127.0.0.1:9051
CookieAuthentication 1

Restart Tor:

sudo systemctl restart tor
sudo systemctl status tor

Configure the correct Tor authentication cookie path inside the Python source if necessary.

6. Usage

Run the terminal interface:

python3 TOR_UNKNOWN_Enterprise.py

Run the graphical interface:

python3 TOR_UNKNOWN_Enterprise.py --gui

7. Available Operations

1. Check Tor status and exit IP.
2. Request a new Tor circuit.
3. Perform a DNS/proxy-path check.
4. Monitor Tor connectivity.
5. Send a Telegram test notification.

8. Telegram Configuration

Edit the configuration constants in the Python source:

DEFAULT_CONFIG = {
    # Other settings...
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
}

Keep your bot token private.

9. Log Files

The tool automatically creates:

logs/
├── tor_unknown.jsonl
└── tor_unknown.csv

These files contain connection events, timestamps, exit IP information, and monitoring results.

10. Security Notes

- NEWNYM does not guarantee a different exit IP.
- Tor may rate-limit identity change requests.
- SOCKS5h routes DNS resolution through the Tor proxy for this application's requests.
- This tool does not automatically route all operating-system traffic through Tor.
- The DNS check is not a complete system-wide DNS leak audit.
- Never expose the Tor ControlPort to public networks.
- Protect authentication cookies and Telegram credentials.
- Do not use Tor as a guarantee of complete anonymity.

11. Disclaimer

TOR_UNKNOWN Enterprise is intended for lawful privacy testing, educational purposes, and network diagnostics.

⚠️The developer assumes no responsibility for misuse or unlawful activities.

---

TOR_UNKNOWN Enterprise
Privacy Monitoring. Tor Management. Network Diagnostics.