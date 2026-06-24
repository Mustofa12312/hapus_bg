# PNG Background Remover Desktop v1.1

Aplikasi desktop berbasis Python + CustomTkinter untuk menghapus background secara otomatis dari banyak file PNG dalam sebuah folder menggunakan AI offline (`rembg`).

## ✨ Fitur Utama (v1.1)

- ✅ **AI Offline**: Gunakan rembg untuk menghapus background tanpa internet
- ✅ **Batch Processing**: Proses ratusan gambar sekaligus secara otomatis
- ✅ **Drag & Drop**: Mudah memilih folder dengan drag and drop
- ✅ **Validasi Input**: Cek integritas file sebelum diproses
- ✅ **Error Handling**: Penanganan error komprehensif dengan retry otomatis
- ✅ **Disk Space Check**: Verifikasi ruang disk sebelum proses
- ✅ **Resource Monitoring**: Monitor penggunaan RAM dan disk
- ✅ **File Logging**: Log lengkap tersimpan di folder `logs/`
- ✅ **Progress Tracking**: Progress bar real-time dengan persentase
- ✅ **Detailed Reports**: Ringkasan proses dengan statistik terperinci
- ✅ **Path Traversal Protection**: Validasi keamanan path
- ✅ **Directory Structure**: Preservasi struktur folder di output
- ✅ **Activity Log**: Log terformat dengan warna untuk setiap event

## 🚀 Instalasi

Pastikan sistem Anda (Ubuntu Linux) sudah terinstall `python3-tk` dan `python3-venv`.
Jika belum, jalankan:

```bash
sudo apt update
sudo apt install python3-tk python3-venv
```

Karena Ubuntu membatasi instalasi paket secara global, buatlah **Virtual Environment** (venv) terlebih dahulu:

```bash
cd ~/Documents/python/hapus_bg
python3 -m venv .venv
source .venv/bin/activate
```

Setelah `venv` aktif (ditandai dengan awalan `(.venv)` di terminal Anda), install dependencies Python:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Menjalankan Aplikasi

Pastikan `venv` Anda aktif, lalu jalankan:

```bash
python main.py
```

## 📋 Cara Menggunakan

1. **Pilih Folder Sumber**
   - Klik tombol "📁 Pilih Folder" atau drag & drop folder
   - Aplikasi akan memindai dan menampilkan jumlah gambar ditemukan

2. **Review File Count**
   - Cek jumlah gambar yang akan diproses
   - Pastikan ada cukup ruang disk

3. **Mulai Proses**
   - Klik tombol "▶️  Mulai Proses"
   - Monitor progress dengan progress bar
   - Lihat detail di Activity Log

4. **Buka Hasil**
   - Klik "📂 Buka Folder Hasil" untuk membuka folder output
   - Hasil tersimpan di `{nama_folder}_output`
   - Struktur folder otomatis dipertahankan

5. **Check Log**
   - Klik "📝 Open Logs" untuk membuka folder log
   - File log tersimpan dengan timestamp
   - Terpisah untuk log umum dan error log

## ⚙️ Konfigurasi

Edit file `config.py` untuk mengatur:

```python
# Processing settings
MAX_IMAGE_SIZE_MB = 100          # Maksimal ukuran file
PROCESS_TIMEOUT_SECONDS = 300    # Timeout per gambar
RETRY_ATTEMPTS = 2               # Jumlah retry untuk file gagal
BATCH_SIZE_WARNING = 500         # Warning untuk batch besar

# Resource limits
MIN_FREE_DISK_SPACE_MB = 500     # Minimal ruang disk diperlukan
MAX_RAM_USAGE_PERCENT = 80       # Maksimal penggunaan RAM

# Output settings
PRESERVE_DIR_STRUCTURE = True    # Pertahankan struktur folder
OVERWRITE_EXISTING = False       # Overwrite file yang sudah ada
```

## 📊 Fitur Baru (v1.1)

### 1. **Validasi Input Komprehensif**
- Cek file magic bytes (header file)
- Validasi format gambar dengan PIL
- Deteksi symlink untuk keamanan
- Check read/write permissions

