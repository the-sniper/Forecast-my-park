#!/usr/bin/env python3
"""
Forecast My Park - Comprehensive Dataset Generator

🚀 ONE SCRIPT TO RULE THEM ALL! 🚀

This comprehensive script provides everything needed to generate a complete 
park visitor dataset for ML forecasting:

✅ Creates enhanced database schema (18 columns)
✅ Generates 39,000+ records with rich features
✅ 3.5+ years of data across 30+ parks
✅ Weather, temporal, economic, and geographic factors
✅ Production-ready for advanced ML forecasting

Usage:
    python generate_park_dataset.py

No other scripts needed - this does it all!
"""

import os
import datetime
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ENGINE = create_engine(os.getenv("DATABASE_URL"))

def setup_logging():
    """Set up comprehensive logging."""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "park_dataset_generation.log")),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_enhanced_schema():
    """Create enhanced database schema with all 18 features."""
    schema_sql = """
    DROP TABLE IF EXISTS visitor_data;
    
    CREATE TABLE visitor_data (
        park_id VARCHAR(10) NOT NULL,
        date DATE NOT NULL,
        visitor_count INTEGER NOT NULL,
        
        -- Park characteristics
        park_type VARCHAR(50),
        state VARCHAR(2),
        region VARCHAR(20),
        
        -- Weather factors
        temperature_high FLOAT,
        precipitation FLOAT,
        weather_condition VARCHAR(30),
        
        -- Temporal factors
        day_of_week INTEGER,
        month INTEGER,
        is_weekend BOOLEAN,
        is_holiday BOOLEAN,
        school_in_session BOOLEAN,
        
        -- Economic factors
        gas_price FLOAT,
        
        -- Calculated features
        seasonal_factor FLOAT,
        visitor_category VARCHAR(20),
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        PRIMARY KEY (park_id, date)
    );
    
    CREATE INDEX idx_visitor_data_date ON visitor_data(date);
    CREATE INDEX idx_visitor_data_park ON visitor_data(park_id);
    CREATE INDEX idx_visitor_data_park_type ON visitor_data(park_type);
    CREATE INDEX idx_visitor_data_region ON visitor_data(region);
    """
    
    try:
        with ENGINE.begin() as conn:
            conn.execute(text(schema_sql))
        return True
    except Exception as e:
        print(f"Schema creation failed: {e}")
        return False

def get_federal_holidays(year):
    """Get federal holidays with visitor impact multipliers."""
    holidays = {}
    
    # Fixed holidays
    fixed_holidays = [
        (1, 1, 1.3),   # New Year's Day
        (7, 4, 1.5),   # Independence Day  
        (12, 25, 1.2)  # Christmas
    ]
    
    for month, day, multiplier in fixed_holidays:
        holidays[datetime.date(year, month, day)] = multiplier
    
    # Memorial Day (last Monday in May)
    memorial_day = datetime.date(year, 5, 31)
    while memorial_day.weekday() != 0:
        memorial_day -= datetime.timedelta(days=1)
    holidays[memorial_day] = 1.5
    
    # Labor Day (first Monday in September)
    labor_day = datetime.date(year, 9, 1)
    while labor_day.weekday() != 0:
        labor_day += datetime.timedelta(days=1)
    holidays[labor_day] = 1.4
    
    return holidays

def get_seasonal_factor(date):
    """Enhanced seasonal factors based on month."""
    month_factors = {
        1: 0.6, 2: 0.65, 3: 0.8, 4: 1.1, 5: 1.3, 6: 1.5,
        7: 1.6, 8: 1.5, 9: 1.2, 10: 1.1, 11: 0.8, 12: 0.7
    }
    return month_factors.get(date.month, 1.0)

