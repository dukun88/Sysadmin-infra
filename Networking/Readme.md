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
