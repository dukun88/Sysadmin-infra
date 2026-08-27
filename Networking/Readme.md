# Lab 1: IP Addressing & Subnetting

## 1. Tujuan Praktikum

- Memahami konsep dasar IP Addressing dan struktur network/host bit pada IPv4.
- Melakukan perhitungan manual subnetting menggunakan metode VLSM/CIDR sederhana.
- Membagi satu network besar menjadi beberapa subnet yang lebih kecil.
- Mengonfigurasi static IP pada dua Virtual Machine (VM) sesuai hasil perhitungan subnetting.
- Menganalisis dan memverifikasi perilaku komunikasi antar host pada subnet yang berbeda tanpa adanya routing.

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Perhitungan Subnetting

Network awal yang digunakan adalah `192.168.10.0/24`, yang akan dibagi menjadi 4 subnet dengan jumlah host yang sama besar.

- **Analisis Kebutuhan**: Untuk membagi network menjadi 4 subnet, dibutuhkan tambahan 2 bit dari bagian host, karena 2² = 4.
- **Penentuan Subnet Mask Baru**: Prefix diubah dari `/24` menjadi `/26` (24 + 2 bit pinjaman).
- **Jumlah Alamat per Subnet**: Dengan `/26`, sisa bit host adalah 32 - 26 = 6 bit, sehingga tiap subnet memiliki 2⁶ = 64 alamat.

Hasil pembagian subnet:

| Subnet | Network Address | Usable Host Range | Broadcast Address |
|--------|------------------|--------------------|---------------------|
| 1 | 192.168.10.0 | 192.168.10.1 – 192.168.10.62 | 192.168.10.63 |
| 2 | 192.168.10.64 | 192.168.10.65 – 192.168.10.126 | 192.168.10.127 |
| 3 | 192.168.10.128 | 192.168.10.129 – 192.168.10.190 | 192.168.10.191 |
| 4 | 192.168.10.192 | 192.168.10.193 – 192.168.10.254 | 192.168.10.255 |

### 2.2 Persiapan Virtual Machine

- Menyiapkan 2 buah VM (Ubuntu Server) menggunakan aplikasi virtualisasi (VirtualBox/VMware).
- Menempatkan kedua VM pada jaringan yang sama secara fisik (misalnya menggunakan mode Host-Only atau Internal Network), namun akan dikonfigurasi pada subnet logis yang berbeda.

### 2.3 Konfigurasi Static IP VM 1 (Subnet 1)

Mengarahkan VM 1 ke dalam rentang alamat Subnet 1 (`192.168.10.0/26`).

Membuka file konfigurasi Netplan:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Menyesuaikan konfigurasi file seperti berikut:

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses:
        - 192.168.10.10/26
      nameservers:
        addresses:
          - 8.8.8.8
```

Menerapkan konfigurasi dan memverifikasi alamat IP:

```bash
sudo netplan apply
ip a
```

**Hasil**: Alamat IP interface `enp0s3` pada VM 1 berhasil terkonfigurasi sebagai `192.168.10.10/26`, berada pada rentang Subnet 1.

### 2.4 Konfigurasi Static IP VM 2 (Subnet 2)

Mengarahkan VM 2 ke dalam rentang alamat Subnet 2 (`192.168.10.64/26`).

Membuka file konfigurasi Netplan pada VM 2:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Menyesuaikan konfigurasi file:

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses:
        - 192.168.10.70/26
      nameservers:
        addresses:
          - 8.8.8.8
```

Menerapkan konfigurasi dan memverifikasi alamat IP:

```bash
sudo netplan apply
ip a
```

**Hasil**: Alamat IP interface `enp0s3` pada VM 2 berhasil terkonfigurasi sebagai `192.168.10.70/26`, berada pada rentang Subnet 2.

### 2.5 Pengujian Konektivitas Antar Subnet

Melakukan pengujian ping dari VM 1 menuju VM 2 untuk menganalisis perilaku komunikasi antar subnet yang berbeda.

Perintah yang dijalankan pada VM 1:

```bash
ping 192.168.10.70
```

**Hasil**: Paket *request time out* / *Destination Host Unreachable*. Komunikasi gagal karena kedua VM berada pada subnet logis yang berbeda (Subnet 1 dan Subnet 2), sehingga secara default tidak dapat saling terhubung tanpa adanya perangkat routing (Layer 3) di antara keduanya.

## 3. Kesimpulan

Praktikum Lab 1: IP Addressing & Subnetting berhasil diselesaikan. Berdasarkan hasil pengujian:

- Perhitungan subnetting manual dari `/24` menjadi 4 subnet `/26` berhasil dilakukan dengan benar, menghasilkan network address, broadcast address, dan usable host range yang sesuai teori.
- Konfigurasi static IP pada kedua VM berhasil diterapkan sesuai hasil perhitungan subnetting.
- Host yang berada pada subnet berbeda terbukti tidak dapat saling berkomunikasi secara langsung, sehingga menegaskan pentingnya fungsi routing/router sebagai penghubung antar subnet, yang akan dibahas lebih lanjut pada lab berikutnya (Routing Dasar).
- Ditemukan bahwa nama file konfigurasi Netplan dapat berbeda-beda tergantung metode instalasi (misalnya 50-cloud-init.yaml yang di-generate otomatis oleh cloud-init, atau 00-installer-config.yaml dari installer versi lama). Oleh karena itu, praktik yang benar adalah memeriksa file yang aktif terlebih dahulu menggunakan `ls /etc/netplan/` sebelum melakukan konfigurasi, bukan mengasumsikan nama file secara langsung.

# Lab 2: Konfigurasi Network di Linux

## 1. Tujuan Praktikum

- Memahami perbedaan konfigurasi network sementara (temporary) dan permanen (persistent) di Linux.
- Menggunakan `ip addr` untuk melihat dan mengubah IP secara sementara.
- Mengidentifikasi apakah server dikelola oleh `NetworkManager` atau `Netplan`/`systemd-networkd`.
- Mengonfigurasi resolusi hostname manual melalui `/etc/hosts`.
- Memahami mekanisme DNS resolver di Ubuntu modern melalui `systemd-resolved` dan `/etc/resolv.conf`.

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Cek IP Config Aktif

Menampilkan konfigurasi IP yang sedang aktif pada interface:

```bash
ip a
```

**Hasil**: Interface `enp0s3` menunjukkan IP address yang sudah dikonfigurasi sebelumnya melalui Netplan pada Lab 1.

### 2.2 Mengubah IP Secara Sementara dengan `ip` Command

Menambahkan IP address baru secara sementara tanpa mengubah file konfigurasi:

```bash
sudo ip addr add 192.168.10.20/26 dev enp0s3
ip a
```

**Hasil**: IP baru `192.168.10.20/26` berhasil ditambahkan pada interface, berdampingan dengan IP lama (bukan menggantikannya).

Menghapus kembali IP tambahan tersebut:

```bash
sudo ip addr del 192.168.10.20/26 dev enp0s3
```

**Kesimpulan sementara**: Perubahan melalui `ip addr` bersifat sementara dan akan hilang setelah reboot, karena tidak menulis ke file konfigurasi manapun — berbeda dengan Netplan yang bersifat persisten.

### 2.3 Identifikasi Network Manager yang Digunakan

Mengecek status `NetworkManager`:

```bash
systemctl status NetworkManager
```

**Hasil**: `NetworkManager` tidak aktif/tidak ditemukan pada Ubuntu Server. Hal ini menunjukkan bahwa manajemen network pada Ubuntu Server dikelola sepenuhnya oleh **Netplan** dan **systemd-networkd**, berbeda dengan Ubuntu Desktop yang umumnya menggunakan `NetworkManager`.

### 2.4 Konfigurasi Hostname Manual via `/etc/hosts`

Menambahkan mapping IP ke hostname agar dapat saling resolve tanpa DNS server:

```bash
sudo nano /etc/hosts
```

Menambahkan baris berikut:

```
192.168.10.10   server1.lab.local   server1
192.168.10.70   server2.lab.local   server2
```

Menguji resolusi hostname dari VM 1 ke VM 2:

```bash
ping server2
```

**Hasil**: Ping berhasil menggunakan nama host `server2`, membuktikan bahwa resolusi nama berhasil dilakukan secara lokal tanpa memerlukan DNS server eksternal.

### 2.5 Pemeriksaan Konfigurasi DNS Resolver

Memeriksa isi file `/etc/resolv.conf`:

```bash
cat /etc/resolv.conf
```

Memeriksa apakah file tersebut dikelola otomatis oleh sistem:

```bash
readlink -f /etc/resolv.conf
```

**Hasil**: File `/etc/resolv.conf` mengarah (symlink) ke `/run/systemd/resolve/stub-resolv.conf`, menandakan bahwa DNS resolver dikelola secara otomatis oleh `systemd-resolved`. Oleh karena itu, perubahan DNS server yang benar harus dilakukan melalui konfigurasi Netplan (`nameservers`), bukan dengan mengedit file `/etc/resolv.conf` secara langsung.

### 2.6 Verifikasi DNS Resolution

Menguji resolusi domain publik menggunakan DNS server yang dikonfigurasi di Netplan:

```bash
nslookup google.com
dig google.com
```

**Hasil**: Query DNS berhasil dijawab oleh DNS server yang telah dikonfigurasi sebelumnya di file Netplan (`8.8.8.8`), sesuai dengan konfigurasi yang diterapkan.

## 3. Kesimpulan

Praktikum Lab 2: Konfigurasi Network di Linux berhasil diselesaikan. Berdasarkan hasil pengujian:

