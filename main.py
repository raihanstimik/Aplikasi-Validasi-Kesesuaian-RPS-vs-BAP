import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry 
from database import DatabaseManager
from models import Validator
from pdf_extractor import PDFExtractor
from datetime import datetime

# ── Warna tema ──────────────────────────────────────────────────────────────
CLR_BG        = "#F0F2F5"
CLR_PRIMARY   = "#1565C0"
CLR_SUCCESS   = "#2E7D32"
CLR_WARNING   = "#E65100"
CLR_DANGER    = "#B71C1C" 
CLR_ACCENT    = "#6A1B9A"
CLR_RESET     = "#37474F"
CLR_WHITE     = "#FFFFFF"
CLR_HEADER_BG = "#1A237E"

class RPSBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Validasi RPS vs BAP – Pemrograman Berorientasi Objek")
        self.root.geometry("1340x880")
        self.root.configure(bg=CLR_BG)
        self.root.resizable(True, True)

        self.db        = DatabaseManager()
        self.validator = Validator(self.db, logger=self.log_message)
        self.last_results = []   # Menyimpan data cache hasil validasi untuk dicetak
        self.last_persen  = 0.0

        self._build_ui()

    def log_message(self, message):
        self.txt_log.configure(state="normal")
        self.txt_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.txt_log.see(tk.END) 
        self.txt_log.configure(state="disabled")
        self.root.update_idletasks()

    def clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.insert(tk.END, "=== LOG CLEARED ===\n")
        self.txt_log.configure(state="disabled")

    def _build_ui(self):
        # ── Header
        hdr = tk.Frame(self.root, bg=CLR_HEADER_BG, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Aplikasi Validasi Kesesuaian RPS vs BAP",
                 font=("Arial", 18, "bold"), fg=CLR_WHITE, bg=CLR_HEADER_BG).pack()
        tk.Label(hdr, text="PBO Python + MySQL",
                 font=("Arial", 11), fg="#90CAF9", bg=CLR_HEADER_BG).pack()

        # ── Action bar
        act = tk.Frame(self.root, bg=CLR_BG, pady=10)
        act.pack(fill="x", padx=30)

        self._btn(act, "📄  1. Load RPS dari PDF → MySQL", CLR_SUCCESS, self.load_rps_pdf).pack(side="left", padx=6)
        self._btn(act, "📋  2. Upload BAP dari PDF (opsional)", CLR_ACCENT, self.load_bap_pdf).pack(side="left", padx=6)
        self._btn(act, "🔄  Reset Semua Data", CLR_RESET, self.reset_all).pack(side="right", padx=6)

        # ── AREA TENGAH: Form Input & Terminal Log
        middle_frame = tk.Frame(self.root, bg=CLR_BG)
        middle_frame.pack(fill="x", padx=30, pady=4)

        # 🏠 KIRI: Form Input BAP manual
        frm = tk.LabelFrame(middle_frame, text="  Input Data BAP Manual  ",
                             bg=CLR_BG, font=("Arial", 10, "bold"), fg=CLR_PRIMARY, padx=14, pady=10)
        frm.pack(side="left", fill="both", expand=True)

        tk.Label(frm, text="Pertemuan Ke-:", bg=CLR_BG).grid(row=0, column=0, sticky="w")
        self.ent_pert = tk.Entry(frm, width=8); self.ent_pert.grid(row=0, column=1, padx=6, sticky="w")

        tk.Label(frm, text="Tanggal:", bg=CLR_BG).grid(row=0, column=2, sticky="w", padx=10)
        self.ent_tgl = DateEntry(frm, width=16, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.ent_tgl.grid(row=0, column=3, padx=6, sticky="w")

        tk.Label(frm, text="Materi yang Diajarkan:", bg=CLR_BG).grid(row=1, column=0, sticky="nw", pady=4)
        self.txt_materi = tk.Text(frm, height=3, width=48)
        self.txt_materi.grid(row=1, column=1, columnspan=3, pady=4, sticky="w")

        tk.Label(frm, text="Sub Materi:", bg=CLR_BG).grid(row=2, column=0, sticky="nw", pady=4)
        self.txt_sub_materi = tk.Text(frm, height=2, width=48)
        self.txt_sub_materi.grid(row=2, column=1, columnspan=3, pady=4, sticky="w")

        btn_bar = tk.Frame(frm, bg=CLR_BG); btn_bar.grid(row=3, column=1, columnspan=3, pady=6, sticky="w")
        self._btn(btn_bar, "➕  Tambahkan ke BAP", CLR_WARNING, self.add_bap, h=1).pack(side="left", padx=4)
        self._btn(btn_bar, "🗑  Bersihkan Form", CLR_DANGER, self._clear_form, h=1).pack(side="left", padx=4)

        # 🖥️ KANAN: Terminal Log
        log_frame = tk.LabelFrame(middle_frame, text="  Live Terminal Matcher Log  ", bg=CLR_BG, font=("Arial", 10, "bold"), fg="#333333", padx=10, pady=10)
        log_frame.pack(side="right", fill="both", padx=(15, 0))

        log_sub = tk.Frame(log_frame, bg=CLR_BG)
        log_sub.pack(fill="both", expand=True)

        self.txt_log = tk.Text(log_sub, width=52, height=10, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 9), insertbackground="white")
        self.txt_log.pack(side="left", fill="both", expand=True)
        
        log_scroll = ttk.Scrollbar(log_sub, orient="vertical", command=self.txt_log.yview)
        log_scroll.pack(side="right", fill="y")
        self.txt_log.configure(yscrollcommand=log_scroll.set)
        
        btn_log_frame = tk.Frame(log_frame, bg=CLR_BG)
        btn_log_frame.pack(fill="x", pady=(5, 0))
        self._btn(btn_log_frame, "🗑️  Bersihkan Log Terminal", CLR_RESET, self.clear_log, h=1, font=("Arial", 9)).pack(side="right")

        self.txt_log.insert(tk.END, "=== SYSTEM REALTIME LOG READY ===\n")
        self.txt_log.configure(state="disabled")

        # ── Tombol Utama Validasi & Cetak
        val_f = tk.Frame(self.root, bg=CLR_BG, pady=10)
        val_f.pack()
        self._btn(val_f, "🔍  3. Validasi RPS vs BAP", CLR_PRIMARY, self.validate_data, font=("Arial", 12, "bold"), h=2, w=35).pack(side="left", padx=10)
        self._btn(val_f, "📥  Cetak Laporan Validasi", "#00796B", self.export_report, font=("Arial", 12, "bold"), h=2, w=28).pack(side="left", padx=10)

        # ── Status bar
        self.lbl_status = tk.Label(self.root, text="Siap.", bg=CLR_BG, fg="#555", font=("Arial", 10, "bold"), anchor="w")
        self.lbl_status.pack(fill="x", padx=30, pady=(4, 0))

        # ── Tabel hasil (RESPONSIF KANAN-KIRI)
        tbl_f = tk.Frame(self.root, bg=CLR_BG)
        tbl_f.pack(fill="both", expand=True, padx=25, pady=(5, 10))

        cols = ("RPS Pert.", "Pokok Bahasan (RPS)", "Sub Pokok (RPS)",
                "BAP Pert.", "Materi BAP", "Sub Materi BAP",
                "Status", "Keterangan")
        self.tree = ttk.Treeview(tbl_f, columns=cols, show="headings", height=15)

        # Optimasi Lebar & Mengaktifkan Stretch agar tulisan tidak terpotong saat diperbesar
        col_w = {
            "RPS Pert.": 75, "Pokok Bahasan (RPS)": 230, "Sub Pokok (RPS)": 180,
            "BAP Pert.": 75, "Materi BAP": 230, "Sub Materi BAP": 180,
            "Status": 130, "Keterangan": 240
        }
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_w.get(c, 120), anchor="w" if "Bahasan" in c or "Materi" in c or "Ket" in c else "center", stretch=True)

        self.tree.tag_configure("sesuai",   background="#C8E6C9")
        self.tree.tag_configure("acak",     background="#FFF9C4")
        self.tree.tag_configure("hilang",   background="#FFCDD2")

        vsb = ttk.Scrollbar(tbl_f, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_f, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_f.grid_rowconfigure(0, weight=1)
        tbl_f.grid_columnconfigure(0, weight=1)

    def _btn(self, parent, text, bg, cmd, font=("Arial", 11), h=2, w=None):
        kw = dict(text=text, bg=bg, fg=CLR_WHITE, font=font, height=h, relief="flat", cursor="hand2", command=cmd, bd=0)
        if w: kw["width"] = w
        return tk.Button(parent, **kw)

    def _set_status(self, msg):
        self.lbl_status.config(text=msg)
        self.root.update_idletasks()

    def _clear_form(self):
        self.ent_pert.delete(0, tk.END)
        self.txt_materi.delete("1.0", tk.END)
        self.txt_sub_materi.delete("1.0", tk.END)
        try: self.ent_tgl.set_date(datetime.now())
        except: pass

    def _clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_rps_pdf(self):
        file = filedialog.askopenfilename(title="Pilih file PDF RPS", filetypes=[("PDF Files", "*.pdf")])
        if not file: return
        self.log_message("⏳ Membaca RPS dari PDF…")
        try:
            extractor = PDFExtractor()
            count = extractor.extract_rps_to_db(file)
            self._set_status(f"✓ {count} data RPS berhasil dimuat.")
            self.log_message(f"✅ Ekstraksi selesai. {count} data RPS disimpan.")
            messagebox.showinfo("Sukses", f"Berhasil memasukkan {count} data RPS ke MySQL!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_bap_pdf(self):
        file = filedialog.askopenfilename(title="Pilih file PDF BAP", filetypes=[("PDF Files", "*.pdf")])
        if not file: return
        self.log_message("⏳ Membaca BAP dari PDF…")
        try:
            extractor = PDFExtractor()
            count = extractor.extract_bap_from_pdf(file)
            self.log_message(f"✅ Ekstraksi selesai. {count} data BAP berhasil dimuat.")
            if count > 0:
                self.validate_data(silent=True)
            messagebox.showinfo("Sukses", f"{count} data BAP berhasil dimuat & divalidasi!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_all(self):
        konfirm = messagebox.askyesno("Konfirmasi Reset", "Yakin ingin menghapus SEMUA data RPS dan BAP?")
        if not konfirm: return
        self.db.execute_query("DELETE FROM rps")
        self.db.execute_query("DELETE FROM bap")
        self._clear_table()
        self._clear_form()
        self.last_results = []
        self.last_persen = 0.0
        
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.insert(tk.END, "=== SYSTEM RESET: LOG CLEARED ===\n")
        self.txt_log.configure(state="disabled")
        
        self.lbl_status.config(text="Siap.") 
        messagebox.showinfo("Reset", "Semua data berhasil dibersihkan.")

    def add_bap(self):
        pert      = self.ent_pert.get().strip()
        tgl       = self.ent_tgl.get() 
        materi    = self.txt_materi.get("1.0", tk.END).strip()
        sub_materi = self.txt_sub_materi.get("1.0", tk.END).strip()

        if not pert or not materi:
            messagebox.showwarning("Peringatan", "Pertemuan dan Materi harus diisi!")
            return

        query = "INSERT INTO bap (pertemuan, tanggal, materi, sub_materi) VALUES (%s, %s, %s, %s)"
        self.db.execute_query(query, (pert, tgl, materi, sub_materi or None))
        self.log_message(f"➕ Berhasil menambahkan BAP manual Pertemuan {pert}.")
        self._clear_form()

    def validate_data(self, silent=False):
        self._clear_table()
        self.log_message("⚡ Memulai proses validasi & pencocokan kata...")

        self.last_results, self.last_persen = self.validator.validate()

        for res in self.last_results:
            status  = res['status']
            tag     = ("sesuai"  if status == "Sesuai" else
                       "acak"    if "Acak" in status else
                       "hilang")

            self.tree.insert("", "end", tags=(tag,), values=(
                res.get('rps_pertemuan') or '-',
                res.get('rps_pokok', '-'),
                res.get('rps_sub', ''),
                res.get('bap_pertemuan', '-'),
                res.get('bap_materi', ''),
                res.get('bap_sub', ''),
                status,
                res['keterangan']
            ))

        self._set_status(f"Validasi selesai — Kesesuaian: {self.last_persen}% | Total entri: {len(self.last_results)}")
        if not silent:
            messagebox.showinfo("Hasil Validasi", f"Kesesuaian RPS–BAP : {self.last_persen}%\nTotal baris hasil  : {len(self.last_results)}")

    def export_report(self):
        """Fungsi ekspor laporan standar ke file PDF Formal"""
        if not self.last_results:
            messagebox.showwarning("Peringatan", "Belum ada data validasi yang diproses. Silakan klik tombol Validasi dahulu.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Simpan Laporan Validasi ke PDF"
        )
        if not file_path:
            return
            
        try:
            from fpdf import FPDF
            
            # Filter pembersih karakter Unicode agar fpdf tidak crash saat render halaman
            def clean_pdf_text(text):
                if not text:
                    return ""
                t = str(text).replace("—", "-").replace("–", "-")
                return t.encode('latin-1', 'replace').decode('latin-1')
            
            class PDFReport(FPDF):
                def header(self):
                    self.set_fill_color(26, 35, 126) 
                    self.rect(0, 0, 210, 38, 'F')
                    self.set_text_color(255, 255, 255)
                    self.set_font("Arial", "B", 16)
                    self.cell(0, 8, "LAPORAN HASIL VALIDASI KESESUAIAN RPS VS BAP", ln=True, align="C")
                    self.set_font("Arial", "", 10)
                    self.cell(0, 6, "Program Studi Teknik Informatika - Universitas Komputer", ln=True, align="C")
                    self.ln(12)
                    
                def footer(self):
                    self.set_y(-15)
                    self.set_font("Arial", "I", 8)
                    self.set_text_color(128, 128, 128)
                    self.cell(0, 10, f"Halaman {self.page_no()} | Diunduh via Sistem Validasi Otomatis PBO", align="C")

            pdf = PDFReport()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=20)
            
            # --- Ringkasan Evaluasi ---
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 7, "1. RINGKASAN EVALUASI SISTEM", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            
            pdf.set_font("Arial", "", 10)
            pdf.cell(50, 6, "Tanggal Cetak Evaluasi")
            pdf.cell(0, 6, f": {datetime.now().strftime('%d %B %Y - %H:%M:%S')} WIB", ln=True)
            pdf.cell(50, 6, "Total Baris Diperiksa")
            pdf.cell(0, 6, f": {len(self.last_results)} Pertemuan", ln=True)
            
            pdf.set_font("Arial", "B", 11)
            pdf.cell(50, 8, "Persentase Kepatuhan")
            pdf.set_text_color(46, 125, 50) if self.last_persen >= 75 else pdf.set_text_color(198, 40, 40)
            pdf.cell(0, 8, f": {self.last_persen}% (Status Kelayakan Terlampir)", ln=True)
            pdf.ln(6)
            
            # --- Tabel Atribut ---
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 7, "2. DETAIL KESESUAIAN ATRIBUT", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(220, 225, 242)
            pdf.cell(15, 8, "Pert.RPS", border=1, align="C", fill=True)
            pdf.cell(15, 8, "Pert.BAP", border=1, align="C", fill=True)
            pdf.cell(40, 8, "Status Penilaian", border=1, align="C", fill=True)
            pdf.cell(120, 8, "Keterangan / Log Rekomendasi Modul", border=1, align="L", fill=True)
            pdf.ln()
            
            pdf.set_font("Arial", "", 9)
            for r in self.last_results:
                rps_p = clean_pdf_text(r.get('rps_pertemuan') or '-')
                bap_p = clean_pdf_text(r.get('bap_pertemuan') or '-')
                st    = clean_pdf_text(r.get('status', '-'))
                ket   = clean_pdf_text(r.get('keterangan', '-'))
                
                if "Sesuai" in st:
                    pdf.set_fill_color(200, 230, 201)
                elif "Acak" in st or "Tidak Sesuai" in st:
                    pdf.set_fill_color(255, 249, 196)
                else:
                    pdf.set_fill_color(255, 205, 210)
                    
                pdf.cell(15, 7, rps_p, border=1, align="C", fill=True)
                pdf.cell(15, 7, bap_p, border=1, align="C", fill=True)
                pdf.cell(40, 7, st, border=1, align="C", fill=True)
                
                x_pos = pdf.get_x()
                y_pos = pdf.get_y()
                pdf.multi_cell(120, 7, ket, border=1, align="L", fill=True)
                pdf.set_xy(x_pos + 120, y_pos)
                pdf.ln()
                
            pdf.ln(10)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 10)
            pdf.cell(130, 5, "")
            pdf.cell(0, 5, "Bandung, " + datetime.now().strftime('%d %B %Y'), ln=True, align="C")
            pdf.cell(130, 5, "")
            pdf.cell(0, 5, "Dosen Verifikator PBO,", ln=True, align="C")
            pdf.ln(18)
            pdf.cell(130, 5, "")
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 5, "_______________________", ln=True, align="C")
            
            pdf.output(file_path)
            self.log_message(f"📥 Dokumen Laporan PDF Resmi Sukses Diekspor ke: {file_path}")
            messagebox.showinfo("Ekspor Berhasil", "Berkas Laporan PDF Berhasil Dibuat!")
            
        except Exception as e:
            messagebox.showerror("Gagal Ekspor PDF", f"Terjadi galat saat merender dokumen PDF: {str(e)}")


# ── BLOK DEBUG TERMINAL AKTIF UTAMA ──────────────────────────────────────────
if __name__ == "__main__":
    print("[DEBUG] Membuat objek root Tkinter...")
    root = tk.Tk()
    
    print("[DEBUG] Menginisialisasi class RPSBApp...")
    app = RPSBApp(root)
    
    print("[DEBUG] Memulai root.mainloop() — Window harusnya muncul sekarang!")
    root.mainloop()