-- ============================================================================
-- Forecast My Park - Enhanced Visitor Data Table Creation
-- ============================================================================
-- This migration creates the complete visitor_data table with all features
-- needed for advanced ML forecasting including weather, temporal, and 
-- economic factors.
--
-- Run this ONCE to set up your database:
-- psql $DATABASE_URL -f data-scripts/Migrations/001_create_enhanced_visitor_data_table.sql
-- ============================================================================

-- Drop existing table if it exists (clean slate)
DROP TABLE IF EXISTS visitor_data;

-- Create enhanced visitor_data table with all forecasting features
CREATE TABLE visitor_data (
    -- ========================================================================
    -- CORE DATA (Required)
    -- ========================================================================
    park_id           VARCHAR(10)  NOT NULL,  -- Park code (e.g., 'YELL', 'GRCA')
    date              DATE         NOT NULL,  -- Visit date
    visitor_count     INTEGER      NOT NULL,  -- Daily visitor count
    
    -- ========================================================================
    -- PARK CHARACTERISTICS (Geographic/Administrative)
    -- ========================================================================
    park_type         VARCHAR(50),            -- National Park, Monument, etc.
    state             VARCHAR(2),             -- Two-letter state code
    region            VARCHAR(20),            -- Geographic region (West, Northeast, etc.)
    
    -- ========================================================================
    -- WEATHER FACTORS (Major impact on visitation)
    -- ========================================================================
    temperature_high  FLOAT,                  -- Daily high temperature (°F)
    precipitation     FLOAT,                  -- Rainfall amount (inches)
    weather_condition VARCHAR(30),            -- Clear, Light Rain, Heavy Rain, etc.
    
    -- ========================================================================
    -- TEMPORAL FACTORS (Time-based patterns)
    -- ========================================================================
    day_of_week       INTEGER,                -- 0=Monday, 6=Sunday
    month             INTEGER,                -- 1-12
    is_weekend        BOOLEAN,                -- Weekend effect (+28% visitors)
    is_holiday        BOOLEAN,                -- Federal holiday effect (+35% visitors)
    school_in_session BOOLEAN,                -- School calendar impact
    
    -- ========================================================================
    -- ECONOMIC FACTORS (Travel cost impact)
    -- ========================================================================
    gas_price         FLOAT,                  -- Daily gas price (affects travel decisions)
    
    -- ========================================================================
    -- CALCULATED FEATURES (Derived insights)
    -- ========================================================================
    seasonal_factor   FLOAT,                  -- 0.6 (winter) to 1.6 (summer)
    visitor_category  VARCHAR(20),            -- Low, Medium, High, Peak
    
    -- ========================================================================
    -- METADATA
    -- ========================================================================
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ========================================================================
    -- CONSTRAINTS
    -- ========================================================================
    PRIMARY KEY (park_id, date)
);

-- ============================================================================
-- INDEXES for Query Performance
-- ============================================================================
CREATE INDEX idx_visitor_data_date ON visitor_data(date);
CREATE INDEX idx_visitor_data_park ON visitor_data(park_id);
CREATE INDEX idx_visitor_data_park_type ON visitor_data(park_type);
CREATE INDEX idx_visitor_data_region ON visitor_data(region);
CREATE INDEX idx_visitor_data_weekend ON visitor_data(is_weekend);
CREATE INDEX idx_visitor_data_holiday ON visitor_data(is_holiday);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
\echo ''
\echo '🎉 SUCCESS: Enhanced visitor_data table created!'
\echo ''
\echo 'Table Features:'
\echo '  ✅ 18 columns including weather, temporal, and economic factors'
\echo '  ✅ Optimized indexes for fast queries'
\echo '  ✅ Ready for advanced ML forecasting'
\echo ''
\echo 'Next Steps:'
\echo '  1. Run: python data-scripts/data_expansion_strategy.py'
\echo '  2. This will populate ~39,000 records with rich features'
\echo '  3. Your ML models will have production-ready data!'
\echo '' 