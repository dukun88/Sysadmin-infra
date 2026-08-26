# Script Multi-Cloud Offsite Backup & Real-Time Alerting

Skrip Bash ini dirancang untuk melakukan proses pemadatan (*backup*) direktori target dan mengunggahnya secara fleksibel ke salah satu dari tiga penyedia *cloud storage* terkemuka: **AWS S3**, **Google Cloud Storage (GCS)**, atau **Azure Blob Storage** (atau ke **Remote Server via Rsync**). Setelah proses pengunggahan selesai, skrip akan mengirimkan notifikasi ringkas beserta ukuran berkas dan durasi proses ke **Telegram Admin**.

---

## 🏗️ Fitur Utama

- **Multi-Cloud Target:** Mendukung tujuan pengunggahan ke **AWS S3** (`aws-cli`), **Google Cloud Storage** (`gcloud` / `gsutil`), **Azure Blob Storage** (`azcopy`), serta **Remote Server** (`rsync`).
- **Timestamped Archiving:** Kompresi `.tar.gz` dengan penanda waktu otomatis.
- **Detailed Logging:** Pencatatan setiap langkah ke berkas log terpusat (`/var/log/backup_offsite.log`).
- **Instant Telegram Notification:** Mengirimkan ringkasan status (*SUCCESS* / *FAILED*), nama file, ukuran akhir, serta lokasi penyimpanan ke Telegram.
- **Fail-Safe Mechanism:** Memvalidasi keberhasilan setiap tahapan sebelum melanjutkan ke proses berikutnya.

---

## 🛠️ Prasyarat & Dependensi

Sesuaikan perangkat lunak CLI yang diinstal di server sesuai dengan *cloud provider* yang dipilih:

1. **AWS S3:**
   ```bash
   sudo apt update && sudo apt install awscli -y
   # Konfigurasi kredensial AWS
   aws configure
   ```

2. **Google Cloud Storage (GCS):**
   ```bash
   # Install Google Cloud SDK
   sudo apt install google-cloud-sdk -y
   # Login & otentikasi
   gcloud auth login
   ```

3. **Microsoft Azure Blob Storage:**
   ```bash
   # Download dan install AzCopy CLI
   wget https://aka.ms/downloadazcopy-v10-linux -O azcopy.tar.gz
   tar -xvf azcopy.tar.gz && sudo cp azcopy_linux_amd64_*/azcopy /usr/local/bin/
   ```

---

## 📄 Skrip Utama: `/usr/local/bin/offsite_backup.sh`

Buat berkas skrip baru:
```bash
sudo nano /usr/local/bin/offsite_backup.sh
```

Tempelkan (*paste*) seluruh isi kode skrip berikut:

