CREATE TABLE barrios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    coordenadas_centroide VARCHAR(100)
);

CREATE TABLE sensores (
    id SERIAL PRIMARY KEY,
    codigo_sensor VARCHAR(50) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    barrio_id INT REFERENCES barrios(id) ON DELETE CASCADE
);

CREATE TABLE mediciones (
    id BIGSERIAL PRIMARY KEY,
    sensor_id INT REFERENCES sensores(id) ON DELETE CASCADE,
    valor NUMERIC(10, 2) NOT NULL,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    sensor_id INT REFERENCES sensores(id) ON DELETE CASCADE,
    valor_disparado DECIMAL(10, 2) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO barrios (nombre, coordenadas_centroide) VALUES 
('Centro', '40.417,-3.703'),
('Norte', '40.480,-3.680'),
('Sur', '40.350,-3.690');

INSERT INTO sensores (codigo_sensor, tipo, unidad_medida, barrio_id) VALUES 
('SEN-CENTRO-CO2', 'CO2', 'ppm', 1),
('SEN-NORTE-CO2', 'CO2', 'ppm', 2),
('SEN-SUR-CO2', 'CO2', 'ppm', 3),
('SEN-CENTRO-RUIDO', 'RUIDO', 'dB', 1),
('SEN-NORTE-TRAFICO', 'TRAFICO', 'vehiculos/min', 2),
('SEN-SUR-CO2', 'CO2', 'ppm', 3);