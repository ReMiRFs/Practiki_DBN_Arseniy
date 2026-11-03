import sqlite3
import sys

from run import load_app

app = load_app()
db_path = sys.modules["app"].db.path

with sqlite3.connect(db_path) as conn:
    if conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]:
        sys.exit(f"В базе {db_path} уже есть заявки — демо-данные не добавлены.")

c = app.test_client()


def login(user, password):
    c.post("/login", data=dict(login=user, password=password))


people = [("ivanov01", "Иванов Иван Иванович", "ivanov@mail.ru", "8(912)345-67-89"),
          ("petrova02", "Петрова Анна Сергеевна", "petrova@yandex.ru", "8(903)111-22-33"),
          ("sidorov03", "Сидоров Пётр Алексеевич", "sidorov@gmail.com", "8(921)555-44-11")]
plan = {"ivanov01": [(1, "Банковская карта", "Большой зал"), (3, "Наличные на месте", "Онлайн-трансляция")],
        "petrova02": [(2, "Безналичный расчёт (для организаций)", "Малый зал")],
        "sidorov03": [(4, "Банковская карта", "Большой зал"), (1, "Наличные на месте", "Малый зал")]}

for user, fio, email, phone in people:
    c.post("/register", data=dict(login=user, password="Password1", full_name=fio, email=email, phone=phone))
    login(user, "Password1")
    for event_id, pay, hall in plan[user]:
        c.post("/applications/new", data=dict(event_id=str(event_id), payment_method=pay, hall=hall, comment=""))
    c.get("/logout")

login("Admin26", "Demo2026")
for app_id, status in [(2, 3), (3, 2), (4, 1), (5, 3)]:
    c.post(f"/admin/status/{app_id}", data=dict(status_id=status))
c.get("/logout")

login("ivanov01", "Password1")
c.post("/applications/2/review",
       data=dict(rating="5", text="Очень полезные доклады, особенно про нейросети в обучении. Спасибо организаторам!"))

with sqlite3.connect(db_path) as conn:
    apps = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    revs = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
print(f"Демо-данные добавлены в {db_path}: заявок — {apps}, отзывов — {revs}")