- Perubahan IP menggunakan perintah `ip addr` bersifat sementara (non-persistent) dan hanya efektif hingga sistem di-reboot, sedangkan konfigurasi permanen harus dilakukan melalui Netplan.
- Ubuntu Server menggunakan Netplan dan `systemd-networkd` sebagai pengelola network utama, bukan `NetworkManager` yang umum digunakan pada Ubuntu Desktop.
- Resolusi hostname dapat dilakukan secara manual dan lokal melalui file `/etc/hosts` tanpa memerlukan DNS server.
- File `/etc/resolv.conf` pada Ubuntu modern dikelola otomatis oleh `systemd-resolved`, sehingga konfigurasi DNS yang benar dan persisten harus dilakukan melalui file Netplan, bukan dengan mengedit `/etc/resolv.conf` secara langsung.

# Lab 3: Routing Dasar

## 1. Tujuan Praktikum

- Memahami konsep dasar routing sebagai penghubung antar subnet yang berbeda.
- Mengonfigurasi satu VM sebagai router dengan dua network interface (dual-homed).
- Mengaktifkan IP forwarding pada kernel Linux agar paket dapat diteruskan antar interface.
- Menambahkan static route pada host agar dapat berkomunikasi melalui router.
- Memverifikasi routing table dan menguji konektivitas antar subnet melalui router.

## 2. Topologi Lab

```
VM1 (Subnet 1)  ---  VM-Router (2 NIC)  ---  VM2 (Subnet 2)
192.168.10.10        enp0s3: 192.168.10.1        192.168.10.70
                      enp0s8: 192.168.10.65
```

## 3. Langkah Kerja dan Hasil Praktikum

### 3.1 Persiapan VM Router (Dual Interface)

Menambahkan network adapter kedua pada VM Router melalui pengaturan virtualisasi (VirtualBox/VMware), sehingga VM Router memiliki dua interface yang masing-masing terhubung ke subnet berbeda.

Memverifikasi kedua interface terdeteksi oleh sistem:

```bash
ip a
```

**Hasil**: Sistem mendeteksi dua interface, yaitu `enp0s3` dan `enp0s8`, masing-masing akan dihubungkan ke Subnet 1 dan Subnet 2.

### 3.2 Konfigurasi IP pada VM Router

Mengedit file konfigurasi Netplan pada VM Router:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Isi konfigurasi:

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses:
        - 192.168.10.1/26
    enp0s8:
      dhcp4: no
      addresses:
        - 192.168.10.65/26
```

Menerapkan konfigurasi:

```bash
sudo netplan apply
ip a
```

**Hasil**: Interface `enp0s3` terkonfigurasi sebagai gateway Subnet 1 (`192.168.10.1`) dan `enp0s8` sebagai gateway Subnet 2 (`192.168.10.65`).

### 3.3 Mengaktifkan IP Forwarding

Memeriksa status IP forwarding pada kernel (default: nonaktif):

```bash
cat /proc/sys/net/ipv4/ip_forward
```

Mengaktifkan IP forwarding secara langsung:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Mengaktifkan IP forwarding secara permanen agar tetap berlaku setelah reboot:

```bash
sudo nano /etc/sysctl.conf
```

Menghapus tanda komentar (`#`) pada baris `net.ipv4.ip_forward=1`, kemudian menerapkan perubahan:

```bash
sudo sysctl -p
```

**Hasil**: Nilai `ip_forward` berhasil diubah dari `0` menjadi `1`, menandakan kernel VM Router sekarang meneruskan paket antar interface, bukan hanya menerima paket yang ditujukan untuk dirinya sendiri.

### 3.4 Menambahkan Static Route pada VM1 dan VM2

Menambahkan static route pada VM1 agar paket menuju Subnet 2 diarahkan melalui VM Router:

```bash
sudo ip route add 192.168.10.64/26 via 192.168.10.1
```

Menambahkan static route pada VM2 agar paket menuju Subnet 1 diarahkan melalui VM Router:

```bash
sudo ip route add 192.168.10.0/26 via 192.168.10.65
```

### 3.5 Verifikasi Routing Table

Memeriksa routing table pada VM1 dan VM2:

```bash
ip route
```

**Hasil**: Routing table pada masing-masing VM menampilkan entri baru berupa route menuju subnet lawan melalui IP interface VM Router yang bersesuaian (`192.168.10.1` untuk VM1, `192.168.10.65` untuk VM2), selain entri `default` bawaan.

### 3.6 Pengujian Konektivitas Antar Subnet

Melakukan ping dari VM1 menuju VM2 melalui VM Router:

```bash
ping 192.168.10.70
```

**Hasil**: Ping berhasil mendapatkan reply. Berbeda dengan hasil pada Lab 1 (tanpa router, komunikasi gagal), pada lab ini komunikasi antar subnet berhasil dilakukan setelah IP forwarding diaktifkan dan static route ditambahkan pada kedua host.

## 4. Kesimpulan

Praktikum Lab 3: Routing Dasar berhasil diselesaikan. Berdasarkan hasil pengujian:

