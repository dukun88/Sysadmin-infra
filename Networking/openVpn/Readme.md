# Bonus Lab: OpenVPN Gateway ke Private Network (Simulasi Lokal)

> Lab tambahan di luar urutan Lab 1-8, mensimulasikan pattern akses aman ke private subnet menggunakan OpenVPN — umum digunakan di lingkungan cloud (AWS/Azure/GCP) untuk mengamankan resource internal.

## 1. Tujuan Praktikum

- Mensimulasikan arsitektur *bastion/VPN gateway* untuk mengakses server private yang terisolasi dari jaringan luar.
- Mengonfigurasi VM dengan dua interface (public-facing dan internal network) sebagai VPN gateway.
- Menginstal dan mengonfigurasi OpenVPN Server menggunakan automated installer script.
- Membuktikan isolasi network sebelum dan sesudah VPN diaktifkan.
- Memverifikasi routing traffic melalui VPN tunnel (`tun0`) menuju private network.

## 2. Topologi Lab

```
Laptop (Client)
    |
    | VPN tunnel (port 1194)
    v
VM-VPN-Server (2 NIC)
    enp0s3 (Host-Only)    : 192.168.56.10   <- diakses laptop
    enp0s8 (Internal Net) : 10.10.10.1      <- ke private network
    |
    | Internal Network (terisolasi dari laptop)
    v
VM-Private-Server
    enp0s3 (Internal Net) : 10.10.10.20
```

## 3. Langkah Kerja dan Hasil Praktikum

### 3.1 Konfigurasi Network Adapter

Menambahkan dua network adapter pada VM-VPN-Server melalui pengaturan virtualisasi:

- Adapter 1: Host-Only Network (agar dapat diakses langsung dari laptop)
- Adapter 2: Internal Network dengan nama `privatenet` (jaringan terisolasi)

Menambahkan satu network adapter pada VM-Private-Server:

- Adapter 1: Internal Network dengan nama yang sama, `privatenet`

### 3.2 Konfigurasi IP VM-VPN-Server

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses:
        - 192.168.56.10/24
    enp0s8:
      dhcp4: no
      addresses:
        - 10.10.10.1/24
```

```bash
sudo netplan apply
```

### 3.3 Konfigurasi IP VM-Private-Server

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: no
      addresses:
        - 10.10.10.20/24
      routes:
        - to: default
          via: 10.10.10.1
```

```bash
sudo netplan apply
```

### 3.4 Verifikasi Isolasi Network (Sebelum VPN Aktif)

Melakukan ping dari laptop langsung ke VM-Private-Server:

```bash
ping 10.10.10.20
```

**Hasil**: Ping gagal/timeout. Hal ini membuktikan bahwa VM-Private-Server berada pada Internal Network yang sepenuhnya terisolasi dan tidak dapat dijangkau langsung dari luar tanpa melalui VPN gateway.

### 3.5 Instalasi OpenVPN Server

Menginstal OpenVPN menggunakan automated installer script:

```bash
sudo apt update
curl -O https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
chmod +x openvpn-install.sh
sudo ./openvpn-install.sh
```

Konfigurasi yang dipilih pada wizard instalasi:

- IP Address: `192.168.56.10` (interface Host-Only)
- Port: `1194` (default)
- Protocol: UDP
- Client name: `laptop-client`

**Hasil**: Instalasi berhasil, menghasilkan file konfigurasi client `laptop-client.ovpn`.

### 3.6 Verifikasi IP Forwarding

```bash
cat /proc/sys/net/ipv4/ip_forward
```

**Hasil**: Nilai bernilai `1`, menandakan VM-VPN-Server telah dikonfigurasi untuk meneruskan traffic dari VPN tunnel menuju Internal Network.

### 3.7 Instalasi OpenVPN Client & Koneksi

Mengambil file konfigurasi client ke laptop:

```bash
scp sysadmin@192.168.56.10:~/laptop-client.ovpn .
```

Menghubungkan ke VPN server:

```bash
sudo openvpn --config laptop-client.ovpn
```

**Hasil**: Koneksi VPN berhasil dibangun, ditandai dengan log `Initialization Sequence Completed`.

### 3.8 Verifikasi Akses ke Private Server (Setelah VPN Aktif)

```bash
ping 10.10.10.20
```

**Hasil**: Ping berhasil mendapatkan reply. Berbeda dengan pengujian pada langkah 3.4, akses ke VM-Private-Server berhasil dilakukan setelah tunnel VPN aktif.

### 3.9 Verifikasi Routing Table

```bash
ip route
```

**Hasil**: Ditemukan route baru menuju `10.10.10.0/24` melalui interface `tun0`, membuktikan bahwa traffic menuju private network dilewatkan melalui VPN tunnel, bukan melalui jalur lain.

## 4. Kesimpulan

Bonus Lab: OpenVPN Gateway ke Private Network berhasil diselesaikan. Berdasarkan hasil pengujian:

- Arsitektur VPN gateway berhasil mengisolasi server private dari akses langsung, dan hanya dapat diakses melalui satu pintu masuk terkontrol (VPN server).
- IP forwarding pada VPN server berperan penting untuk meneruskan traffic dari tunnel VPN menuju internal network, konsep yang sama dengan yang dipelajari pada Lab 3 (Routing Dasar).
- Pattern ini merepresentasikan praktik umum di lingkungan cloud (AWS/Azure/GCP), di mana resource sensitif ditempatkan pada private subnet dan hanya dapat diakses melalui VPN/bastion host, sehingga memperkecil attack surface.

---

