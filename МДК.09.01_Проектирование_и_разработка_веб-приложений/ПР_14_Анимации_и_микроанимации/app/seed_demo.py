from app import app

c = app.test_client()
people = [("ivanov01", "Иванов Иван Иванович", "ivanov@mail.ru", "8(912)345-67-89"),
          ("petrova02", "Петрова Анна Сергеевна", "petrova@yandex.ru", "8(903)111-22-33"),
          ("sidorov03", "Сидоров Пётр Алексеевич", "sidorov@gmail.com", "8(921)555-44-11")]
plan = {"ivanov01": [(1, "Банковская карта", "Большой зал"), (3, "Наличные на месте", "Онлайн-трансляция")],
        "petrova02": [(2, "Безналичный расчёт (для организаций)", "Малый зал")],
        "sidorov03": [(4, "Банковская карта", "Большой зал"), (1, "Наличные на месте", "Малый зал")]}
for login, fio, email, phone in people:
    c.post("/register", data=dict(login=login, password="Password1", full_name=fio, email=email, phone=phone))
    c.post("/login", data=dict(login=login, password="Password1"))
    for ev, pay, hall in plan[login]:
        c.post("/applications/new", data=dict(event_id=str(ev), payment_method=pay, hall=hall, comment=""))
    c.get("/logout")
c.post("/login", data=dict(login="Admin26", password="Demo2026"))
for app_id, st in [(2, 3), (3, 2), (4, 1), (5, 3)]:
    c.post(f"/admin/status/{app_id}", data=dict(status_id=st))
c.get("/logout")
c.post("/login", data=dict(login="ivanov01", password="Password1"))
c.post("/applications/2/review", data=dict(rating="5", text="Очень полезные доклады, особенно про нейросети в обучении. Спасибо организаторам!"))
print("Демо-данные добавлены")