- VM dengan dua network interface dapat difungsikan sebagai router sederhana yang menghubungkan dua subnet berbeda.
- IP forwarding pada kernel Linux wajib diaktifkan (`net.ipv4.ip_forward=1`) agar VM Router dapat meneruskan paket antar interface, karena secara default kernel Linux akan mengabaikan paket yang bukan ditujukan untuk dirinya sendiri.
- Static route pada host tujuan diperlukan agar host mengetahui jalur (gateway) menuju subnet lain yang bukan merupakan jaringan lokalnya.
- Hasil pengujian ping antar subnet yang sebelumnya gagal pada Lab 1 (tanpa router) berhasil dilakukan setelah router, IP forwarding, dan static route dikonfigurasi dengan benar, membuktikan fungsi routing sebagai penghubung logis antar subnet.

# Lab 4: DNS Server Sederhana

## 1. Tujuan Praktikum

- Memahami cara kerja DNS server dari sisi penyedia layanan (server), bukan hanya sebagai pengguna.
- Menginstal dan mengonfigurasi BIND9 sebagai authoritative DNS server untuk domain lokal.
- Membuat zone file dan DNS record tipe A untuk domain `lab.local`.
- Mengarahkan VM client agar menggunakan DNS server lokal untuk resolusi domain.
- Menambahkan record baru dan memverifikasi propagasi perubahan tanpa restart penuh service.

## 2. Topologi Lab

```
VM-DNS-Server (BIND9)          VM-Client
192.168.10.10       <-------   192.168.10.70
```

## 3. Langkah Kerja dan Hasil Praktikum

### 3.1 Instalasi BIND9

```bash
sudo apt update
sudo apt install bind9 bind9utils -y
```

**Hasil**: BIND9 berhasil terinstal sebagai DNS server.

### 3.2 Konfigurasi Zone Domain Lokal

Mendaftarkan zone `lab.local` pada konfigurasi BIND:

```bash
sudo nano /etc/bind/named.conf.local
```

```
zone "lab.local" {
    type master;
    file "/etc/bind/db.lab.local";
};
```

### 3.3 Pembuatan Zone File

Membuat file zone dari template bawaan:

```bash
sudo cp /etc/bind/db.local /etc/bind/db.lab.local
sudo nano /etc/bind/db.lab.local
```

Isi zone file:

```
;
; BIND data file for lab.local
;
$TTL    604800
@       IN      SOA     lab.local. admin.lab.local. (
                              3         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      server.lab.local.
server  IN      A       192.168.10.10
```

**Hasil**: Zone file berisi record `NS` untuk nameserver dan record `A` yang mengarahkan `server.lab.local` ke `192.168.10.10`.

### 3.4 Verifikasi Konfigurasi dan Restart Service

```bash
sudo named-checkzone lab.local /etc/bind/db.lab.local
sudo named-checkconf
sudo systemctl restart bind9
sudo systemctl status bind9
```

**Hasil**: Pemeriksaan `named-checkzone` mengembalikan status `OK`, menandakan syntax zone file valid. Service `bind9` berhasil restart dan berjalan dengan status `active (running)`.

### 3.5 Pengujian DNS Server Secara Lokal

```bash
dig @localhost server.lab.local
```

**Hasil**: Query berhasil dijawab, dengan `ANSWER SECTION` menampilkan `server.lab.local` mengarah ke `192.168.10.10`, sesuai dengan record yang telah didefinisikan.

### 3.6 Konfigurasi DNS pada VM Client

Mengarahkan VM Client untuk menggunakan DNS server lokal melalui Netplan:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

```yaml
      nameservers:
        addresses:
          - 192.168.10.10
```

```bash
sudo netplan apply
```

### 3.7 Pengujian Resolusi dari VM Client

```bash
dig server.lab.local
```

**Hasil**: Query dari VM Client berhasil dijawab oleh DNS server `192.168.10.10`, dengan hasil resolusi yang sesuai (`server.lab.local` → `192.168.10.10`), membuktikan VM Client telah menggunakan DNS server lokal, bukan DNS publik.

### 3.8 Penambahan Record Baru dan Verifikasi Propagasi

Menambahkan record `A` baru untuk `client.lab.local`, serta menaikkan nomor Serial pada SOA record:

```bash
sudo nano /etc/bind/db.lab.local
```

```
;
; BIND data file for lab.local
;
$TTL    604800
@       IN      SOA     lab.local. admin.lab.local. (
                              4         ; Serial (naik dari 3 ke 4)
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      server.lab.local.
server  IN      A       192.168.10.10
client  IN      A       192.168.10.70
```

Menerapkan perubahan tanpa restart penuh:

```bash
sudo systemctl reload bind9
```

Menguji record baru dari VM Client:

```bash
dig client.lab.local
```

**Hasil**: Record baru `client.lab.local` berhasil di-resolve menjadi `192.168.10.70`, membuktikan bahwa perubahan zone file berhasil diterapkan melalui `reload` tanpa perlu me-restart service BIND9 secara penuh.

## 4. Kesimpulan

Praktikum Lab 4: DNS Server Sederhana berhasil diselesaikan. Berdasarkan hasil pengujian:

- BIND9 berhasil dikonfigurasi sebagai authoritative DNS server untuk domain lokal `lab.local`.
- Zone file dengan record `SOA`, `NS`, dan `A` berhasil dibuat dan divalidasi menggunakan `named-checkzone` sebelum diterapkan.
- VM Client berhasil diarahkan untuk menggunakan DNS server lokal, dan berhasil melakukan resolusi domain lokal yang tidak tersedia di DNS publik manapun.
- Penambahan record baru pada zone file dapat diterapkan cukup dengan `systemctl reload` (bukan `restart`), asalkan nomor Serial pada SOA record dinaikkan agar BIND mengenali adanya perubahan data zone.

# Lab 5: DHCP Server Sederhana

## 1. Tujuan Praktikum

- Memahami cara kerja DHCP server dalam memberikan alamat IP secara otomatis kepada client.
- Menginstal dan mengonfigurasi ISC DHCP Server pada satu VM.
- Mengonfigurasi range IP, subnet, gateway, dan DNS yang akan didistribusikan ke client.
- Mengubah konfigurasi client dari static IP menjadi DHCP client, dan memverifikasi IP yang diperoleh secara otomatis.
- Memeriksa lease log untuk melihat riwayat alokasi IP kepada client.

## 2. Topologi Lab

```
VM-DHCP-Server                VM-Client
192.168.10.10   <-- DHCP -->  (IP diperoleh otomatis)
```

## 3. Langkah Kerja dan Hasil Praktikum

### 3.1 Instalasi ISC DHCP Server

```bash
sudo apt update
sudo apt install isc-dhcp-server -y
```

**Hasil**: ISC DHCP Server berhasil terinstal pada VM-DHCP-Server.

### 3.2 Penentuan Interface DHCP

Menentukan interface yang akan digunakan untuk melayani permintaan DHCP:

```bash
sudo nano /etc/default/isc-dhcp-server
```

```
INTERFACESv4="enp0s3"
```

### 3.3 Konfigurasi Range IP, Subnet, Gateway, dan DNS

```bash
sudo nano /etc/dhcp/dhcpd.conf
```

```
subnet 192.168.10.0 netmask 255.255.255.192 {
  range 192.168.10.30 192.168.10.40;
  option routers 192.168.10.1;
  option subnet-mask 255.255.255.192;
  option domain-name-servers 192.168.10.10;
  option domain-name "lab.local";
  default-lease-time 600;
  max-lease-time 7200;
}
```

Penjelasan konfigurasi:

- `range` — rentang IP yang dapat dipinjamkan kepada client (`192.168.10.30` – `192.168.10.40`).
- `option routers` — gateway yang diberikan kepada client (`192.168.10.1`).
- `option domain-name-servers` — DNS server yang diberikan kepada client, memanfaatkan DNS server dari Lab 4 (`192.168.10.10`).
- `default-lease-time` / `max-lease-time` — durasi peminjaman IP sebelum client harus melakukan renewal.

### 3.4 Restart dan Verifikasi Status Service

```bash
sudo systemctl restart isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

**Hasil**: Service `isc-dhcp-server` berhasil berjalan dengan status `active (running)`, menandakan konfigurasi subnet dan netmask telah sesuai dengan interface DHCP server.

### 3.5 Konfigurasi VM Client sebagai DHCP Client

Mengubah konfigurasi Netplan pada VM Client dari static IP menjadi DHCP:

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: yes
```

```bash
sudo netplan apply
```

### 3.6 Verifikasi IP yang Diperoleh Secara Otomatis

```bash
ip a
```

**Hasil**: Interface `enp0s3` pada VM Client berhasil memperoleh IP secara otomatis dari rentang yang telah dikonfigurasi (`192.168.10.30` – `192.168.10.40`), menggantikan static IP yang sebelumnya digunakan.

Memverifikasi gateway dan DNS yang diterima:

```bash
ip route
resolvectl status
```

**Hasil**: Gateway dan DNS server yang diterima VM Client sesuai dengan konfigurasi `option routers` dan `option domain-name-servers` pada `dhcpd.conf`.

### 3.7 Pemeriksaan Lease Log

```bash
cat /var/lib/dhcp/dhcpd.leases
```

**Hasil**: File lease menampilkan entri IP yang telah diberikan kepada VM Client, mencakup informasi `starts`, `ends`, `binding state active`, dan `client-hostname`, sesuai dengan IP yang diverifikasi pada langkah sebelumnya.

### 3.8 Live Monitoring Lease (Bonus)

```bash
sudo journalctl -u isc-dhcp-server -f
```

**Hasil**: Log DHCP server berhasil menangkap request secara real-time saat VM Client melakukan permintaan ulang IP (`netplan apply`), menampilkan proses DHCP handshake (DISCOVER, OFFER, REQUEST, ACK).

## 4. Kesimpulan

Praktikum Lab 5: DHCP Server Sederhana berhasil diselesaikan. Berdasarkan hasil pengujian:

