# PNG Background Remover Desktop

Aplikasi desktop berbasis Python + CustomTkinter untuk menghapus background secara otomatis dari banyak file PNG dalam sebuah folder menggunakan AI offline (`rembg`).

## Instalasi

Pastikan sistem Anda (Ubuntu Linux) sudah terinstall `python3-tk` dan `python3-venv`.
Jika belum, jalankan:
```bash
sudo apt update
sudo apt install python3-tk python3-venv
```

Karena Ubuntu membatasi instalasi paket secara global, buatlah **Virtual Environment** (venv) terlebih dahulu:
```bash
python3 -m venv venv
source venv/bin/activate
```

Setelah `venv` aktif (ditandai dengan awalan `(venv)` di terminal Anda), install dependencies Python:
```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

Pastikan `venv` Anda aktif, lalu jalankan:
```bash
python main.py
```

## Build Distribusi (PyInstaller)

Untuk membuat executable mandiri, install PyInstaller:
```bash
pip install pyinstaller
```

Jalankan build:
```bash
pyinstaller --onefile --windowed main.py
```

File executable akan tersedia di dalam folder `dist/`.
