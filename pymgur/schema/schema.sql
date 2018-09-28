CREATE TABLE schema_version (version INTEGER PRIMARY KEY);
INSERT INTO schema_version VALUES (1);

CREATE TABLE pictures (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	uid TEXT,
	title TEXT,
	author TEXT,
	width INTEGER,
	height INTEGER,
	status INTEGER NOT NULL DEFAULT 0, -- bitmask
	imageset INTEGER,
	extension TEXT,
	thumb_extension TEXT, -- may be different (PNG -> JPEG)
	secret TEXT,
	remote_addr TEXT,
	date_created TIMESTAMP,
	date_expire TIMESTAMP
);

CREATE UNIQUE INDEX idx_pictures_uid ON pictures(uid);
CREATE INDEX idx_pictures_imageset ON pictures(imageset)
	WHERE imageset IS NOT NULL;
CREATE INDEX idx_pictures_date_created ON pictures(date_created);
CREATE INDEX idx_pictures_date_expire ON pictures(date_expire)
	WHERE date_expire IS NOT NULL;

CREATE TABLE imagesets (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT);

CREATE TABLE session_secret (
	id INTEGER PRIMARY KEY,
	secret BLOB
);

-- 48 bytes random secret
INSERT INTO session_secret VALUES (1,
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) ||
	CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256) || CHAR(RANDOM() % 256)
);
