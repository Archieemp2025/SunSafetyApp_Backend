-- 1. Dimension tables

DROP TABLE IF EXISTS CANCER_INCIDENCE_STAT CASCADE; 
DROP TABLE IF EXISTS CANCER_TYPE CASCADE;
DROP TABLE IF EXISTS SEX CASCADE;
DROP TABLE IF EXISTS AGE_GROUP CASCADE;
DROP TABLE IF EXISTS STATE CASCADE;
DROP TABLE IF EXISTS CITY CASCADE;

CREATE TABLE CANCER_TYPE (
    cancer_id SERIAL PRIMARY KEY,
    cancer_name VARCHAR(255) UNIQUE NOT NULL,
    icd10_code VARCHAR(20) -- New column added here
);


CREATE TABLE SEX (
    sex_id SERIAL PRIMARY KEY,
    sex_label VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE AGE_GROUP (
    age_group_id SERIAL PRIMARY KEY,
    age_bracket VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE STATE (
    state_id SERIAL PRIMARY KEY,
    state_code VARCHAR(10) UNIQUE NOT NULL, -- e.g., 'VIC'
    state_name VARCHAR(100) NOT NULL        -- e.g., 'Victoria'
);


CREATE TABLE CITY (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) UNIQUE NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    state_id INTEGER REFERENCES STATE(state_id) ON DELETE CASCADE
);



-- 2. Fact Tables

CREATE TABLE CANCER_INCIDENCE_STAT (
    stat_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    count INTEGER,
    incidence_rate FLOAT,
    cancer_id INTEGER REFERENCES CANCER_TYPE(cancer_id),
    sex_id INTEGER REFERENCES SEX(sex_id),
    age_group_id INTEGER REFERENCES AGE_GROUP(age_group_id)
);



-- 3. Inserting Values into STATE table
INSERT INTO STATE (state_code, state_name) VALUES 
('VIC', 'Victoria'),
('NSW', 'New South Wales'),
('QLD', 'Queensland'),
('WA', 'Western Australia'),
('SA', 'South Australia'),
('TAS', 'Tasmania'),
('ACT', 'Australian Capital Territory'),
('NT', 'Northern Territory')
ON CONFLICT (state_code) DO NOTHING;
