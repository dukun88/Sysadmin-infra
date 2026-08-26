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

# Networking Labs

## Lab 1: IP Addressing & Subnetting

* Tentukan network 192.168.10.0/24, bagi jadi 4 subnet lebih kecil
* Hitung manual: network address, broadcast address, usable host range tiap subnet
* Konfigurasi static IP di 2 VM sesuai subnet yang beda, coba ping antar subnet (harusnya gagal tanpa routing)

## Lab 2: Konfigurasi Network di Linux

* Cek & ubah IP config pakai `ip addr`, `nmcli`, dan `netplan`
* Setup network interface dengan static IP lewat file netplan/YAML
* Edit `/etc/hosts` buat resolve hostname custom tanpa DNS
* Edit `/etc/resolv.conf`, coba ganti DNS server, uji pakai `nslookup`/`dig`

## Lab 3: Routing Dasar

* Siapkan 2 VM di subnet berbeda + 1 VM jadi "router" (IP forwarding enabled)
* Aktifkan `ip_forward` di kernel (`/proc/sys/net/ipv4/ip_forward`)
* Tambahkan static route di kedua VM supaya bisa saling ping lewat router
* Cek routing table pakai `ip route` / `route -n`

## Lab 4: DNS Server Sederhana

* Install `bind9` (atau `dnsmasq` untuk versi ringan) di satu VM
* Buat DNS record A untuk domain lokal (misal `server.lab.local`)
* Arahkan VM lain pakai DNS server ini, uji resolve pakai `dig`/`nslookup`
* Coba tambah record baru, reload service, verifikasi propagasi

## Lab 5: DHCP Server Sederhana

* Install `isc-dhcp-server` di satu VM
* Konfigurasi range IP yang di-lease, subnet, gateway, DNS
* Set VM lain jadi DHCP client, cek apakah dapat IP otomatis
* Cek lease log buat lihat siapa dapat IP apa

## Lab 6: Firewall & Port Filtering

* Setup `iptables` atau `ufw` di satu VM sebagai gateway
* Blokir semua trafik masuk kecuali SSH & HTTP
* Uji dari VM lain: coba akses port yang diblokir vs yang dibuka
* Tambahkan NAT rule sederhana (masquerade) biar VM di belakang gateway bisa akses internet

## Lab 7: Network Troubleshooting

* Simulasikan masalah konektivitas (misal salah gateway, DNS mati, kabel/interface down)
* Diagnosa pakai `ping`, `traceroute`, `mtr`, `netstat`/`ss`, `nmap`
* Cek koneksi service tertentu pakai `telnet`/`nc` ke port spesifik
* Dokumentasikan alur troubleshooting: dari gejala sampai ketemu akar masalah

## Lab 8: Packet Capture & Analysis

* Install `tcpdump` dan/atau Wireshark
* Capture trafik saat melakukan `ping`, `curl`, atau SSH ke server lain
* Analisis handshake TCP (SYN, SYN-ACK, ACK) dari hasil capture
* Filter capture berdasarkan IP/port tertentu buat latihan baca trafik

# Windows Server & Active Directory Labs

## Lab 1: Instalasi Windows Server

* Install Windows Server (2019/2022) di VM
* Set static IP, hostname, dan timezone
* Aktivasi Remote Desktop, coba remote dari mesin lain
* Update Windows lewat Windows Update

## Lab 2: Install Active Directory Domain Services (AD DS)

* Install role AD DS via Server Manager / PowerShell
* Promosikan server jadi Domain Controller
* Buat domain baru (misal `lab.local`)
* Verifikasi domain jalan: cek DNS, `nslookup`, dan Active Directory Users and Computers (ADUC)

## Lab 3: User & Group Management

* Buat Organizational Unit (OU) untuk struktur (misal: IT, Finance, HR)
* Buat beberapa user account di tiap OU
* Buat security group, masukkan user ke group tertentu
* Coba bulk-create user pakai PowerShell (`New-ADUser`)

## Lab 4: Join Client ke Domain

* Siapkan 1 VM client (Windows 10/11)
* Join client ke domain `lab.local`
* Login pakai domain user dari client
* Verifikasi user muncul login history di Domain Controller

## Lab 5: Group Policy Object (GPO)

* Buat GPO baru, terapkan ke OU tertentu
* Contoh policy: set wallpaper, disable Control Panel, password policy (minimum length, complexity)
* Force update GPO di client (`gpupdate /force`)
* Verifikasi policy berlaku di client

## Lab 6: File Sharing & NTFS Permission

* Buat shared folder di server
* Set NTFS permission berbeda untuk tiap group (misal: Finance read-only, IT full control)
* Mapping network drive dari client ke shared folder
* Uji akses dari user dengan permission berbeda-beda

## Lab 7: DNS & DHCP di Windows Server

* Install role DNS & DHCP
* Buat DHCP scope, tentukan range IP, gateway, DNS server
* Set client dapat IP otomatis dari DHCP server
* Buat DNS record (A record) untuk resource internal

## Lab 8: Backup & Disaster Recovery Dasar

* Setup Windows Server Backup
* Backup System State dari Domain Controller
* Simulasikan restore (misal user ke-delete, restore dari Active Directory Recycle Bin)
* Dokumentasikan langkah recovery step-by-step

## Lab 9: Troubleshooting Simulasi

* Simulasikan client gagal join domain, diagnosa penyebabnya (DNS salah, firewall, dll)
* Simulasikan GPO tidak apply, cek pakai `gpresult /r`
* Simulasikan user lupa password, praktik reset via ADUC dan PowerShell

# Virtualization & Cloud Fundamentals Labs

## Lab 1: Proxmox VE Setup

