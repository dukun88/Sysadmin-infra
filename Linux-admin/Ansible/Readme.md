# 🚀 Automated Infrastructure & Security Monitoring (Daemon Version)

Repositori ini berisi **Ansible Playbook** serbaguna untuk otomatisasi *deployment*, *server hardening*, **real-time Security Monitor Daemon (systemd)**, serta skrip *backup multi-cloud* dari **Lab 1 hingga Lab 6**.

---

## 📋 Fitur Utama Automation Playbook

- **Lab 1: User Management & SSH Access**
  - Pembuatan user sysadmin (`devopsadmin`).
  - Konfigurasi *SSH Public Key* untuk akses bebas kata sandi.
  - Akses *Passwordless Sudo*.
- **Lab 2 & Lab 3: Web Server & Application Deployment**
  - Instalasi Nginx, PHP-FPM, Python 3, Git, rsync, dan Curl.
  - Pengaturan *document root* web server (`/var/www/html`).
  - Deployment *landing page* PHP/HTML.
- **Lab 4: Real-Time Security Monitoring Daemon**
  - Deployment skrip Python pemantau log sudo real-time (`security_monitor.py`).
  - Didaftarkan sebagai **Systemd Service** (`security_monitor.service`) yang berjalan di background secara otomatis.
  - Deteksi perintah berbahaya (blacklist: `rm -rf`, `chmod 777`, `mkfs`, dll) via `journalctl`.
  - Integrasi Notifikasi Alert via **Telegram Bot**.
- **Lab 5: Multi-Cloud Offsite Backup**
  - Deployment skrip bash otomatisasi backup (`offsite_backup.sh`).
  - Dukungan upload backup otomatis ke **AWS S3**, **GCS**, **Azure Blob Storage**, atau **Remote Server (rsync)**.
  - Cron Job harian otomatis pukul 02:00 pagi.
- **Lab 6: Firewall & Server Security Hardening**
  - Perubahan port default SSH (**22 -> 2222**).
  - Konfigurasi **UFW Firewall** (*default deny incoming*, izinkan port 80 & 2222).
  - Proteksi *brute-force* SSH menggunakan **Fail2ban**.

---

## 🛠️ Persyaratan Sistem (Prerequisites)

- **Control Node (Komputer Pengendali):**
  - Linux / macOS / WSL dengan Ansible (>= 2.9) & Python 3.
- **Target Node (Server Tujuan):**
  - Ubuntu Server 20.04 / 22.04 / 24.04 LTS (menggunakan systemd & journalctl).

---

## 📁 Struktur File Playbook

```text
.
├── site.yml               # Playbook Ansible utama (Lab 1 - Lab 6)
├── inventory.ini          # Daftar IP / Host Target Server
└── README.md              # Dokumentasi repositori
```

---

## ⚙️ Persiapan & Kustomisasi Variabel

Buka file `site.yml` dan sesuaikan variabel pada bagian `vars`:

```yaml
vars:
  # SSH & User Setup
  web_port: 80
  ssh_custom_port: 2222
  sysadmin_user: "devopsadmin"
  sysadmin_ssh_pubkey: "ssh-rsa AAAAB3NzaC1yc2E..."

  # Multi-Cloud Backup Setup (Pilih: aws / gcs / azure / rsync)
  cloud_provider: "aws"
  aws_s3_bucket: "s3://nama-bucket-backup-kamu"
  
  # Telegram Notification Setup (Wajib diisi agar bot aktif)
  telegram_bot_token: "123456789:ABCdefGHIjklMNO..."
  telegram_chat_id: "987654321"
```

---

## 🚀 Cara Menggunakan Playbook

### 1. Simulasikan Playbook (*Dry Run*)
```bash
ansible-playbook -i inventory.ini site.yml --check
```

### 2. Eksekusi Otomatisasi
```bash
ansible-playbook -i inventory.ini site.yml
```

---

## 🔍 Verifikasi Daemon Security Monitor

Setelah Ansible selesai dijalankan, kamu bisa memverifikasi bahwa skrip Python pemantau log sudah berjalan sebagai service daemon di background:

1. **Cek Status Service Daemon:**
   ```bash
   sudo systemctl status security_monitor
   ```

2. **Cek Log Real-Time Daemon:**
   ```bash
   sudo journalctl -u security_monitor -f
   ```

3. **Uji Coba Deteksi Alert (Sengaja Panggil Blacklist):**
   ```bash
   sudo rm -rf /tmp/dummy_test_folder
   ```
   *Lihat ke Telegram kamu, alert notifikasi akan langsung masuk secara real-time!* 🚀
