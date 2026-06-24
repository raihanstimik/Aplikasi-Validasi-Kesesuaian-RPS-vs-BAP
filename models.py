import re

class Validator:
    def __init__(self, db_manager, logger=None):
        self.db = db_manager
        self.logger = logger

    def log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(message)

    def clean_text_to_keywords(self, text):
        """
        Fungsi Pembersihan Teks Tingkat Lanjut (Pintar).
        Mengubah teks menjadi kumpulan kata kunci murni tanpa kata hubung & tanda baca.
        """
        if text is None:
            return set()
        try:
            # 1. Ubah ke huruf kecil
            text = str(text).lower()
            
            # 2. Ganti semua tanda baca (/, -, ,, ., \n) dengan spasi biasa
            text = re.sub(r"[/\-,\.\(\)\n\r]", " ", text)
            
            # 3. Pecah menjadi list kata dasar
            raw_words = text.split()
            
            # 4. Daftar kata buang (Stopwords) bahasa Indonesia yang tidak bernilai sebagai materi
            stopwords = {
                "yang", "dan", "di", "ke", "dari", "pada", "atau", "dengan", "tentang", 
                "untuk", "secara", "dalam", "materi", "pembahasan", "studi", "kasus"
            }
            
            cleaned_words = set()
            for word in raw_words:
                word = word.strip()
                if len(word) < 2 or word in stopwords:
                    continue
                
                # 5. Stemming Sederhana: Menyamakan kata berimbuhan (misal: pemrograman -> program)
                # Membantu menyamakan input manual user yang sering berbeda imbuhan dengan RPS
                if word.startswith("pem") or word.startswith("per"):
                    stemmed = word[3:]
                    if len(stemmed) >= 3: word = stemmed
                if word.endswith("an") and not word.endswith("bukan"):
                    stemmed = word[:-2]
                    if len(stemmed) >= 3: word = stemmed
                    
                cleaned_words.add(word)
                
            return cleaned_words
        except Exception:
            return set()

    def validate(self):
        """
        Mengambil data rps dan bap, lalu mencocokkannya secara pintar dan aman.
        """
        results = []
        match_count = 0

        try:
            # 1. Ambil data RPS secara aman
            query_rps = "SELECT pertemuan, pokok_bahasan, sub_pokok_bahasan FROM rps ORDER BY pertemuan ASC"
            rows_rps = self.db.fetch_all(query_rps) or []

            # 2. Ambil data BAP secara aman
            query_bap = "SELECT pertemuan, materi, sub_materi FROM bap ORDER BY pertemuan ASC"
            rows_bap = self.db.fetch_all(query_bap) or []

            # 3. Mapping BAP ke dictionary berbasis nomor pertemuan (anti-crash jika nomor kosong)
            bap_dict = {}
            for b in rows_bap:
                if not b or 'pertemuan' not in b:
                    continue
                val_pert = b['pertemuan']
                if val_pert is None:
                    continue
                
                try:
                    p_num = int(val_pert)
                    bap_dict[p_num] = b
                except (ValueError, TypeError):
                    bap_dict[str(val_pert).strip()] = b

            self.log(f"📋 Memulai validasi pintar terhadap {len(rows_rps)} entri rencana di RPS...")

            # 4. Proses Validasi Utama Menggunakan NLP Logika Sederhana
            for rps in rows_rps:
                if not rps or 'pertemuan' not in rps:
                    continue
                
                val_rps_pert = rps['pertemuan']
                if val_rps_pert is None:
                    continue

                try:
                    pert_rps = int(val_rps_pert)
                except (ValueError, TypeError):
                    pert_rps = str(val_rps_pert).strip()

                pokok_rps = rps.get('pokok_bahasan') or ""
                sub_rps = rps.get('sub_pokok_bahasan') or ""

                # Cari data pelaksanaan di BAP
                bap = bap_dict.get(pert_rps)

                if bap:
                    materi_bap = bap.get('materi') or ""
                    sub_bap = bap.get('sub_materi') or ""

                    # Ekstraksi kata kunci pintar (sudah melalui case-folding, stopword removal, dan stemming)
                    words_rps = self.clean_text_to_keywords(pokok_rps)
                    words_bap = self.clean_text_to_keywords(materi_bap)

                    # Gabungkan dengan sub-materi jika kolom pokok_bahasan utama kurang lengkap
                    if sub_rps: 
                        words_rps.update(self.clean_text_to_keywords(sub_rps))
                    if sub_bap: 
                        words_bap.update(self.clean_text_to_keywords(sub_bap))

                    # Lakukan Irisan Kata (Word Intersection)
                    intersection = words_rps.intersection(words_bap)

                    if len(intersection) > 0:
                        status = "Sesuai"
                        keterangan = f"Cocok! Ditemukan kata kunci inti yang sama: {', '.join(intersection)}"
                        match_count += 1
                        self.log(f"   🟢 Pertemuan {pert_rps}: Sesuai ({len(intersection)} kata kunci cocok)")
                    else:
                        # Logika Tambahan: Jika kata kunci tidak langsung beririsan, cek kesamaan sebagian (sub-string matching)
                        partial_match = []
                        for wr in words_rps:
                            for wb in words_bap:
                                if wr in wb or wb in wr:
                                    partial_match.append(f"{wr}<->{wb}")
                        
                        if len(partial_match) > 0:
                            status = "Sesuai"
                            keterangan = f"Cocok Sebagian (Variasi Kata)! Terdeteksi kemiripan materi: {', '.join(partial_match)}"
                            match_count += 1
                            self.log(f"   🟢 Pertemuan {pert_rps}: Sesuai via Pencocokan Parsial")
                        else:
                            status = "Tidak Sesuai"
                            keterangan = "Materi pada BAP sama sekali tidak mengandung kata kunci yang diajarkan pada RPS pertemuan ini."
                            self.log(f"   实时 🟡 Pertemuan {pert_rps}: Tidak Sesuai (Kata kunci berbeda jauh)")
                    
                    results.append({
                        'rps_pertemuan': pert_rps,
                        'rps_pokok': pokok_rps,
                        'rps_sub': sub_rps,
                        'bap_pertemuan': bap.get('pertemuan'),
                        'bap_materi': materi_bap,
                        'bap_sub': sub_bap,
                        'status': status,
                        'keterangan': keterangan
                    })
                else:
                    # Jika pertemuan RPS tidak ada eksekusinya di BAP
                    self.log(f"   🔴 Pertemuan {pert_rps}: Hilang (Belum tercatat melaksanakan BAP)")
                    results.append({
                        'rps_pertemuan': pert_rps,
                        'rps_pokok': pokok_rps,
                        'rps_sub': sub_rps,
                        'bap_pertemuan': None,
                        'bap_materi': None,
                        'bap_sub': None,
                        'status': "Hilang",
                        'keterangan': "Pertemuan terjadwal di RPS tetapi datanya kosong/belum diinput pada laporan BAP."
                    })

            # 5. Hitung Persentase Akurasi Akhir
            total_rps = len(rows_rps)
            persentase = round((match_count / total_rps) * 100, 2) if total_rps > 0 else 0.0
            
            self.log(f"📊 Hasil Akhir Validasi: Kesesuaian {persentase}% ({match_count}/{total_rps} Pertemuan)")
            return results, persentase

        except Exception as error_global:
            self.log(f"❌ Terjadi gangguan internal sistem validasi: {str(error_global)}")
            return [], 0.0