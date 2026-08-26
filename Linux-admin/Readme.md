# Lab 1: Server Setup Dasar

## 1. Tujuan Praktikum

1. Melakukan instalasi sistem operasi Linux (Ubuntu Server) tanpa Graphical User Interface (GUI).
2. Memahami dan mengonfigurasi alamat IP Statis (*Static IP*) menggunakan **Netplan**.
3. Mengelola hak akses pengguna (*User & Group Management*) serta hak akses superuser (`sudo`).
4. Meningkatkan keamanan server dengan mengonfigurasi autentikasi SSH berbasis kunci (*SSH Key-based Authentication*) dan mematikan login kata sandi (*Password Authentication*).
5. Melakukan pembaruan paket dan pemeliharaan dasar sistem (*System Update & Upgrade*).

---

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Instalasi Ubuntu Server
* **Persiapan:** Menyiapkan Virtual Machine (VM) menggunakan aplikasi virtualisasi (VirtualBox / VMware) dengan alokasi resource standar (2 vCPU, 2GB RAM, 20GB Disk).
* **Proses:** Menginstal Ubuntu Server versi minimal (CLI-only) hingga proses bootstrap selesai dan server dapat melakukan *booting* ke prompt shell.

---

### 2.2 Konfigurasi Static IP (Netplan)
Untuk memastikan server memiliki alamat jaringan yang konsisten, alamat IP diubah dari DHCP ke Statis.

1. Membuka file konfigurasi Netplan:
   ```bash
   sudo nano /etc/netplan/50-cloud-init.yaml
   ```

2. Menyesuaikan konfigurasi file seperti berikut:
   ```yaml
   network:
     version: 2
     ethernets:
       enp0s3:
         dhcp4: no
         addresses:
           - 192.168.1.100/24
         routes:
           - to: default
             via: 192.168.1.1
         nameservers:
           addresses:
             - 8.8.8.8
             - 1.1.1.1
   ```

3. Menerapkan konfigurasi dan memverifikasi alamat IP:
   ```bash
   sudo netplan apply
   ip a
   ```
   *Hasil:* Alamat IP interface `enp0s3` berhasil berubah menjadi `192.168.1.100/24`.

---

### 2.3 Manajemen Pengguna (User Management)
Membuat dua akun pengguna baru dengan tingkat hak akses yang berbeda.

1. **Membuat User Admin (`sysadmin`):**
   ```bash
   sudo adduser sysadmin
   sudo usermod -aG sudo sysadmin
   ```
   *Verifikasi:* User `sysadmin` dapat menjalankan perintah dengan instruksi `sudo`.

2. **Membuat User Biasa (`userbiasa`):**
   ```bash
   sudo adduser userbiasa
   ```
   *Verifikasi:* Saat mencoba menjalankan `sudo apt update` dari akun `userbiasa`, sistem menolak akses (*User is not in the sudoers file*).

---

### 2.4 Setup SSH Key & Hardening SSH
Untuk meningkatkan keamanan server dari serangan *brute-force*, autentikasi diubah menggunakan *SSH Public/Private Key Pair*.

1. **Generate SSH Key di Machine Lokal Client:**
   ```bash
   ssh-keygen -t ed25519 -C "lab1-key"
   ```

2. **Pengiriman Public Key ke Server:**
   ```bash
   ssh-copy-id sysadmin@192.168.1.100
   ```

3. **Pengaturan Hardening SSH (`/etc/ssh/sshd_config`):**
   Mengubah parameter konfigurasi SSH daemon:
   ```ini
   PasswordAuthentication no
   PubkeyAuthentication yes
   PermitRootLogin no
   ```
   
4. Menyiapkan ulang layanan SSH:
   ```bash
   sudo systemctl restart ssh
   ```
   *Hasil:* Klien hanya dapat masuk ke dalam server menggunakan *private key* yang sah. Percobaan login menggunakan kata sandi ditolak otomatis oleh server.

---

### 2.5 Pembaruan & Pemeliharaan Sistem (Update & Upgrade)
Memastikan seluruh repositori paket software pada server berada di versi terbaru dan aman dari kerentanan keamanan.

Perintah yang dijalankan:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

---

## 3. Kesimpulan

Praktikum **Lab 1: Server Setup Dasar** berhasil diselesaikan. Berdasarkan hasil pengujian:
1. Server berhasil beroperasi penuh dalam modus CLI tanpa layar grafis.
2. Pengaturan IP Statis dan resolusi DNS berfungsi dengan baik.
3. Pemisahan hak akses antara akun administratif (`sysadmin`) dan akun biasa (`userbiasa`) berjalan sesuai kebijakan akses *Least Privilege*.
4. Akses remote SSH telah berhasil diamankan dengan kunci kriptografi (Ed25519) serta pembatasan kata sandi.
5. Seluruh paket sistem berhasil diperbarui ke versi paling aman.

---
# Lab 2: Pemetaan Hak Akses & Manajemen Berkas (Permission & File Management)

