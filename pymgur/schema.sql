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
	date_expire TIMESTAMP,
);

CREATE UNIQUE INDEX idx_pictures_uid ON pictures(uid);
CREATE INDEX idx_pictures_imageset ON pictures(imageset)
	WHERE imageset IS NOT NULL;
CREATE INDEX idx_pictures_date_created ON pictures(date_created);
CREATE INDEX idx_pictures_date_expire ON pictures(date_expire)
	WHERE date_expire IS NOT NULL;

CREATE TABLE imagesets (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT);