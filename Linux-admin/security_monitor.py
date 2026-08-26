#!/usr/bin/env python3
import time
import subprocess
import requests

# Konfigurasi Telegram Bot (Ganti token & chat_id milikmu)
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Daftar Kata Terlarang (Blacklist)
BLACKLIST = [
    "rm -rf", "mkfs", "dd if=", "chmod -R 777",
    "shutdown", "reboot", "init 0", "passwd root",
    "wget", "curl", "visudo"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Gagal mengirim alert: {e}")

def monitor_logs():
    # Membaca log auth/sudo secara real-time via journalctl
    cmd = ["journalctl", "-u", "sudo", "-f", "-n", "0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print("Security Monitor Daemon Berjalan...")

    for line in process.stdout:
        for pattern in BLACKLIST:
            if pattern in line:
                alert_msg = f"⚠️ *PERINGATAN KEAMANAN SERVER* ⚠️\n\nTerdeteksi perintah terlarang!\n\n`{line.strip()}`"
                print(alert_msg)
                send_telegram_alert(alert_msg)
                break

if __name__ == "__main__":
    monitor_logs()
