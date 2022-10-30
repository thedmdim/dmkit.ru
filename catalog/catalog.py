from flask import Blueprint, render_template
from db_tools import execq

catalog = Blueprint('catalog', __name__, template_folder='templates', static_folder='static', static_url_path='/catalog/static')

@catalog.route("/")
@catalog.route("/<string:brand>/")
@catalog.route("/<string:brand>/<string:model>/")
@catalog.route("/<string:brand>/<string:model>/<string:_type>/")
@catalog.route("/<string:brand>/<string:model>/<string:_type>/<string:product>")
def index(brand=None, model=None, product=None, _type=None):
    """Интерфейс каталога"""
    if brand and model and _type and product:
        query = '''
        SELECT 
            t.*,
            group_concat(gallery.filename) gallery
        FROM (
        SELECT
            products.*,
            group_concat(items.id) items_ids, 
            group_concat(items.name) items_names,
            group_concat(items.price) items_prices,
            group_concat(items.checked) items_checked,
            models.id AS model_id,
            manufacturers.id AS manufacturer_id
        FROM products
        JOIN models ON products.model_id = models.id
        JOIN brands ON models.brand_id = brands.id
        LEFT JOIN manufacturers ON manufacturers.id = products.manufacturer_id
        LEFT JOIN
            (
            SELECT items.*,
            CASE
                WHEN ? = 'body-kit' THEN 1
                WHEN types.slug = ? THEN 1 ELSE 0
                END checked 
            FROM items
            JOIN types ON items.type_id = types.id
            ) items ON products.id = items.product_id
        WHERE 
            products.slug = ? AND
            models.slug = ? AND
            brands.slug = ?
        GROUP BY products.id
        ) t
        LEFT JOIN gallery ON gallery.product_id = t.id
        GROUP BY t.id
        '''

        data = dict(execq(query, (_type, _type, product, model, brand)))


        items_ids = data.pop("items_ids")
        items_ids = [int(i) for i in items_ids.split(",")] if items_ids else []

        items_names = data.pop("items_names")
        items_names = items_names.split(",") if items_names else []

        items_prices = data.pop("items_prices")
        items_prices = [int(i) for i in items_prices.split(",")] if items_prices else []

        items_checked = data.pop("items_checked")
        items_checked = [int(i) for i in items_checked.split(",")] if items_prices else []

        data.update(
            {
                "items": [
                    {"id": f, "name": u, "price": c, "checked": k} for f, u, c, k in
                    zip(items_ids, items_names, items_prices, items_checked)
                ],

                "gallery": data["gallery"].split(",") if data.get("gallery") else []
            }
        )
        return render_template("product.html", product=data)
    if brand and model and _type:
        if _type == 'body-kit':  # nosec
            query = f'''
        	SELECT products.*, sum(items.price) AS price FROM items 
        		JOIN products ON products.id = items.product_id 
        		JOIN models ON products.model_id = models.id
        		WHERE models.slug = "{model}"
        		GROUP BY products.id 
        		HAVING count(items.id) > 1
        	'''
        else:  # nosec
            query = f'''
        	SELECT products.*, sum(items.price) AS price FROM items
        		JOIN types ON items.type_id = types.id
        		JOIN products ON products.id = items.product_id 
        		JOIN models ON products.model_id = models.id 
        		WHERE models.slug="{model}" AND types.slug="{_type}"
        		GROUP BY products.id 
        	'''
        data = execq(query)
        return render_template("catalog.html", records=data)
    if brand and model:
        query = '''
        SELECT DISTINCT slug, name, thumbnail FROM (
        	SELECT * FROM types WHERE id = 1 AND EXISTS(
        	SELECT * FROM items 
        		JOIN products ON products.id = items.product_id 
        		JOIN models ON products.model_id = models.id 
        		WHERE models.slug = '?'
        		GROUP BY products.id 
        		HAVING count(items.id) > 1
        	)
        	UNION 
        	SELECT types.id, types.slug, types.name, types.thumbnail FROM items 
        		JOIN products ON products.id = items.product_id 
        		JOIN types ON items.type_id = types.id 
        		JOIN models ON products.model_id = models.id 
        		WHERE models.slug = '?' ORDER BY id
        );
        '''
        data = execq(query, (model, model))
        return render_template("catalog.html", records=data)
    
    if brand:
        query = """
        SELECT models.slug, models.name, models.thumbnail FROM models
        JOIN brands ON brands.id = models.brand_id
        WHERE brands.slug = '?';
        """
        data = execq(query, (brand,))
        return render_template("catalog.html", records=data)

    query = "SELECT slug, name, thumbnail FROM brands;"
    data = execq(query)
    return render_template("catalog.html", records=data)
