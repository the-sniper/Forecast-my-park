import os
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import logging

from .model_trainer import ParkVisitorPredictor
from .database import db_manager
from .config import config

logger = logging.getLogger(__name__)

# Park coordinates mapping (latitude, longitude)
PARK_COORDINATES = {
    # Major National Parks
    'YELL': (44.428, -110.588),  # Yellowstone
    'GRCA': (36.1069, -112.1129),  # Grand Canyon
    'YOSE': (37.8651, -119.5383),  # Yosemite
    'ZION': (37.2982, -113.0263),  # Zion
    'ACAD': (44.35, -68.21),  # Acadia
    'ARCH': (38.68, -109.57),  # Arches
    'ROMO': (40.4, -105.58),  # Rocky Mountain
    'GRSM': (35.6117, -83.4895),  # Great Smoky Mountains
    'OLYM': (47.8021, -123.6044),  # Olympic
    'GLAC': (48.7596, -113.787),  # Glacier
    
    # National Monuments & Historic Sites
    'DEVA': (36.5054, -117.0794),  # Death Valley
    'JOTR': (33.8734, -115.901),  # Joshua Tree
    'BAND': (35.7781, -106.2708),  # Bandelier
    'CACO': (42.0699, -70.0464),  # Cape Cod
    'STLI': (40.6892, -74.0445),  # Statue of Liberty
    
    # National Recreation Areas
    'GLEN': (37.0042, -111.1892),  # Glen Canyon
    'LAME': (36.0905, -114.7366),  # Lake Mead
    'CURE': (38.4619, -107.1817),  # Curecanti
    
    # National Seashores
    'CAHA': (35.2590, -75.5277),  # Cape Hatteras
    'ASIS': (38.0593, -75.1458),  # Assateague Island
    
    # Historical Parks
    'INDE': (39.9496, -75.1503),  # Independence
    'COLO': (37.2707, -76.6135),  # Colonial
    'BOST': (42.3601, -71.0589),  # Boston
    'GETT': (39.8309, -77.2361),  # Gettysburg
    'ANTI': (39.4618, -77.7311),  # Antietam
    
    # Additional Parks
    'BRCA': (37.5930, -112.1871),  # Bryce Canyon
    'CANY': (38.2, -109.93),  # Canyonlands
    'CARE': (38.0877, -111.1660),  # Capitol Reef
    'REDW': (41.2132, -124.0046),  # Redwood
    'SHEN': (38.2928, -78.6795),  # Shenandoah
    'BADL': (43.8554, -101.9777),  # Badlands
    'EVER': (25.2866, -80.8987),  # Everglades
    'ABLI': (37.5429, -85.6739),  # Abraham Lincoln Birthplace
    'ADAM': (42.2553, -71.0275),  # Adams
    'AFBG': (40.7150, -74.0042),  # African Burial Ground
    'AGFO': (42.4186, -103.7273),  # Agate Fossil Beds
    'ALFL': (35.5669, -101.6719),  # Alibates Flint Quarries
    'AMIS': (29.5255, -101.0769),  # Amistad
    'ANIA': (56.8987, -158.6114),  # Aniakchak
    'APCO': (37.3760, -78.7959),  # Appomattox Court House
    'AZRU': (36.8389, -107.9983),  # Aztec Ruins
    'BEPA': (38.9072, -77.0369),  # Belmont-Paul Women's Equality
    'BIBE': (29.1275, -103.2425),  # Big Bend
    'BICA': (45.0293, -108.1618),  # Bighorn Canyon
    'BICR': (33.5186, -86.8104),  # Birmingham Civil Rights
    'BISC': (25.4390, -80.4017),  # Biscayne
    'BLCA': (38.5753, -107.7018),  # Black Canyon of the Gunnison
    'BLRV': (42.1341, -71.1636),  # Blackstone River Valley
    'BOWA': (37.1214, -79.9081),  # Booker T Washington
    'BOHA': (42.3398, -70.9661),  # Boston Harbor Islands
    'BRVB': (39.0409, -95.6890),  # Brown v. Board of Education
    'BUIS': (17.7539, -64.6255),  # Buck Island Reef
    'CABR': (32.6722, -117.2417),  # Cabrillo
    'CANE': (37.7862, -84.5985),  # Camp Nelson
    'CANA': (28.8123, -80.8101),  # Canaveral
    'CARI': (31.0407, -93.0096),  # Cane River Creole
    'CACH': (36.1490, -109.3389),  # Canyon de Chelly
    'CALO': (34.6204, -76.5197),  # Cape Lookout
    'CAVO': (36.7828, -103.9705),  # Capulin Volcano
    'CIBS': (40.2019, -77.1956),  # Carlisle Federal Indian Boarding School
    'CAVE': (32.1478, -104.5567),  # Carlsbad Caverns
    'CAGR': (32.4797, -111.5375),  # Casa Grande Ruins
    'CASA': (29.8974, -81.3123),  # Castillo de San Marcos
    'CACL': (40.7033, -74.0170),  # Castle Clinton
    'CAMO': (35.2917, -115.0881),  # Castle Mountains
    'CEBR': (37.6283, -112.8453),  # Cedar Breaks
    'CEBE': (39.0052, -78.3086),  # Cedar Creek & Belle Grove
    'CAME': (36.9212, -76.0051),  # Cape Henry Memorial
    'CAKR': (67.4162, -163.1524),  # Cape Krusenstern
    'CHCU': (36.0544, -107.9914),  # Chaco Culture
    'CHIS': (34.0069, -119.7785),  # Channel Islands
}