* Install Proxmox VE di bare metal atau nested VM
* Konfigurasi network bridge, storage
* Buat VM baru dari ISO, catat resource allocation (CPU, RAM, disk)
* Buat template VM, clone jadi VM baru dari template

## Lab 2: VM Management & Snapshot

* Praktik clone, resize disk, dan migrate VM antar storage
* Buat snapshot sebelum perubahan besar, coba rollback
* Setup resource limit (CPU/RAM) per VM
* Monitoring resource usage tiap VM dari dashboard Proxmox

## Lab 3: Docker Dasar

* Install Docker di Ubuntu Server
* Jalankan container pertama (`docker run`), pahami image vs container
* Build image sendiri dari `Dockerfile` (misal aplikasi web sederhana)
* Kelola container: `docker ps`, `docker logs`, `docker exec`, `docker stop/rm`

## Lab 4: Docker Compose

* Buat `docker-compose.yml` untuk multi-container app (misal web app + database)
* Setup volume untuk persistent data
* Setup network antar container
* Praktik `docker compose up/down`, cek log tiap service

## Lab 5: AWS Account & IAM Dasar

* Buat AWS Free Tier account
* Setup IAM user baru (jangan pakai root untuk kerja sehari-hari)
* Buat IAM policy & group, terapkan ke user
* Aktifkan MFA untuk root & IAM user

## Lab 6: EC2 (Virtual Machine di Cloud)

* Launch instance EC2 (pilih free tier eligible, misal t2.micro)
* Setup security group (buka port SSH & HTTP saja)
* SSH ke instance pakai key pair
* Install web server sederhana, akses dari browser via public IP

## Lab 7: S3 & Storage Dasar

* Buat S3 bucket
* Upload/download file via console dan AWS CLI
* Setup bucket policy dasar (public read untuk static website)
* Host static website sederhana di S3

## Lab 8: VPC Dasar

* Buat VPC custom dengan subnet public & private
* Setup Internet Gateway untuk subnet public
* Launch EC2 di subnet private, akses lewat bastion host di subnet public
* Verifikasi subnet private tidak bisa diakses langsung dari internet

## Lab 9: Monitoring & Cost Awareness

* Setup CloudWatch alarm dasar (misal CPU usage tinggi)
* Cek AWS Billing Dashboard, pahami cara baca cost breakdown
* Set budget alert biar nggak kena tagihan tak terduga
* Praktik stop/terminate resource yang nggak dipakai biar tetap di free tier

# Sertifikasi & Portfolio Checklist

## Lab 1: Riset & Pilih Sertifikasi

* Bandingkan CompTIA A+, Network+, dan Linux LPIC-1 (biaya, materi, pengakuan industri)
* Cek lowongan sysadmin/IT support di job portal, catat sertifikasi apa yang paling sering diminta
* Tentukan 1 sertifikasi prioritas untuk 3-6 bulan ke depan
* Cari exam voucher/diskon (biasanya ada program student/bootcamp)

## Lab 2: Susun Rencana Belajar Sertifikasi

* Download exam objectives resmi dari provider sertifikasi
* Petakan objectives ke lab yang sudah pernah dikerjakan (mana yang udah cover, mana yang belum)
* Buat jadwal belajar mingguan sampai target tanggal ujian
* Cari practice exam/soal latihan buat ukur kesiapan

## Lab 3: Setup Portfolio di GitHub

* Buat repo terpisah untuk tiap kategori lab (Linux, Networking, Windows/AD, Cloud)
* Pastikan tiap repo punya README yang jelas (tujuan, langkah, command dipakai)
* Tambahkan screenshot/output hasil eksekusi di tiap lab sebagai bukti
* Buat 1 repo "index" yang me-link semua repo lab jadi satu portofolio utuh

## Lab 4: Dokumentasi Troubleshooting

* Kumpulkan minimal 5 kasus troubleshooting dari lab-lab sebelumnya
* Tulis dalam format: Problem → Diagnosa → Root Cause → Solusi
* Publish sebagai blog post singkat (Medium, Dev.to, atau LinkedIn article)
* Ini jadi bukti kuat problem-solving skill buat recruiter

## Lab 5: Bangun Home Lab Permanen

* Setup home lab yang jalan terus (bukan cuma VM sementara), bisa pakai server bekas/mini PC atau tetap virtual
* Dokumentasikan arsitektur home lab (diagram network, service apa aja yang jalan)
* Tambahkan monitoring sederhana (misal Uptime Kuma atau Netdata)
* Screenshot dashboard monitoring buat portofolio

## Lab 6: Siapkan CV & LinkedIn

* Update CV dengan project/lab yang sudah dikerjakan, fokus ke hasil dan skill teknis
* Update LinkedIn: headline, about, dan pengalaman project sesuai lab
* Minta feedback CV dari orang yang sudah kerja di IT (kalau ada koneksi)
* Siapkan link portofolio GitHub di CV dan LinkedIn

## Lab 7: Latihan Interview Teknis

* Kumpulkan pertanyaan interview umum sysadmin (permission, service, troubleshooting, networking dasar)
* Latihan jawab sambil buka home lab, praktikkan langsung di depan "interviewer" (bisa teman/rekaman diri sendiri)
* Latihan menjelaskan salah satu project dari portofolio secara runtut (STAR method: Situation, Task, Action, Result)
* Review kembali dasar teori yang sering ditanya tapi jarang dipakai praktik (misal OSI layer, port number umum)

## Lab 8: Ambil Ujian Sertifikasi

* Daftar jadwal ujian resmi
* H-1: review ringkasan materi, jangan belajar hal baru
* Ambil ujian
* Update CV, LinkedIn, dan portofolio GitHub begitu lulus (tambahkan badge/sertifikat)
