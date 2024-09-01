import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QPushButton, QMessageBox, QGroupBox, QRadioButton, QInputDialog
from PyQt6.QtCore import Qt

class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Quiz")
        self.setGeometry(100, 100, 600, 400)
        
        self.create_main_menu()

        # Pastikan file skor tertinggi ada
        self.ensure_high_scores_file()

        # Muat skor tertinggi yang ada atau inisialisasi daftar kosong
        self.high_scores = self.load_high_scores()

    def get_high_scores_file_path(self):
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, "high_scores.json")

    def ensure_high_scores_file(self):
        file_path = self.get_high_scores_file_path()
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump([], file)

    def create_main_menu(self):
        self.main_menu = QWidget()
        self.setCentralWidget(self.main_menu)

        layout = QVBoxLayout()

        label_welcome = QLabel("Selamat datang di Aplikasi Quiz!")
        label_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_welcome)

        btn_start_quiz = QPushButton("Mulai Kuis")
        btn_start_quiz.clicked.connect(self.start_quiz)
        layout.addWidget(btn_start_quiz)

        btn_high_scores = QPushButton("Score Tertinggi")
        btn_high_scores.clicked.connect(self.show_high_scores)
        layout.addWidget(btn_high_scores)

        btn_exit = QPushButton("Keluar")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

        self.main_menu.setLayout(layout)

    def start_quiz(self):
        self.quiz_page = QuizPage(self)
        self.setCentralWidget(self.quiz_page)
        self.quiz_page.display_question()  # Mulai menampilkan pertanyaan pertama

    def show_high_scores(self):
        # Urutkan skor tertinggi dari yang tertinggi ke terendah
        sorted_high_scores = sorted(self.high_scores, key=lambda x: x['score'], reverse=True)

        high_scores_msg = "Skor Tertinggi:\n\n"
        if sorted_high_scores:
            for rank, score in enumerate(sorted_high_scores, start=1):
                high_scores_msg += f"{rank}. {score['name']}: {score['score']}\n"
        else:
            high_scores_msg += "Belum ada skor tertinggi yang disimpan."
        
        QMessageBox.information(self, "Score Tertinggi", high_scores_msg)

    def load_high_scores(self):
        file_path = self.get_high_scores_file_path()
        try:
            with open(file_path, "r") as file:
                high_scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            high_scores = []
        return high_scores

    def save_high_score(self, name, score):
        file_path = self.get_high_scores_file_path()
        self.high_scores.append({"name": name, "score": score})
        with open(file_path, "w") as file:
            json.dump(self.high_scores, file, indent=4)

    def return_to_main_menu(self):
        self.create_main_menu()

