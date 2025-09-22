import tkinter as tk
from tkinter import messagebox, ttk
import random
import re
import csv
import os

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Interaktif")
        self.geometry("700x550")

        # --- Manajemen Data Pengguna ---
        self.db_file = "quiz.csv"
        self.users = {}  # Format: {username: {'password': 'pass', 'score': -1}}
        self.current_user = None
        self.load_users()

        # Container utama untuk semua frame/halaman
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (WelcomePage, RegisterPage, LoginPage, QuizPage, ResultPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def load_users(self):
        """Memuat data pengguna dari file CSV saat aplikasi dimulai."""
        if not os.path.exists(self.db_file):
            return  # Jika file tidak ada, lewati
        
        with open(self.db_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            for rows in reader:
                if len(rows) == 3:
                    username, password, score = rows
                    self.users[username] = {'password': password, 'score': int(score)}

    def save_user(self, username, password):
        """Menyimpan pengguna baru ke file CSV."""
        with open(self.db_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Simpan skor awal sebagai -1
            writer.writerow([username, password, -1])
        # Update dictionary di memori
        self.users[username] = {'password': password, 'score': -1}
        
    def update_score(self, username, new_score):
        """Memperbarui skor pengguna di file CSV setelah kuis selesai."""
        self.users[username]['score'] = new_score
        
        # Baca semua data, update, lalu tulis kembali
        rows = []
        with open(self.db_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    row[2] = new_score
                rows.append(row)

        with open(self.db_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def start_quiz(self, username):
        self.current_user = username
        quiz_frame = self.frames["QuizPage"]
        quiz_frame.start_new_quiz()
        self.show_frame("QuizPage")
        
    def show_previous_result(self, username, score):
        """Langsung menampilkan halaman hasil untuk pengguna yang sudah ada."""
        self.current_user = username
        result_frame = self.frames["ResultPage"]
        result_frame.display_results(score) # Panggil metode untuk menampilkan hasil
        self.show_frame("ResultPage")

# --- Halaman-halaman Aplikasi ---

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        tk.Label(self, text="Selamat Datang di Quiz Interaktif!", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=(50, 20))
        tk.Label(self, text="Program ini hanya untuk pengguna baru. Silakan mendaftar.", font=("Arial", 14), bg="#f0f0f0").pack(pady=10)

        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(pady=50)

        tk.Button(btn_frame, text="Daftar", font=("Arial", 14, "bold"), bg="blue", fg="white", width=15, height=2,
                  command=lambda: controller.show_frame("RegisterPage")).pack(side="left", padx=20)
        
        tk.Button(btn_frame, text="Login", font=("Arial", 14, "bold"), bg="green", fg="white", width=15, height=2,
                  command=lambda: controller.show_frame("LoginPage")).pack(side="left", padx=20)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        self.nama_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(self, text="Halaman Pendaftaran", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=30)
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(pady=10, padx=50)

        tk.Label(input_frame, text="Nama Pengguna:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=5)
        self.nama_entry = tk.Entry(input_frame, textvariable=self.nama_var, font=("Arial", 12), width=30)
        self.nama_entry.grid(row=0, column=1, pady=5)
        self.nama_hint = tk.Label(input_frame, text="Minimal 3 karakter, tanpa spasi.", font=("Arial", 9), fg="gray", bg="#f0f0f0")
        self.nama_hint.grid(row=1, column=1, sticky="w")

        tk.Label(input_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(input_frame, textvariable=self.password_var, font=("Arial", 12), width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        self.password_hint = tk.Label(input_frame, text="Minimal 5 karakter.", font=("Arial", 9), fg="gray", bg="#f0f0f0")
        self.password_hint.grid(row=3, column=1, sticky="w")

        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Daftar", font=("Arial", 12, "bold"), bg="green", fg="white", width=15, command=self.register_user).pack()
        tk.Button(btn_frame, text="Kembali", font=("Arial", 10), command=lambda: controller.show_frame("WelcomePage")).pack(pady=10)

    def register_user(self):
        username = self.nama_var.get()
        password = self.password_var.get()
        
        if len(username) < 3 or ' ' in username:
            messagebox.showerror("Error", "Nama pengguna tidak valid. Minimal 3 karakter dan tanpa spasi.")
            return
        if len(password) < 5:
            messagebox.showerror("Error", "Password terlalu pendek. Minimal 5 karakter.")
            return
        if username in self.controller.users:
            messagebox.showerror("Error", "Nama pengguna sudah terdaftar. Silakan login.")
            return

        self.controller.save_user(username, password)
        messagebox.showinfo("Sukses", "Pendaftaran berhasil! Silakan login.")
        self.controller.show_frame("LoginPage")

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        
        self.nama_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(self, text="Halaman Login", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=30)
        input_frame = tk.Frame(self, bg="#f0f0f0")
        input_frame.pack(pady=10, padx=50)

        tk.Label(input_frame, text="Nama Pengguna:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=10)
        tk.Entry(input_frame, textvariable=self.nama_var, font=("Arial", 12), width=30).grid(row=0, column=1, pady=10)

        tk.Label(input_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(input_frame, textvariable=self.password_var, font=("Arial", 12), width=30, show="*").grid(row=1, column=1, pady=10)

        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Login", font=("Arial", 12, "bold"), bg="green", fg="white", width=15, command=self.login_user).pack()
        tk.Button(btn_frame, text="Kembali", font=("Arial", 10), command=lambda: controller.show_frame("WelcomePage")).pack(pady=10)

    def login_user(self):
        username = self.nama_var.get()
        password = self.password_var.get()
        user_data = self.controller.users.get(username)

        if user_data and user_data['password'] == password:
            # Cek skor pengguna
            score = user_data['score']
            if score == -1:
                # Skor -1 berarti pengguna baru, mulai kuis
                messagebox.showinfo("Sukses", f"Selamat datang, {username}! Kuis akan dimulai.")
                self.controller.start_quiz(username)
            else:
                # Pengguna sudah pernah main, langsung tampilkan hasil
                messagebox.showinfo("Info", f"Anda sudah pernah mengerjakan kuis ini, {username}. Menampilkan hasil Anda.")
                self.controller.show_previous_result(username, score)
        else:
            messagebox.showerror("Error", "Nama pengguna atau password salah.")

class QuizPage(tk.Frame):
    # ... (Isi kelas QuizPage sama persis seperti kode sebelumnya, tidak ada perubahan)
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        # Pindahkan data & state kuis ke sini
        self.questions = [
            {
                "question": "Apa konsep utama dari 'Event-Driven Programming' (EDP) yang ditunjukkan pada aplikasi kalkulator?",
                "options": ["Program berjalan lurus dari atas ke bawah", "Alur program ditentukan oleh aksi pengguna (misal: klik tombol)", "Program hanya menggunakan command-line", "Semua logika ditulis dalam satu fungsi"],
                "correct": 1
            },
            {
                "question": "Di aplikasi Paint, metode apa yang digunakan untuk mengikat event keyboard (seperti Ctrl+S) ke sebuah fungsi?",
                "options": ["self.window.command()", "self.canvas.on_key_press()", "self.window.bind()", "self.window.after()"],
                "correct": 2
            },
            {
                "question": "Bagaimana aplikasi Konverter Suhu mengelola 'state' sehingga perubahan di satu field otomatis mengupdate field lain?",
                "options": ["Dengan loop 'while True'", "Dengan metode trace_add() pada variabel Tkinter", "Dengan menulis ulang nilai setiap detik", "Dengan tombol 'Update' manual"],
                "correct": 1
            },
            {
                "question": "Aplikasi Registrasi menggunakan progress bar untuk melacak kelengkapan form. Ini adalah contoh dari...?",
                "options": ["Animasi kompleks", "Event handling keyboard", "Real-time state management", "Validasi sisi server"],
                "correct": 2
            },
            {
                "question": "Pada aplikasi Stopwatch, metode `window.after()` digunakan untuk apa?",
                "options": ["Menghentikan program setelah jeda waktu", "Menjadwalkan eksekusi fungsi setelah delay tertentu", "Membuat animasi tombol", "Mengikat event mouse"],
                "correct": 1
            },
            {
                "question": "Validasi input secara real-time pada form registrasi (misal: memeriksa format email saat diketik) meningkatkan aspek...?",
                "options": ["Kecepatan kompilasi", "User Experience (UX)", "Ukuran file aplikasi", "Penggunaan memori"],
                "correct": 1
            },
            {
                "question": "Widget Tkinter apa yang digunakan di aplikasi Paint sebagai media untuk menggambar?",
                "options": ["tk.Frame", "tk.Label", "tk.Canvas", "tk.Text"],
                "correct": 2
            },
            {
                "question": "Mengubah status tombol 'DAFTAR' menjadi `state=tk.DISABLED` sampai semua field valid adalah implementasi dari?",
                "options": ["Mencegah pengguna berinteraksi sebelum kondisi terpenuhi", "Membuat aplikasi lebih cepat", "Menghemat daya baterai", "Hanya sebagai hiasan visual"],
                "correct": 0
            },
            {
                "question": "Pada Stopwatch, lap time ditampilkan dalam sebuah list. Widget yang paling sesuai untuk ini adalah...?",
                "options": ["tk.Entry", "tk.Listbox", "tk.Spinbox", "tk.Scale"],
                "correct": 1
            },
            {
                "question": "Timer countdown pada setiap soal di kuis ini adalah contoh dari event berbasis...?",
                "options": ["Input pengguna (User-generated event)", "Waktu (Temporal event)", "Jaringan (Network event)", "Sistem Operasi (System event)"],
                "correct": 1
            }
        ]
        self.buat_interface()
        
    def start_new_quiz(self):
        # Reset semua state kuis
        random.shuffle(self.questions)
        self.current_question_index = 0
        self.score = 0
        self.time_left = 15
        self.timer_job = None
        self.answer_submitted = False
        self.selected_answer.set(-1)
        
        # Reset UI
        self.score_label.config(text="Skor: 0")
        self.progress_var.set(0)
        self.clear_feedback()
        self.submit_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.NORMAL)

        self.load_question()
        self.bind_shortcuts()
        self.start_timer()

    def buat_interface(self):
        # State Management untuk QuizPage
        self.selected_answer = tk.IntVar(value=-1)

        # Frame utama
        main_frame = tk.Frame(self, padx=20, pady=20, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame Header
        header_frame = tk.Frame(main_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        self.score_label = tk.Label(header_frame, text="Skor: 0", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.score_label.pack(side=tk.LEFT)

        self.timer_label = tk.Label(header_frame, text="Waktu: 15", font=("Arial", 12, "bold"), fg="red", bg="#f0f0f0")
        self.timer_label.pack(side=tk.RIGHT)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=len(self.questions))
        self.progress_bar.pack(fill=tk.X, pady=10)

        # Frame Soal
        self.question_label = tk.Label(
            main_frame, text="Pertanyaan...", font=("Arial", 14, "bold"),
            wraplength=650, justify="center", bg="#f0f0f0"
        )
        self.question_label.pack(pady=20)

        # Opsi Jawaban
        self.options_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.options_frame.pack(pady=10)
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(
                self.options_frame, text=f"Opsi {i+1}", variable=self.selected_answer,
                value=i, font=("Arial", 12), bg="#f0f0f0",
                command=lambda: self.submit_btn.config(state=tk.NORMAL)
            )
            rb.pack(anchor="w", pady=5)
            self.radio_buttons.append(rb)

        # Frame Feedback
        self.feedback_frame = tk.Frame(main_frame, height=30, bg="#f0f0f0")
        self.feedback_frame.pack(fill=tk.X, pady=10)
        self.feedback_label = tk.Label(self.feedback_frame, text="", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.feedback_label.pack()

        # Tombol Kontrol
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(pady=20)

        self.submit_btn = tk.Button(
            control_frame, text="Submit (Enter)", font=("Arial", 12, "bold"),
            bg="#4CAF50", fg="white", width=15, height=2,
            command=self.submit_answer, state=tk.DISABLED
        )
        self.submit_btn.pack(side=tk.LEFT, padx=10)

        self.skip_btn = tk.Button(
            control_frame, text="Skip (Esc)", font=("Arial", 12, "bold"),
            bg="#f44336", fg="white", width=15, height=2,
            command=self.skip_question
        )
        self.skip_btn.pack(side=tk.LEFT, padx=10)

    # Metode lainnya (load_question, start_timer, submit_answer, etc.) sama seperti sebelumnya
    # ... (Saya salin metode-metode tersebut di bawah ini untuk kelengkapan)

    def load_question(self):
        self.answer_submitted = False
        self.selected_answer.set(-1)
        self.submit_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.NORMAL)

        if self.current_question_index >= len(self.questions):
            # Kuis selesai, update skor dan tampilkan hasil
            self.controller.update_score(self.controller.current_user, self.score)
            self.show_result()
            return

        self.progress_var.set(self.current_question_index)
        question_data = self.questions[self.current_question_index]
        self.question_label.config(text=question_data["question"])

        for i, option in enumerate(question_data["options"]):
            self.radio_buttons[i].config(text=option, state=tk.NORMAL)
        
        self.time_left = 15
        self.start_timer()

    def start_timer(self):
        if hasattr(self, 'timer_job') and self.timer_job:
            self.after_cancel(self.timer_job)
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0 and not self.answer_submitted:
            self.timer_label.config(text=f"Waktu: {self.time_left}")
            self.time_left -= 1
            self.timer_job = self.after(1000, self.update_timer)
        elif not self.answer_submitted:
            self.timer_label.config(text="Waktu Habis!")
            self.skip_question()

    def submit_answer(self, event=None):
        if self.selected_answer.get() == -1: return
        self.answer_submitted = True
        self.disable_controls()

        question_data = self.questions[self.current_question_index]
        correct_answer_index = question_data["correct"]
        user_answer_index = self.selected_answer.get()

        if user_answer_index == correct_answer_index:
            self.score += 10
            self.score_label.config(text=f"Skor: {self.score}")
            self.visual_feedback(True)
        else:
            self.visual_feedback(False)

    def skip_question(self, event=None):
        if not self.answer_submitted:
            self.answer_submitted = True
            self.disable_controls()
            self.feedback_label.config(text="Soal Dilewati", fg="orange")
            self.feedback_frame.config(bg="orange")
            self.after(1000, self.next_question)
    
    def disable_controls(self):
        self.submit_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.DISABLED)

    def visual_feedback(self, is_correct):
        if is_correct:
            self.feedback_label.config(text="BENAR!", fg="white")
            new_color = "#4CAF50"
        else:
            correct_text = self.questions[self.current_question_index]["options"][self.questions[self.current_question_index]["correct"]]
            self.feedback_label.config(text=f"SALAH! Jawaban: {correct_text}", fg="white")
            new_color = "#f44336"
        
        self.feedback_frame.config(bg=new_color)
        self.after(1500, self.next_question)

    def next_question(self):
        self.clear_feedback()
        self.current_question_index += 1
        self.load_question()
    
    def clear_feedback(self):
        self.feedback_label.config(text="")
        self.feedback_frame.config(bg="#f0f0f0")

    def show_result(self):
        # Alihkan ke ResultPage
        result_page = self.controller.frames["ResultPage"]
        result_page.display_results(self.score)
        self.controller.show_frame("ResultPage")

    def bind_shortcuts(self):
        # Binding event ke window utama untuk konsistensi
        self.controller.bind("<Return>", lambda event: self.submit_btn.invoke() if self.submit_btn['state'] == tk.NORMAL else None)
        self.controller.bind("<Escape>", lambda event: self.skip_btn.invoke() if self.skip_btn['state'] == tk.NORMAL else None)

class ResultPage(tk.Frame):
    """Halaman terpisah untuk menampilkan hasil."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        
        self.result_frame = tk.Frame(self, padx=20, pady=20, bg="#f0f0f0")
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(self.result_frame, text="KUIS SELESAI!", font=("Arial", 24, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=20)
        
        self.user_label = tk.Label(self.result_frame, text="", font=("Arial", 16), bg="#f0f0f0")
        self.user_label.pack(pady=5)
        
        self.score_label = tk.Label(self.result_frame, text="", font=("Arial", 18), bg="#f0f0f0")
        self.score_label.pack(pady=10)
        
        self.detail_label = tk.Label(self.result_frame, text="", font=("Arial", 14), bg="#f0f0f0")
        self.detail_label.pack(pady=10)
        
        tk.Button(self.result_frame, text="Keluar & Kembali ke Awal", command=lambda: self.controller.show_frame("WelcomePage"), font=("Arial", 12, "bold"), bg="blue", fg="white").pack(pady=20)
    
    def display_results(self, score):
        username = self.controller.current_user
        total_questions = 10 # Hardcoded, sesuaikan jika soal dinamis
        percentage = (score / (total_questions * 10)) * 100

        self.user_label.config(text=f"Hasil untuk {username}:")
        self.score_label.config(text=f"Skor Akhir Anda: {score}")
        self.detail_label.config(text=f"Anda menjawab {score//10} dari {total_questions} soal dengan benar ({percentage:.1f}%)")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