def simulate_weather(date, region):
    """Simulate realistic weather impact on visitation."""
    month = date.month
    
    # Temperature by season and region
    if region in ['West', 'Southwest']:
        base_temp = [45, 55, 65, 75, 85, 95, 100, 95, 85, 75, 60, 50][month-1]
    elif region in ['Northeast', 'Midwest']:
        base_temp = [25, 35, 45, 60, 70, 80, 85, 80, 70, 55, 40, 30][month-1]
    else:  # Southeast
        base_temp = [50, 60, 70, 80, 85, 90, 92, 90, 85, 75, 65, 55][month-1]
    
    # Add daily variation
    temp_variation = (hash(f"temp{date}") % 20) - 10
    temp_high = base_temp + temp_variation
    
    # Precipitation simulation
    precip_chance = [0.3, 0.3, 0.4, 0.4, 0.3, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.3][month-1]
    has_precip = (hash(f"precip{date}") % 100) / 100 < precip_chance
    precipitation = (hash(f"rain{date}") % 20) / 10 if has_precip else 0
    
    # Weather impact on visitors
    if precipitation > 1.0:
        weather_factor, condition = 0.6, "Heavy Rain"
    elif precipitation > 0.1:
        weather_factor, condition = 0.8, "Light Rain"
    elif temp_high > 95:
        weather_factor, condition = 0.85, "Very Hot"
    elif temp_high < 25:
        weather_factor, condition = 0.7, "Very Cold"
    else:
        weather_factor, condition = 1.0, "Clear"
    
    return {
        'temp_high': temp_high,
        'precipitation': precipitation,
        'condition': condition,
        'factor': weather_factor
    }

def is_school_in_session(date):
    """Determine if school is in session (affects family travel)."""
    month, day = date.month, date.day
    
    # Summer break (June-August)
    if month in [6, 7, 8]:
        return False
    # Winter break (late December - early January)
    if (month == 12 and day > 20) or (month == 1 and day < 8):
        return False
    # Spring break (varies, but typically mid-March)
    if month == 3 and 10 <= day <= 20:
        return False
    
    return True

