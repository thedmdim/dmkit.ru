BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "items_orders" (
	"item_id"	INTEGER NOT NULL,
	"order_id"	INTEGER NOT NULL,
	FOREIGN KEY("item_id") REFERENCES "items"("id"),
	FOREIGN KEY("order_id") REFERENCES "orders"("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "orders" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"surname"	TEXT NOT NULL,
	"patronymic"	TEXT NOT NULL,
	"city"	TEXT NOT NULL,
	"address"	TEXT NOT NULL,
	"number"	INTEGER NOT NULL,
	"passport1"	INTEGER NOT NULL,
	"passport2"	INTEGER NOT NULL,
	"product_id"	INTEGER,
	"timestamp"	INTEGER NOT NULL,
	"link"	TEXT NOT NULL,
	"payment_id"	TEXT NOT NULL,
	"status"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "manufacturers" (
	"id"	INTEGER,
	"name"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "brands" (
	"id"	INTEGER,
	"slug"	TEXT,
	"name"	TEXT NOT NULL,
	"thumbnail"	TEXT DEFAULT 'placeholder.png',
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "models" (
	"id"	INTEGER,
	"slug"	TEXT,
	"name"	TEXT NOT NULL,
	"thumbnail"	TEXT DEFAULT 'placeholder.png',
	"brand_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("brand_id") REFERENCES "brands"("id")
);
CREATE TABLE IF NOT EXISTS "products" (
	"id"	INTEGER,
	"slug"	TEXT UNIQUE,
	"name"	TEXT NOT NULL,
	"desc"	TEXT,
	"thumbnail"	TEXT DEFAULT 'placeholder.png',
	"manufacturer_id"	INTEGER,
	"model_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("manufacturer_id") REFERENCES "manufacturers"("id"),
	FOREIGN KEY("model_id") REFERENCES "models"("id")
);
CREATE TABLE IF NOT EXISTS "items" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"price"	INTEGER NOT NULL,
	"product_id"	INTEGER NOT NULL,
	"type_id"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("type_id") REFERENCES "types"("id"),
	FOREIGN KEY("product_id") REFERENCES "products"("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "types" (
	"id"	INTEGER,
	"slug"	TEXT,
	"name"	TEXT,
	"thumbnail"	TEXT DEFAULT 'placeholder.png',
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "gallery" (
	"filename"	TEXT DEFAULT 'placeholder.png',
	"product_id"	INTEGER NOT NULL,
	FOREIGN KEY("product_id") REFERENCES "products"("id") ON DELETE CASCADE
);
COMMIT;
