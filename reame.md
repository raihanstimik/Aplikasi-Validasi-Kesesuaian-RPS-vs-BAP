# 🔍 Aplikasi Validasi Kesesuaian RPS vs BAP (Sistem Matcher Pintar)

Aplikasi berbasis **GUI Desktop (Tkinter)** yang berfungsi untuk memvalidasi kesesuaian materi antara **Rencana Pembelajaran Semester (RPS)** dengan **Berita Acara Perkuliahan (BAP)** secara otomatis. Menggunakan pendekatan pemrosesan teks (*Text Preprocessing*) dan algoritma *NLP/String Matching* pintar yang kebal terhadap perbedaan tanda baca serta variasi penulisan kata.

---

## ✨ Fitur Utama

- **Ekstraksi PDF Otomatis**: Membaca data langsung dari dokumen berkas PDF RPS maupun BAP secara instan ke dalam database MySQL.
- **Input BAP Manual**: Menyediakan form GUI yang responsif dilengkapi dengan widget kalender (`tkcalendar`) jika pengguna ingin memasukkan riwayat perkuliahan secara manual.
- **Validasi Pintar (Text Preprocessing & Stemming)**:
  - *Case-Insensitive* (Abaikan huruf besar/kecil).
  - *Punctuation Removal* (Kebal terhadap perbedaan tanda baca seperti koma `,`, garis miring `/`, strip `-`, dll).
  - *Stopwords Removal* (Menghapus kata hubung/kata depan tidak penting agar fokus pada topik inti perkuliahan).
  - *Simple Stemming & Partial Matching* (Menyamakan kata berimbuhan serta variasi kata parsial secara otomatis).
- **Live Terminal Matcher Log**: Menampilkan log sistem pencocokan kata secara *real-time* di layar untuk mempermudah proses pemantauan.
- **Cetak Laporan PDF Formal**: Hasil persentase kepatuhan kepatutan perkuliahan dan tabel detail evaluasi dapat langsung diekspor menjadi file PDF berformat rapi dan formal lengkap dengan tanda tangan verifikator.

---

## 🛠️ Arsitektur Proyek & File

```text
├── main.py            # Entry point aplikasi & Manajemen User Interface (Tkinter)
├── database.py        # Pengelolaan koneksi & query MySQL (DatabaseManager)
├── models.py          # Logika NLP, pembersihan teks, & algoritma validasi (Validator)
├── pdf_extractor.py   # Modul pembaca & ekstraktor teks dari file PDF
├── requirements.txt   # Daftar dependensi library Python
└── README.md          # Dokumentasi proyek

```

---

## 🚀 Persyaratan Sistem & Instalasi

### 1. Prasyarat (Prerequisites)

Pastikan sistem Anda sudah terpasang:

* Python versi 3.8 atau yang lebih baru.
* MySQL Server (misal lewat XAMPP).

### 2. Instalasi Dependensi Library

Buka terminal/command prompt di direktori proyek Anda, lalu jalankan perintah berikut untuk memasang seluruh library yang dibutuhkan:

```bash
pip install mysql-connector-python tkcalendar fpdf2 PyPDF2 python-dotenv

```

### 3. Konfigurasi Database

1. Aktifkan MySQL di XAMPP/server lokal Anda.
2. Buat sebuah database baru bernama `pbo_rps_bap`.
3. Buat file `.env` di folder utama proyek (atau pastikan konfigurasi di `database.py` sudah sesuai dengan kredensial MySQL Anda):
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=pbo_rps_bap

```



---

## 💻 Cara Menjalankan Aplikasi

Jalankan skrip utama melalui terminal menggunakan perintah Python:

```bash
python main.py

```

Setelah aplikasi GUI terbuka, Anda dapat mengikuti alur berikut:

1. Klik tombol **📄 1. Load RPS dari PDF** untuk membaca file cetak kurikulum/RPS Anda ke database.
2. Masukkan data realisasi perkuliahan Anda melalui form input manual atau unggah berkas PDF BAP pendukung.
3. Klik tombol **🔍 3. Validasi RPS vs BAP**. Sistem akan memproses data dan mewarnai baris tabel (**Hijau**: Sesuai, **Kuning**: Acak/Sebagian, **Merah**: Hilang/Belum Terisi).
4. Klik tombol **📥 Cetak Laporan Validasi** untuk menyimpan laporan hasil kelayakan ke dalam bentuk dokumen berkas PDF resmi.

---

## 📝 Catatan Pembaruan Sistem (Changelog)

* **Pembersihan PDF String Anti-Crash**: Mengintegrasikan modul `clean_pdf_text` berbasis filter encoding `latin-1` untuk mencegah kegagalan pembuatan laporan akibat karakter unicode tersembunyi (seperti em-dash `—`).
* **Engine Matcher Lebih Pintar**: Peningkatan stabilitas dari *infinite loop* (anti-stuck) dengan penanganan error query database yang berlapis (`fetch_all`).

```

### 💡 Tips Tambahan:
Jika repositori GitHub Anda bersifat **publik**, pastikan untuk membuat file bernama `.gitignore` lalu masukkan tulisan `.env` di dalamnya agar data kata sandi atau kredensial database lokal Anda tidak ikut tersebar di internet demi alasan keamanan.

```