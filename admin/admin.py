from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
from db_tools import execq, get_orders
from admin.edit import edit_api

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
admin.register_blueprint(edit_api, url_prefix='/edit/api')


@admin.route("/")
def menu():
    """Меню админ панели"""
    return render_template("menu.html")


@admin.route("/orders")
def show_orders():
    """Показать страницу с заказами"""
    page = request.args.get('page', default=0, type=int) * 10

    if request.cookies.get("payment") == "true":
        orders = get_orders(paid=True, offset=page)
        pass
    else:
        orders = get_orders(offset=page)
        pass

    return render_template("orders.html", orders=orders)


@admin.route("/edit")
def edit_products():
    """Страница редактирования товаров"""
    return render_template("edit.html",
                           products=execq("SELECT * FROM products;"),
                           models=execq("SELECT * FROM models;"),
                           types=execq("SELECT * FROM types;"),
                           manufacturers=execq("SELECT * FROM manufacturers;"))


@admin.before_request
def if_logged():
    """Проверка авторизации"""
    if not session.get("logged") == 1 and request.endpoint != 'admin.login':
        return redirect(url_for(".login"))


@admin.route("/login", methods=["GET", "POST"])
def login():
    """Страница входа в админ панель"""
    if session.get("logged") == 1:
        return redirect(url_for("/"))
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        if username == current_app.config["LOGIN"] and password == current_app.config["PASSWORD"]:
            session["logged"] = 1
            # print("Admin logged in", request.remote_addr)
            return redirect(url_for(".menu"))
        return redirect(request.url)
    return render_template("login.html"), 401


@admin.route("/logout")
def logout():
    """Разлогинить с админ панели"""
    session.pop("logged")
    return redirect("/")