## 1. Tujuan Praktikum

1. Memahami hirarki sistem berkas Linux dan mempraktikkan pembuatan direktori kerja terpola di bawah `/opt/project`.
2. Mengimplementasikan manajemen pengguna dan grup (*User & Group Management*) untuk membatasi kepemilikan (*ownership*) direktori secara spesifik.
3. Menguasai konsep dan penerapan modulasi hak akses berkas/direktori menggunakan dua metode: **Notasi Numerik (Octal)** dan **Notasi Simbolik**.
4. Mengonfigurasi hak akses khusus (*Granular Permissions*) untuk skenario spesifik (misalnya: berkas hanya dapat dibaca oleh *owner*, tetapi dapat dieksekusi oleh *group*).

---

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Pembuatan Struktur Direktori `/opt/project`
Direktori `/opt` digunakan untuk menyimpan aplikasi atau proyek tambahan di luar paket bawaan OS.

1. Membuka terminal dengan akses administratif (`sudo`) untuk membuat struktur direktori bertingkat:
   ```bash
   sudo mkdir -p /opt/project/{data,logs,backup}
   ```
2. Memverifikasi hasil pembuatan direktori:
   ```bash
   ls -la /opt/project
   ```
   *Hasil:* Direktori `data`, `logs`, dan `backup` berhasil dibuat secara otomatis di bawah `/opt/project`.

---

### 2.2 Konfigurasi Grup Khusus & Kepemilikan (*Ownership*)
Agar direktori `data` hanya dapat dikelola oleh anggota tim khusus, dibuat grup baru bernama `devteam`.

1. **Membuat Group Baru:**
   ```bash
   sudo groupadd devteam
   ```
2. **Menambahkan User ke Dalam Group:**
   ```bash
   sudo usermod -aG devteam sysadmin
   ```
3. **Mengubah Kepemilikan (Ownership & Group Ownership):**
   Mengubah *group owner* direktori `/opt/project/data` menjadi `devteam`, serta membatasi hak akses pengguna lain (*others*).
   ```bash
   sudo chown -R root:devteam /opt/project/data
   sudo chmod 770 /opt/project/data
   ```
   *Hasil:* Hanya user `root` dan pengguna yang tergabung dalam grup `devteam` yang dapat membaca, menulis, dan masuk ke direktori `/opt/project/data`. Pengguna luar (*others*) ditolak aksesnya (`d----rwx---` / `770`).

---

### 2.3 Praktik Pengadaan Hak Akses (Chmod Numeric vs Symbolic)

Selama praktikum, dilakukan latihan pengubahan izin akses (*permission*) secara berulang pada direktori pengujian menggunakan dua metode hingga dipahami dengan baik:

#### A. Notasi Numerik (Octal Notation)
Menggunakan penjumlahan nilai biner: **Read (4)**, **Write (2)**, **Execute (1)**.

| Kombinasi Nilai | Biner / Detail | Izin Akses |
| :--- | :--- | :--- |
| **7 (4+2+1)** | Read + Write + Execute | `rwx` |
| **6 (4+2)** | Read + Write | `rw-` |
| **5 (4+1)** | Read + Execute | `r-x` |
| **4 (4)** | Read Only | `r--` |
| **0 (0)** | No Access | `---` |

*Contoh Eksekusi Perintah:*
```bash
# Memberikan rwx untuk owner, r-x untuk group, no access untuk others (750)
sudo chmod 750 /opt/project/logs

# Memberikan rw- untuk owner, r-- untuk group, no access untuk others (640)
sudo chmod 640 /opt/project/backup
```

#### B. Notasi Simbolik (Symbolic Notation)
Menggunakan representasi Karakter: **User/Owner (`u`)**, **Group (`g`)**, **Others (`o`)**, **All (`a`)** dengan operator (`+`, `-`, `=`).

*Contoh Eksekusi Perintah:*
```bash
# Menambahkan izin eksekusi (x) ke group pada direktori logs
sudo chmod g+x /opt/project/logs

# Menghapus izin baca dan tulis dari others pada direktori backup
sudo chmod o-rw /opt/project/backup

# Mengatur tepat rw- untuk owner dan group secara simultan
sudo chmod ug=rw /opt/project/logs
```

---

### 2.4 Skenario Khusus: File Read-Only Owner & Executable Group
Membuat sebuah berkas uji `/opt/project/logs/script_test.sh` dengan syarat khusus:
* **Owner:** Hanya bisa membaca (*Read-only* = `r--` / `4`)
* **Group:** Bisa membaca dan mengeksekusi (*Read + Execute* = `r-x` / `5`)
* **Others:** Tidak memiliki akses sama sekali (*No access* = `---` / `0`)

1. **Membuat File Uji:**
   ```bash
   sudo touch /opt/project/logs/script_test.sh
   ```

