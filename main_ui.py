from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QDateEdit, QMessageBox, QFileDialog
from PyQt5.QtCore import QDate
from db.database import Database


class TaskTracker(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Task Tracker')
        self.setGeometry(100, 100, 600, 400)

        self.tab_widget = QTabWidget(self)

        self.login_tab = QWidget()
        self.tab_widget.addTab(self.login_tab, "Вход")
        self.setup_login_tab()

        self.tasks_tab = QWidget()
        self.tab_widget.addTab(self.tasks_tab, "Задачи")
        self.setup_tasks_tab()

        self.completed_tasks_tab = QWidget()
        self.tab_widget.addTab(self.completed_tasks_tab, "Завершенные задачи")
        self.setup_completed_tasks_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def setup_login_tab(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пароль")
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация", self)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.login_tab.setLayout(layout)

    def setup_tasks_tab(self):
        layout = QVBoxLayout()

        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Новая задача")
        layout.addWidget(self.task_input)

        self.due_date_input = QDateEdit(self)
        self.due_date_input.setDate(QDate.currentDate())
        layout.addWidget(self.due_date_input)

        self.add_task_button = QPushButton("Добавить задачу", self)
        self.add_task_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_button)

        self.task_table = QTableWidget(self)
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["Задача", "Срок выполнения", "Действия"])

        # Кнопки завершения и удаления задач в столбце
        self.task_table.setColumnWidth(2, 100)
        layout.addWidget(self.task_table)

        self.load_tasks_button = QPushButton("Загрузить задачи", self)
        self.load_tasks_button.clicked.connect(self.import_tasks)
        layout.addWidget(self.load_tasks_button)

        self.tasks_tab.setLayout(layout)

    def setup_completed_tasks_tab(self):
        layout = QVBoxLayout()

        self.completed_task_table = QTableWidget(self)
        self.completed_task_table.setColumnCount(2)
        self.completed_task_table.setHorizontalHeaderLabels(["Задача", "Срок выполнения"])
        layout.addWidget(self.completed_task_table)

        self.completed_tasks_tab.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = self.db.get_user(username, password)
        if user:
            self.current_user = user
            self.tab_widget.setCurrentIndex(1)
            self.load_tasks()
        else:
            self.show_error("Ошибка", "Неверное имя пользователя или пароль")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if self.db.add_user(username, password):
            self.show_message("Успех", "Регистрация успешна!")
        else:
            self.show_error("Ошибка", "Пользователь уже существует")

    def load_tasks(self):
        if not self.current_user:
            return

        self.task_table.setRowCount(0)
        tasks = self.db.get_tasks(self.current_user[0])
        for task_id, task_text, due_date, completed in tasks:
            row_position = self.task_table.rowCount()
            self.task_table.insertRow(row_position)
            self.task_table.setItem(row_position, 0, QTableWidgetItem(task_text))
            self.task_table.setItem(row_position, 1, QTableWidgetItem(due_date))

            complete_button = QPushButton("Завершить")
            complete_button.clicked.connect(lambda ch, task_id=task_id: self.complete_task(task_id))
            self.task_table.setCellWidget(row_position, 2, complete_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda ch, task_id=task_id: self.delete_task(task_id))
            self.task_table.setCellWidget(row_position, 3, delete_button)

        self.completed_task_table.setRowCount(0)
        completed_tasks = self.db.get_completed_tasks(self.current_user[0])
        for task_id, task_text, due_date in completed_tasks:
            row_position = self.completed_task_table.rowCount()
            self.completed_task_table.insertRow(row_position)
            self.completed_task_table.setItem(row_position, 0, QTableWidgetItem(task_text))
            self.completed_task_table.setItem(row_position, 1, QTableWidgetItem(due_date))

    def add_task(self):
        if not self.current_user:
            self.show_error("Ошибка", "Сначала войдите в систему")
            return

        task_text = self.task_input.text()
        due_date = self.due_date_input.date().toString("yyyy-MM-dd")
        if task_text:
            if self.db.add_task(self.current_user[0], task_text, due_date):
                self.task_input.clear()
                self.load_tasks()
            else:
                self.show_error("Ошибка", "Не удалось добавить задачу")

    def complete_task(self, task_id):
        if self.db.complete_task(task_id):
            self.load_tasks()

    def delete_task(self, task_id):
        if self.db.delete_task(task_id):
            self.load_tasks()
            self.show_message("Успех", "Задача удалена")

    def import_tasks(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                tasks = file.readlines()

            for task in tasks:
                task = task.strip()
                if task:
                    self.db.add_task(self.current_user[0], task, "2025-01-15")

            self.load_tasks()
            self.show_message("Успех", "Задачи импортированы!")

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)
