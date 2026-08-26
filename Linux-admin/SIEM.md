# Security Audit & Real-Time Monitoring Daemon

Proyek ini berisi panduan dan konfigurasi untuk membangun sistem **Security Information and Event Monitoring (SIEM)** sederhana pada sistem operasi Linux. Sistem ini memantau eksekusi perintah berbahaya (*blacklisted commands*) secara *real-time* via `journalctl` dan mengirimkan notifikasi instan ke admin melalui **Telegram Bot API**.

---

## 🛠️ Fitur Utama

- **Real-Time Log Audit:** Memantau log eksekusi `sudo` menggunakan utilitas native `journalctl`.
- **User Identification:** Menangkap *username*, terminal (*TTY*), *working directory*, serta perintah lengkap yang dijalankan pelakunya.
- **Pattern Matching:** Mendeteksi baris perintah destruktif seperti `rm -rf`, `chmod 777`, `mkfs`, `dd`, `shutdown`, dan perintah berbahaya lainnya.
- **Instant Alerting:** Mengirimkan peringatan langsung ke Telegram Admin.
- **Background Daemon:** Berjalan persisten sebagai *systemd service* dengan fitur *auto-restart*.

---

## 📁 Struktur Berkas

```text
├── security_monitor.py             # Skrip Python utama penangkap log & pengirim alert
└── security-monitor.service        # Systemd unit file untuk otomasi daemon
```

---

## 🚀 Langkah-Langkah Instalasi & Konfigurasi

### 1. Prasyarat Sistem
Pastikan paket `python3-requests` sudah terpasang pada server:
```bash
sudo apt update && sudo apt install python3-requests -y
```

---

### 2. Membuat Skrip Monitoring Python

Buat file baru di lokasi `/usr/local/bin/security_monitor.py`:
```bash
sudo nano /usr/local/bin/security_monitor.py
```

Isikan kode berikut (Jangan lupa mengganti `BOT_TOKEN` dan `CHAT_ID` sesuai konfigurasi Bot Telegram Anda):

```python
#!/usr/bin/env python3
import subprocess
import requests

# Konfigurasi Telegram Bot API
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Daftar Kata Terlarang (Blacklist Commands)
BLACKLIST = [
    "rm -rf", "mkfs", "dd if=", "chmod -R 777",
    "shutdown", "reboot", "init 0", "passwd root",
    "wget", "curl", "visudo"
]

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[ERROR] Gagal mengirim alert Telegram: {e}")

def monitor_logs():
    # Membaca log sudo secara real-time via journalctl
    cmd = ["journalctl", "-u", "sudo", "-f", "-n", "0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print("[INFO] Security Monitor Daemon Berjalan...")

    for line in process.stdout:
        for pattern in BLACKLIST:
            if pattern in line:
                alert_msg = (
                    "⚠️ *PERINGATAN KEAMANAN SERVER* ⚠️

"
                    "Terdeteksi perintah terlarang!

"
                    f"`{line.strip()}`"
                )
                print(alert_msg)
                send_telegram_alert(alert_msg)
                break

if __name__ == "__main__":
    monitor_logs()
```

Berikan hak akses eksekusi pada berkas tersebut:
```bash
sudo chmod +x /usr/local/bin/security_monitor.py
```

---

### 3. Membuat Systemd Unit File

Buat berkas service baru di `/etc/systemd/system/security-monitor.service`:
```bash
sudo nano /etc/systemd/system/security-monitor.service
```

Isikan konfigurasi unit service berikut:

```ini
[Unit]
Description=Security Audit & Monitoring Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/security_monitor.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

---

### 4. Mengaktifkan & Menjalankan Service

Muat ulang konfigurasikan Systemd agar mengenali unit baru:
```bash
sudo systemctl daemon-reload
```

Aktifkan service agar otomatis menyala saat *booting*, lalu jalankan sekarang:
```bash
sudo systemctl enable --now security-monitor.service
```

Periksa status daemon untuk memastikan statusnya berjalan normal (*active running*):
```bash
sudo systemctl status security-monitor.service
```

---

## 🧪 Pengujian (Testing)

1. Buka terminal baru atau lakukan login sebagai user lain di server.
2. Jalankan perintah yang memicu *blacklist* (misalnya tes dengan perintah bantuan):
   ```bash
   sudo shutdown --help
   ```
3. Cek log service secara *real-time*:
   ```bash
   sudo journalctl -u security-monitor.service -f
   ```
4. Peringatan (*alert*) akan otomatis terkirim ke Telegram Admin lengkap dengan nama *user* dan *command* yang dieksekusi.
