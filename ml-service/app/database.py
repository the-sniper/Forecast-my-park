import pandas as pd
from sqlalchemy import create_engine, text
from typing import List, Optional
from .config import config
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(config.database_url)
    
    def get_park_data(self, park_id: str, days_back: int = 365) -> pd.DataFrame:
        """
        Fetch historical visitor data for a specific park from enhanced dataset.
        
        Args:
            park_id: Park identifier
            days_back: Number of days to look back from today
            
        Returns:
            DataFrame with columns: date, visitor_count, and rich features
        """
        try:
            with self.engine.begin() as conn:
                # Get enhanced data with all features
                df = pd.read_sql(
                    """
                    SELECT 
                        date, 
                        visitor_count,
                        temperature_high,
                        precipitation,
                        weather_condition,
                        is_weekend,
                        is_holiday,
                        school_in_session,
                        seasonal_factor,
                        gas_price,
                        park_type,
                        state,
                        region,
                        day_of_week,
                        month
                    FROM visitor_data 
                    WHERE park_id = %(park_id)s 
                    ORDER BY date ASC
                    """, 
                    conn, 
                    params={"park_id": park_id}
                )
                
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            logger.info(f"Retrieved {len(df)} enhanced records for park {park_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching enhanced data for park {park_id}: {e}")
            return pd.DataFrame()
    
    def get_all_parks(self) -> List[str]:
        """Get list of all available park IDs from enhanced dataset."""
        query = text("SELECT DISTINCT park_id FROM visitor_data ORDER BY park_id")
        
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query)
                parks = [row[0] for row in result.fetchall()]
                
            logger.info(f"Found {len(parks)} parks in enhanced database")
            return parks
            
        except Exception as e:
            logger.error(f"Error fetching park list: {e}")
            return []
    
    def get_park_stats(self, park_id: str) -> Optional[dict]:
        """Get basic statistics for a park from enhanced dataset."""
        query = text("""
            SELECT 
                COUNT(*) as total_days,
                AVG(visitor_count) as avg_visitors,
                MIN(visitor_count) as min_visitors,
                MAX(visitor_count) as max_visitors,
                MIN(date) as first_date,
                MAX(date) as last_date,
                AVG(temperature_high) as avg_temperature,
                SUM(CASE WHEN is_weekend = true THEN 1 ELSE 0 END) as weekend_days,
                SUM(CASE WHEN is_holiday = true THEN 1 ELSE 0 END) as holiday_days
            FROM visitor_data 
            WHERE park_id = :park_id
        """)
        
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"park_id": park_id}).fetchone()
                
            if result:
                return {
                    "park_id": park_id,
                    "total_days": result[0],
                    "avg_visitors": round(result[1], 0) if result[1] else 0,
                    "min_visitors": result[2],
                    "max_visitors": result[3],
                    "first_date": str(result[4]),
                    "last_date": str(result[5]),
                    "avg_temperature": round(result[6], 1) if result[6] else None,
                    "weekend_days": result[7],
                    "holiday_days": result[8]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching enhanced stats for park {park_id}: {e}")
            return None
    
    def get_park_metadata(self, park_id: str) -> Optional[dict]:
        """Get comprehensive park metadata with aggregated values."""
        query = text("""
            SELECT 
                park_type,
                state,
                region,
                AVG(temperature_high) as avg_temperature_high,
                AVG(precipitation) as avg_precipitation,
                MODE() WITHIN GROUP (ORDER BY weather_condition) as most_common_weather,
                AVG(CASE WHEN is_weekend = true THEN 1.0 ELSE 0.0 END) as weekend_ratio,
                AVG(CASE WHEN is_holiday = true THEN 1.0 ELSE 0.0 END) as holiday_ratio,
                AVG(CASE WHEN school_in_session = true THEN 1.0 ELSE 0.0 END) as school_session_ratio,
                AVG(seasonal_factor) as avg_seasonal_factor,
                MODE() WITHIN GROUP (ORDER BY visitor_category) as most_common_visitor_category,
                COUNT(*) as total_data_points,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM visitor_data 
            WHERE park_id = :park_id
            GROUP BY park_type, state, region
        """)
        
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"park_id": park_id}).fetchone()
                
            if result:
                return {
                    "park_type": result[0],
                    "state": result[1],
                    "region": result[2],
                    "avg_temperature_high": round(result[3], 1) if result[3] else None,
                    "avg_precipitation": round(result[4], 2) if result[4] else None,
                    "most_common_weather": result[5],
                    "weekend_ratio": round(result[6], 3) if result[6] else None,
                    "holiday_ratio": round(result[7], 3) if result[7] else None,
                    "school_session_ratio": round(result[8], 3) if result[8] else None,
                    "avg_seasonal_factor": round(result[9], 3) if result[9] else None,
                    "most_common_visitor_category": result[10],
                    "total_data_points": result[11],
                    "earliest_date": str(result[12]) if result[12] else None,
                    "latest_date": str(result[13]) if result[13] else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching metadata for park {park_id}: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager() 