def get_region_for_state(state):
    """Get geographic region for state."""
    regions = {
        'West': ['CA', 'OR', 'WA', 'AK', 'HI', 'NV', 'UT', 'CO', 'WY', 'MT', 'ID'],
        'Southwest': ['AZ', 'NM', 'TX'],
        'Midwest': ['IL', 'IN', 'IA', 'KS', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'SD', 'WI'],
        'Southeast': ['AL', 'AR', 'FL', 'GA', 'KY', 'LA', 'MS', 'NC', 'SC', 'TN', 'VA', 'WV'],
        'Northeast': ['CT', 'DE', 'ME', 'MD', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT']
    }
    
    for region, states in regions.items():
        if state in states:
            return region
    return 'Other'

def categorize_visitor_level(visitors, base_visitors):
    """Categorize visitor level for analysis."""
    if base_visitors == 0:
        return 'Low'
    
    ratio = visitors / base_visitors
    if ratio < 0.5:
        return 'Low'
    elif ratio < 1.0:
        return 'Medium'
    elif ratio < 1.5:
        return 'High'
    else:
        return 'Peak'

def get_expanded_park_list():
    """Get list of diverse parks with characteristics for comprehensive dataset."""
    parks = [
        # Major National Parks
        {'code': 'YELL', 'type': 'National Park', 'state': 'WY', 'base_visitors': 3000},
        {'code': 'GRCA', 'type': 'National Park', 'state': 'AZ', 'base_visitors': 5000},
        {'code': 'YOSE', 'type': 'National Park', 'state': 'CA', 'base_visitors': 4000},
        {'code': 'ZION', 'type': 'National Park', 'state': 'UT', 'base_visitors': 3500},
        {'code': 'ACAD', 'type': 'National Park', 'state': 'ME', 'base_visitors': 2500},
        {'code': 'ARCH', 'type': 'National Park', 'state': 'UT', 'base_visitors': 2800},
        {'code': 'ROMO', 'type': 'National Park', 'state': 'CO', 'base_visitors': 2200},
        {'code': 'GRSM', 'type': 'National Park', 'state': 'TN', 'base_visitors': 4500},
        {'code': 'OLYM', 'type': 'National Park', 'state': 'WA', 'base_visitors': 2000},
        {'code': 'GLAC', 'type': 'National Park', 'state': 'MT', 'base_visitors': 1800},
        
        # National Monuments
        {'code': 'STLI', 'type': 'National Monument', 'state': 'NY', 'base_visitors': 1200},
        {'code': 'DEVA', 'type': 'National Monument', 'state': 'CA', 'base_visitors': 800},
        {'code': 'JOTR', 'type': 'National Monument', 'state': 'CA', 'base_visitors': 1500},
        {'code': 'BAND', 'type': 'National Monument', 'state': 'NM', 'base_visitors': 600},
        {'code': 'CACO', 'type': 'National Monument', 'state': 'AZ', 'base_visitors': 700},
        
        # National Recreation Areas
        {'code': 'GLEN', 'type': 'National Recreation Area', 'state': 'UT', 'base_visitors': 2000},
        {'code': 'LAME', 'type': 'National Recreation Area', 'state': 'NV', 'base_visitors': 1800},
        {'code': 'CURE', 'type': 'National Recreation Area', 'state': 'CO', 'base_visitors': 1200},
        
        # National Seashores
        {'code': 'CAHA', 'type': 'National Seashore', 'state': 'NC', 'base_visitors': 1500},
        {'code': 'ASIS', 'type': 'National Seashore', 'state': 'MD', 'base_visitors': 1200},
        
        # Historical Parks
        {'code': 'INDE', 'type': 'National Historical Park', 'state': 'PA', 'base_visitors': 800},
        {'code': 'COLO', 'type': 'National Historical Park', 'state': 'VA', 'base_visitors': 600},
        {'code': 'BOST', 'type': 'National Historical Park', 'state': 'MA', 'base_visitors': 500},
        
        # Battlefields
        {'code': 'GETT', 'type': 'National Battlefield', 'state': 'PA', 'base_visitors': 400},
        {'code': 'ANTI', 'type': 'National Battlefield', 'state': 'MD', 'base_visitors': 300},
        
        # Additional diversity
        {'code': 'BRCA', 'type': 'National Park', 'state': 'UT', 'base_visitors': 2500},
        {'code': 'CANY', 'type': 'National Park', 'state': 'UT', 'base_visitors': 2000},
        {'code': 'CARE', 'type': 'National Park', 'state': 'UT', 'base_visitors': 1800},
        {'code': 'REDW', 'type': 'National Park', 'state': 'CA', 'base_visitors': 1500},
        {'code': 'SHEN', 'type': 'National Park', 'state': 'VA', 'base_visitors': 2200},
    ]
    
    return parks

def generate_park_data(park_info, start_date, end_date):
    """Generate enhanced data for a single park with all 18 features."""
    park_code = park_info['code']
    park_type = park_info['type']
    state = park_info['state']
    base_visitors = park_info['base_visitors']
    
    region = get_region_for_state(state)
    records = []
    
    # Get holidays for the date range
    holidays = {}
    for year in range(start_date.year, end_date.year + 1):
        holidays.update(get_federal_holidays(year))
    
    current_date = start_date
    while current_date <= end_date:
        # Calculate visitor factors
        seasonal_factor = get_seasonal_factor(current_date)
        weekend_factor = 1.3 if current_date.weekday() >= 5 else 1.0
        holiday_factor = holidays.get(current_date, 1.0)
        
        # Weather simulation
        weather = simulate_weather(current_date, region)
        weather_factor = weather['factor']
        
        # School impact
        school_factor = 0.7 if is_school_in_session(current_date) else 1.2
        
        # Gas price simulation (affects travel)
        gas_price = 3.20 + (hash(f"gas{current_date}") % 100) / 100
        gas_factor = max(0.8, 2.0 - (gas_price - 3.0) * 0.3)
        
        # Random daily variation
        random_factor = 0.85 + (hash(f"{park_code}{current_date}") % 30) / 100
        
        # Calculate daily visitors
        daily_visitors = int(
            base_visitors * 
            seasonal_factor * 
            weekend_factor * 
            holiday_factor * 
            weather_factor * 
            school_factor * 
            gas_factor *
            random_factor
        )
        
        daily_visitors = max(0, daily_visitors)  # Ensure non-negative
        
        record = {
            'park_id': park_code,
            'date': current_date,
            'visitor_count': daily_visitors,
            'park_type': park_type,
            'state': state,
            'region': region,
            'temperature_high': weather['temp_high'],
            'precipitation': weather['precipitation'],
            'weather_condition': weather['condition'],
            'day_of_week': current_date.weekday(),
            'month': current_date.month,
            'is_weekend': current_date.weekday() >= 5,
            'is_holiday': current_date in holidays,
            'school_in_session': is_school_in_session(current_date),
            'gas_price': gas_price,
            'seasonal_factor': seasonal_factor,
            'visitor_category': categorize_visitor_level(daily_visitors, base_visitors)
        }
        
        records.append(record)
        current_date += datetime.timedelta(days=1)
    
    return pd.DataFrame(records)

def upsert_enhanced_data(df):
    """Insert enhanced data into database."""
    try:
        with ENGINE.begin() as conn:
            for _, row in df.iterrows():
                sql = text("""
                    INSERT INTO visitor_data (
                        park_id, date, visitor_count, park_type, state, region,
                        temperature_high, precipitation, weather_condition,
                        day_of_week, month, is_weekend, is_holiday, school_in_session,
                        gas_price, seasonal_factor, visitor_category
                    ) VALUES (
                        :park_id, :date, :visitor_count, :park_type, :state, :region,
                        :temperature_high, :precipitation, :weather_condition,
                        :day_of_week, :month, :is_weekend, :is_holiday, :school_in_session,
                        :gas_price, :seasonal_factor, :visitor_category
                    )
                    ON CONFLICT (park_id, date)
                    DO UPDATE SET visitor_count = EXCLUDED.visitor_count
                """)
                conn.execute(sql, row.to_dict())
        return True
    except Exception as e:
        print(f"Database insert failed: {e}")
        return False

def main():
    """Complete dataset generation pipeline - one script to rule them all!"""
    logger = setup_logging()
    
    print("🚀 Forecast My Park - Comprehensive Dataset Generator")
    print("=" * 65)
    print("🎯 ONE SCRIPT TO RULE THEM ALL!")
    print("🔧 Creating enhanced database schema...")
    print("📊 Generating 39,000+ records with 18+ features...")
    print("🏞️  Processing 30+ parks across all regions...")
    print("🎯 Building production-ready ML dataset...")
    print("=" * 65)
    
    try:
        # Step 1: Create enhanced schema
        logger.info("🔧 Creating enhanced database schema...")
        if not create_enhanced_schema():
            logger.error("❌ Failed to create enhanced schema")
            return False
        logger.info("✅ Enhanced schema created successfully")
        
        # Step 2: Get park list
        parks = get_expanded_park_list()
        logger.info(f"🎯 Selected {len(parks)} diverse parks for processing")
        
        # Step 3: Generate comprehensive data
        start_date = datetime.date(2022, 1, 1)
        end_date = datetime.date.today()
        days_per_park = (end_date - start_date).days + 1
        
        logger.info(f"📊 Generating {days_per_park} days per park ({start_date} to {end_date})")
        
        success_count = 0
        error_count = 0
        total_records = 0
        
        # Process each park
        for i, park_info in enumerate(parks):
            park_code = park_info['code']
            
            try:
                logger.info(f"🏞️  Processing park {i+1}/{len(parks)}: {park_code}")
                
                # Generate data
                df = generate_park_data(park_info, start_date, end_date)
                
                # Save to database
                if upsert_enhanced_data(df):
                    total_records += len(df)
                    success_count += 1
                    logger.info(f"✅ {park_code}: {len(df)} records generated")
                else:
                    logger.error(f"❌ Failed to save data for {park_code}")
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error processing {park_code}: {e}")
                continue
        
        # Summary
        improvement_factor = total_records / 1500  # vs original 1,500 records
        
        logger.info("=" * 65)
        logger.info("🎉 DATASET GENERATION COMPLETE!")
        logger.info(f"   • Parks processed: {success_count}/{len(parks)}")
        logger.info(f"   • Total records: {total_records:,}")
        logger.info(f"   • Days per park: {days_per_park}")
        logger.info(f"   • Improvement: {improvement_factor:.1f}x more data")
        logger.info(f"   • Rich features: Weather, holidays, economics, temporal")
        logger.info("=" * 65)
        
        if success_count == 0:
            logger.error("❌ No parks processed successfully!")
            return False
        
        # Success message
        print(f"\n🎉 SUCCESS! Generated {total_records:,} records for {success_count} parks!")
        print("\nYour comprehensive dataset includes:")
        print("  ✅ Enhanced database table with 18 columns")
        print("  ✅ Weather factors (temperature, precipitation, conditions)")
        print("  ✅ Temporal patterns (weekends, holidays, seasonality)")
        print("  ✅ Economic factors (gas prices, travel costs)")
        print("  ✅ Geographic diversity (5 regions, multiple park types)")
        print("  ✅ 3.5+ years of data per park (2022-2025)")
        print("  ✅ Production-ready for ML forecasting")
        print("\n🚀 Your Prophet models now have professional-grade data!")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Critical error in dataset generation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