2. **Mengatur Hak Akses Spesifik:**
   * Menggunakan Notasi Numerik:
     ```bash
     sudo chmod 450 /opt/project/logs/script_test.sh
     ```
   * Atau Menggunakan Notasi Simbolik:
     ```bash
     sudo chmod u=r,g=rx,o= /opt/project/logs/script_test.sh
     ```

3. **Verifikasi Hak Akses File:**
   ```bash
   ls -l /opt/project/logs/script_test.sh
   ```
   *Tampilan Output Terminal:*
   ```text
   -r--r-x--- 1 root devteam 0 Aug 26 14:00 /opt/project/logs/script_test.sh
   ```

---

## 3. Kesimpulan

Praktikum **Lab 2: Permission & File Management** telah selesai dilaksanakan dengan hasil sebagai berikut:
1. Pembentukan struktur direktori `/opt/project` beserta seluruh sub-direktorinya berhasil dilakukan menggunakan utilitas `mkdir -p`.
2. Pengisian dan isolasi grup `devteam` pada direktori `/opt/project/data` berhasil dikonfigurasi menggunakan `chown` dan `chmod`.
3. Pemahaman perbedaan antara Notasi Numerik (oktal `4-2-1`) dan Notasi Simbolik (`u/g/o/a`) telah diuji dan dibuktikan melalui latihan berulang.
4. Skenario unik pengkonfigurasian file (`450` atau `u=r,g=rx,o=`) terverifikasi sukses dengan keluaran atribut `-r--r-x---`.

# Lab 3: Instalasi & Pengelolaan Layanan Sistem (Service Management with Systemd)

## 1. Tujuan Praktikum

1. Memahami konsep pengelolaan *service/daemon* pada Linux menggunakan utiilitas init system modern (**Systemd** / `systemctl`).
2. Melakukan instalasi, pengaktifan, dan konfigurasi auto-start layanan web server (Nginx) menggunakan manajer paket `apt`.
3. Mempelajari metode penghentian paksa (*process termination*) menggunakan perintah `kill` / `pkill` serta melakukan analisis jejak krisis (*debugging/troubleshooting*) memanfaatkan log sistem (**`journalctl`**).
4. Membuat, mengonfigurasi, dan menguji layanan kustom (*custom systemd service unit*) untuk mengelola skrip buatan sendiri (Bash/Python) agar berjalan secara persisten di latar belakang (*background process*).

---

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Instalasi & Konfigurasi Auto-start Nginx Web Server

1. **Memperbarui Repositori dan Menginstal Nginx:**
   ```bash
   sudo apt update
   sudo apt install nginx -y
   ```

2. **Pengaturan Auto-Start & Memulai Service:**
   Mengatur agar layanan Nginx menyala otomatis saat server melakukan *booting*:
   ```bash
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

3. **Verifikasi Status Service:**
   ```bash
   sudo systemctl status nginx
   ```
   *Hasil:* Status Nginx menunjukkan **`active (running)`** dan terkonfigurasi **`enabled`** untuk booting otomatis.

---

### 2.2 Penghentian Paksa Service & Analisis Log (`journalctl`)

1. **Mencari Process ID (PID) Nginx Master Process:**
   ```bash
   ps aux | grep nginx
   # Atau menggunakan pgrep
   pgrep -f "nginx: master process"
   ```

2. **Menghentikan Layanan Secara Paksa (*Force Kill*):**
   Mengeksekusi sinyal `SIGKILL` (`-9`) langsung ke PID proses master Nginx untuk mensimulasikan kegagalan/crash sistem:
   ```bash
   sudo kill -9 <PID_NGINX_MASTER>
   ```

3. **Melakukan Analisis Penyebab Kematian Service Lewat `journalctl`:**
   Memeriksa log spesifik unit Nginx untuk menganalisis mengapa layanan berhenti secara mendadak:
   ```bash
   sudo journalctl -u nginx -e --no-pager
   ```
   *Hasil Analisis Log:* Log mencatat bahwa proses utama Nginx dihentikan oleh sinyal eksternal abnormal (`SIGKILL` / `signal 9`). Status `systemctl status nginx` berubah menjadi `failed` atau `inactive`.

---

### 2.3 Pembuatan Custom Systemd Service File

Tujuannya adalah membuat skrip kustom yang akan terus berjalan di latar belakang dan dikelola penuh oleh Systemd.

#### Step A: Membuat Skrip Bash Kustom
Membuat skrip sederhana di `/usr/local/bin/myservice.sh` yang menulis timestamp ke dalam log setiap 5 detik:
```bash
sudo nano /usr/local/bin/myservice.sh
```

Isi dari skrip `/usr/local/bin/myservice.sh`:
```bash
#!/bin/bash
while true; do
    echo "Custom Service Lab 3 sedang berjalan pada: $(date)"
    sleep 5
