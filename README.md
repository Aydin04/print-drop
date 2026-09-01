# PrintDrop 🖨️
Sistem Otomatis Hotspot 5GHz & Upload File Cetak Tanpa Kuota / Internet untuk PC Kasir (Linux Aurora / Fedora / Ubuntu / Arch).

## 🚀 Cara Pasang Cepat (1 Baris Perintah)

Buka terminal di PC kasir Anda lalu jalankan:

```bash
curl -sSL https://raw.githubusercontent.com/Aydin04/print-drop/main/install.sh | bash
```

## ⚙️ Fitur
- **Wi-Fi Hotspot 5GHz Otomatis**: Memanfaatkan Wi-Fi Card internal (Qualcomm Atheros QCA9377) untuk transfer ultra cepat.
- **Autostart saat PC Booting**: Hotspot dan server web langsung aktif otomatis begitu komputer dinyalakan.
- **Otomatis Manajemen Folder**: File pelanggan otomatis dibuatkan folder berdasarkan nama/antrian.
- **Tahan Duplikasi**: File dengan nama sama tidak akan tertimpa (otomatis ditambah penomoran).
- **Gambar QR Code Otomatis**: Tersimpan di `~/PrintDrop/QR_MEJA_PRINT.png` siap cetak untuk meja kasir.