- ISC DHCP Server berhasil dikonfigurasi untuk mendistribusikan IP secara otomatis dalam rentang yang telah ditentukan, lengkap dengan gateway dan DNS server.
- VM Client yang dikonfigurasi sebagai DHCP client berhasil memperoleh IP, gateway, dan DNS secara otomatis, tanpa perlu konfigurasi manual seperti pada lab-lab sebelumnya.
- Lease log pada DHCP server berhasil mencatat riwayat alokasi IP kepada client, membuktikan bahwa DHCP server dapat digunakan untuk melacak alokasi IP dalam jaringan.
- DHCP server dapat diintegrasikan dengan DNS server internal (hasil Lab 4), sehingga client secara otomatis menerima konfigurasi DNS yang konsisten dengan infrastruktur lab.

# Lab 6: Firewall & Port Filtering

## 1. Tujuan Praktikum

- Mengonfigurasi UFW (Uncomplicated Firewall) pada satu VM yang berperan sebagai gateway.
- Menerapkan kebijakan default deny incoming dan hanya mengizinkan port tertentu (SSH & HTTP).
- Menguji perbedaan akses antara port yang dibuka dan port yang diblokir dari VM lain.
- Mengonfigurasi NAT (Masquerade) agar VM di jaringan lokal (LAN) dapat mengakses internet melalui gateway.
- Memverifikasi traffic NAT menggunakan counter pada iptables.

## 2. Topologi Lab

```
Internet
   |
   | (NAT Adapter, IP otomatis dari VirtualBox)
   v
enp0s8 (WAN) -- VM-Gateway -- enp0s3 (LAN): 192.168.10.1/26
                                    |
                              VM-Client: 192.168.10.70
```

## 3. Langkah Kerja dan Hasil Praktikum

### 3.1 Konfigurasi Adapter WAN

Menambahkan network adapter kedua pada VM-Gateway dengan mode NAT (bukan Internal Network/Host-Only), memberikan akses internet langsung ke VM.

```bash
ip a
```

**Hasil**: Interface baru (`enp0s8`) terdeteksi dan memperoleh IP secara otomatis dari DHCP internal virtualisasi.

### 3.2 Instalasi UFW dan Kebijakan Default

```bash
sudo apt update
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

**Hasil**: Kebijakan default diterapkan — seluruh traffic masuk ditolak, seluruh traffic keluar diizinkan.

### 3.3 Mengizinkan Port SSH dan HTTP

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
```

**Hasil**: Hanya port 22 (SSH) dan 80 (HTTP) yang diizinkan menerima koneksi masuk, port lainnya mengikuti kebijakan default (deny).

### 3.4 Mengaktifkan IP Forwarding

Mengubah kebijakan forward pada UFW:

```bash
sudo nano /etc/default/ufw
```

```
DEFAULT_FORWARD_POLICY="ACCEPT"
```

Mengaktifkan IP forwarding pada kernel:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

**Hasil**: VM-Gateway dikonfigurasi untuk meneruskan traffic antar interface, diperlukan agar NAT dapat berfungsi.

### 3.5 Konfigurasi NAT (Masquerade)

```bash
sudo nano /etc/ufw/before.rules
```

Menambahkan blok berikut di bagian paling atas file (sebelum baris `*filter`):

```
# NAT table rules
*nat
:POSTROUTING ACCEPT [0:0]
-A POSTROUTING -s 192.168.10.0/26 -o enp0s8 -j MASQUERADE
COMMIT
```

**Hasil**: Rule NAT berhasil ditambahkan, mengarahkan seluruh traffic dari subnet LAN (`192.168.10.0/26`) untuk di-masquerade menggunakan IP interface WAN (`enp0s8`) saat keluar ke internet.

### 3.6 Mengaktifkan UFW dan Verifikasi Status

```bash
sudo ufw enable
sudo ufw status verbose
```

**Hasil**: UFW aktif dengan status menunjukkan port 22/tcp dan 80/tcp berstatus `ALLOW`, sementara port lainnya mengikuti kebijakan default `DENY`.

### 3.7 Pengujian Port dari VM-Client

Menguji port yang diizinkan (SSH):

```bash
nc -zv 192.168.10.1 22
```

**Hasil**: Koneksi berhasil (`succeeded`/`open`).

Menguji port yang tidak diizinkan (misal port 23):

```bash
nc -zv 192.168.10.1 23
```

**Hasil**: Koneksi gagal (`timeout`/`refused`), membuktikan firewall berhasil memblokir port yang tidak didaftarkan secara eksplisit.

### 3.8 Pengujian NAT dari VM-Client

```bash
ping 8.8.8.8
```

**Hasil**: Ping berhasil mendapatkan reply, membuktikan VM-Client — yang tidak memiliki akses internet langsung — berhasil mengakses internet melalui NAT yang dikonfigurasi di VM-Gateway.

### 3.9 Verifikasi Counter NAT

```bash
sudo iptables -t nat -L POSTROUTING -n -v
```

**Hasil**: Kolom `pkts` dan `bytes` pada baris `MASQUERADE` menunjukkan peningkatan jumlah paket setelah pengujian ping dari VM-Client, membuktikan traffic benar-benar melewati rule NAT yang dikonfigurasi.

## 4. Kesimpulan

Praktikum Lab 6: Firewall & Port Filtering berhasil diselesaikan. Berdasarkan hasil pengujian:

