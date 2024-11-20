CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    folder TEXT NOT NULL,  -- e.g., 'data_aloha' or 'data_heartbeach'
    wave_height REAL,      -- Parsed from the filename
    wave_period REAL,      -- Parsed from the filename
    wave_direction TEXT,   -- Parsed from the filename
    wind_speed REAL,       -- Parsed from the filename
    wind_direction TEXT    -- Parsed from the filename
);

CREATE INDEX idx_conditions ON images (
    wave_height, wave_period, wave_direction, wind_speed, wind_direction
);
