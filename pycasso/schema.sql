CREATE TABLE pictures (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	uid TEXT,
	author TEXT,
	height INTEGER,
	width INTEGER,
	status INTEGER NOT NULL DEFAULT 0, -- 0/1
	extension TEXT,
	thumb_extension TEXT, -- may be different (PNG -> JPEG)
	secret TEXT,
	date_created TIMESTAMP,
	date_expire TIMESTAMP
);

CREATE UNIQUE INDEX idx_pictures_uid ON pictures(uid);
CREATE INDEX idx_pictures_date_expire ON pictures(date_expire);

CREATE TABLE sets (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT);