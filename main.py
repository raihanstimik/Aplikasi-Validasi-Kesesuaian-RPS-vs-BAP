import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import DatabaseManager
from models import Validator
from pdf_extractor import PDFExtractor

class RPSBAPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Validasi RPS vs BAP - Pemrograman Berorientasi Objek")
        self.root.geometry("1150x780")
        
        self.db = DatabaseManager()
        self.validator = Validator(self.db)
        
        self.create_ui()

    def create_ui(self):
        tk.Label(self.root, text="Aplikasi Validasi Kesesuaian RPS vs BAP\nPBO Python + MySQL", 
                 font=("Arial", 16, "bold"), justify="center").pack(pady=15)

        # Tombol Load PDF
        tk.Button(self.root, text="📄 1. Load RPS dari PDF ke MySQL", 
                  bg="#4CAF50", fg="white", font=("Arial", 12), height=2, width=50,
                  command=self.load_pdf).pack(pady=8)

        # Input BAP
        input_frame = tk.LabelFrame(self.root, text=" 2. Input Data BAP ", padx=15, pady=10)
        input_frame.pack(pady=10, fill="x", padx=30)

        tk.Label(input_frame, text="Pertemuan Ke-:").grid(row=0, column=0, sticky="w")
        self.ent_pert = tk.Entry(input_frame, width=8)
        self.ent_pert.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Tanggal (YYYY-MM-DD):").grid(row=0, column=2, sticky="w", padx=10)
        self.ent_tgl = tk.Entry(input_frame, width=15)
        self.ent_tgl.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Materi yang Diajarkan:").grid(row=1, column=0, sticky="nw", pady=5)
        self.txt_materi = tk.Text(input_frame, height=4, width=70)
        self.txt_materi.grid(row=1, column=1, columnspan=3, pady=5)

        tk.Button(input_frame, text="Tambahkan ke BAP", bg="#FF9800", fg="white", 
                  command=self.add_bap).grid(row=2, column=1, pady=8)

        # Tombol Validasi
        tk.Button(self.root, text="🔍 3. Validasi RPS vs BAP", 
                  bg="#2196F3", fg="white", font=("Arial", 12), height=2, width=50,
                  command=self.validate_data).pack(pady=15)

        # Tabel Hasil
        columns = ("RPS", "BAP", "Status", "Keterangan")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=18)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill="both", expand=True, padx=25, pady=10)

    def load_pdf(self):
        file = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if file:
            extractor = PDFExtractor()
            count = extractor.extract_rps_to_db(file)
            messagebox.showinfo("Sukses", f"Berhasil memasukkan {count} data RPS!")

    def add_bap(self):
        pert = self.ent_pert.get().strip()
        tgl = self.ent_tgl.get().strip()
        materi = self.txt_materi.get("1.0", tk.END).strip()

        if not pert or not materi:
            messagebox.showwarning("Peringatan", "Pertemuan dan Materi harus diisi!")
            return

        query = "INSERT INTO bap (pertemuan, tanggal, materi) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (pert, tgl or None, materi))
        
        messagebox.showinfo("Sukses", f"Data BAP Pertemuan {pert} berhasil ditambahkan!")
        
        # Clear form
        self.ent_pert.delete(0, tk.END)
        self.ent_tgl.delete(0, tk.END)
        self.txt_materi.delete("1.0", tk.END)

    def validate_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        results, persentase = self.validator.validate()

        for res in results:
            self.tree.insert("", "end", values=(
                res.get('rps_pertemuan', '-'),
                res.get('bap_pertemuan', '-'),
                res['status'],
                res['keterangan']
            ))

        messagebox.showinfo("Hasil Validasi", 
                          f"Kesesuaian RPS-BAP: {persentase}%\n"
                          f"Total RPS: {len(results)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RPSBAPApp(root)
    root.mainloop()