done
```

Atur izin eksekusi (*executable permission*) pada skrip:
```bash
sudo chmod +x /usr/local/bin/myservice.sh
```

#### Step B: Membuat Systemd Unit File
Membuat file unit service baru bernama `custom-app.service` pada direktori `/etc/systemd/system/`:
```bash
sudo nano /etc/systemd/system/custom-app.service
```

Isi konfigurasi file `custom-app.service`:
```ini
[Unit]
Description=Custom Daemon App Lab 3 DevOps
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/myservice.sh
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
```

#### Step C: Reload Systemd, Start, & Verifikasi Service Baru
1. Reload daemon Systemd agar mengenali file unit baru:
   ```bash
   sudo systemctl daemon-reload
   ```
2. Mengaktifkan dan menjalankan `custom-app.service`:
   ```bash
   sudo systemctl enable --now custom-app.service
   ```
3. Memeriksa status dan log output dari service kustom:
   ```bash
   sudo systemctl status custom-app.service
   sudo journalctl -u custom-app.service -f
   ```
   *Hasil:* Service kustom berhasil berjalan (*active/running*), melakukan auto-restart jika terhenti, dan menghasilkan output log secara konsisten di `journalctl`.

---

## 3. Kesimpulan

Praktikum **Lab 3: Install & Kelola Service** berhasil dilaksanakan dengan poin penting:
1. Perintah `systemctl` terbukti efektif untuk mengontrol *lifecycle* layanan sistem (`start`, `stop`, `enable`, `disable`).
2. Penggunaan sinyal `kill -9` terbukti mematikan proses seketika, dan jejak kejadian tersebut berhasil diidentifikasi melalui fasilitas pengisian log terpusat **`journalctl`**.
3. Pembuatan *Custom Systemd Unit File* berhasil diimplementasikan, membuktikan bahwa aplikasi/skrip apapun dapat diubah menjadi layanan tingkat sistem dengan kemampuan pemulihan otomatis (*Auto-Restart*).

# Lab 4: Pengelolaan Media Penyimpanan & LVM (Storage & Logical Volume Management)

## 1. Tujuan Praktikum

1. Memahami konsep manajemen media penyimpanan (*storage management*) pada Linux OS.
2. Melakukan instalasi, partisi, format *filesystem*, dan pengaitan (*mount*) disk virtual baru secara manual.
3. Menguasai arsitektur **Logical Volume Management (LVM)** mencakup pembuatan *Physical Volume (PV)*, *Volume Group (VG)*, dan *Logical Volume (LV)*.
4. Melakukan ekspansi/perluasan kapasitas *Logical Volume* secara dinamis (*online resize*) tanpa memerlukan penghentian sistem (*reboot*).
5. Memahami dan mengonfigurasi pengaitan otomatis *storage* saat proses *booting* melalui berkas `/etc/fstab` menggunakan **UUID**.

---

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Menambahkan & Identifikasi Virtual Disk Baru
1. Menambahkan 2 harddisk virtual baru pada setting VM (VirtualBox/VMware):
   - Disk 1: `/dev/sdb` (misal 10 GB)
   - Disk 2: `/dev/sdc` (misal 10 GB)
2. Memeriksa identifikasi disk yang terdeteksi di server:
   ```bash
   lsblk
   ```
   *Hasil:* Disk `/dev/sdb` dan `/dev/sdc` terdeteksi di dalam hirarki blok sistem.

---

### 2.2 Partisi, Format (EXT4/XFS), dan Manual Mount
1. **Membuat Partisi Baru pada Disk `/dev/sdb`:**
   ```bash
   sudo fdisk /dev/sdb
   ```
   *(Mengetik `n` untuk partisi baru, memilih tipe utama `p`, menekan `Enter` untuk opsi default, lalu `w` untuk menyimpan perubahan).*

2. **Memformat Partisi dengan Filesystem EXT4:**
   ```bash
   sudo mkfs.ext4 /dev/sdb1
   ```

3. **Membuat Mount Point & Pengaitan Manual:**
   ```bash
   sudo mkdir -p /mnt/data_manual
   sudo mount /dev/sdb1 /mnt/data_manual
   ```
4. **Verifikasi Mount:**
   ```bash
   df -h /mnt/data_manual
   ```
   *Hasil:* Partisi `/dev/sdb1` berhasil terkait (*mounted*) pada direktori `/mnt/data_manual`.

---

### 2.3 Konfigurasi LVM (Physical Volume, Volume Group, Logical Volume)

LVM digunakan agar ruang penyimpanan dapat digabungkan dan diperluas secara fleksibel.

#### Step A: Inisialisasi Physical Volume (PV)
Mengubah disk mentah `/dev/sdc` menjadi Physical Volume LVM:
```bash
sudo pvcreate /dev/sdc
```

#### Step B: Pembuatan Volume Group (VG)
Membuat Volume Group baru bernama `vg_app` yang menggunakan alokasi dari `/dev/sdc`:
```bash
sudo vgcreate vg_app /dev/sdc
```

#### Step C: Pembuatan Logical Volume (LV) & Format
1. Membuat Logical Volume bernama `lv_storage` sebesar 5 GB di dalam `vg_app`:
   ```bash
   sudo lvcreate -L 5G -n lv_storage vg_app
   ```
2. Memformat `lv_storage` menggunakan *filesystem* EXT4:
   ```bash
   sudo mkfs.ext4 /dev/vg_app/lv_storage
   ```
3. Melakukan mount ke titik direktori tujuan:
   ```bash
   sudo mkdir -p /mnt/app_data
   sudo mount /dev/vg_app/lv_storage /mnt/app_data
   ```

---

### 2.4 Ekspansi Logical Volume Tanpa Reboot (*Online Resize*)

Salah satu keunggulan LVM adalah kemampuan memperluas kapasitas disk yang sedang digunakan tanpa *downtime*.

1. **Memperluas Ukuran Logical Volume:**
   Menambahkan kapasitas `lv_storage` sebesar 3 GB tambahan dari sisa alokasi `vg_app`:
   ```bash
   sudo lvextend -L +3G /dev/vg_app/lv_storage
   ```
2. **Memperluas Filesystem (*Resize On-the-Fly*):**
   ```bash
   sudo resize2fs /dev/vg_app/lv_storage
   ```
3. **Verifikasi Perubahan Ukuran:**
   ```bash
   df -h /mnt/app_data
   ```
   *Hasil:* Ukuran direktori `/mnt/app_data` meningkat dari 5 GB menjadi 8 GB tanpa melakukan proses *restart/reboot* server.

---

### 2.5 Konfigurasi Persistent Mount (`/etc/fstab`)

Agar partisi dan LVM tetap terkait secara otomatis saat server di-booting ulang, dilakukan pendaftaran pada `/etc/fstab`.

1. **Mengambil Universal Unique Identifier (UUID) Disk:**
   ```bash
   sudo blkid
   ```
   *Catat UUID dari `/dev/sdb1` dan `/dev/vg_app/lv_storage`.*

2. **Menambahkan Konfigurasi ke `/etc/fstab`:**
   ```bash
   sudo nano /etc/fstab
   ```
   Tambahkan baris berikut di paling bawah file:
   ```text
   UUID=<UUID_SDB1>          /mnt/data_manual  ext4  defaults  0  2
   UUID=<UUID_LV_STORAGE>   /mnt/app_data     ext4  defaults  0  2
   ```

3. **Menguji Konfigurasi `/etc/fstab` (Penting):**
   Memastikan tidak ada kesalahan sintaks yang dapat menyebabkan kegagalan booting (*boot loop*):
   ```bash
   sudo umount /mnt/data_manual /mnt/app_data
   sudo mount -a
   df -h
   ```
   *Hasil:* Seluruh mount point berhasil terpasang kembali dengan sempurna melalui perintah `mount -a`.

---

## 3. Kesimpulan

Praktikum **Lab 4: Storage & LVM** berhasil diselesaikan dengan hasil:
1. Pemahaman mendalam mengenai siklus pengelolaan disk (Partisi -> Format -> Mount).
2. Arsitektur LVM (PV -> VG -> LV) terbukti sangat fleksibel untuk kebutuhan sistem skala besar (*enterprise*).
3. Fitur *online expansion* (`lvextend` & `resize2fs`) sukses menambah alokasi ruang simpan tanpa mengganggu kestabilan sistem atau melakukan reboot.
4. Penggunaan UUID pada `/etc/fstab` berhasil menjamin konsistensi pengaitan media penyimpanan saat proses *booting*.

# Lab 5: Otomasi Tugas Menggunakan Skrip Bash & Cron (Automasi dengan Bash + Cron)

## 1. Tujuan Praktikum

1. Memahami konsep otomatisasi tugas berkala (*scheduled tasks*) pada lingkungan sistem operasi Linux.
2. Membuat skrip **Bash** kustom untuk melakukan kompresi dan *backup* otomatis pada direktori `/opt/project/data` dengan format penamaan berbasis *timestamp*.
3. Mengonfigurasi mekanisme pengarsipan (*logging*) untuk mencatat status keberhasilan atau kegagalan eksekusi skrip ke dalam berkas log terpusat.
4. Mengonfigurasi utilitas **Cron** (`crontab`) untuk menjadwalkan eksekusi skrip secara otomatis setiap jam 02:00 pagi.

---

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Pembuatan Skrip Backup Bash (`backup_project.sh`)

Skrip dibuat di lokasi `/usr/local/bin/backup_project.sh`. Skrip ini akan melakukan kompresi berkas dalam bentuk `.tar.gz`, membuat penamaan unik dengan *timestamp*, serta mencatat hasilnya ke `/var/log/backup_project.log`.

1. **Membuat File Skrip:**
   ```bash
   sudo nano /usr/local/bin/backup_project.sh
   ```

2. **Isi Kode Skrip Bash:**
   ```bash
   #!/bin/bash

   # Variable Konfigurasi
   SOURCE_DIR="/opt/project/data"
   BACKUP_DIR="/opt/project/backup"
   TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
   BACKUP_FILE="${BACKUP_DIR}/backup_data_${TIMESTAMP}.tar.gz"
   LOG_FILE="/var/log/backup_project.log"

   # Pastikan folder backup dan log file ada
   mkdir -p "$BACKUP_DIR"
   touch "$LOG_FILE"

   # Catat Waktu Mulai
   echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] Memulai proses backup direktori ${SOURCE_DIR}..." >> "$LOG_FILE"

   # Eksekusi Kompresi tar.gz
   if tar -czf "$BACKUP_FILE" -C "$SOURCE_DIR" . >> "$LOG_FILE" 2>&1; then
       echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS] Backup berhasil dibuat: ${BACKUP_FILE}" >> "$LOG_FILE"
   else
       echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] Gagal membuat backup!" >> "$LOG_FILE"
   fi
   ```

3. **Memberikan Izin Eksekusi (*Executable Permission*):**
   ```bash
   sudo chmod +x /usr/local/bin/backup_project.sh
   ```

---

### 2.2 Pengujian Skrip Secara Manual

Sebelum dimasukkan ke dalam penjadwalan Cron, skrip diuji secara manual untuk memastikan logika *backup* dan pengarsipan *log* berjalan tanpa error.

1. Memanggil skrip secara langsung:
   ```bash
   sudo /usr/local/bin/backup_project.sh
   ```

2. Verifikasi Berkas Hasil Backup:
   ```bash
   ls -la /opt/project/backup
   ```
   *Hasil:* Terbuat berkas arsip seperti `backup_data_20260826_020000.tar.gz`.

3. Verifikasi Isi Berkas Log:
   ```bash
   cat /var/log/backup_project.log
   ```
   *Hasil Output Log:*
   ```text
   [2026-08-26 14:30:00] [INFO] Memulai proses backup direktori /opt/project/data...
   [2026-08-26 14:30:01] [SUCCESS] Backup berhasil dibuat: /opt/project/backup/backup_data_20260826_143000.tar.gz
   ```

---

### 2.3 Penjadwalan Otomatis Menggunakan Cron

Skrip dijadwalkan agar berjalan otomatis setiap jam 02:00 pagi setiap hari.

1. Mengedit tabel Cron untuk akun `root` (karena proses butuh akses ke `/opt/project/data` dan `/var/log`):
   ```bash
   sudo crontab -e
   ```

2. Menambahkan ekspresi Cron berikut pada baris paling bawah:
   ```cron
   0 2 * * * /usr/local/bin/backup_project.sh
   ```

   **Penjelasan Sintaks Cron (`0 2 * * *`):**
   - `0`  : Menit ke-0.
   - `2`  : Jam 02 (format 24-jam / 02:00 AM).
   - `*`  : Setiap hari dalam sebulan.
   - `*`  : Setiap bulan.
   - `*`  : Setiap hari dalam seminggu.

3. Verifikasi Penjadwalan Cron:
   ```bash
   sudo crontab -l
   ```
   *Hasil:* Aturan penjadwalan jam 02:00 pagi terverifikasi terdaftar aktif.

---

## 3. Kesimpulan

Praktikum **Lab 5: Automasi dengan Bash + Cron** berhasil dilaksanakan:
1. Skrip pemeliharaan berkas berbasis Bash berhasil mengarsip folder `/opt/project/data` menggunakan algoritma kompresi `tar.gz`.
2. Format penamaan penanda waktu (*timestamp*) dinamis berhasil dipraktikkan untuk mencegah duplikasi atau *overwriting* berkas *backup*.
3. Mekanisme pengoperasian log (*logging*) terbukti mampu mencatat status eksekusi secara rinci untuk keperluan pemantauan (*monitoring*).
4. Penjadwalan tugas otomatis menggunakan `crontab` berhasil dikonfigurasi untuk mengeksekusi *backup* secara konsisten setiap pukul 02:00 pagi.

# Lab 6: Pengaturan Keamanan Dasar Server & Firewall (Firewall & Security Dasar)

## 1. Tujuan Praktikum

1. Memahami konsep keamanan dasar server Linux menggunakan utilitas **Uncomplicated Firewall (UFW)**.
2. Mengonfigurasi *firewall rules* untuk membatasi lalu lintas jaringan (hanya mengizinkan port SSH dan HTTP).
3. Melakukan pengujian aksesabilitas port dari jaringan luar (*port scanning*) untuk memastikan aturan keamanan bekerja dengan baik.
4. Mengubah port *default* SSH dari port `22` ke port kustom untuk meminimalisir serangan otomatis (*automated bot scanner*).
5. Mengonfigurasi utilitas **Fail2ban** untuk mencegah serangan *Brute-Force* pada layanan SSH secara otomatis.

---

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Konfigurasi UFW (Uncomplicated Firewall)

1. **Memeriksa Status Awal UFW:**
   ```bash
   sudo ufw status verbose
   ```

2. **Pengaturan Aturan Default & Pengizinan Port (SSH & HTTP):**
   ```bash
   # Aturan Default: Blokir semua koneksi masuk, izinkan semua koneksi keluar
   sudo ufw default deny incoming
   sudo ufw default allow outgoing

   # Mengizinkan Port SSH (22) dan HTTP (80)
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   ```

3. **Mengaktifkan Firewall:**
   ```bash
   sudo ufw enable
   ```

4. **Verifikasi Aturan UFW:**
   ```bash
   sudo ufw status numbered
   ```
   *Hasil:* Port `22/tcp` dan `80/tcp` berstatus **`ALLOW IN`** dari lokasi mana pun (*Anywhere*).

---

### 2.2 Pengujian Port dari Komputer Luar

Dilakukan pengujian menggunakan utilitas `nmap` atau `nc` (netcat) dari komputer klien/luar:

```bash
# Pengujian Port Scanning dari Laptop Klien
nmap -p 22,80,21,3306 <IP_SERVER>
```

*Hasil Pengujian:*
- Port **22** (SSH): `open`
- Port **80** (HTTP): `open`
- Port **21** (FTP) & **3306** (MySQL): `filtered` / `closed` (Tersaring oleh UFW).

---

### 2.3 Mengubah Port Default SSH & Update Firewall Rules

Mengubah port *default* SSH dari `22` ke port kustom `2222` untuk meningkatkan *security by obscurity*.

1. **Mengedit Konfigurasi SSH Daemon (`sshd_config`):**
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   *Ubah baris `#Port 22` menjadi:*
   ```text
   Port 2222
   ```

