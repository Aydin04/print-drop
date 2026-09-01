# Aydin Print Drop (Web Studio & Hotspot 5GHz)

Sistem Otomatis Hotspot Wi-Fi 5GHz & Web Upload Pintar untuk Percetakan **Aydin Print** di Linux Aurora / Fedora Atomic / Ubuntu.

---

## ⚡ Fitur Unggulan

1. **Auto Hotspot 5GHz (Qualcomm Atheros QCA9377)**:
   - SSID: `AYDIN-PRINT` (Password: `aydinprint`)
   - Otomatis aktif saat PC menyala (*autoconnect*).
   - Kecepatan hingga 433 Mbps untuk transfer foto/dokumen ukuran besar instan tanpa memakan kuota internet.

2. **Halaman Pelanggan (Web UI)**:
   - **Mode Dokumen / Fotocopy**: Upload PDF, Word, JPG, PNG dengan live preview, pilihan warna (B/W vs Color), Duplex (bolak-balik), jenis kertas & rangkap fotocopy.
   - **Mode Pas Foto & Custom Size**: Dilengkapi **Interactive Canvas Cropper** (Zoom, Geser, Putar), preset resmi (2x3, 3x4, 4x6, 2R, 4R) dan Custom mm.
   - **Smart Template Layout Generator**: Otomatis menyusun foto (misal: 2 pcs 3x4) ke lembar template siap cetak bergaris potong (*cut marks*).
   - **Live Pricing Calculation**: Pelanggan langsung melihat total estimasi biaya sebelum mengirim.

3. **Panel Admin & Kalkulator HPP Kasir (`/admin`)**:
   - Master Data Printer (Brother DCP-T720DW, Epson L800, dll).
   - Master Data Kertas, Tinta & Aksesoris (Gantungan Kunci Akrilik, ID Card, Laminasi, Jilid).
   - Pengaturan Margin Keuntungan (Markup / Gross Margin) & Tarif Listrik.
   - Antrian pesanan masuk secara *real-time*.

---

## 🚀 Cara Pemasangan di PC Linux (Cukup 1 Baris)

Buka terminal di Linux Aurora / PC Anda, lalu jalankan:

```bash
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/install.sh | bash
```