# Park names mapping
PARK_NAMES = {
    'YELL': 'Yellowstone National Park',
    'GRCA': 'Grand Canyon National Park',
    'YOSE': 'Yosemite National Park',
    'ZION': 'Zion National Park',
    'ACAD': 'Acadia National Park',
    'ARCH': 'Arches National Park',
    'ROMO': 'Rocky Mountain National Park',
    'GRSM': 'Great Smoky Mountains National Park',
    'OLYM': 'Olympic National Park',
    'GLAC': 'Glacier National Park',
    'DEVA': 'Death Valley National Monument',
    'JOTR': 'Joshua Tree National Park',
    'BAND': 'Bandelier National Monument',
    'CACO': 'Cape Cod National Seashore',
    'GLEN': 'Glen Canyon National Recreation Area',
    'LAME': 'Lake Mead National Recreation Area',
    'CURE': 'Curecanti National Recreation Area',
    'CAHA': 'Cape Hatteras National Seashore',
    'ASIS': 'Assateague Island National Seashore',
    'INDE': 'Independence National Historical Park',
    'COLO': 'Colonial National Historical Park',
    'BOST': 'Boston National Historical Park',
    'GETT': 'Gettysburg National Battlefield',
    'ANTI': 'Antietam National Battlefield',
    'BRCA': 'Bryce Canyon National Park',
    'CANY': 'Canyonlands National Park',
    'CARE': 'Capitol Reef National Park',
    'REDW': 'Redwood National and State Parks',
    'SHEN': 'Shenandoah National Park',
    'BADL': 'Badlands National Park',
    'EVER': 'Everglades National Park',
    'ABLI': 'Abraham Lincoln Birthplace National Historical Park',
    'ADAM': 'Adams National Historical Park',
    'AFBG': 'African Burial Ground National Monument',
    'AGFO': 'Agate Fossil Beds National Monument',
    'ALFL': 'Alibates Flint Quarries National Monument',
    'AMIS': 'Amistad National Recreation Area',
    'ANIA': 'Aniakchak National Monument & Preserve',
    'APCO': 'Appomattox Court House National Historical Park',
    'AZRU': 'Aztec Ruins National Monument',
    'BEPA': 'Belmont-Paul Women\'s Equality National Monument',
    'BIBE': 'Big Bend National Park',
    'BICA': 'Bighorn Canyon National Recreation Area',
    'BICR': 'Birmingham Civil Rights National Monument',
    'BISC': 'Biscayne National Park',
    'BLCA': 'Black Canyon Of The Gunnison National Park',
    'BLRV': 'Blackstone River Valley National Historical Park',
    'BOWA': 'Booker T Washington National Monument',
    'BOHA': 'Boston Harbor Islands National Recreation Area',
    'BRVB': 'Brown v. Board of Education National Historical Park',
    'BUIS': 'Buck Island Reef National Monument',
    'CABR': 'Cabrillo National Monument',
    'CANE': 'Camp Nelson National Monument',
    'CANA': 'Canaveral National Seashore',
    'CARI': 'Cane River Creole National Historical Park',
    'CACH': 'Canyon de Chelly National Monument',
    'CALO': 'Cape Lookout National Seashore',
    'CAVO': 'Capulin Volcano National Monument',
    'CIBS': 'Carlisle Federal Indian Boarding School National Monument',
    'CAVE': 'Carlsbad Caverns National Park',
    'CAGR': 'Casa Grande Ruins National Monument',
    'CASA': 'Castillo de San Marcos National Monument',
    'CACL': 'Castle Clinton National Monument',
    'CAMO': 'Castle Mountains National Monument',
    'CEBR': 'Cedar Breaks National Monument',
    'CEBE': 'Cedar Creek & Belle Grove National Historical Park',
    'CAME': 'Cape Henry Memorial Part of Colonial National Historical Park',
    'CAKR': 'Cape Krusenstern National Monument',
}