2. **Memperbarui Aturan UFW:**
   ```bash
   # Tambahkan port kustom baru
   sudo ufw allow 2222/tcp

   # Hapus aturan port 22 lama
   sudo ufw delete allow 22/tcp
   ```

3. **Restart Service SSH & Verifikasi:**
   ```bash
   sudo systemctl restart ssh
   ```
   *Uji Koneksi SSH Baru:*
   ```bash
   ssh -p 2222 user@<IP_SERVER>
   ```
   *Hasil:* Koneksi SSH berhasil terhubung menggunakan port `2222`.

---

### 2.4 Setup Fail2ban untuk Mitigasi Brute-Force SSH

1. **Instalasi Fail2ban:**
   ```bash
   sudo apt update && sudo apt install fail2ban -y
   ```

2. **Konfigurasi Jail Fail2ban Kustom (`jail.local`):**
   ```bash
   sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
   sudo nano /etc/fail2ban/jail.local
   ```

   *Tambahkan/Edit blok konfigurasi `[sshd]` berikut:*
   ```ini
   [sshd]
   enabled = true
   port = 2222
   filter = sshd
   logpath = /var/log/auth.log
   maxretry = 3
   findtime = 10m
   bantime = 1h
   ```

3. **Restart & Cek Status Fail2ban:**
   ```bash
   sudo systemctl restart fail2ban
   sudo fail2ban-client status sshd
   ```
   *Hasil:* Service Fail2ban aktif memantau port `2222` dengan batas percobaan gagal sebanyak 3 kali (*maxretry = 3*).

