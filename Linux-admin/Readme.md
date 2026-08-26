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
