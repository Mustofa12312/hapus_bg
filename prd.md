# PRD (Product Requirements Document)

## PNG Background Remover Desktop

Versi: 1.0

Platform: Desktop Linux (Ubuntu Native)

Teknologi: Python + CustomTkinter + rembg

Status: MVP

---

# 1. Ringkasan Produk

PNG Background Remover Desktop adalah aplikasi desktop berbasis Python yang digunakan untuk menghapus background secara otomatis dari seluruh file PNG dalam sebuah folder menggunakan AI offline.

Aplikasi ditujukan untuk penggunaan pribadi dengan fokus pada:

- Sederhana
- Cepat
- Offline
- Mudah digunakan

Pengguna cukup memilih atau melakukan drag & drop folder yang berisi gambar PNG, kemudian aplikasi akan memproses seluruh gambar dan menyimpan hasilnya ke folder output dengan background transparan.

---

# 2. Tujuan Produk

### Tujuan Utama

Menghapus background ratusan hingga ribuan gambar PNG secara otomatis tanpa perlu membuka editor gambar satu per satu.

### Masalah yang Diselesaikan

Sebelum:

- Harus menghapus background secara manual.
- Membuka satu gambar demi satu.
- Memakan banyak waktu.

Sesudah:

- Pilih folder.
- Klik Proses.
- Semua gambar diproses otomatis.

---

# 3. Ruang Lingkup MVP

## Termasuk

- Pilih folder input.
- Drag & Drop folder.
- Scan seluruh PNG.
- Scan subfolder otomatis.
- Hapus background menggunakan AI offline.
- Menyimpan hasil ke folder output.
- Progress bar.
- Log proses.
- Skip file rusak.
- Tombol buka folder hasil.

## Tidak Termasuk

- Login.
- Database.
- Cloud storage.
- Preview gambar.
- Edit gambar.
- Resize gambar.
- Crop gambar.
- Multi-format selain PNG.
- API online.

---

# 4. User Persona

### Mustofa

Profil:

- Programmer
- Pengguna Ubuntu
- Memiliki banyak gambar PNG
- Ingin proses otomatis

Kebutuhan:

- Cepat
- Offline
- Tidak ribet

---

# 5. User Flow

## Flow 1 - Pilih Folder

1. Buka aplikasi.
2. Klik tombol Pilih Folder.
3. Memilih folder sumber.
4. Folder tampil pada UI.

---

## Flow 2 - Drag & Drop

1. Buka aplikasi.
2. Drag folder.
3. Drop ke area aplikasi.
4. Folder otomatis terpilih.

---

## Flow 3 - Proses

1. Klik Proses.
2. Sistem scan file PNG.
3. Sistem membuat folder output.
4. Sistem menghapus background seluruh gambar.
5. Progress diperbarui.
6. Selesai.

---

# 6. Struktur Folder Output

Input:

```text
produk/
├── A/
│   ├── 1.png
│   └── 2.png
├── B/
│   └── 3.png
```

Output:

```text
output/
├── A/
│   ├── 1.png
│   └── 2.png
├── B/
│   └── 3.png
```

Struktur folder harus dipertahankan.

---

# 7. UI Requirement

## Window

Ukuran:

```text
1000 x 650
```

Resizable:

```text
Yes
```

Tema:

```text
Dark Mode
```

Framework:

```text
CustomTkinter
```

---

## Layout

### Header

```text
PNG Background Remover
AI Offline Batch Processor
```

---

### Folder Section

Komponen:

- Label Folder
- Tombol Pilih Folder
- Area Drag & Drop

Contoh:

```text
+------------------------------------+
| Drag Folder Here                   |
+------------------------------------+

[ Pilih Folder ]
```

---

### Process Section

Komponen:

- Tombol Mulai

```text
[ Mulai Proses ]
```

---

### Progress Section

Komponen:

- Progress Bar
- Persentase

Contoh:

```text
65%
[██████████░░░░░░]
```

---

### Log Section

Komponen:

```text
[INFO] Scan folder...
[INFO] 120 file ditemukan...
[INFO] Memproses 1.png...
[INFO] Memproses 2.png...
[ERROR] gambar5.png rusak...
```

---

### Footer

Komponen:

```text
[ Buka Folder Hasil ]
```

---

# 8. Arsitektur Sistem

## Library

### UI

```python
customtkinter
```

### Drag & Drop

```python
tkinterdnd2
```

### Remove Background

```python
rembg
```

### AI Runtime

```python
onnxruntime
```

### Image Processing

```python
Pillow
```

---

# 9. Struktur Project

```text
bg-remover/

├── main.py

├── ui/
│   ├── app.py
│   ├── widgets.py

├── core/
│   ├── remover.py
│   ├── scanner.py
│   ├── processor.py

├── utils/
│   ├── logger.py
│   ├── paths.py

├── assets/
│   ├── icon.ico

├── output/

├── requirements.txt

└── README.md
```

---

# 10. Modul Scanner

Tugas:

- Scan folder
- Scan subfolder
- Cari seluruh PNG

Output:

```python
[
  "A/1.png",
  "A/2.png",
  "B/3.png"
]
```

---

# 11. Modul Remover

Tugas:

- Membaca PNG
- Menjalankan rembg
- Menghasilkan PNG transparan

Proses:

```python
input.png
↓
rembg
↓
transparent.png
```

---

# 12. Modul Processor

Tugas:

- Mengatur antrian file
- Mengirim progress
- Menangani error

Flow:

```text
Scan
↓
Loop File
↓
Remove BG
↓
Save
↓
Update Progress
```

---

# 13. Error Handling

Jika file rusak:

```text
[ERROR] gambar.png gagal diproses
```

Sistem:

- Tidak berhenti.
- Lanjut ke file berikutnya.

---

# 14. Performa

Target:

- 100 gambar PNG
- Resolusi 1024x1024

Waktu:

```text
± 2 - 10 menit
```

Tergantung spesifikasi perangkat.

---

# 15. Dependensi

```bash
pip install customtkinter

pip install tkinterdnd2

pip install rembg

pip install onnxruntime

pip install pillow
```

---

# 16. Build Distribusi

Ubuntu:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --onefile main.py
```

Output:

```text
dist/
└── bg-remover
```

---

# 17. Kriteria Keberhasilan

Aplikasi dianggap berhasil apabila:

- Folder dapat dipilih.
- Drag & Drop berfungsi.
- Semua PNG ditemukan.
- Background terhapus.
- Hasil PNG transparan.
- Struktur folder tetap sama.
- Progress tampil.
- File rusak tidak menghentikan proses.
- Folder hasil dapat dibuka otomatis.
- Seluruh proses berjalan tanpa internet.