---

## 3. Kesimpulan

Praktikum **Lab 6: Firewall & Security Dasar** berhasil dilaksanakan:
1. Konfigurasi **UFW** terbukti efektif dalam membatasi akses port server hanya untuk layanan yang diizinkan (SSH & HTTP).
2. Pengubahan port *default* SSH ke port kustom (`2222`) berhasil diimplementasikan dan disesuaikan pada aturan *firewall*.
3. Utilitas **Fail2ban** sukses dikonfigurasi untuk mendeteksi serta memblokir alamat IP penyerang yang melakukan percobaan login (*brute-force*) secara otomatis.

# Lab 7: Simulasi Troubleshooting & Pemulihan Server (Troubleshooting Simulasi)

## 1. Tujuan Praktikum

1. Melatih kemampuan diagnosa krisis (*system troubleshooting*) pada skenario kegagalan server nyata (*real-world failure scenarios*).
2. Mempelajari pemulihan layanan web (*Nginx*) yang terhenti melalui analisis log sistem (`journalctl` & log aplikasi).
3. Melakukan identifikasi dan pembersihan lonjakan penggunaan ruang penyimpanan (*disk full*) menggunakan utilitas `df`, `du`, dan `find`.
4. Mendiagnosa dan memulihkan kegagalan akses akibat kesalahan konfigurasi hak akses berkas (*permission & ownership error*).

