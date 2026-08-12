-- Genius Database Architect: Spec-6 (Karak)
-- Schema implementation for Jaimini Chara Karakas.

-- We store the computed Karakas for a given astrological chart to allow high-performance 
-- lookups and filtering (e.g., "Find all charts where Moon is Atmakaraka and in the 9th house").

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Base table for charts (Assuming this already exists in the system)
-- CREATE TABLE astrological_charts (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     user_id UUID NOT NULL,
--     chart_name VARCHAR(255),
--     event_time TIMESTAMP WITH TIME ZONE NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- Table strictly for storing the 7 Jaimini Chara Karakas
CREATE TABLE jaimini_char_karakas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chart_id UUID NOT NULL, -- FOREIGN KEY REFERENCES astrological_charts(id) ON DELETE CASCADE
    
    -- We store the enum string or varchar of the planet acting as the Karaka
    atma_karaka_planet VARCHAR(10) NOT NULL,    -- AK (Highest degree)
    amatya_karaka_planet VARCHAR(10) NOT NULL,  -- AmK (2nd highest)
    bhratru_karaka_planet VARCHAR(10) NOT NULL, -- BK (3rd highest)
    matru_karaka_planet VARCHAR(10) NOT NULL,   -- MK (4th highest)
    putra_karaka_planet VARCHAR(10) NOT NULL,   -- PK (5th highest)
    gnati_karaka_planet VARCHAR(10) NOT NULL,   -- GK (6th highest)
    dara_karaka_planet VARCHAR(10) NOT NULL,    -- DK (7th highest)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint to ensure we only have valid visible planets as Karakas
    CONSTRAINT chk_valid_atma CHECK (atma_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    CONSTRAINT chk_valid_amatya CHECK (amatya_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    CONSTRAINT chk_valid_bhratru CHECK (bhratru_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    CONSTRAINT chk_valid_matru CHECK (matru_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    CONSTRAINT chk_valid_putra CHECK (putra_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    CONSTRAINT chk_valid_gnati CHECK (gnati_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    CONSTRAINT chk_valid_dara CHECK (dara_karaka_planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')),
    
    -- Ensure 1-to-1 relationship between a chart and its karaka setup
    CONSTRAINT uq_chart_karakas UNIQUE (chart_id)
);

-- Indexing Strategy
-- =================
-- For an astrological trading system, we often query charts by their Atmakaraka or Amatyakaraka.
-- We index the top two most important Karakas for career/wealth (AK and AmK).
CREATE INDEX idx_karakas_atma ON jaimini_char_karakas(atma_karaka_planet);
CREATE INDEX idx_karakas_amatya ON jaimini_char_karakas(amatya_karaka_planet);

-- Index for resolving joins quickly from the chart side
CREATE INDEX idx_karakas_chart_id ON jaimini_char_karakas(chart_id);

-- Optional: Composite index if queries frequently filter by AK + AmK combinations 
-- (e.g., "AK is Sun AND AmK is Jupiter")
CREATE INDEX idx_karakas_ak_amk ON jaimini_char_karakas(atma_karaka_planet, amatya_karaka_planet);

-- View: AstroSage Karak Table Representation
-- Provides a normalized row-per-planet output mimicking the AstroSage table format
CREATE OR REPLACE VIEW view_astrosage_karak_table AS
SELECT 
    chart_id,
    atma_karaka_planet AS planet,
    'Atma' AS karaka_name,
    'AK' AS karaka_abbr,
    1 AS karaka_rank
FROM jaimini_char_karakas
UNION ALL
SELECT chart_id, amatya_karaka_planet, 'Amatya', 'AmK', 2 FROM jaimini_char_karakas
UNION ALL
SELECT chart_id, bhratru_karaka_planet, 'Bhratru', 'BK', 3 FROM jaimini_char_karakas
UNION ALL
SELECT chart_id, matru_karaka_planet, 'Matru', 'MK', 4 FROM jaimini_char_karakas
UNION ALL
SELECT chart_id, putra_karaka_planet, 'Putra', 'PK', 5 FROM jaimini_char_karakas
UNION ALL
SELECT chart_id, gnati_karaka_planet, 'Gnati', 'GK', 6 FROM jaimini_char_karakas
UNION ALL
SELECT chart_id, dara_karaka_planet, 'Dara', 'DK', 7 FROM jaimini_char_karakas;
