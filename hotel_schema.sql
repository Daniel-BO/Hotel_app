CREATE TABLE IF NOT EXISTS huespedes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT UNIQUE NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS habitaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL,
    tipo TEXT NOT NULL,
    precio_por_noche REAL NOT NULL,
    disponible INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    huesped_id INTEGER,
    habitacion_id INTEGER,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    FOREIGN KEY (huesped_id) REFERENCES huespedes(id),
    FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,  -- idealmente con hash en producción
    rol TEXT DEFAULT 'recepcionista'
);

