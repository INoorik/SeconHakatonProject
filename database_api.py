import sqlite3

database_connection = sqlite3.connect("database.sqlite")


def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY, name TEXT, rating INTEGER NOT NULL)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Tasks(id INTEGER PRIMARY KEY, name TEXT, description TEXT, difficulty INTEGER, "
        "answer_key TEXT, file TExT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Submissions(id INTEGER PRIMARY KEY, user_id INTEGER, task_id INTEGER, "
        "verdict TEXT, time DATE, solution TEXT)")
    connection.commit()


class Submission:
    def __init__(self, user_id, task_id, verdict, time, solution):
        self.user_id = user_id
        self.task_id = task_id
        self.verdict = verdict
        self.time = time
        self.solution = solution

    def flush(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
                      INSERT INTO Submissions(user_id, task_id, verdict, time, solution) VALUES (?, ?, ?, ?, ?) 
                       """,
                       [self.user_id, self.task_id, self.verdict, self.time, self.solution])
        connection.commit()


class User:
    def __init__(self, id, name, rating):
        self.id = id
        self.name = name
        self.rating = rating

    @staticmethod
    def get_top(connection, count):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT id, name, rating FROM Users ORDER BY rating DESC
                       """)

        for user in cursor.fetchmany(count):
            yield User(*user)

    @staticmethod
    def pull_from_database(connection, id):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT rating, name FROM Users WHERE id=?
                       """,
                       [id])
        result = cursor.fetchone()
        if result is None:
            raise Exception("No such user")
        rating, name = result
        return User(id, name, rating)

    def is_exist(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT id FROM Users WHERE id=?
                       """,
                       [self.id])
        return not (cursor.fetchone() is None)

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
        connection.commit()


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
                       SELECT name, description, difficulty, answer_key, file FROM Tasks WHERE id=?
                       """,
                       [id])
        result = cursor.fetchone()
        if result is None:
            raise Exception("Could not find task")
        name, description, difficulty, answer_key, file = result
        return Task(id, name, description, difficulty, answer_key, file)

    @staticmethod
    def get_all(connection):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT id, name, description, difficulty, answer_key, file FROM Tasks ORDER BY id DESC
                       """
                       )
        for task in cursor.fetchall():
            yield Task(*task)

    def flush(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
                      REPLACE INTO Tasks(name, description, difficulty, answer_key, file) VALUES (?, ?, ?, ?, ?) 
                      """,
                       [self.name, self.description, self.difficulty, self.answer_key, self.file])
        connection.commit()
