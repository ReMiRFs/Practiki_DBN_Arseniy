import csv
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5000').rstrip('/')
SUFFIX = time.strftime('%H%M%S')
VALID = dict(login='ivanov01', password='Password1', full_name='Тестов Тест Тестович',
             phone='8(999)123-45-67', email='test01@mail.ru')
n = [0]


def new_login():
    n[0] += 1
    return f'auto{SUFFIX}{n[0]:02d}'


REG = [
    ('Р-01', 'Корректные данные', dict(VALID, login=new_login()), True),
    ('Р-02', 'Логин 6 символов (граница)', dict(VALID, login='a' + SUFFIX[:5]), True),
    ('Р-03', 'Логин 5 символов', dict(VALID, login='abc12'), False),
    ('Р-04', 'Логин кириллицей', dict(VALID, login='иванов01'), False),
    ('Р-06', 'Логин занят', dict(VALID, login='ivanov01'), False),
    ('Р-07', 'Логин занят, другой регистр', dict(VALID, login='IVANOV01'), False),
    ('Р-09', 'Пароль 7 символов', dict(VALID, login=new_login(), password='Abcde12'), False),
    ('Р-10', 'Пароль из пробелов', dict(VALID, login=new_login(), password=' ' * 8), False),
    ('Р-11', 'ФИО латиницей', dict(VALID, login=new_login(), full_name='Ivanov Ivan'), False),
    ('Р-13', 'ФИО без букв', dict(VALID, login=new_login(), full_name='- -'), False),
    ('Р-14', 'Телефон без маски', dict(VALID, login=new_login(), phone='89123456789'), False),
    ('Р-16', 'Email без @', dict(VALID, login=new_login(), email='test.mail.ru'), False),
    ('Р-18', 'Все поля пустые', {k: '' for k in VALID}, False),
    ('Р-19', 'Логин 255 символов', dict(VALID, login='b' * 250 + SUFFIX[:5]), False),
]
LOGIN = [
    ('А-01', 'Верные данные участника', 'ivanov01', 'Password1', True),
    ('А-03', 'Неверный пароль', 'ivanov01', 'WrongPass1', False),
    ('А-04', 'Несуществующий логин', 'nouser999', 'Password1', False),
    ('А-06', 'SQL-инъекция', "' OR '1'='1", "' OR '1'='1", False),
]


def main():
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for tid, title, data, expect_ok in REG:
            page.goto(BASE + '/register')
            for field, value in data.items():
                page.fill(f'[name={field}]', value)
            page.click('button[type=submit]')
            page.wait_for_load_state()
            page.wait_for_timeout(200)
            ok = page.url.endswith('/login')
            errors = page.eval_on_selector_all('.field__error', 'e => e.map(x => x.textContent.trim()).filter(Boolean)')
            actual = 'зарегистрирован' if ok else 'отказ: ' + '; '.join(errors)
            rows.append((tid, title, 'успех' if expect_ok else 'отказ', actual, 'PASS' if ok == expect_ok else 'FAIL'))
        for tid, title, lg, pw, expect_ok in LOGIN:
            page.goto(BASE + '/logout')
            page.goto(BASE + '/login')
            page.fill('[name=login]', lg)
            page.fill('[name=password]', pw)
            page.click('button[type=submit]')
            page.wait_for_load_state()
            ok = not page.url.endswith('/login')
            rows.append((tid, title, 'вход' if expect_ok else 'отказ', 'вход выполнен' if ok else 'вход не выполнен',
                         'PASS' if ok == expect_ok else 'FAIL'))
        browser.close()

    out = Path(__file__).with_name('results.csv')
    with out.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['ID', 'Проверка', 'Ожидание', 'Факт', 'Итог'])
        w.writerows(rows)
    for r in rows:
        print(f'{r[4]:4}  {r[0]:5} {r[1]:32} -> {r[3][:70]}')
    print(f"\nPASS: {sum(r[4] == 'PASS' for r in rows)}  FAIL: {sum(r[4] == 'FAIL' for r in rows)}  (результаты: {out})")


if __name__ == '__main__':
    main()
