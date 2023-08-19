import sqlite3


def get_db_connection():
    conn = sqlite3.connect('gradegpt.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

answerTb= """CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
	student_id INTEGER,
    answer_text TEXT,
    FOREIGN KEY (question_id) REFERENCES questions(id)
)"""

modelAnswer = """CREATE TABLE model (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    answer_text TEXT,
    FOREIGN KEY (question_id) REFERENCES questions(id)
)"""

questionTb = """CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT
)"""