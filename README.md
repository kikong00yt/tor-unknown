# 🛡️ TOR_UNKNOWN (Enterprise Edition)

**TOR_UNKNOWN** is an advanced, automated Python-based tool designed to seamlessly rotate Tor identities (IP addresses) at fixed or random intervals. Built with built-in leak protection, structured JSON logging, and instant Telegram alert notifications, it ensures maximum stealth and monitoring for privacy-conscious users and security researchers.

---

## ✨ Features

*   **🔄 Dual Rotation Modes:** Choose between a **Fixed Interval** (constant delay) or a **Random Interval** (dynamic delay range) for enhanced stealth and behavioral unpredictability.
*   **🛡️ Leak Protection Shield (`Leak Shield`):** Automatically checks for potential public IP and DNS leaks against your real connection before starting rotation.
*   **📝 Structured JSON Logging:** Automatically logs all IP transitions, timestamps, and ISP details into a structured `tor_unknown.json` file.
*   **📱 Instant Telegram Alerts:** Optional webhook integration to send real-time security notifications straight to your Telegram chat or channel whenever a new identity is secured.
*   **🎨 Clean CLI Interface:** Professional, color-coded terminal output powered by `colorama`.

---

## ⚙️ Prerequisites

Before running the tool, ensure you have the following installed and configured on your system (tested on Linux/Debian/Kali):

1. **Tor Service:** Must be installed and running (`sudo systemctl start tor`).
2. **Tor ControlPort:** Enabled on port `9051` (via `/etc/tor/torrc` configuration).
3. **Python 3.x**

---

## 📥 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/tor-unknown.git](https://github.com/YOUR_USERNAME/tor-unknown.git)
   cd tor-unknown
2:Install required Python packages:

pip install -r requirements.txt

3:Run the tool:
(Root/sudo permissions may be required for service checks and control port access)

sudo python3 tor_unknown.py

📱 Setting Up Telegram Alerts (Optional)
If you want to receive real-time notifications on Telegram:
1_Create a new bot via @BotFather to get your Bot Token.
2_Get your unique Chat ID (e.g., via @userinfobot).
3_Open tor_unknown.py and fill in your credentials at the top of the file:

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"



⚠️ Disclaimer
This tool is created for educational purposes, privacy enhancement, and authorized security testing only. The user is solely responsible for complying with local laws and terms of service of the networks they interact with.

