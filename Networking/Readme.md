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
