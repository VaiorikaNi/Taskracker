import sqlite3

class Database:
    def __init__(self, db_name="database.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_text TEXT NOT NULL,
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.connection.commit()

    def add_user(self, username, password):
        try:
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username, password):
        self.cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
        return self.cursor.fetchone()

    def add_task(self, user_id, task_text, due_date):
        try:
            self.cursor.execute('INSERT INTO tasks (user_id, task_text, due_date) VALUES (?, ?, ?)', (user_id, task_text, due_date))
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def get_tasks(self, user_id):
        self.cursor.execute('SELECT id, task_text, due_date, completed FROM tasks WHERE user_id = ? AND completed = 0', (user_id,))
        return self.cursor.fetchall()

    def get_completed_tasks(self, user_id):
        self.cursor.execute('SELECT id, task_text, due_date FROM tasks WHERE user_id = ? AND completed = 1', (user_id,))
        return self.cursor.fetchall()

    def complete_task(self, task_id):
        try:
            self.cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def delete_task(self, task_id):
        try:
            self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False
    def close(self):
        self.connection.close()
