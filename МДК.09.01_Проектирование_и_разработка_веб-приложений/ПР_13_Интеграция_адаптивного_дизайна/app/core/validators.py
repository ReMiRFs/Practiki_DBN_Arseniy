import re

LOGIN_RE = re.compile(r"^[A-Za-z0-9]{6,}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^8\(\d{3}\)\d{3}-\d{2}-\d{2}$")
NAME_RE = re.compile(r"^[А-Яа-яЁё\- ]+$")


class RegistrationValidator:
    def __init__(self, users_repo):
        self.users = users_repo

    def validate(self, form: dict) -> dict:
        errors = {}
        login = form.get("login", "")
        password = form.get("password", "")
        full_name = form.get("full_name", "")
        email = form.get("email", "")
        phone = form.get("phone", "")

        if not LOGIN_RE.match(login):
            errors["login"] = "Логин: только латиница и цифры, не менее 6 символов"
        elif self.users.get_by_login(login):
            errors["login"] = "Пользователь с таким логином уже существует"

        if len(password) < 8:
            errors["password"] = "Пароль должен содержать не менее 8 символов"

        if not full_name.strip() or not NAME_RE.match(full_name):
            errors["full_name"] = "ФИО: только кириллица, пробелы и дефис"

        if not EMAIL_RE.match(email):
            errors["email"] = "Введите email в формате name@example.ru"

        if not PHONE_RE.match(phone):
            errors["phone"] = "Телефон в формате 8(XXX)XXX-XX-XX"

        return errors


PAYMENT_METHODS = ["Банковская карта", "Наличные на месте", "Безналичный расчёт (для организаций)"]
HALLS = ["Большой зал", "Малый зал", "Онлайн-трансляция"]


class ApplicationValidator:
    def __init__(self, events_repo):
        self.events = events_repo

    def validate(self, form: dict) -> dict:
        errors = {}
        event_id = form.get("event_id", "")
        if not event_id.isdigit() or not self.events.get(int(event_id)):
            errors["event_id"] = "Выберите мероприятие из списка"
        if form.get("payment_method") not in PAYMENT_METHODS:
            errors["payment_method"] = "Выберите способ оплаты"
        if form.get("hall") not in HALLS:
            errors["hall"] = "Выберите помещение"
        if len(form.get("comment", "")) > 500:
            errors["comment"] = "Комментарий — не более 500 символов"
        return errors


class ReviewValidator:
    def validate(self, form: dict) -> dict:
        errors = {}
        text = form.get("text", "").strip()
        if len(text) < 10:
            errors["text"] = "Отзыв должен содержать не менее 10 символов"
        rating = form.get("rating", "")
        if rating not in {"1", "2", "3", "4", "5"}:
            errors["rating"] = "Поставьте оценку от 1 до 5"
        return errors
