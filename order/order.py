import uuid
from datetime import datetime

from flask import Blueprint, abort, request, redirect, render_template, flash

import yk_acquiring
from db_tools import execq


order = Blueprint('order', __name__, template_folder='templates', static_folder='static')


@order.route("/<uuid:link>")
def show_order(link):
    """Посмотреть созданный заказ"""
    data = execq(f'SELECT * FROM orders WHERE link = "?"', (link,))
    return render_template("order.html", order=data)


@order.route("", methods=["GET", "POST"])
def order_endpoint():
    """Заказать"""
    if request.method == 'POST':
        required_fields = ['id','name', 'surname', 'patronymic', 'city', 'address', 'tel', 'passport1', 'passport2']
        form = request.form

        # проверка форм
        items = [item_id for item_id in form if form.get(item_id) == 'on']
        if all(form.get(field) for field in required_fields) and all(item.isdigit() for item in items):

            # создать payment request
            return_link = str(uuid.uuid4())
            value = execq(f"SELECT sum(price) FROM items WHERE id IN ({','.join(items)});")['sum(price)']

            payment = yk_acquiring.create_payment(value, return_link)

            # записать заказ
            order_query = "INSERT INTO orders (name,surname,patronymic,city,address,number,passport1,passport2,product_id,timestamp,link,payment_id,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) RETURNING id;"
            order_data = (
                form.get('name'),
                form.get('surname'),
                form.get('patronymic'),
                form.get('city'),
                form.get('address'),
                form.get('tel'),
                form.get('passport1'),
                form.get('passport2'),
                form.get('id'),
                datetime.now().timestamp(),
                return_link,
                payment.id,
                payment.status
            )
            order_id, = execq(order_query, order_data)

            # записать items заказа
            items_query = "INSERT INTO items_orders VALUES (?, ?);"
            items_data = [(item_id, order_id) for item_id in items]
            execq(items_query, items_data)

            return redirect(payment.confirmation.confirmation_url)
        
        flash('Заполните поля')
        return redirect(request.referrer)
    return abort(404)
