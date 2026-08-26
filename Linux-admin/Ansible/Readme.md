🚀 Automated Infrastructure & Server Security via Ansible

Repositori ini berisi **Ansible Playbook** serbaguna untuk melakukan otomatisasi *deployment*, *server hardening*, konfigurasi *monitoring*, serta skrip *backup multi-cloud* dari **Lab 1 hingga Lab 6** secara terstruktur dan efisien.

---

## 📋 Fitur Utama Automation Playbook

- **Lab 1: User Management & SSH Access**
  - Pembuatan user sysadmin (`devopsadmin`).
  - Konfigurasi *SSH Public Key* untuk akses bebas kata sandi.
  - Akses *Passwordless Sudo*.
- **Lab 2 & Lab 3: Web Server & Application Deployment**
  - Instalasi otomatis Nginx, PHP-FPM, Python 3, Git, rsync, dan Curl.
  - Pengaturan *document root* web server (`/var/www/html`).
  - Deployment *landing page* PHP/HTML.
- **Lab 4: Automated Security Monitoring**
  - Deployment skrip Python pemantau server (`security_monitor.py`).
  - Integrasi Notifikasi Alert via **Telegram Bot** (CPU/RAM/Disk > threshold).
  - Pemasangan *Cron Job* otomatis berjalan tiap 5 menit.
- **Lab 5: Multi-Cloud Offsite Backup**
  - Deployment skrip bash otomatisasi backup (`offsite_backup.sh`).
  - Dukungan upload backup otomatis ke **AWS S3**, **Google Cloud Storage (GCS)**, **Azure Blob Storage**, atau **Remote Server (rsync)**.
  - Pemasangan *Cron Job* harian otomatis pukul 02:00 pagi.
- **Lab 6: Firewall & Server Security Hardening**
  - Perubahan port default SSH (**22 $
ightarrow$ 2222**).
  - Konfigurasi **UFW Firewall** (*default deny incoming*, izinkan port 80 & 2222).
  - Proteksi *brute-force* SSH menggunakan **Fail2ban**.

---

## 🛠️ Persyaratan Sistem (Prerequisites)

- **Control Node (Komputer Anda/Server Pengendali):**
  - Linux / macOS / WSL
  - Ansible (versi $\ge$ 2.9)
  - Python 3
- **Target Node (Server Tujuan):**
  - Ubuntu Server 20.04 / 22.04 / 24.04 LTS
  - Akses `sudo` / `root` awal

---

## 📁 Struktur File Playbook

```text
.
├── site.yml               # Playbook Ansible utama (Lab 1 - Lab 6)
├── inventory.ini          # Daftar IP / Host Target Server
└── README.md              # Dokumentasi repositori
```

---

## ⚙️ Persiapan & Konfigurasi

### 1. Setup File Inventory (`inventory.ini`)

Buat berkas `inventory.ini` dan masukkan IP target server kamu:

```ini
[webservers]
server1 ansible_host=192.168.1.50 ansible_user=root
```

> **Catatan:** Jika pertama kali setup dan port SSH masih 22, gunakan `ansible_port=22`. Setelah playbook selesai dieksekusi, port SSH server akan berubah menjadi `2222`.

### 2. Kustomisasi Variabel pada `site.yml`

Buka file `site.yml` dan sesuaikan variabel di bagian `vars`:

```yaml
vars:
  # SSH & User Setup
  web_port: 80
  ssh_custom_port: 2222
  sysadmin_user: "admin"
  sysadmin_ssh_pubkey: "ssh-rsa AAAAB3NzaC1yc2E..."

  # Multi-Cloud Backup Setup (Pilih: aws / gcs / azure / rsync)
  cloud_provider: "aws"
  aws_s3_bucket: "s3://nama-bucket-backup-kamu"
  
  # Telegram Notification Setup
  telegram_bot_token: "123456789:ABCdefGHIjklMNO..."
  telegram_chat_id: "987654321"
```

---

## 🚀 Cara Menggunakan Playbook

### Step 1: Simulasikan Playbook (*Dry Run*)
Jalankan tes tanpa membuat perubahan fisik pada server untuk memvalidasi syntax dan langkah kerja:

```bash
ansible-playbook -i inventory.ini site.yml --check
```

### Step 2: Eksekusi Otomatisasi
Jalankan otomatisasi ke server target:

```bash
ansible-playbook -i inventory.ini site.yml
```

---

## 🔍 Verifikasi Setelah Deployment

1. **Uji Akses SSH Port Baru (2222):**
   ```bash
   ssh -p 2222 admin@192.168.1.50
   ```

2. **Cek Status Service Web Server & Firewall:**
   ```bash
   sudo systemctl status nginx
   sudo ufw status verbose
   sudo systemctl status fail2ban
   ```

3. **Cek Pemasangan Cron Job (Monitoring & Backup):**
   ```bash
   sudo crontab -l
   ```

4. **Uji Jalankan Skrip Backup Manual:**
   ```bash
   sudo /usr/local/bin/offsite_backup.sh
   ```

---

## 📄 Lisensi & Kontribusi

Proyek ini dibuat untuk keperluan otomatisasi infrastruktur DevOps dan pelatihan keamanan sistem. Silakan di-fork dan dikembangkan sesuai kebutuhan environment kamu! 🚀
