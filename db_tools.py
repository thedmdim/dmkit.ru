import sqlite3
from typing import Union

from flask import g, abort



def init_db(db_name):
    """Создать базу данных если нету"""
    with sqlite3.connect(db_name) as db:
        cur = db.cursor()
        schema = open("db.schema.sql").read()
        cur.executescript(schema)


def get_orders(paid=False, offset=0):
    """Получить список заказов"""
    query = '''
    SELECT orders.*,
        group_concat(items.id) items_ids, 
        group_concat(items.name) items_names,
        group_concat(items.price) items_prices,
        group_concat(DISTINCT products.name) product_name,
        sum(items.price) price
    FROM orders
    JOIN items_orders ON items_orders.order_id = orders.id
    JOIN items ON items.id = items_orders.item_id
    JOIN products ON products.id = items.product_id
    {}
    GROUP BY orders.id
    ORDER BY timestamp 
    DESC
    LIMIT {},10;
    '''

    if paid:
        query = query.format("WHERE orders.status='succeeded'", offset)
    else:
        query = query.format("", offset)

    data = [dict(order) for order in execq(query)]

    for product in data:
        items_ids = product.pop("items_ids")
        items_ids = [int(i) for i in items_ids.split(",")] if items_ids else []

        items_names = product.pop("items_names")
        items_names = items_names.split(",") if items_names else []

        items_prices = product.pop("items_prices")
        items_prices = [int(i) for i in items_prices.split(",")] if items_prices else []

        product.update(
            {
                "items": [
                    {"id": f, "name": u, "price": c} for
                    f, u, c in
                    zip(items_ids, items_names, items_prices)
                ],

            }
        )

    return data


def execq(query: str, data: Union[tuple, list] = None) -> Union[tuple, list]:
    """Универсальная функция выполнения SQL запроса"""
    db = g._database
    cur = db.cursor()

    if isinstance(data, tuple):
        res = cur.execute(query, data).fetchall()
    elif isinstance(data, list):
        res = cur.executemany(query, data).fetchall()
    else:
        res = cur.execute(query).fetchall()

    if "INSERT" in query or "UPDATE" in query or "DELETE" in query:
        db.commit()

    return res if res else abort(404)
