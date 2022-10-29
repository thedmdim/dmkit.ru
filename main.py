import os.path, sqlite3, json
from flask import Flask, render_template, g
from datetime import datetime

from admin import admin
from catalog import catalog
from order import order
from yk_acquiring import yk_acquiring

from yookassa import Configuration
from yookassa.domain.common.user_agent import Version

from db_tools import init_db

s = json.load(open("settings.json"))

app = Flask(__name__)
app.register_blueprint(catalog, url_prefix='/')
app.register_blueprint(order, url_prefix='/order')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(yk_acquiring, url_prefix='/ykntfctn')

TEMPLATES_AUTO_RELOAD = True

DATABASE_NAME = "server.db"

init_db(DATABASE_NAME)

DATABASE = os.path.join(app.root_path, DATABASE_NAME)

SECRET_KEY = s["session"]

UPLOAD_FOLDER = os.path.join(catalog.static_folder, 'pics/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# админка
LOGIN = s["admin"]["login"]
PASSWORD = s["admin"]["password"]

# json output
JSONIFY_PRETTYPRINT_REGULAR = True
JSON_AS_ASCII = False
JSON_SORT_KEYS = False

app.config.from_object(__name__)

# yookassa
Configuration.configure(s["yookassa"]["account_id"], s["yookassa"]["secret_key"])
Configuration.configure_user_agent(framework=Version('Flask', '2.0.1'))

@app.before_request
def open_connection():
    if not hasattr(g, '_database'):
        g._database = sqlite3.connect(app.config['DATABASE'])
        g._database.row_factory = sqlite3.Row

@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, '_database'):
        g._database.close()

@app.template_filter('date')
def date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")

@app.errorhandler(404)
def rrr(error):
    return render_template("404.html"), 404

@app.route("/delivery")
def delivery():
    return render_template("delivery.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/test")
def test():
    return render_template("form.html")
