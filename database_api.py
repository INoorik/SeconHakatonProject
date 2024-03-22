import sqlite3

database_connection = sqlite3.connect("database.sqlite")


def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY, name TEXT, rating INTEGER NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Tasks(id INTEGER PRIMARY KEY, name TEXT, description TEXT, difficulty INTEGER, answer_key TEXT, file TExT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Submissions(id INTEGER PRIMARY KEY, user_id INTEGER, task_id INTEGER, verdict TEXT, time DATE, solution TEXT)")


class Submission:
    def __init__(self, user_id, task_id, verdict, time, solution):
        self.user_id = user_id
        self.task_id = task_id
        self.verdict = verdict
        self.time = time
        self.solution = solution


class User:
    def __init__(self, id, name, rating):
        self.id = id
        self.name = name
        self.rating = rating

    @staticmethod
    def pull_from_database(connection, id):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT rating, name FROM Users WHERE user_id=?
                       """,
                       [id])
        if cursor.rowcount() == 0:
            Exception("No such user")
        rating, name = cursor.fetchone()
        return User(id, name, rating)

    @staticmethod
    def if_exist(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT user_id FROM Users WHERE user_id=?
                       """,
                       [id])
        return cursor.rowcount() != 0

    def get_submissions(self, connection):
       cursor = connection.cursor()
       cursor.execute("""
                      SELECT user_id, task_id, verdict, time, solution FROM Submissions WHERE user_id=?
                      """, 
                      [self.id])
       for submission in cursor.fetchall():
           yield Submission(*submission)

    def update_rating(self, delta):
        self.rating += delta

    def flush(self, connection):
       cursor = connection.cursor()
       cursor.execute("""
                      REPLACE INTO Users(id, rating, name) VALUES (?, ?, ?) 
                      """,
                      [self.id, self.rating, self.name])


class Task:
    def __init__(self, id, name, description, difficulty, answer_key, file):
        self.id = id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.answer_key = answer_key
        self.file = file

    def get_submissions(self, connection):
       cursor = connection.cursor()
       cursor.execute("""
                      SELECT user_id, task_id, verdict, time, solution FROM Submissions WHERE task_id=?
                      """, 
                      [self.id])
       for submission in cursor.fetchall():
           yield Submission(*submission)

    @staticmethod
    def pull_from_database(connection, id):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT name, description, difficulty, answer_key FROM Tasks WHERE id=?
                       """,
                       [id])
        if cursor.rowcount() == 0:
            Exception("No such user")
        name, description, difficulty, answer_key = cursor.fetchone()
        return Task(id, name, description, difficulty, answer_key, file)

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT name, description, difficulty, answer_key FROM Tasks 
                       """
                       )
        for task in cursor.fetchall():
            yield Task(id, *task)
