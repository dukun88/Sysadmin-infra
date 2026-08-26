# Lab 1: Server Setup Dasar

**Mata Kuliah:** Administrasi Server & DevOps  
**Nama Pengumpul:** [Nama Mahasiswa]  
**NIM:** [NIM Mahasiswa]  
**Tanggal:** 26 Agustus 2026  
**Sistem Operasi:** Ubuntu Server 22.04 / 24.04 LTS  

---

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
