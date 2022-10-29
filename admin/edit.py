import json, os
from sqlite3 import IntegrityError

from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask import Blueprint, request, url_for, current_app, jsonify, flash

from db_tools import execq


edit_api = Blueprint('api', __name__)

def check_extension(filename: str) -> bool:
    """Проверить расширения файлов формы"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_files(files: ImmutableMultiDict) -> list:
    """Сохранить изображения из формы"""
    saved = []
    for file in files:
        if file and check_extension(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
            saved.append(filename)
    return saved


@edit_api.route("/types/", methods=["GET"])
def api_types():
    """Показать все типы деталей товара"""
    query = "SELECT id, slug, name FROM types;"
    data = [dict(i) for i in execq(query)]
    return jsonify(data)

@edit_api.route("/models/")
def api_models():
    """Показать все модели бренда"""
    query = "SELECT * FROM models;"
    data = [dict(i) for i in execq(query)]
    return jsonify(data)

@edit_api.route("/brands/")
def api_brands():
    """Показать все бренды товаров"""
    query = "SELECT id, slug, name, thumbnail FROM brands;"
    data = [dict(i) for i in execq(query)]
    return jsonify(data)


@edit_api.route("/products/", methods=['GET', "POST"])
@edit_api.route("/products/<int:product_id>", methods=['GET', "PUT", "DELETE"])
def api_products(product_id=None):
    """Редактирования товара"""
    if request.method == "GET":
        query = '''
            SELECT 
                t.id,
                t.slug,
                t.name,
                t.desc,
                t.thumbnail,
                t.manufacturer_id,
                t.model_id,
                t.items_ids,
                t.items_names,
                t.items_prices,
                t.items_type_ids,
                group_concat(gallery.filename) gallery
            FROM (
        		SELECT products.*,
        			group_concat(items.id) items_ids, 
        			group_concat(items.name) items_names,
        			group_concat(items.price) items_prices,
        			group_concat(items.type_id) items_type_ids,
        			models.id AS model_id,
        			manufacturers.id AS manufacturer_id
        		FROM products
        		LEFT JOIN items ON products.id = items.product_id
        		LEFT JOIN models ON products.model_id = models.id
        		LEFT JOIN types ON items.type_id = types.id
        		LEFT JOIN manufacturers ON manufacturers.id = products.manufacturer_id
        		{}
        		GROUP BY products.id
        	) t
            LEFT JOIN gallery ON gallery.product_id = t.id
            GROUP BY t.id
        	'''

        if product_id:
            query = query.format(f"WHERE products.id = {product_id}")
        else:
            query = query.format("")

        data = [dict(product) for product in execq(query)]

        for product in data:
            items_ids = product.pop("items_ids")
            items_ids = [int(i) for i in items_ids.split(",")] if items_ids else []

            items_names = product.pop("items_names")
            items_names = items_names.split(",") if items_names else []

            items_prices = product.pop("items_prices")
            items_prices = [int(i) for i in items_prices.split(",")] if items_prices else []

            items_type_ids = product.pop("items_type_ids")
            items_type_ids = [int(i) for i in items_type_ids.split(",")] if items_type_ids else []

            product.update(
                {
                    "items": [
                        {"id": f, "name": u, "price": c, "type_id": k} for f, u, c, k in
                        zip(items_ids, items_names, items_prices, items_type_ids)
                    ],

                    "gallery": product["gallery"].split(",") if product.get("gallery") else []
                }
            )

        if product_id:
            [data] = data
            return jsonify(data)
        
        return jsonify(data)

    if request.method == "POST":
        
        product = request.form
        
        [thumbnail] = save_files(request.files.getlist("thumbnail")) or [""]
                        
        product_data = {
            "slug": product.get('slug') or None,
            "name": product.get('name') or None,
            "desc": product.get('desc') or None,
            "thumbnail": thumbnail,
            "manufacturer_id": product.get('manufacturer_id') if product.get('manufacturer_id').isdigit() else None,
            "model_id": product.get('model_id') if product.get('model_id').isdigit() else None
        }
        
        product_query = f"INSERT INTO products ({', '.join([k for k, v in product_data.items() if v])}) " \
                        f"VALUES ({','.join(['?' for v in product_data.values() if v])}) RETURNING *;"
        
        try:
            res = dict(execq(product_query, tuple(product_data.values())))
        except IntegrityError as e:
            flash("\n".join(e.args), "error") 
            return jsonify({"error": list(e.args)}), 400
        
        # res.headers['Location'] = url_for(".api_products", product_id=res["id"])

        return jsonify(res), 201

    if request.method == "PUT":
        
        product = request.form        
        [thumbnail] = save_files(request.files.getlist("thumbnail")) or [None]
        
        product_data = {
            "slug": product.get('slug') or None,
            "name": product.get('name') or None,
            "desc": product.get('desc') or None,
            "thumbnail": thumbnail,
            "manufacturer_id": product.get('manufacturer_id') if product.get('manufacturer_id').isdigit() else None,
            "model_id": product.get('model_id') if product.get('model_id').isdigit() else None
        }
        
        query = """
            UPDATE products 
            SET {", ".join([f"{k} = '{v}'" for k, v in product_data.items() if v])}
            WHERE products.id = {product_id} 
            RETURNING *;
        """
        
        [res] = execq(query)

        return jsonify(dict(res))

    if request.method == "DELETE":
        query = "DELETE FROM products WHERE id = ? RETURNING id;"
        res = execq(query, (product_id,))
        return jsonify(res)


@edit_api.route("/products/<int:product_id>/gallery", methods=["GET", "POST"])
@edit_api.route("/products/<int:product_id>/gallery/<string:filename>", methods=["DELETE"])
def api_gallery(product_id, filename=None):
    """Редактирование галереи товара"""
    if request.method == "GET":
        query = """
            SELECT filename FROM gallery
            JOIN products ON products.id = gallery.product_id 
            WHERE products.id = ?;
        """
        data = [i["filename"] for i in execq(query, (product_id,))]
        [i.update({"url": url_for('catalog.static', filename=f'pics/{i}')}) for i in data]
        return jsonify(data)

    if request.method == "POST":
        files = request.files.getlist("gallery")
        if files:
            gallery = save_files(files)
            

            gallery_query = "INSERT INTO gallery (filename, product_id) VALUES (?,?) RETURNING filename"
            data = []
            for image in gallery:
                res = execq(gallery_query, (image, product_id))
                data.append(res["filename"])
            return jsonify(data)
        return jsonify({"error": "empty input"}), 400

    if request.method == "DELETE":        
        query = "DELETE FROM gallery " \
                "WHERE filename = ? " \
                "RETURNING filename;"
        [res] = execq(query, (filename,))
        return jsonify(dict(res))


@edit_api.route("/products/<int:product_id>/items", methods=["GET", "POST", "PUT"])
@edit_api.route("/products/<int:product_id>/items/<int:item_id>", methods=["DELETE"])
def api_items(product_id, item_id = None):
    """Редактирование деталей товара"""
    if request.method == "GET":
        query = "SELECT items.* " \
                "FROM products " \
                "JOIN items ON products.id = items.product_id " \
                f"WHERE products.id = '{product_id}';"
        data = [dict(item) for item in execq(query)]
        return jsonify(data)

    if request.method == "POST":
        items = request.json

        items_query = "INSERT INTO items (name, price, type_id, product_id) " \
                    "VALUES (?,?,?,?) RETURNING *"
        items_data = [(item.get("name"),item.get("price"),item.get("type_id"),product_id) for item in items]
        
        print("items_data", items_data)
        
        # this is because RETURNING doesn't work with executemany
        items_res = []
        for item in items:
            item_data = (
                item.get("name"),
                item.get("price"),
                item.get("type_id"),
                product_id
            )
            items_res.append(dict(execq(items_query, item_data)))
        return jsonify(items_res), 201


    if request.method == "PUT":
        items = request.json
        
        items_query = "UPDATE items " \
                "SET name = ?, price = ?, type_id = ? " \
                "WHERE items.id = ? " \
                "RETURNING *;"
        
        items_res = []
        for item in items:
            item_data = (
                item.get("name"),
                item.get("price"),
                item.get("type_id"),
                item.get("id")
            )
            items_res.append(dict(execq(items_query, item_data)))
        return jsonify(items_res), 200
    
    if request.method == "DELETE":
        query = "DELETE FROM items " \
                "WHERE id = ? RETURNING id;"
        res = execq(query, (item_id,))
        return jsonify(res)


@edit_api.route("/products/<int:product_id>/thumbnail", methods=["GET", "POST"])
def api_product_thumbnail(product_id):
    """Редактирование значка товара"""
    if request.method == "GET":
        query = "SELECT thumbnail FROM products " \
                f"WHERE products.id = {product_id}"
        res = dict(execq(query, False))
        res.update({"url": url_for('catalog.static', filename=f'pics/{res["thumbnail"]}')})
        return jsonify(res)

    if request.method == "POST":
        files = request.files.getlist("thumbnail")
        if len(files) == 1:
            [thumbnail] = json.dumps(save_files(files))
            query = "UPDATE products SET thumbnail = ? WHERE products.id = ? RETURNING thumbnail"
            [res] = execq(query, (thumbnail,))
            return jsonify(dict(res))
        return jsonify({"message": "input should be only one file"}), 400
