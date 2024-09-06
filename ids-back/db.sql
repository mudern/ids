CREATE TABLE IF NOT EXISTS DataPackets (
    packet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_name TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    packet_size INTEGER
);

CREATE TABLE IF NOT EXISTS PredictionResults (
    predict_id INTEGER PRIMARY KEY AUTOINCREMENT,
    predict_name TEXT NOT NULL,
    predict_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predict_size INTEGER
);