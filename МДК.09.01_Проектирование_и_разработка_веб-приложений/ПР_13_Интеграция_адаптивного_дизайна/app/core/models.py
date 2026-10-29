from werkzeug.security import check_password_hash, generate_password_hash

from .db import Database


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_login(self, login: str):
        return self.db.query_one(
            "SELECT u.*, r.name AS role FROM users u JOIN roles r ON r.id = u.role_id"
            " WHERE u.login = ?", (login,))

    def get(self, user_id: int):
        return self.db.query_one(
            "SELECT u.*, r.name AS role FROM users u JOIN roles r ON r.id = u.role_id"
            " WHERE u.id = ?", (user_id,))

    def create(self, login, password, full_name, email, phone) -> int:
        return self.db.execute(
            "INSERT INTO users(login, password_hash, full_name, email, phone) VALUES (?, ?, ?, ?, ?)",
            (login, generate_password_hash(password), full_name, email, phone))

    def authenticate(self, login: str, password: str):
        user = self.get_by_login(login)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None


class EventRepository:
    def __init__(self, db: Database):
        self.db = db

    def all(self):
        return self.db.query("SELECT * FROM events ORDER BY event_date")

    def get(self, event_id: int):
        return self.db.query_one("SELECT * FROM events WHERE id = ?", (event_id,))


class ApplicationRepository:
    BASE_SQL = (
        "SELECT a.*, e.title AS event_title, e.event_date, e.place, s.name AS status,"
        " u.full_name, u.login, u.phone, u.email,"
        " r.text AS review_text, r.rating AS review_rating"
        " FROM applications a"
        " JOIN events e ON e.id = a.event_id"
        " JOIN statuses s ON s.id = a.status_id"
        " JOIN users u ON u.id = a.user_id"
        " LEFT JOIN reviews r ON r.application_id = a.id")

    def __init__(self, db: Database):
        self.db = db

    def create(self, user_id, event_id, payment_method, hall, comment) -> int:
        return self.db.execute(
            "INSERT INTO applications(user_id, event_id, payment_method, hall, comment)"
            " VALUES (?, ?, ?, ?, ?)",
            (user_id, event_id, payment_method, hall, comment))

    def get(self, app_id: int):
        return self.db.query_one(self.BASE_SQL + " WHERE a.id = ?", (app_id,))

    def for_user(self, user_id: int):
        return self.db.query(self.BASE_SQL + " WHERE a.user_id = ? ORDER BY a.id DESC", (user_id,))

    def all(self, status_id: int | None = None):
        if status_id:
            return self.db.query(self.BASE_SQL + " WHERE a.status_id = ? ORDER BY a.id DESC", (status_id,))
        return self.db.query(self.BASE_SQL + " ORDER BY a.id DESC")

    def statuses(self):
        return self.db.query("SELECT * FROM statuses ORDER BY id")

    def set_status(self, app_id: int, status_id: int) -> None:
        self.db.execute("UPDATE applications SET status_id = ? WHERE id = ?", (status_id, app_id))


class ReviewRepository:
    COMPLETED_STATUS = "Завершено"

    def __init__(self, db: Database):
        self.db = db

    def can_review(self, application) -> bool:
        return (application is not None
                and application["status"] == self.COMPLETED_STATUS
                and application["review_text"] is None)

    def create(self, application_id: int, text: str, rating: int) -> int:
        return self.db.execute(
            "INSERT INTO reviews(application_id, text, rating) VALUES (?, ?, ?)",
            (application_id, text, rating))
