# 🖨️ Aydin Print — Self-Service Studio & Auto Print Server

Sistem percetakan mandiri (*self-service*), transfer file cepat via QR Code & Wi-Fi 5GHz lokal, kalkulator HPP otomatis, live image cropper, dan pembuat template PDF siap cetak untuk **Aydin Print**.

---

## ✨ Fitur Utama

1. **📱 Web UI Pelanggan (Self-Service)**:
   - **Mode Dokumen / Fotocopy**: Upload PDF, Word, Excel, JPG, PNG dengan live preview dan deteksi jumlah halaman otomatis.
   - **Mode Foto & Kustom Studio**: Alat crop interaktif (*zoom in/out*, putar, geser, bebas rasio atau sesuai preset ukuran resmi).
   - **Preset Pas Foto**: 2x3, 3x4, 4x6, 2R, 3R, 4R, Polaroid, Gantungan Kunci Akrilik (2 sisi).
   - **Smart PDF Template Generator**: Misal pesan *2 pcs foto 3x4*, otomatis dibuatkan 1 lembar PDF berisi 2 foto presisi lengkap dengan garis potong (*cut marks*).
   - **Kalkulasi Harga & HPP Real-time**: Pelanggan langsung melihat rincian biaya cetak, aksesoris, dan total yang harus dibayar.
   - **Pilihan Duplex**: Opsi cetak bolak-balik untuk hemat kertas.

2. **🛡️ Panel Kasir / Admin (`/admin`)**:
   - **Dashboard Order Real-Time**: Daftar pesanan masuk otomatis muncul tanpa reload dengan audio notifikasi beep.
   - **Cetak 1-Klik**: Tombol langsung membuka file PDF siap cetak.
   - **Master Data Printer & Mesin**: Manajemen harga beli printer, estimasi kapasitas cetak, dan watt listrik (Brother DCP-T720DW, Epson L800/L805, dll).
   - **Master Kertas & Tinta**: HVS, Glossy Photo Paper, Art Paper, Stiker Vinyl, dll.
   - **Master Aksesoris**: Gantungan kunci akrilik foto, laminasi panas, plastik ID Card/lanyard, jilid lakban & spiral kawat.
   - **Kalkulator HPP Otomatis**: Menghitung biaya kertas + tinta + listrik + penyusutan mesin per order.

3. **📶 Hotspot Wi-Fi 5GHz Terisolasi (Atheros QCA9377)**:
   - SSID: **`AYDIN-PRINT`**
   - Password: **`aydinprint`**
   - Menggunakan frekuensi 5GHz channel 36 (transfer file super cepat).
   - Hotspot murni LAN (tidak membagikan internet pribadi toko).

---

## ⚡ Cara Instalasi di PC Linux Aurora (Cukup 1 Baris)

Buka aplikasi **Terminal** di PC Anda, lalu jalankan:

```bash
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/install.sh | bash
```

---

## 📂 Lokasi File & Direktori

- **Web Pelanggan**: `http://10.42.0.1:5000`
- **Panel Kasir**: `http://10.42.0.1:5000/admin`
- **Folder Hasil Order**: `~/Hasil_Print/<TIMESTAMP>_<NAMA_PELANGGAN>/`
- **Gambar QR Code Siap Cetak**: `~/PrintDrop/QR_AYDIN_PRINT.png`
