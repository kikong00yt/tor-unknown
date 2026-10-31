# 🛡️ TOR_UNKNOWN | Advanced Pro Edition with ISP Shield

**TOR_UNKNOWN** is an advanced Python-based utility designed to automate IP rotation and identity switching through the Tor network, featuring built-in ISP masking and automatic session logging.

---

## 🚀 Features

* **Dual Rotation Modes:** Choose between a fixed time interval or a dynamic random interval for better stealth.
* **Tor ControlPort Integration:** Securely requests new identity signals (`NEWNYM`) programmatically via Stem.
* **ISP Shield:** Fetches and displays exit node details (IP, Country, City, and Exit ISP) through Tor's SOCKS5 proxy.
* **Automatic Logging:** Saves every secured session timestamp and IP details to an external log file (`tor_unknown.log`).

---

## 🛠️ Prerequisites & Tools Required

Before running the tool, ensure your system has the following installed:
* **Operating System:** Linux (Kali Linux, Ubuntu, etc.)
* **Python 3**
* **Tor Service**
* **Python Libraries:** `requests`, `stem`, `colorama`

---

## ⚙️ Installation & Setup

Follow these steps to set up and run the tool on your system:

### 1. Update system and install Tor & Python pip
```bash
sudo apt update && sudo apt install tor python3-pip -y
2. Install required Python packages
Bash
pip3 install requests stem colorama
3. Configure Tor ControlPort
Open the Tor configuration file:

Bash
sudo nano /etc/tor/torrc
Make sure the following lines are present and uncommented (add them if they don't exist):

Plaintext
ControlPort 9051
CookieAuthentication 1
Save the file (Ctrl + O, then Enter) and exit (Ctrl + X). Then, restart the Tor service:

Bash
sudo systemctl restart tor
🚀 Usage
Clone the repository:

Bash
git clone [https://github.com/kikong00yt/tor-unknown.git](https://github.com/kikong00yt/tor-unknown.git)
cd tor-unknown
Run the tool:

Bash
sudo python3 tor_unknown.py
Select Rotation Mode:

Mode 1: Fixed Interval (Constant time between changes).

Mode 2: Random Interval (Dynamic time range for enhanced security).

⚠️ Disclaimer
This tool (TOR_UNKNOWN) is developed for educational, security auditing, and privacy research purposes only. The author and contributors are not responsible for any misuse, illegal activities, or damages caused by this software. Use it responsibly and at your own risk.