---

## 2. Langkah Kerja, Investigasi & Pemulihan

### 2.1 Skenario 1: Web Server Crash / Service Down

#### A. Simulasi Kerusakan (Sengaja Dimatikan)
```bash
sudo systemctl stop nginx
```

#### B. Gejala & Investigasi
- **Gejala:** Website tidak dapat diakses (muncul *Connection Refused* atau *ERR_CONNECTION_REFUSED* di browser).
- **Langkah Diagnosa:**
  1. Cek status service web server:
     ```bash
     sudo systemctl status nginx
     ```
     *Temuan:* Status Nginx menunjukkan **`inactive (dead)`**.
  2. Cek log error sistem via `journalctl` dan log error Nginx:
     ```bash
     sudo journalctl -u nginx -n 20 --no-pager
     sudo tail -n 20 /var/log/nginx/error.log
     ```
     *Hasil Analisis:* Ditemukan catatan bahwa service dihentikan secara sengaja/abnormal tanpa adanya proses pengikatan (*binding*) pada port HTTP 80.

#### C. Solusi & Pemulihan
Nyalakan kembali service Nginx dan pastikan fitur *auto-start* aktif:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```
*Verifikasi:* Akses ulang via `curl -I http://localhost` atau browser. Response mengembalikan **`HTTP/1.1 200 OK`**.

