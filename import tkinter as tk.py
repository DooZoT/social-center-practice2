import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


class SocialCenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЦСОН: учёт социальных услуг")
        self.root.geometry("700x600")

        # Подключение к БД
        self.conn = sqlite3.connect("social_center.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        # Создание интерфейса
        self.create_widgets()
        self.load_requests()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT,
                snils TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Новая заявка", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Фамилия
        tk.Label(input_frame, text="Фамилия:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_last_name = tk.Entry(input_frame, width=40)
        self.entry_last_name.grid(row=0, column=1, pady=5, padx=5)

        # Имя
        tk.Label(input_frame, text="Имя:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_first_name = tk.Entry(input_frame, width=40)
        self.entry_first_name.grid(row=1, column=1, pady=5, padx=5)

        # Отчество
        tk.Label(input_frame, text="Отчество:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_middle_name = tk.Entry(input_frame, width=40)
        self.entry_middle_name.grid(row=2, column=1, pady=5, padx=5)

        # СНИЛС
        tk.Label(input_frame, text="СНИЛС:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_snils = tk.Entry(input_frame, width=40)
        self.entry_snils.grid(row=3, column=1, pady=5, padx=5)

        # Телефон
        tk.Label(input_frame, text="Телефон:").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_phone = tk.Entry(input_frame, width=40)
        self.entry_phone.grid(row=4, column=1, pady=5, padx=5)

        # Услуга
        tk.Label(input_frame, text="Услуга:").grid(row=5, column=0, sticky="w", pady=5)
        self.combo_service = ttk.Combobox(input_frame, width=37, state="readonly")
        self.combo_service["values"] = [
            "Социально-бытовая",
            "Социально-медицинская",
            "Социально-психологическая",
            "Социально-педагогическая",
            "Социально-трудовая",
            "Социально-правовая"
        ]
        self.combo_service.current(0)
        self.combo_service.grid(row=5, column=1, pady=5, padx=5)

        # Кнопка отправки
        btn_submit = tk.Button(input_frame, text="Отправить заявку", command=self.submit_request)
        btn_submit.grid(row=6, column=0, columnspan=2, pady=10)

        # Рамка для списка заявок
        list_frame = tk.LabelFrame(self.root, text="Сохранённые заявки", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Выпадающий список
        self.combo_requests = ttk.Combobox(list_frame, state="readonly", width=90)
        self.combo_requests.pack(fill="x", pady=5)
        self.combo_requests.bind("<<ComboboxSelected>>", self.show_details)

        # Поле для отображения деталей
        self.text_details = tk.Text(list_frame, height=6, width=90, wrap="word")
        self.text_details.pack(fill="both", expand=True, pady=5)

        # Рамка для кнопок
        buttons_frame = tk.Frame(list_frame)
        buttons_frame.pack(fill="x", pady=5)

        # Кнопка обновления
        btn_refresh = tk.Button(buttons_frame, text="Обновить список", command=self.load_requests)
        btn_refresh.pack(side="left", padx=5)

        # Кнопка удаления заявки
        btn_delete = tk.Button(buttons_frame, text="Удалить заявку", command=self.delete_request)
        btn_delete.pack(side="left", padx=5)

    def submit_request(self):
        last_name = self.entry_last_name.get().strip()
        first_name = self.entry_first_name.get().strip()
        middle_name = self.entry_middle_name.get().strip()
        snils = self.entry_snils.get().strip()
        phone = self.entry_phone.get().strip()
        service = self.combo_service.get()

        # Проверка обязательных полей
        if not last_name or not first_name or not snils or not phone:
            messagebox.showwarning("Ошибка", "Заполните обязательные поля: Фамилия, Имя, СНИЛС, Телефон")
            return

        # Проверка СНИЛС (11 цифр)
        if not snils.isdigit() or len(snils) != 11:
            messagebox.showwarning("Ошибка", "СНИЛС должен состоять из 11 цифр")
            return

        # Проверка телефона (только цифры, +, -)
        if not all(c.isdigit() or c in "+-() " for c in phone):
            messagebox.showwarning("Ошибка", "Некорректный формат телефона")
            return

        # Сохранение в БД
        self.cursor.execute("""
            INSERT INTO requests (last_name, first_name, middle_name, snils, phone, service)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (last_name, first_name, middle_name, snils, phone, service))
        self.conn.commit()

        messagebox.showinfo("Успех", "Заявка успешно сохранена!")

        # Очистка полей
        self.entry_last_name.delete(0, tk.END)
        self.entry_first_name.delete(0, tk.END)
        self.entry_middle_name.delete(0, tk.END)
        self.entry_snils.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.combo_service.current(0)

        # Обновление списка
        self.load_requests()

    def delete_request(self):
        selected = self.combo_requests.get()

        if selected == "— Выберите заявку —" or selected not in self.requests_data:
            messagebox.showwarning("Ошибка", "Сначала выберите заявку для удаления")
            return

        req_id, ln, fn, mn, snils, phone, service, created = self.requests_data[selected]

        # Подтверждение удаления
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заявку?\n\n"
            f"ID: {req_id}\n"
            f"Фамилия: {ln}\n"
            f"Имя: {fn}\n"
            f"СНИЛС: {snils}\n"
            f"Услуга: {service}"
        )

        if not confirm:
            return

        # Удаление из БД
        self.cursor.execute("DELETE FROM requests WHERE id = ?", (req_id,))
        self.conn.commit()

        messagebox.showinfo("Успех", "Заявка успешно удалена!")

        # Обновление списка
        self.load_requests()

    def load_requests(self):
        self.cursor.execute("""
            SELECT id, last_name, first_name, middle_name, snils, phone, service, created_at
            FROM requests ORDER BY id DESC
        """)
        rows = self.cursor.fetchall()

        self.requests_data = {}
        display_values = ["— Выберите заявку —"]

        for row in rows:
            req_id, ln, fn, mn, snils, phone, service, created = row
            display = f"#{req_id} | {ln} {fn} {mn or ''} | {service} | {created}"
            display_values.append(display)
            self.requests_data[display] = row

        self.combo_requests["values"] = display_values
        self.combo_requests.current(0)
        self.text_details.delete("1.0", tk.END)

    def show_details(self, event=None):
        selected = self.combo_requests.get()
        if selected == "— Выберите заявку —" or selected not in self.requests_data:
            self.text_details.delete("1.0", tk.END)
            return

        req_id, ln, fn, mn, snils, phone, service, created = self.requests_data[selected]
        details = (
            f"ID: {req_id}\n"
            f"Фамилия: {ln}\n"
            f"Имя: {fn}\n"
            f"Отчество: {mn or '—'}\n"
            f"СНИЛС: {snils}\n"
            f"Телефон: {phone}\n"
            f"Услуга: {service}\n"
            f"Дата создания: {created}"
        )
        self.text_details.delete("1.0", tk.END)
        self.text_details.insert("1.0", details)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = SocialCenterApp(root)
    root.mainloop()