### 2. **Error Handling Terperinci**
- Kategorisasi jenis error (corrupted, timeout, memory, etc)
- Retry otomatis untuk file yang gagal
- Pesan error spesifik untuk debugging
- Skip file rusak tanpa berhenti

### 3. **Resource Monitoring**
- Cek penggunaan RAM sebelum proses
- Verifikasi ruang disk tersedia
- Monitor file size sebelum loading
- Timeout protection per file

### 4. **Logging Komprehensif**
- Log ke file dengan timestamp detail
- Separate error log untuk masalah
- Color-coded UI log untuk readability
- Log directory auto-created

### 5. **UI Improvements**
- Better error messages dalam Bahasa Indonesia
- Real-time file count preview
- Detailed completion report
- File validation feedback
- Open logs button untuk debugging

### 6. **Statistics & Reporting**
- Success rate percentage
- Failed files list dengan alasan
- Processing time tracking
- Average time per file
- Retry statistics

## 📁 Struktur Folder

```
hapus_bg/
├── main.py                 # Entry point
├── config.py              # Konfigurasi (NEW)
├── requirements.txt
├── README.md
├── prd.md
│
├── ui/
│   ├── app.py             # Main UI (IMPROVED)
│   └── widgets.py         # Custom widgets (IMPROVED)
│
├── core/
│   ├── processor.py       # Batch processor (IMPROVED)
│   ├── remover.py         # Background remover (IMPROVED)
│   └── scanner.py         # Image scanner (IMPROVED)
│
├── utils/
│   ├── logger.py          # Logging system (IMPROVED)
│   └── paths.py           # Path utilities (IMPROVED)
│
├── logs/                  # Log files (NEW)
│   ├── bg_remover_*.log   # Main logs
│   └── errors_*.log       # Error logs only
│
└── .venv/                 # Virtual environment
```

## 🔍 Troubleshooting

### Aplikasi crash saat startup
- Pastikan virtual environment sudah aktif
- Update semua packages: `pip install -r requirements.txt --upgrade`
- Check Python version: `python --version` (harus 3.8+)

### Gambar tidak diproses
- Cek di Activity Log untuk error message
- Open logs folder untuk detail lengkap
- Pastikan format file benar (PNG, JPG, JPEG)
- Check file integrity dengan image viewer

### Proses lambat
- File gambar besar? Check ukuran file
- Komputer spec rendah? Proses lebih sedikit file sekaligus
- RAM penuh? Close aplikasi lain
- Check CPU usage di Activity Monitor

### Error "Disk space not enough"
- Bersihkan folder output lama
- Delete temporary files
- Check `df -h` untuk ruang disk total

## 🏗️ Build Distribusi (PyInstaller)

Untuk membuat executable mandiri:

```bash
pip install pyinstaller

# Build one-file executable
pyinstaller --onefile --windowed --name "PNG-BG-Remover" main.py

# Executable akan tersedia di folder `dist/`
```

## 📝 Log File Examples

### Main Log (`bg_remover_20240101_120000.log`)
```
2024-01-01 12:00:00 - [INFO] - _process_worker:45 - Starting batch process...
2024-01-01 12:00:01 - [INFO] - validate_input_folder:23 - Input validation OK
2024-01-01 12:00:05 - [INFO] - scan_for_images:67 - Found 150 valid images
```

### Error Log (`errors_20240101_120000.log`)
```
2024-01-01 12:00:30 - [ERROR] - remove_background:78 - File corrupted: image.png
2024-01-01 12:00:35 - [WARNING] - _check_system_resources:120 - RAM usage: 85%
```

## 🐛 Debug Mode

Untuk melihat debug log:

1. Cari file log terbaru di folder `logs/`
2. Open dengan text editor untuk melihat detail
3. Cari `[DEBUG]` untuk informasi teknis lengkap

## 📄 License

Personal use application. Dibuat untuk processing gambar batch otomatis.

## 🤝 Support

Untuk issues atau suggestions, check log files terlebih dahulu untuk diagnostik.

---

**Version**: 1.1  
**Last Updated**: 2024

