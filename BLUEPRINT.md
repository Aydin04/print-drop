# 📐 BLUEPRINT ARSITEKTUR & SISTEM: AYDIN PRINT STUDIO

Dokumen Blueprint ini merangkum rancangan arsitektur, alur data, model perhitungan HPP/Laba, integrasi hardware, dan keamanan sistem **Aydin Print** yang mengadaptasi engine dari `Aydin04/auto-print`.

---

## 🏗️ 1. Topologi Jaringan & Hardware

```text
  [ HP PELANGGAN ]
         │ (Koneksi ke Wi-Fi 5GHz: "AYDIN-PRINT")
         ▼
  [ Wi-Fi Card PC: Qualcomm Atheros QCA9377 ]
         │ (Mode AP / Hotspot 5GHz Channel 36, Subnet 10.42.0.0/24)
         ▼
  [ PC KASIR (Linux Aurora) ]
         ├─► [ Backend Server Flask ] (Port 5000)
         ├─► [ Layout Engine & HPP Calculator ]
         ├─► [ Penyimpanan File: ~/Hasil_Print/ ]
         └─► [ Printer Fisik (Brother DCP-T720DW / Epson L800) ]
```

### Isolasi Jaringan:
1. **Wi-Fi Hotspot Toko (`AYDIN-PRINT`)**: Murni jaringan transfer lokal (*Isolated Local Network*). Tidak menyedot kuota internet modem/toko.
2. **Koneksi Kasir**: PC Kasir tetap bisa menggunakan koneksi internet terpisah (via LAN kabel / USB tethering) tanpa terhubung ke jaringan pelanggan.

---

## 🔄 2. Alur Kerja (End-to-End Workflow)

### A. Alur Pelanggan (Client Side)
1. **Scan QR Code**: Pelanggan scan QR Code di meja kasir $\rightarrow$ Langsung membuka `http://10.42.0.1:5000`.
2. **Pilih Mode**:
   - **Mode Dokumen**: Upload PDF/Word/Excel/Gambar $\rightarrow$ Pilih Kertas $\rightarrow$ B/W atau Warna $\rightarrow$ Duplex/1-Sisi $\rightarrow$ Rangkap $\rightarrow$ Jilid/Laminasi.
   - **Mode Foto Studio**: Upload Foto $\rightarrow$ Interactive Canvas Cropper $\rightarrow$ Pilih Preset (Pas Foto 2x3, 3x4, 4x6, 2R, 3R, 4R, Polaroid, Gantungan Kunci) atau Custom Ukuran (mm) $\rightarrow$ Tentukan Jumlah Pcs.
3. **Kalkulasi Biaya Transparan**: Web menampilkan estimasi biaya cetak, aksesoris, dan total tagihan secara *real-time*.
4. **Kirim Pesanan**: File terkirim dalam hitungan detik melalui kecepatan 5GHz.

### B. Alur Komputer Kasir (Server & Admin Side)
1. **Folder Otomatis Terbuat**:
   📁 `~/Hasil_Print/[TIMESTAMP]_[NAMA_PELANGGAN]/`
2. **Auto-Generate PDF Siap Cetak (Smart Layout)**:
   - Jika order 2 pcs foto 3x4 $\rightarrow$ Otomatis tercipta file `CETAK_28x38mm_2pcs_Budi.pdf` yang sudah memuat 2 foto rapi dengan garis potong (*crop marks*).
3. **Notifikasi Suara (*Beep*)**: Dashboard kasir berbunyi saat ada pesanan baru.
4. **Pencetakan 1-Klik**: Kasir klik tombol **"Cetak PDF Siap Print"** $\rightarrow$ Langsung kirim ke printer.

---

## 🧮 3. Engine Perhitungan HPP & Laba (Adopsi dari `auto-print`)

Rumus dasar HPP per pesanan:

$$\text{HPP Total} = \text{Biaya Kertas} + \text{Biaya Tinta} + \text{Biaya Listrik} + \text{Biaya Penyusutan Mesin} + \text{Biaya Aksesoris}$$

