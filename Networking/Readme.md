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

