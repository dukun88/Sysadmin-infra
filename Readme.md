# Linux Administration

## Lab 1: Server Setup Dasar
Install Ubuntu Server 22.04/24.04 di VM (jangan desktop version, biar terbiasa CLI penuh).

* Set static IP
* Bikin 2 user baru: satu admin (sudo), satu user biasa (no sudo)
* Setup SSH key-based login, matikan password login
* Update & upgrade system

## Lab 2: Permission & File Management

* Bikin struktur folder `/opt/project` dengan sub-folder `data`, `logs`, `backup`
* Set ownership: folder `data` cuma bisa diakses grup tertentu
* Praktikkan `chmod` numeric vs symbolic sampai hafal di luar kepala
* Coba bikin file yang cuma bisa dibaca owner, tapi executable buat group

## Lab 3: Install & Kelola Service

* Install Nginx via `apt`
* Jadikan auto-start pakai `systemctl enable`
* Matikan service secara paksa (`kill`), lalu cek kenapa dia mati lewat `journalctl`
* Bikin custom `systemd` service file buat script kamu sendiri (misal script Python/Bash sederhana yang jalan terus)

## Lab 4: Storage & LVM

* Tambah disk virtual baru di VM
* Partisi, format, mount manual
* Setup LVM: bikin volume group, extend logical volume tanpa reboot
* Edit `/etc/fstab` biar mount otomatis saat boot

## Lab 5: Automasi dengan Bash + Cron

* Tulis script backup yang nge-zip folder `/opt/project/data` ke `/opt/project/backup` dengan timestamp
* Jadwalkan pakai `cron` tiap jam 2 pagi
* Tambahkan logging: setiap kali script jalan, catat hasilnya ke file log

## Lab 6: Firewall & Security Dasar

* Setup `ufw`, cuma buka port SSH & HTTP
* Coba akses dari luar, pastikan port lain ketutup
* Ganti port SSH default (22 → custom), update firewall rule
* Setup fail2ban buat block brute-force SSH

## Lab 7: Troubleshooting Simulasi
Ini yang paling sering ditanya interview — sengaja "rusakin" server, terus perbaiki sendiri:

* Matikan service penting, cari tahu lewat log kenapa website nggak bisa diakses
* Habisin disk space sengaja, latihan cari file besar (`du -sh`, `find`)
* Salah konfigurasi permission, latihan diagnosa dari error message

## Lab 8 (Bonus): Multi-server

* Bikin 2 VM: satu jadi "server", satu jadi "client"
* Setup SSH passwordless antar server
* Coba transfer file pakai `scp`/`rsync`
* Setup NFS share sederhana antar dua VM
