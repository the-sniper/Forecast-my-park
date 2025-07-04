
DROP TABLE IF EXISTS visitor_data;

CREATE TABLE visitor_data (

    park_id           VARCHAR(10)  NOT NULL,
    date              DATE         NOT NULL,
    visitor_count     INTEGER      NOT NULL,
    

    park_type         VARCHAR(50),
    state             VARCHAR(2),
    region            VARCHAR(20),
    

    temperature_high  FLOAT,
    precipitation     FLOAT,
    weather_condition VARCHAR(30),
    

    day_of_week       INTEGER,
    month             INTEGER,
    is_weekend        BOOLEAN,
    is_holiday        BOOLEAN,
    school_in_session BOOLEAN,
    
 
    gas_price         FLOAT,
    
 
    seasonal_factor   FLOAT,
    visitor_category  VARCHAR(20),

    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    

    PRIMARY KEY (park_id, date)
);

CREATE INDEX idx_visitor_data_date ON visitor_data(date);
CREATE INDEX idx_visitor_data_park ON visitor_data(park_id);
CREATE INDEX idx_visitor_data_park_type ON visitor_data(park_type);
CREATE INDEX idx_visitor_data_region ON visitor_data(region);
CREATE INDEX idx_visitor_data_weekend ON visitor_data(is_weekend);
CREATE INDEX idx_visitor_data_holiday ON visitor_data(is_holiday);