- UFW berhasil dikonfigurasi dengan kebijakan default deny incoming, dan hanya mengizinkan port SSH (22) dan HTTP (80), sehingga memperkecil attack surface pada VM-Gateway.
- Pengujian port membuktikan bahwa port yang tidak didaftarkan secara eksplisit (misal port 23) berhasil diblokir, sementara port yang diizinkan tetap dapat diakses.
- Konfigurasi NAT (Masquerade) berhasil memungkinkan VM di jaringan lokal (LAN) mengakses internet melalui satu titik keluar (Gateway), tanpa VM tersebut memiliki akses internet langsung.
- IP forwarding dan NAT saling melengkapi: IP forwarding memastikan paket diteruskan antar interface, sementara Masquerade memastikan paket tersebut "menyamar" menggunakan IP WAN yang valid di internet.

# Lab 7: Network Troubleshooting

## 1. Tujuan Praktikum

- Melakukan simulasi berbagai skenario gangguan jaringan secara sengaja untuk melatih kemampuan diagnosa.
- Menggunakan tools diagnostik standar (`ip route`, `traceroute`, `resolvectl`, `nc`) untuk mengidentifikasi akar masalah konektivitas.
- Membedakan jenis masalah jaringan berdasarkan gejala: masalah routing, DNS, interface, dan port filtering.
- Mendokumentasikan alur troubleshooting dari gejala hingga solusi (Problem → Diagnosa → Root Cause → Solusi).

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Skenario 1: Kesalahan Default Gateway

**Simulasi masalah:**

```bash
sudo ip route del default
sudo ip route add default via 192.168.10.99
```

**Pengujian:**

```bash
ping 8.8.8.8
```

**Gejala**: Ping gagal/timeout ke seluruh tujuan di luar subnet lokal.

**Diagnosa:**

```bash
ip route
traceroute 8.8.8.8
```

**Root Cause**: Default gateway diarahkan ke IP (`192.168.10.99`) yang tidak valid/tidak ada pada jaringan, sehingga paket tidak dapat diteruskan keluar dari subnet lokal.

**Solusi:**

```bash
sudo ip route del default
sudo ip route add default via 192.168.10.1
```

### 2.2 Skenario 2: DNS Tidak Valid

**Simulasi masalah:**

```bash
sudo resolvectl dns enp0s3 1.1.1.1.1.1
```

**Pengujian:**

```bash
ping google.com
ping 8.8.8.8
```

**Gejala**: Ping menggunakan nama domain (`google.com`) gagal, namun ping menggunakan IP langsung (`8.8.8.8`) tetap berhasil.

**Diagnosa:**

```bash
resolvectl status
nslookup google.com
```

**Root Cause**: DNS server yang dikonfigurasi tidak valid, sehingga proses resolusi nama domain ke IP gagal dilakukan — meskipun jalur konektivitas jaringan itu sendiri masih normal (dibuktikan dengan keberhasilan ping ke IP).

**Solusi:**

```bash
sudo resolvectl dns enp0s3 192.168.10.10
```

### 2.3 Skenario 3: Network Interface Down

**Simulasi masalah:**

```bash
sudo ip link set enp0s3 down
```

**Pengujian:**

```bash
ping 192.168.10.1
```

**Gejala**: Ping gagal total, bahkan ke default gateway sekalipun (berbeda dengan Skenario 1 & 2 yang masih bisa menjangkau sebagian jaringan).

**Diagnosa:**

```bash
ip link show enp0s3
```

**Root Cause**: Interface jaringan dalam status `DOWN`, sehingga tidak ada traffic yang dapat dikirim maupun diterima sama sekali melalui interface tersebut.

**Solusi:**

```bash
sudo ip link set enp0s3 up
```

### 2.4 Skenario 4: Port Service Diblokir Firewall

**Pengujian (menggunakan konfigurasi firewall dari Lab 6):**

```bash
nc -zv 192.168.10.1 23
telnet 192.168.10.1 23
```

**Gejala**: Koneksi ke port 23 gagal/timeout, sementara ping ke IP yang sama (`192.168.10.1`) tetap berhasil.

**Diagnosa**: Karena ping (ICMP) berhasil namun koneksi ke port tertentu gagal, masalah dipastikan bersifat **spesifik pada port/service** (firewall filtering), bukan masalah konektivitas jaringan secara keseluruhan.

**Root Cause**: Port 23 tidak termasuk dalam daftar port yang diizinkan pada konfigurasi UFW (hanya port 22 dan 80 yang diizinkan sesuai Lab 6), sehingga request ditolak oleh firewall.

**Solusi**: Bukan merupakan kesalahan konfigurasi — ini adalah perilaku yang diharapkan dari firewall. Solusi hanya diperlukan jika port tersebut memang perlu dibuka, dengan menambahkan rule `sudo ufw allow 23/tcp`.

## 3. Kesimpulan

Praktikum Lab 7: Network Troubleshooting berhasil diselesaikan. Berdasarkan hasil simulasi:

