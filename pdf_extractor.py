import pdfplumber
from database import DatabaseManager

class PDFExtractor:
    def __init__(self):
        self.db = DatabaseManager()

    def extract_rps_to_db(self, pdf_path):
        self.db.execute_query("DELETE FROM rps")
        success = 0

        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Total halaman: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"🔍 Halaman {page_num}")
                table = page.extract_table()
                
                if not table:
                    continue
                    
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    
                    # Cari kolom pertama yang berisi angka (Pertemuan)
                    pert_str = str(row[0]).strip() if row[0] else ""
                    
                    if pert_str.isdigit() and int(pert_str) > 0:
                        try:
                            pertemuan = int(pert_str)
                            # Ambil kolom pokok bahasan (biasanya index 1 atau 2)
                            pokok = ""
                            for cell in row[1:]:
                                if cell and str(cell).strip() and "None" not in str(cell):
                                    pokok = str(cell).strip()
                                    break
                            
                            sub = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                            
                            if pokok and len(pokok) > 5:  # Filter teks yang terlalu pendek
                                query = """INSERT INTO rps 
                                           (pertemuan, pokok_bahasan, sub_pokok_bahasan) 
                                           VALUES (%s, %s, %s)"""
                                self.db.execute_query(query, (pertemuan, pokok, sub))
                                success += 1
                                print(f"   ✅ Pertemuan {pertemuan}: {pokok[:60]}...")
                        except:
                            continue

        print(f"\n🎉 Berhasil memasukkan {success} data RPS")
        return success