## 5. Automasi dengan Ansible (Opsional)

Beberapa bagian dari lab ini bersifat repetitif dan cocok diotomasi, terutama jika topologi ini perlu direplikasi ke banyak environment (misal beberapa client baru, atau rebuild lab dari nol). Berikut breakdown mana yang **layak** diotomasi dan mana yang **sebaiknya tetap manual**.

### Bagian yang Cocok Diotomasi

| Task | Alasan |
|---|---|
| Konfigurasi Netplan (IP VPN Server & Private Server) | Konfigurasi berulang, rawan typo kalau manual |
| Instalasi OpenVPN Server | Task idempotent, bisa dijalankan ulang tanpa efek samping |
| Verifikasi `ip_forward` & set permanen | Konsisten di semua environment |
| Generate client config baru (`.ovpn`) untuk user tambahan | Task rutin kalau lab dipakai banyak orang |

### Bagian yang Sebaiknya Tetap Manual

- **Verifikasi isolasi network (ping test)** — ini murni pengujian/observasi, bukan konfigurasi state, jadi kurang relevan dimasukkan ke playbook.
- **Koneksi VPN dari client (laptop)** — ini dilakukan di sisi client kamu sendiri, di luar cakupan managed nodes Ansible.

### Contoh Playbook (Fleksibel — Bisa Disesuaikan Jumlah/Nama Host)

Struktur folder:

```
ansible-vpn-lab/
├── inventory.ini
├── setup-vpn-gateway.yml
├── setup-private-server.yml
└── templates/
    ├── vpn-server-netplan.j2
    └── private-server-netplan.j2
```

**`inventory.ini`** — gunakan group terpisah agar mudah menambah host baru tanpa mengubah playbook:

```ini
[vpn_gateway]
vpn-server ansible_host=192.168.56.10 ansible_user=sysadmin

[private_servers]
private-server-1 ansible_host=10.10.10.20 ansible_user=sysadmin
# tambahkan private-server-2, private-server-3, dst di sini
# tanpa perlu mengubah playbook
```

**`templates/vpn-server-netplan.j2`** — pakai variable, bukan hardcode, biar reusable:

```yaml
network:
  version: 2
  ethernets:
    {{ public_interface }}:
      dhcp4: no
      addresses:
        - {{ public_ip }}
    {{ internal_interface }}:
      dhcp4: no
      addresses:
        - {{ internal_ip }}
```

**`setup-vpn-gateway.yml`**:

```yaml
---
- name: Configure VPN Gateway
  hosts: vpn_gateway
  become: yes
  vars:
    public_interface: enp0s3
    internal_interface: enp0s8
    public_ip: "192.168.56.10/24"
    internal_ip: "10.10.10.1/24"

  tasks:
    - name: Deploy netplan configuration
      template:
        src: templates/vpn-server-netplan.j2
        dest: /etc/netplan/50-cloud-init.yaml
      notify: apply netplan

    - name: Enable IP forwarding (runtime)
      sysctl:
        name: net.ipv4.ip_forward
        value: '1'
        sysctl_set: yes
        state: present
        reload: yes

    - name: Enable IP forwarding permanently
      lineinfile:
        path: /etc/sysctl.conf
        regexp: '^#?net.ipv4.ip_forward='
        line: 'net.ipv4.ip_forward=1'

    - name: Check if OpenVPN is already installed
      stat:
        path: /etc/openvpn/server.conf
      register: openvpn_installed

    - name: Download OpenVPN install script
      get_url:
        url: https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
        dest: /tmp/openvpn-install.sh
        mode: '0755'
      when: not openvpn_installed.stat.exists

    # Catatan: openvpn-install.sh bersifat interaktif (wizard),
    # sehingga untuk otomasi penuh perlu dijalankan dengan
    # environment variable non-interaktif (AUTO_INSTALL=y),
    # yang didukung oleh script tersebut.
    - name: Run OpenVPN install script (non-interactive)
      shell: AUTO_INSTALL=y /tmp/openvpn-install.sh
      when: not openvpn_installed.stat.exists

  handlers:
    - name: apply netplan
      command: netplan apply
```

**`setup-private-server.yml`** — playbook terpisah, bisa dijalankan ke banyak private server sekaligus:

```yaml
---
- name: Configure Private Server(s)
  hosts: private_servers
  become: yes
  vars:
    interface: enp0s3
    gateway_ip: "10.10.10.1"

  tasks:
    - name: Deploy netplan configuration
      template:
        src: templates/private-server-netplan.j2
        dest: /etc/netplan/50-cloud-init.yaml
      notify: apply netplan

  handlers:
    - name: apply netplan
      command: netplan apply
```

Menjalankan kedua playbook:

```bash
ansible-playbook -i inventory.ini setup-vpn-gateway.yml
ansible-playbook -i inventory.ini setup-private-server.yml
```

### Kenapa Struktur Ini Fleksibel

- Menambah private server baru cukup tambah baris di `inventory.ini`, tanpa menyentuh playbook.
- IP dan interface name di-parameterize lewat `vars`, sehingga template bisa dipakai ulang untuk topologi lab lain.
- Pengecekan `stat` sebelum install OpenVPN membuat playbook **idempotent** — aman dijalankan berkali-kali tanpa install ulang atau generate certificate baru yang tidak perlu.

> **Catatan**: Playbook di atas belum termasuk task generate `.ovpn` client config per user, karena proses tersebut sebaiknya tetap semi-manual (melibatkan distribusi certificate yang bersifat sensitif) — di luar cakupan otomasi konfigurasi dasar pada lab ini.