```bash
#!/bin/bash

# ==============================================================================
# KONFIGURASI UTAMA
# ==============================================================================
SOURCE_DIR="/opt/project/data"
BACKUP_DIR="/opt/project/backup"
LOG_FILE="/var/log/backup_offsite.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="backup_data_${TIMESTAMP}.tar.gz"
BACKUP_FILE_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Konfigurasi Telegram Bot
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

# ------------------------------------------------------------------------------
# PILIH TARGET DEPLOYMENT ("aws", "gcs", "azure", atau "rsync")
# ------------------------------------------------------------------------------
CLOUD_PROVIDER="aws"

# Parameter Cloud Target
AWS_S3_BUCKET="s3://my-company-backup-bucket"
GCS_BUCKET="gs://my-company-backup-bucket"
AZURE_CONTAINER_URL="https://myaccount.blob.core.windows.net/my-backup-container?SAS_TOKEN"
REMOTE_RSYNC_DEST="user@192.168.1.100:/data/backups/"

# ==============================================================================
# FUNGSI PENDUKUNG
# ==============================================================================
mkdir -p "$BACKUP_DIR"
touch "$LOG_FILE"

log_message() {
    local LEVEL="$1"
    local MSG="$2"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${LEVEL}] ${MSG}" | tee -a "$LOG_FILE"
}

send_telegram_alert() {
    local MESSAGE="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ "$TELEGRAM_BOT_TOKEN" != "YOUR_TELEGRAM_BOT_TOKEN" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"             -d "chat_id=${TELEGRAM_CHAT_ID}"             -d "text=${MESSAGE}"             -d "parse_mode=Markdown" > /dev/null 2>&1
    fi
}

# ==============================================================================
# PROSES BACKUP LOKAL
# ==============================================================================
log_message "INFO" "=================================================="
log_message "INFO" "Memulai proses backup lokal dari ${SOURCE_DIR}..."

START_TIME=$(date +%s)

if tar -czf "$BACKUP_FILE_PATH" -C "$SOURCE_DIR" . >> "$LOG_FILE" 2>&1; then
    FILE_SIZE=$(du -h "$BACKUP_FILE_PATH" | cut -f1)
    log_message "SUCCESS" "Kompresi lokal berhasil: ${BACKUP_FILENAME} (Ukuran: ${FILE_SIZE})"
else
    log_message "ERROR" "Kompresi lokal GAGAL!"
    send_telegram_alert "🚨 *BACKUP FAILED!* 🚨%0A%0AProses kompresi lokal pada server *$(hostname)* gagal!"
    exit 1
fi

# ==============================================================================
# PROSES OFFSITE UPLOAD (MULTI-CLOUD)
# ==============================================================================
log_message "INFO" "Memulai unggahan ke Offsite Target: [${CLOUD_PROVIDER^^}]..."

UPLOAD_SUCCESS=false

case "$CLOUD_PROVIDER" in
    "aws")
        if aws s3 cp "$BACKUP_FILE_PATH" "${AWS_S3_BUCKET}/${BACKUP_FILENAME}" >> "$LOG_FILE" 2>&1; then
            UPLOAD_SUCCESS=true
            DEST_INFO="${AWS_S3_BUCKET}/${BACKUP_FILENAME}"
        fi
        ;;
    "gcs")
        if gcloud storage cp "$BACKUP_FILE_PATH" "${GCS_BUCKET}/${BACKUP_FILENAME}" >> "$LOG_FILE" 2>&1; then
            UPLOAD_SUCCESS=true
            DEST_INFO="${GCS_BUCKET}/${BACKUP_FILENAME}"
        fi
        ;;
    "azure")
        if azcopy copy "$BACKUP_FILE_PATH" "${AZURE_CONTAINER_URL}" >> "$LOG_FILE" 2>&1; then
            UPLOAD_SUCCESS=true
            DEST_INFO="Azure Blob Storage Container"
        fi
        ;;
    "rsync")
        if rsync -avz -e "ssh -o StrictHostKeyChecking=no" "$BACKUP_FILE_PATH" "$REMOTE_RSYNC_DEST" >> "$LOG_FILE" 2>&1; then
            UPLOAD_SUCCESS=true
            DEST_INFO="$REMOTE_RSYNC_DEST"
        fi
        ;;
    *)
        log_message "ERROR" "Provider '${CLOUD_PROVIDER}' tidak dikenali!"
        exit 1
        ;;
esac

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# ==============================================================================
# LAPORAN & NOTIFIKASI
# ==============================================================================
if [ "$UPLOAD_SUCCESS" = true ]; then
    log_message "SUCCESS" "Unggahan ke ${CLOUD_PROVIDER^^} berhasil!"
    
    # Format pesan Telegram
    ALERT_MSG="✅ *BACKUP OFFSITE SUCCESSFUL!*%0A%0A"
    ALERT_MSG+="🖥️ *Server:* \`$(hostname)\`%0A"
    ALERT_MSG+="☁️ *Provider:* \`${CLOUD_PROVIDER^^}\`%0A"
    ALERT_MSG+="📦 *File:* \`${BACKUP_FILENAME}\`%0A"
    ALERT_MSG+="📊 *Size:* \`${FILE_SIZE}\`%0A"
    ALERT_MSG+="⏱️ *Duration:* \`${DURATION} detik\`%0A"
    ALERT_MSG+="📍 *Destination:* \`${DEST_INFO}\`"

    send_telegram_alert "$ALERT_MSG"
else
    log_message "ERROR" "Gagal mengunggah file ke ${CLOUD_PROVIDER^^}!"
    
    ALERT_MSG="❌ *BACKUP OFFSITE FAILED!*%0A%0A"
    ALERT_MSG+="Server \`$(hostname)\` gagal mengunggah file backup ke \`${CLOUD_PROVIDER^^}\`. Silakan periksa file log \`/var/log/backup_offsite.log\`."
    
    send_telegram_alert "$ALERT_MSG"
    exit 1
fi
```

Beri izin eksekusi (*executable permission*) pada berkas tersebut:
```bash
sudo chmod +x /usr/local/bin/offsite_backup.sh
```

---

## ⏰ Pengaturan Penjadwalan (Cron Job)

Daftarkan skrip ke dalam tabel Cron agar berjalan otomatis setiap pukul 02:00 pagi:

```bash
sudo crontab -e
```

Isikan aturan berikut:
```cron
0 2 * * * /usr/local/bin/offsite_backup.sh
```
