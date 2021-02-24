CREATE TABLE "currency" (
	"id"	INTEGER NOT NULL UNIQUE,
	"currency"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"price"	REAL NOT NULL,
	"date"	TEXT NOT NULL,
	"price_1h_change"	REAL NOT NULL,
	"price_1h_change_pct"	REAL NOT NULL,
	"price_1d_change"	REAL NOT NULL,
	"price_1d_change_pct"	REAL NOT NULL,
	"price_30d_change"	REAL NOT NULL,
	"price_30d_change_pct"	REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "listing" (
	"id"	INTEGER NOT NULL UNIQUE,
	"currency"	TEXT NOT NULL,
	"amount"	REAL NOT NULL,
	"price"	REAL NOT NULL,
	"date"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	PRIMARY KEY("id")
)

CREATE TABLE "ticker" (
	"id"	INTEGER NOT NULL,
	"currency"	TEXT NOT NULL,
	"price"	REAL NOT NULL,
	"epoch"	TEXT NOT NULL,
	"datetime"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)