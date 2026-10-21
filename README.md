# AutoDash — Automatic Excel Dashboard Builder

AutoDash adalah aplikasi Streamlit lokal untuk membaca CSV/Excel, memprofilkan kualitas data, menyusun dashboard otomatis, mengedit grafik, memfilter data, mengatur layout, serta mengekspor hasil. Data tidak dikirim ke layanan eksternal.

## Persyaratan
- Windows 10/11
- Python 3.11 (direkomendasikan) atau Python 3.12
- Koneksi internet hanya diperlukan saat memasang dependensi pertama kali

## Instalasi
1. Ekstrak `autodash.zip` ke folder pilihan.
2. Buka Command Prompt di folder `autodash`.
3. Buat virtual environment:
   ```bat
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   ```
4. Pasang dependensi:
   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Jalankan `run.bat`, atau:
   ```bat
   streamlit run app.py
   ```
6. Browser akan terbuka. Jika tidak, kunjungi alamat lokal yang ditampilkan terminal.

## Penggunaan
- Unggah CSV, XLSX, atau XLS dari sidebar. Excel menyediakan pemilihan sheet.
- **Overview** menampilkan KPI, rekomendasi grafik, dan insight deskriptif.
- **Data Explorer** menampilkan pratinjau, profil kolom, duplikasi, nilai kosong, dan statistik numerik.
- **Chart Builder** menambahkan, melihat pratinjau, atau menghapus grafik.
- **Filters** menerapkan filter kategori, numerik, tanggal (jika sudah dikenali sebagai datetime), dan pencarian teks.
- **Layout** mengubah jumlah kolom, urutan, serta visibilitas elemen.
- **Export** mengunduh CSV hasil filter, statistik CSV, konfigurasi JSON, dan laporan HTML. Impor JSON divalidasi terhadap kolom dataset yang sedang aktif.

Dataset contoh `sample_data/sample_sales.csv` dapat dimuat dari halaman awal.

## Pengujian
```bat
python -m pytest -q
```

## Catatan dan batasan
- Batas ukuran upload default 50 MB dapat diubah di sidebar.
- XLS memerlukan `xlrd`, yang disertakan dalam requirements.
- Deteksi tipe dan rekomendasi bersifat heuristik; periksa hasilnya di Data Explorer dan Chart Builder.
- Dashboard tidak menjalankan formula atau kode dari file. File sumber tidak diubah.
- Layout versi pertama memakai pengurutan naik/turun dan jumlah kolom; drag-and-drop bebas belum didukung.
- Laporan HTML memuat maksimal 500 baris tabel agar file tidak terlalu besar. Tidak ada ekspor PDF pada versi ini.
- Konfigurasi JSON hanya menyimpan struktur dashboard, bukan dataset.
- SQLite tidak diaktifkan pada versi pertama untuk menjaga alur lokal tetap sederhana.

## Pemecahan masalah
- **`py` tidak ditemukan:** instal Python dari python.org dan aktifkan opsi penambahan Python ke PATH.
- **Dependensi gagal dipasang:** aktifkan virtual environment lalu jalankan `python -m pip install -r requirements.txt`.
- **XLS gagal dibaca:** pastikan file bukan XLSX yang hanya diganti ekstensi.
- **Port sedang digunakan:** jalankan `streamlit run app.py --server.port 8502`.
- **File terlalu besar:** tingkatkan batas ukuran jika perangkat memiliki memori memadai, atau gunakan subset data.