class QuizPage(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.current_question_index = 0  # Lacak pertanyaan saat ini
        self.questions = [
            {"question": "Negara mana yang mengalahkan Jepang pada saat Perang Dunia II?", "options": ["Amerika Serikat", "Kerajaan Inggris / Britania Raya", "Paris", "Uni Soviet"], "correct_index": 0, "explanation": "Selama Perang Dunia II, Jepun sebagian besar hanya menghadapi pasukan Amerika Serikat."},
            {"question": "Saya Punya 4 Mangga, lalu kalian minta 2. Sisa berapa mangganya?", "options": ["1", "4", "2", "6"], "correct_index": 1, "explanation": "4 lah, Belum tentu Saya kasih."},
            {"question": "Kera apa yang suci?", "options": ["Kera-Kera", "Keranjang", "Kera Sakti", "Keramat"], "correct_index": 3, "explanation": "Keramat lah kan benda yang dijaga kayak benda pusaka itu disebut keremat contoh : Keris Keramat."}
            # Tambahkan lebih banyak pertanyaan di sini
        ]

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_question = QLabel()
        layout.addWidget(self.label_question)

        self.group_options = QGroupBox("Pilih Jawaban:")
        self.radio_buttons = []
        vbox = QVBoxLayout()
        for i in range(4):
            rb = QRadioButton()
            self.radio_buttons.append(rb)
            vbox.addWidget(rb)
        self.group_options.setLayout(vbox)
        layout.addWidget(self.group_options)

        hbox = QHBoxLayout()
        self.btn_prev = QPushButton("Soal Sebelumnya")
        self.btn_prev.clicked.connect(self.prev_question)
        hbox.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Soal Selanjutnya")
        self.btn_next.clicked.connect(self.next_question)
        hbox.addWidget(self.btn_next)

        layout.addLayout(hbox)

        self.setLayout(layout)

    def display_question(self):
        question_data = self.questions[self.current_question_index]
        self.label_question.setText(question_data["question"])
        for i, rb in enumerate(self.radio_buttons):
            rb.setText(question_data["options"][i])
            rb.setChecked(False)  # Reset status radio button

        if "selected_index" in question_data and question_data["selected_index"] is not None:
            self.radio_buttons[question_data["selected_index"]].setChecked(True)

        # Perbarui teks tombol berikutnya jika ini adalah pertanyaan terakhir
        if self.current_question_index == len(self.questions) - 1:
            self.btn_next.setText("Selesaikan Quiz")
        else:
            self.btn_next.setText("Soal Selanjutnya")

        # Tampilkan atau sembunyikan tombol sebelumnya berdasarkan indeks pertanyaan saat ini
        if self.current_question_index > 0:
            self.btn_prev.show()
        else:
            self.btn_prev.hide()

    def save_selected_answer(self):
        selected_index = None
        for i, rb in enumerate(self.radio_buttons):
            if rb.isChecked():
                selected_index = i
                break
        self.questions[self.current_question_index]["selected_index"] = selected_index

    def next_question(self):
        if self.current_question_index < len(self.questions):
            # Simpan jawaban yang dipilih untuk pertanyaan saat ini
            self.save_selected_answer()
            
            # Tingkatkan indeks pertanyaan sebelum menampilkan pertanyaan berikutnya
            self.current_question_index += 1

            if self.current_question_index < len(self.questions):
                self.display_question()
            else:
                self.show_end_confirmation()
        else:
            self.show_end_confirmation()

    def prev_question(self):
        if self.current_question_index > 0:
            # Simpan jawaban yang dipilih untuk pertanyaan saat ini
            self.save_selected_answer()
            
            # Kurangi indeks pertanyaan sebelum menampilkan pertanyaan sebelumnya
            self.current_question_index -= 1
            self.display_question()

    def show_end_confirmation(self):
        msg_box = QMessageBox(QMessageBox.Icon.Question, "Konfirmasi", "Apakah Anda yakin ingin mengakhiri kuis?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.show_results()

    def show_results(self):
        correct_count = 0
        total_questions = len(self.questions)

        for i in range(total_questions):
            if "selected_index" in self.questions[i] and self.questions[i]["selected_index"] == self.questions[i]["correct_index"]:
                correct_count += 1

        result_msg = f"Jawaban Benar: {correct_count}/{total_questions}\n\n"
        for i in range(total_questions):
            if "selected_index" not in self.questions[i]:
                result_msg += f"Pertanyaan {i+1}: Anda tidak menjawab.\n"
            elif self.questions[i]["selected_index"] == self.questions[i]["correct_index"]:
                result_msg += f"Pertanyaan {i+1}: Jawaban Anda benar.\n"
            else:
                result_msg += f"Pertanyaan {i+1}: Jawaban Anda salah. Penjelasan: {self.questions[i]['explanation']}\n"

        result_msg += "\nMasukkan nama Anda untuk menyimpan skor tertinggi:"
        name, ok = QInputDialog.getText(self, "Simpan Skor Tertinggi", result_msg)

        if ok and name.strip():
            self.parent.save_high_score(name, correct_count)
            QMessageBox.information(self, "Skor Tertinggi Disimpan", f"Skor Anda telah disimpan sebagai skor tertinggi oleh {name}.")
            self.parent.return_to_main_menu()  # Kembali ke menu utama setelah menyimpan skor tertinggi
        else:
            QMessageBox.information(self, "Skor Tertinggi", "Skor tidak disimpan.")
            self.parent.return_to_main_menu()  # Kembali ke menu utama jika dibatalkan atau nama kosong

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizApp()
    window.show()
    sys.exit(app.exec())