### Rincian Komponen Biaya:

1. **Kapasitas Lembar (Fit per Page)**:
   $$\text{Fit} = \max\left( \left\lfloor \frac{W_{\text{paper}}}{W_{\text{cut}}} \right\rfloor \times \left\lfloor \frac{H_{\text{paper}}}{H_{\text{cut}}} \right\rfloor , \left\lfloor \frac{W_{\text{paper}}}{H_{\text{cut}}} \right\rfloor \times \left\lfloor \frac{H_{\text{paper}}}{W_{\text{cut}}} \right\rfloor \right)$$
   $$\text{Lembar Master Dibutuhkan} = \left\lceil \frac{\text{Quantity}}{\text{Fit}} \right\rceil$$

2. **Biaya Kertas**:
   $$\text{Biaya Kertas} = \text{Lembar Master} \times \left( \frac{\text{Harga Beli Rim/Pack}}{\text{Isi Lembar per Pack}} \right)$$

3. **Biaya Tinta**:
   $$\text{Biaya Tinta} = \text{Total Halaman Dicetak} \times (\text{ml Tinta per Halaman} \times \text{Harga Tinta per ml})$$
   *(Duplex = 2x Halaman Cetak)*

4. **Biaya Listrik**:
   $$\text{Biaya Listrik} = \text{Total Halaman} \times \left( \frac{\text{Watt Printer}}{1000} \times \frac{\text{Detik Cetak}}{3600} \times \text{Tarif Listrik per kWh} \right)$$

5. **Biaya Penyusutan Mesin**:
   $$\text{Penyusutan} = \text{Total Halaman} \times \left( \frac{\text{Harga Beli Printer}}{\text{Estimasi Total Kapasitas Cetak}} \right)$$

6. **Harga Jual Akhir**:
   $$\text{Harga Jual} = \max\left( \text{HPP} \times (1 + \text{Margin}\%), \text{HPP} + (\text{Min Laba per Lembar} \times \text{Lembar}) \right) + \text{Aksesoris}$$
   *(Dibulatkan ke kelipatan Rp 500 terdekat)*

---

## 🔒 4. Model Keamanan & Otorisasi Panel Admin

| Zona Akses | Akses dari Localhost (PC Kasir) | Akses dari HP Pelanggan (Hotspot) |
|---|---|---|
| **Web Upload Pelanggan (`/`)** | ✅ Buka Langsung | ✅ Buka Langsung |
| **Panel Kasir (`/admin`)** | 🔓 **Bypass Otomatis** (Langsung Masuk) | 🔐 **Wajib Input PIN Kasir** |
| **API Pesanan & File Masuk** | 🔓 Akses Penuh | ⛔ Ditolak (`403 Forbidden`) jika tanpa PIN |
| **Pengaturan HPP & Master Data**| 🔓 Bebas Edit | ⛔ Ditolak (`403 Forbidden`) jika tanpa PIN |

---

## 📦 5. Struktur Modul Proyek

```text
print-drop/
├── app.py                # Server Flask, Router, Endpoint Upload & API Keamanan
├── database.py           # Master Data (Printer, Kertas, Tinta, Aksesoris, Preset)
├── hpp_engine.py         # Mesin Matematika HPP & Kalkulasi Harga Jual
├── pdf_generator.py      # ReportLab Canvas Generator (Grid Pas Foto & Cut Marks)
├── install.sh            # Skrip Instalasi Otomatis (Hotspot 5GHz + Systemd Service)
├── requirements.txt      # Dependensi Python (Flask, Pillow, ReportLab, QRCode)
├── templates/
│   ├── index.html        # Web UI Pelanggan (Cropper.js, PDF.js, Tailwind CSS)
│   └── admin.html        # Web Panel Kasir (Real-Time Live Orders, Audio Beep)
├── BLUEPRINT.md          # Dokumen Arsitektur & Spesifikasi Lengkap
└── README.md             # Panduan Singkat Penggunaan
```
