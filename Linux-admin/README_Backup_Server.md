# 🛡️ Dedicated Backup Server & Remote Sync Automation Playbook

File ini adalah playbook Ansible khusus yang memisahkan **Server Utama (Client)** dan **Dedicated Backup Server** untuk kebutuhan *disaster recovery* dan otomatisasi backup multi-node.

---

## 🏗️ Arsitektur Infrastruktur Multi-Server Backup

```
+-----------------------------------+               +-----------------------------------+
|     PRODUCTION / CLIENT NODE      |               |      DEDICATED BACKUP SERVER      |
|    (IP: 192.168.1.51 / Port 2222) |               |    (IP: 192.168.1.50 / Port 2222) |
+-----------------------------------+               +-----------------------------------+
| - Generator SSH Keypair           |               | - Target Storage Backup           |
| - Mount Point: /mnt/backup_nfs    | <== (NFS) ==> | - NFS Server: /srv/nfs/backups    |
| - Auto Script Sync (RSYNC/SCP)    | == (RSYNC) => | - Authorized SSH Keys (Client Key)|
| - Cron Job Otomatis Jam 02:00 Pagi|               | - UFW Open Port 2049, 2222        |
+-----------------------------------+               +-----------------------------------+
```

---

## 📁 Format Inventory (`inventory_backup.ini`)

Gunakan berkas `inventory_backup.ini` berikut:

```ini
[backup_server]
server_backup ansible_host=192.168.1.50 ansible_user=root ansible_port=22

[backup_client]
server_prod ansible_host=192.168.1.51 ansible_user=root ansible_port=22

[all:children]
backup_server
backup_client
```

---

## 🚀 Cara Eksekusi Playbook Backup Dedicated

Jalankan playbook terpisah ini dengan perintah:

```bash
ansible-playbook -i inventory_backup.ini site_backup.yml
```

---

## 🧪 Cara Pengujian & Verifikasi Hasil Backup Remote

### 1. Jalankan Skrip Backup Manual di Client Node:
```bash
ssh -p 2222 devopsadmin@192.168.1.51
sudo /usr/local/bin/remote_backup_sync.sh
```

### 2. Verifikasi File Masuk di Backup Server (Transfer via RSYNC & NFS):
Log in ke Dedicated Backup Server dan periksa isi direktori backup:
```bash
ssh -p 2222 devopsadmin@192.168.1.50
ls -la /srv/nfs/backups/client_data/
```
