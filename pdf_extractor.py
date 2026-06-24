import pdfplumber
from database import DatabaseManager


class PDFExtractor:
    def __init__(self):
        self.db = DatabaseManager()

    def extract_rps_to_db(self, pdf_path):
        self.db.execute_query("DELETE FROM rps")
        success = 0

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                table = page.extract_table()
                if not table:
                    continue

                for row in table:
                    if not row or len(row) < 2:
                        continue

                    pert_str = str(row[0]).strip() if row[0] else ""

                    if pert_str.isdigit() and int(pert_str) > 0:
                        try:
                            pertemuan = int(pert_str)

                            pokok = ""
                            pokok_idx = -1
                            for i, cell in enumerate(row[1:], 1):
                                if cell and str(cell).strip() and "None" not in str(cell):
                                    pokok = str(cell).strip()
                                    pokok_idx = i
                                    break

                            sub = ""
                            if pokok_idx >= 0 and len(row) > pokok_idx + 1:
                                next_cell = row[pokok_idx + 1]
                                if next_cell and str(next_cell).strip() and "None" not in str(next_cell):
                                    sub = str(next_cell).strip()

                            if not sub and len(row) > 2 and row[2]:
                                sub = str(row[2]).strip() if "None" not in str(row[2]) else ""

                            if pokok and len(pokok) > 5:
                                query = """INSERT INTO rps
                                           (pertemuan, pokok_bahasan, sub_pokok_bahasan)
                                           VALUES (%s, %s, %s)"""
                                self.db.execute_query(query, (pertemuan, pokok, sub))
                                success += 1
                        except Exception:
                            continue
        return success

    def extract_bap_from_pdf(self, pdf_path):
        """
        Ekstrak data BAP dengan optimasi pemisahan sub-materi jika 
        konten menumpuk di kolom materi utama.
        """
        self.db.execute_query("DELETE FROM bap")
        success = 0

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                table = page.extract_table()
                if not table:
                    continue

                for row in table:
                    if not row or len(row) < 2:
                        continue

                    pert_str = str(row[0]).strip() if row[0] else ""

                    if pert_str.isdigit() and int(pert_str) > 0:
                        try:
                            pertemuan = int(pert_str)

                            tanggal = str(row[1]).strip() if len(row) > 1 and row[1] else None
                            if tanggal and "None" in tanggal:
                                tanggal = None

                            materi = ""
                            for cell in row[2:]:
                                if cell and str(cell).strip() and "None" not in str(cell):
                                    materi = str(cell).strip()
                                    break

                            sub_materi = ""
                            if len(row) > 3 and row[3]:
                                val = str(row[3]).strip()
                                if "None" not in val:
                                    sub_materi = val

                            # --- OPTIMASI CERDAS UNTUK MEMECAH RUANG KOSONG ---
                            # Jika sub_materi kosong tetapi di dalam cell 'materi' terdapat karakter pemisah pemutus baris/tanda baca
                            if not sub_materi and materi:
                                if "\n" in materi:
                                    parts = materi.split("\n", 1)
                                    materi = parts[0].strip()
                                    sub_materi = parts[1].strip()
                                elif " : " in materi:
                                    parts = materi.split(" : ", 1)
                                    materi = parts[0].strip()
                                    sub_materi = parts[1].strip()
                                elif " - " in materi:
                                    parts = materi.split(" - ", 1)
                                    materi = parts[0].strip()
                                    sub_materi = parts[1].strip()

                            if materi and len(materi) > 3:
                                query = """INSERT INTO bap
                                           (pertemuan, tanggal, materi, sub_materi)
                                           VALUES (%s, %s, %s, %s)"""
                                self.db.execute_query(query, (pertemuan, tanggal, materi, sub_materi or None))
                                success += 1
                        except Exception:
                            continue
        return success