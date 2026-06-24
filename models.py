import re

class Validator:
    def __init__(self, db_manager):
        self.db = db_manager

    def clean_text(self, text):
        if not text:
            return ""
        text = str(text).lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def validate(self):
        rps_list = self.db.execute_query("SELECT * FROM rps ORDER BY pertemuan") or []
        bap_list = self.db.execute_query("SELECT * FROM bap ORDER BY pertemuan") or []
        
        results = []
        match_count = 0
        rps_dict = {r['pertemuan']: self.clean_text(r['pokok_bahasan']) for r in rps_list}

        for bap in bap_list:
            bap_clean = self.clean_text(bap['materi'])
            found = False

            for rps_pert, rps_clean in rps_dict.items():
                # Matching
                if (rps_clean in bap_clean or 
                    bap_clean in rps_clean or 
                    len(set(rps_clean.split()) & set(bap_clean.split())) >= 3):
                    
                    status = "Sesuai" if rps_pert == bap['pertemuan'] else "Tidak Sesuai / Acak"
                    
                    if status == "Sesuai":
                        keterangan = f"Materi Pertemuan {rps_pert} sesuai dengan RPS"
                        match_count += 1
                    else:
                        keterangan = f"Peringatan: Materi Pertemuan {rps_pert} (RPS) diajarkan di Pertemuan {bap['pertemuan']} (BAP)"
                    
                    results.append({
                        'rps_pertemuan': rps_pert,
                        'bap_pertemuan': bap['pertemuan'],
                        'status': status,
                        'keterangan': keterangan
                    })
                    found = True
                    break

            if not found:
                results.append({
                    'rps_pertemuan': None,
                    'bap_pertemuan': bap['pertemuan'],
                    'status': "Tidak Diajarkan / Hilang",
                    'keterangan': f"Materi di BAP Pertemuan {bap['pertemuan']} tidak ditemukan di RPS"
                })

        total = len(rps_list)
        persentase = (match_count / total * 100) if total > 0 else 0
        
        return results, round(persentase, 2)