- Setiap jenis gangguan jaringan (routing, DNS, interface, port filtering) memiliki gejala yang berbeda dan dapat dibedakan melalui pengujian bertahap, bukan hanya dengan satu jenis pengujian saja.
- Perbandingan hasil ping ke IP versus ping ke domain menjadi indikator penting untuk membedakan masalah DNS dari masalah konektivitas jaringan secara umum.
- Perbandingan hasil ping (ICMP) versus koneksi ke port tertentu menjadi indikator penting untuk membedakan masalah firewall/port filtering dari masalah jaringan secara keseluruhan.
- Pendekatan troubleshooting yang sistematis — memeriksa layer demi layer (interface → routing → DNS → port/service) — mempercepat proses identifikasi akar masalah dibandingkan menebak solusi secara acak.

# Lab 8: Packet Capture & Analysis

## 1. Tujuan Praktikum

- Melakukan capture traffic jaringan secara langsung menggunakan `tcpdump`.
- Menganalisis proses TCP 3-way handshake (SYN, SYN-ACK, ACK) pada koneksi SSH.
- Menyimpan hasil capture ke dalam file `.pcap` untuk analisis lebih lanjut.
- Melakukan filtering traffic berdasarkan IP dan port tertentu dari file capture.
- Memahami struktur dasar paket data yang melewati jaringan, tidak hanya bergantung pada hasil akhir tools seperti `ping`.

## 2. Langkah Kerja dan Hasil Praktikum

### 2.1 Instalasi tcpdump

```bash
sudo apt update
sudo apt install tcpdump -y
```

**Hasil**: `tcpdump` berhasil terinstal dan siap digunakan untuk melakukan capture traffic.

### 2.2 Capture Traffic ICMP (Ping)

Menjalankan capture pada VM-Client:

```bash
sudo tcpdump -i enp0s3 icmp -v
```

Melakukan ping dari VM lain menuju VM-Client:

```bash
ping 192.168.10.70
```

**Hasil**: `tcpdump` menampilkan log secara real-time untuk setiap paket `ICMP echo request` dan `ICMP echo reply`, menunjukkan proses request-reply ping secara langsung pada level paket.

### 2.3 Capture dan Analisis TCP 3-Way Handshake

Menjalankan capture khusus pada port SSH:

```bash
sudo tcpdump -i enp0s3 port 22 -v
```

Melakukan koneksi SSH dari device lain:

```bash
ssh sysadmin@192.168.10.70
```

**Hasil**: Tiga paket pertama pada hasil capture menunjukkan proses TCP 3-way handshake:

1. `Flags [S]` — paket SYN, inisiasi koneksi dari client.
2. `Flags [S.]` — paket SYN-ACK, balasan dari server.
3. `Flags [.]` — paket ACK, konfirmasi dari client.

Proses ini merupakan mekanisme dasar yang terjadi pada setiap koneksi berbasis TCP, termasuk HTTP, SSH, dan koneksi database.

### 2.4 Menyimpan Hasil Capture ke File

```bash
sudo tcpdump -i enp0s3 -w capture.pcap
```

**Hasil**: Traffic jaringan selama sesi capture berhasil disimpan ke dalam file `capture.pcap` untuk keperluan analisis lebih lanjut.

### 2.5 Filtering Hasil Capture Berdasarkan IP dan Port

Memfilter berdasarkan IP tertentu:

```bash
sudo tcpdump -r capture.pcap host 192.168.10.10
```

Memfilter berdasarkan port tertentu:

```bash
sudo tcpdump -r capture.pcap port 80
```

**Hasil**: File `.pcap` berhasil difilter, hanya menampilkan traffic yang relevan dengan IP atau port yang ditentukan, mempermudah analisis pada capture berukuran besar.

### 2.6 Analisis Visual dengan Wireshark (Opsional)

```bash
sudo apt install wireshark -y
wireshark capture.pcap
```

**Hasil**: File capture berhasil dibuka dan dianalisis secara visual melalui antarmuka Wireshark, memudahkan inspeksi detail tiap layer paket (Ethernet, IP, TCP, dan payload) dibandingkan pembacaan melalui terminal.

## 3. Kesimpulan

Praktikum Lab 8: Packet Capture & Analysis berhasil diselesaikan. Berdasarkan hasil pengujian:

- `tcpdump` berhasil digunakan untuk melakukan capture traffic secara real-time, baik untuk protokol ICMP maupun TCP.
- Proses TCP 3-way handshake (SYN, SYN-ACK, ACK) berhasil diamati secara langsung pada koneksi SSH, memberikan pemahaman konkret mengenai mekanisme pembentukan koneksi TCP.
- Hasil capture dapat disimpan dalam format `.pcap` dan difilter berdasarkan kriteria tertentu (IP/port), sehingga analisis dapat difokuskan pada traffic yang relevan.
- Kemampuan membaca traffic pada level paket memberikan pemahaman yang lebih mendalam dibandingkan hanya mengandalkan hasil akhir dari tools seperti `ping` atau `curl`, dan menjadi dasar penting untuk troubleshooting jaringan tingkat lanjut.