---

### 2.2 Skenario 2: Disk Space Penuh (Disk Full Incident)

#### A. Simulasi Kerusakan (Membuat File Sampah Raksasa)
Membuat berkas dummy 5 GB di direktori `/var/log/` untuk memenuhi kapasitas partisinya:
```bash
sudo fallocate -l 5G /var/log/big_junk_file.log
```

#### B. Gejala & Investigasi
- **Gejala:** Aplikasi gagal menulis data, log error *No space left on device*, dan beberapa service crash.
- **Langkah Diagnosa:**
  1. Cek penggunaan disk per partisi:
     ```bash
     df -h
     ```
     *Temuan:* Partisi root `/` menunjukkan kapasitas terisi **100%**.
  2. Cari lokasi folder yang memakan kapasitas terbesar:
     ```bash
     sudo du -sh /* 2>/dev/null | sort -hr | head -n 10
     sudo du -sh /var/* 2>/dev/null | sort -hr | head -n 10
     ```
     *Temuan:* Direktori `/var/log` memakan alokasi terbesar.
  3. Lakukan pencarian berkas besar (> 1 GB) menggunakan perintah `find`:
     ```bash
     sudo find /var/log -type f -size +1G -exec ls -lh {} \;
     ```
     *Temuan:* Ditemukan berkas abnormal `/var/log/big_junk_file.log` berukuran 5 GB.

#### C. Solusi & Pemulihan
Hapus berkas sampah yang menyebabkan disk penuh:
```bash
sudo rm -f /var/log/big_junk_file.log
```
*Verifikasi:* Jalankan kembali `df -h` untuk memastikan persentase penggunaan disk kembali aman (normal).

---

### 2.3 Skenario 3: Error Hak Akses Berkas (Permission / Ownership Misconfiguration)

#### A. Simulasi Kerusakan (Merusak Hak Akses Document Root)
```bash
sudo chmod 000 /var/www/html/index.html
sudo chown root:root /var/www/html/index.html
```

#### B. Gejala & Investigasi
- **Gejala:** Pengunjung web menerima error **`403 Forbidden`** saat membuka halaman web.
- **Langkah Diagnosa:**
  1. Uji akses via `curl`:
     ```bash
     curl -I http://localhost
     ```
     *Hasil:* Mengembalikan status header `HTTP/1.1 403 Forbidden`.
  2. Periksa error log spesifik Nginx:
     ```bash
     sudo tail -n 10 /var/log/nginx/error.log
     ```
     *Temuan Log:* Ditemukan log error: `[error] ... open() "/var/www/html/index.html" failed (13: Permission denied)`.
  3. Cek struktur kepemilikan dan permission berkas target:
     ```bash
     ls -la /var/www/html/index.html
     ```
     *Temuan:* Izin berkas berstatus `----------` (000) sehingga user web server (`www-data`) tidak memiliki hak baca (*read permission*).

#### C. Solusi & Pemulihan
Kembalikan hak akses berkas web server ke konfigurasi standar (`644` untuk berkas, `www-data` sebagai owner):
```bash
sudo chown -R www-data:www-data /var/www/html
sudo chmod 644 /var/www/html/index.html
```
*Verifikasi:* Jalankan `curl -I http://localhost` untuk memastikan halaman mengembalikan status **`200 OK`**.

---

## 3. Kesimpulan

Praktikum **Lab 7: Troubleshooting Simulasi** berhasil diselesaikan dengan beberapa poin penting:
1. Kemampuan membaca log via `journalctl` dan `/var/log/` merupakan fondasi utama dalam mengidentifikasi penyebab kematian suatu *service*.
2. Penggunaan kombinasi perintah `df -h`, `du -sh`, dan `find -size` sangat efektif untuk melacak dan memulihkan krisis disk penuh secara cepat.
3. Kode status HTTP **`403 Forbidden`** dan log `Permission denied` dapat diselesaikan dengan mengoreksi *permission* (chmod) serta kepemilikan user web server (*chown*).
