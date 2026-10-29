import os
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

from core.db import Database
from core.models import ApplicationRepository, EventRepository, UserRepository
from core.validators import RegistrationValidator

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", secrets.token_hex(16)),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

db = Database(os.environ.get("DB_PATH", BASE_DIR / "konferencii.db"))
db.init()
users = UserRepository(db)
events = EventRepository(db)
applications = ApplicationRepository(db)


@app.before_request
def load_user():
    uid = session.get("user_id")
    g.user = users.get(uid) if uid else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.user is None:
            flash("Войдите в систему, чтобы продолжить", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.user is None or g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    return render_template("index.html", events=events.all())


@app.route("/register", methods=["GET", "POST"])
def register():
    form = {}
    if request.method == "POST":
        form = request.form.to_dict()
        errors = RegistrationValidator(users).validate(form)
        if errors:
            for msg in errors.values():
                flash(msg, "error")
        else:
            users.create(form["login"], form["password"], form["full_name"],
                         form["email"], form["phone"])
            flash("Регистрация прошла успешно. Теперь войдите в систему.", "success")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = users.authenticate(request.form.get("login", ""), request.form.get("password", ""))
        if user:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("admin" if user["role"] == "admin" else "my_applications"))
        flash("Неверный логин или пароль", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/applications")
@login_required
def my_applications():
    return render_template("applications.html", items=applications.for_user(g.user["id"]))


@app.route("/applications/new", methods=["GET", "POST"])
@login_required
def new_application():
    if request.method == "POST":
        event_id = request.form.get("event_id", type=int)
        payment = request.form.get("payment_method", "").strip()
        comment = request.form.get("comment", "").strip()
        if not event_id or not events.get(event_id):
            flash("Выберите мероприятие", "error")
        elif not payment:
            flash("Укажите способ оплаты", "error")
        else:
            applications.create(g.user["id"], event_id, payment, comment)
            flash("Заявка отправлена", "success")
            return redirect(url_for("my_applications"))
    return render_template("new_application.html", events=events.all(),
                           selected=request.args.get("event", type=int))


@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html", items=applications.all(), statuses=applications.statuses())


@app.route("/admin/status/<int:app_id>", methods=["POST"])
@admin_required
def change_status(app_id):
    status_id = request.form.get("status_id", type=int)
    if status_id in {s["id"] for s in applications.statuses()}:
        applications.set_status(app_id, status_id)
        flash(f"Статус заявки № {app_id} изменён", "success")
    return redirect(url_for("admin"))


@app.errorhandler(403)
def forbidden(_):
    return render_template("error.html", code=403, text="Доступ запрещён"), 403


@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, text="Страница не найдена"), 404


if __name__ == "__main__":
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)))