class PredictionService:
    def __init__(self):
        self.loaded_models: Dict[str, ParkVisitorPredictor] = {}
        self.model_cache_ttl = timedelta(hours=24)  # Reload models daily
    
    def _get_model_path(self, park_id: str) -> Optional[str]:
        """Get the path to a saved model file for a park."""
        pattern = os.path.join(
            config.MODEL_DIR, 
            f"{config.MODEL_FILE_PREFIX}_{park_id}.joblib"
        )
        
        matching_files = glob.glob(pattern)
        return matching_files[0] if matching_files else None
    
    def _load_model(self, park_id: str) -> Optional[ParkVisitorPredictor]:
        """Load a model for the specified park."""
        model_path = self._get_model_path(park_id)
        
        if not model_path:
            logger.warning(f"No saved model found for park {park_id}")
            return None
        
        predictor = ParkVisitorPredictor(park_id)
        if predictor.load_model(model_path):
            return predictor
        
        return None
    
    def _get_or_load_model(self, park_id: str) -> Optional[ParkVisitorPredictor]:
        """Get model from cache or load from disk."""
        # Check if model is already loaded and fresh
        if park_id in self.loaded_models:
            predictor = self.loaded_models[park_id]
            if predictor.trained_at:
                age = datetime.now() - predictor.trained_at
                if age < self.model_cache_ttl:
                    return predictor
        
        # Load model from disk
        predictor = self._load_model(park_id)
        if predictor:
            self.loaded_models[park_id] = predictor
            
        return predictor
    
    def predict_visitors(
        self, 
        park_id: str, 
        start_date: str, 
        days_ahead: int = 30
    ) -> Dict:
        """
        Generate visitor predictions for a park.
        
        Args:
            park_id: Park identifier
            start_date: Start date for predictions (YYYY-MM-DD)
            days_ahead: Number of days to predict
            
        Returns:
            Dictionary with predictions and metadata
        """
        try:
            # Validate inputs
            if days_ahead < 1 or days_ahead > 365:
                raise ValueError("days_ahead must be between 1 and 365")
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            if start_dt < datetime.now().date():
                raise ValueError("start_date cannot be in the past")
            
            # Load model
            predictor = self._get_or_load_model(park_id)
            if not predictor:
                # Try to train a new model if none exists
                logger.info(f"No model found for {park_id}, attempting to train...")
                predictor = ParkVisitorPredictor(park_id)
                try:
                    predictor.train()
                    predictor.save_model()
                    self.loaded_models[park_id] = predictor
                except Exception as e:
                    raise ValueError(f"Could not train model for park {park_id}: {e}")
            
            # Generate predictions
            forecast_df = predictor.predict(days_ahead)
            
            # Filter predictions to start from the requested date
            forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
            forecast_df = forecast_df[
                forecast_df['ds'] >= pd.to_datetime(start_date)
            ].head(days_ahead)
            
            # Convert to list of dictionaries for JSON response
            predictions = []
            for _, row in forecast_df.iterrows():
                predictions.append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_visitors': int(row['yhat']),
                    'lower_bound': int(row['yhat_lower']),
                    'upper_bound': int(row['yhat_upper']),
                    'confidence_interval': f"{int(row['yhat_lower'])}-{int(row['yhat_upper'])}"
                })
            
            # Get park statistics for context
            park_stats = db_manager.get_park_stats(park_id)
            
            return {
                'success': True,
                'park_id': park_id,
                'prediction_start': start_date,
                'days_predicted': len(predictions),
                'predictions': predictions,
                'model_info': {
                    'trained_at': predictor.trained_at.isoformat() if predictor.trained_at else None,
                    'model_type': 'Prophet',
                },
                'park_stats': park_stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for park {park_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'park_id': park_id
            }
    
    def get_available_parks(self) -> List[Dict]:
        """Get list of parks with available models or data."""
        parks = db_manager.get_all_parks()
        available_parks = []
        
        for park_id in parks:
            stats = db_manager.get_park_stats(park_id)
            metadata = db_manager.get_park_metadata(park_id)
            model_path = self._get_model_path(park_id)
            coordinates = PARK_COORDINATES.get(park_id)
            
            park_info = {
                'park_id': park_id,
                'name': PARK_NAMES.get(park_id, park_id),  # Use park name or fallback to ID
                'state': metadata.get('state') if metadata else 'Unknown',
                'region': metadata.get('region') if metadata else 'Unknown',
                'park_type': metadata.get('park_type') if metadata else 'Unknown',
                'has_model': model_path is not None,
                'data_available': stats is not None
            }
            
            # Add coordinates if available
            if coordinates:
                park_info['latitude'] = coordinates[0]
                park_info['longitude'] = coordinates[1]
            
            if stats:
                park_info['visitor_stats'] = {
                    'min_visitors': stats.get('min_visitors', 0),
                    'max_visitors': stats.get('max_visitors', 0),
                    'avg_visitors': stats.get('avg_visitors', 0)
                }
            
            # Add comprehensive metadata if available
            if metadata:
                park_info['metadata'] = {
                    'avg_temperature_high': metadata.get('avg_temperature_high'),
                    'avg_precipitation': metadata.get('avg_precipitation'),
                    'most_common_weather': metadata.get('most_common_weather'),
                    'weekend_ratio': metadata.get('weekend_ratio'),
                    'holiday_ratio': metadata.get('holiday_ratio'),
                    'school_session_ratio': metadata.get('school_session_ratio'),
                    'avg_seasonal_factor': metadata.get('avg_seasonal_factor'),
                    'most_common_visitor_category': metadata.get('most_common_visitor_category'),
                    'total_data_points': metadata.get('total_data_points'),
                    'earliest_date': metadata.get('earliest_date'),
                    'latest_date': metadata.get('latest_date')
                }
            
            available_parks.append(park_info)
        
        return available_parks
    
    def retrain_model(self, park_id: str) -> Dict:
        """Retrain model for a specific park."""
        try:
            predictor = ParkVisitorPredictor(park_id)
            metrics = predictor.train()
            predictor.save_model()
            
            # Update cache
            self.loaded_models[park_id] = predictor
            
            return {
                'success': True,
                'park_id': park_id,
                'metrics': metrics,
                'message': 'Model retrained successfully'
            }
            
        except Exception as e:
            logger.error(f"Retraining failed for park {park_id}: {e}")
            return {
                'success': False,
                'park_id': park_id,
                'error': str(e)
            }
    
    def get_model_performance(self, park_id: str) -> Dict:
        """Get performance metrics for a park's model."""
        predictor = self._get_or_load_model(park_id)
        
        if not predictor:
            return {
                'success': False,
                'error': f'No model available for park {park_id}'
            }
        
        return {
            'success': True,
            'park_id': park_id,
            'trained_at': predictor.trained_at.isoformat() if predictor.trained_at else None,
            'metrics': predictor.model_metrics.to_dict() if predictor.model_metrics is not None else None
        }

# Global prediction service instance
prediction_service = PredictionService() 