import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
import joblib
import os
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from .database import db_manager
from .config import config

logger = logging.getLogger(__name__)

class ParkVisitorPredictor:
    def __init__(self, park_id: str):
        self.park_id = park_id
        self.model = None
        self.model_metrics = None
        self.trained_at = None
        
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare enhanced data for Prophet training with weather and temporal features.
        Prophet expects columns: ds (date), y (value to predict)
        """
        if df.empty:
            raise ValueError(f"No data available for park {self.park_id}")
            
        # Prophet requires specific column names
        prophet_df = df.copy()
        prophet_df = prophet_df.rename(columns={
            'date': 'ds',
            'visitor_count': 'y'
        })
        
        # Remove any rows with missing values in critical columns
        prophet_df = prophet_df.dropna(subset=['ds', 'y'])
        
        # Keep existing enhanced features for model training
        # Weather features
        prophet_df['temperature'] = prophet_df['temperature_high'].fillna(prophet_df['temperature_high'].mean())
        prophet_df['rain'] = (prophet_df['precipitation'] > 0.1).astype(int)
        prophet_df['precipitation_mm'] = prophet_df['precipitation'].fillna(0)
        
        # Temporal features (already available from enhanced dataset)
        prophet_df['is_weekend'] = prophet_df['is_weekend'].fillna(0).astype(int)
        prophet_df['is_holiday'] = prophet_df['is_holiday'].fillna(0).astype(int)
        prophet_df['school_in_session'] = prophet_df['school_in_session'].fillna(1).astype(int)
        prophet_df['seasonal_factor'] = prophet_df['seasonal_factor'].fillna(1.0)
        
        # Economic features  
        prophet_df['gas_price'] = prophet_df['gas_price'].fillna(prophet_df['gas_price'].mean())
        
        # Create additional engineered features
        prophet_df['temp_squared'] = prophet_df['temperature'] ** 2  # Non-linear temperature effects
        prophet_df['weekend_holiday'] = (prophet_df['is_weekend'] | prophet_df['is_holiday']).astype(int)
        prophet_df['summer_peak'] = ((prophet_df['month'] >= 6) & (prophet_df['month'] <= 8)).astype(int)
        prophet_df['winter_low'] = ((prophet_df['month'] <= 2) | (prophet_df['month'] == 12)).astype(int)
        
        logger.info(f"Prepared {len(prophet_df)} enhanced data points with weather/temporal features for training")
        return prophet_df
    
    def create_model(self) -> Prophet:
        """Create and configure Prophet model optimized for enhanced park visitor data."""
        model = Prophet(
            growth='linear',
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,  # Not relevant for daily data
            seasonality_mode='multiplicative',  # Better for visitor patterns
            changepoint_prior_scale=0.1,  # More aggressive changepoints with more data
            seasonality_prior_scale=15.0,   # Strong seasonality
            holidays_prior_scale=15.0,      # Strong holiday effects
            interval_width=0.8              # 80% confidence intervals
        )
        
        # Add weather regressors
        model.add_regressor('temperature', prior_scale=10.0)
        model.add_regressor('temp_squared', prior_scale=5.0)
        model.add_regressor('rain', prior_scale=10.0)
        model.add_regressor('precipitation_mm', prior_scale=5.0)
        
        # Add temporal regressors
        model.add_regressor('is_weekend', prior_scale=10.0)
        model.add_regressor('is_holiday', prior_scale=15.0)
        model.add_regressor('school_in_session', prior_scale=8.0)
        model.add_regressor('weekend_holiday', prior_scale=12.0)
        
        # Add seasonal regressors
        model.add_regressor('summer_peak', prior_scale=10.0)
        model.add_regressor('winter_low', prior_scale=8.0)
        model.add_regressor('seasonal_factor', prior_scale=12.0)
        
        # Add economic regressor
        model.add_regressor('gas_price', prior_scale=5.0)
        
        # Add enhanced seasonalities
        model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=8  # More complex monthly patterns
        )
        
        model.add_seasonality(
            name='quarterly',
            period=91.25,
            fourier_order=4
        )
        
        return model
    
    def add_holidays(self, model: Prophet) -> Prophet:
        """Add US holidays that affect park visitation."""
        # Create holiday dataframe for US federal holidays
        holidays = pd.DataFrame({
            'holiday': 'US_holidays',
            'ds': pd.to_datetime([
                # Major holidays that affect park visitation
                '2023-01-01',  # New Year's Day
                '2023-05-29',  # Memorial Day
                '2023-07-04',  # Independence Day
                '2023-09-04',  # Labor Day
                '2023-11-23',  # Thanksgiving
                '2023-12-25',  # Christmas
                '2024-01-01',  # New Year's Day
                '2024-05-27',  # Memorial Day
                '2024-07-04',  # Independence Day
                '2024-09-02',  # Labor Day
                '2024-11-28',  # Thanksgiving
                '2024-12-25',  # Christmas
                '2025-01-01',  # New Year's Day
                '2025-05-26',  # Memorial Day
                '2025-07-04',  # Independence Day
                '2025-09-01',  # Labor Day
                '2025-11-27',  # Thanksgiving
                '2025-12-25',  # Christmas
            ]),
            'lower_window': 0,
            'upper_window': 0,
        })
        
        return model.add_seasonality(
            name='holidays',
            period=365.25,
            fourier_order=2,
            condition_name='is_holiday'
        )
    
    def train(self, days_back: int = 365) -> Dict[str, Any]:
        """
        Train the Prophet model for this park.
        
        Args:
            days_back: Number of days of historical data to use
            
        Returns:
            Training metrics and model info
        """
        logger.info(f"Starting training for park {self.park_id}")
        
        # Get historical data
        df = db_manager.get_park_data(self.park_id, days_back)
        if df.empty:
            raise ValueError(f"No data available for park {self.park_id}")
        
        # Prepare data for Prophet
        prophet_df = self.prepare_data(df)
        
        # Create and configure model
        self.model = self.create_model()
        
        # Train the model
        logger.info("Training Prophet model...")
        self.model.fit(prophet_df)
        self.trained_at = datetime.now()
        
        # Perform cross-validation for model evaluation
        logger.info("Performing cross-validation...")
        try:
            cv_results = cross_validation(
                self.model, 
                initial='60 days', 
                period='30 days', 
                horizon='30 days'
            )
            self.model_metrics = performance_metrics(cv_results)
            
            # Calculate summary metrics
            mae = self.model_metrics['mae'].mean()
            mape = self.model_metrics['mape'].mean()
            rmse = self.model_metrics['rmse'].mean()
            
            metrics = {
                'mae': mae,
                'mape': mape, 
                'rmse': rmse,
                'training_points': len(prophet_df),
                'trained_at': self.trained_at.isoformat()
            }
            
            logger.info(f"Training complete. MAE: {mae:.0f}, MAPE: {mape:.2%}, RMSE: {rmse:.0f}")
            
        except Exception as e:
            logger.warning(f"Cross-validation failed: {e}. Using basic metrics.")
            metrics = {
                'training_points': len(prophet_df),
                'trained_at': self.trained_at.isoformat(),
                'mae': None,
                'mape': None,
                'rmse': None
            }
        
        return metrics
    
    def predict(self, days_ahead: int = 30) -> pd.DataFrame:
        """
        Generate predictions for the specified number of days ahead with enhanced features.
        
        Args:
            days_ahead: Number of days to predict
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=days_ahead)
        
        # Generate enhanced features for future dates
        # Get the last known feature values for extrapolation
        historical_data = db_manager.get_park_data(self.park_id)
        if not historical_data.empty:
            # Calculate feature averages for realistic future values
            avg_temp = historical_data['temperature_high'].mean()
            avg_precip = historical_data['precipitation'].mean()
            avg_gas = historical_data['gas_price'].mean()
            
            # Add weather features (use seasonal patterns for future)
            future['temperature'] = avg_temp + 15 * np.sin(2 * np.pi * (future['ds'].dt.dayofyear - 80) / 365)
            future['temp_squared'] = future['temperature'] ** 2
            future['precipitation_mm'] = np.random.poisson(avg_precip, len(future))
            future['rain'] = (future['precipitation_mm'] > 0.1).astype(int)
            
            # Add temporal features
            future['day_of_week'] = future['ds'].dt.dayofweek
            future['month'] = future['ds'].dt.month
            future['is_weekend'] = future['day_of_week'].isin([5, 6]).astype(int)
            
            # Add holiday detection (simplified - major federal holidays)
            future['is_holiday'] = 0
            for _, row in future.iterrows():
                date = row['ds']
                # Major holidays that affect park visitation
                if ((date.month == 7 and date.day == 4) or  # July 4th
                    (date.month == 5 and date.day >= 25 and date.weekday() == 0) or  # Memorial Day
                    (date.month == 9 and date.day <= 7 and date.weekday() == 0) or   # Labor Day
                    (date.month == 11 and date.day >= 22 and date.day <= 28 and date.weekday() == 3) or  # Thanksgiving
                    (date.month == 12 and date.day == 25) or  # Christmas
                    (date.month == 1 and date.day == 1)):     # New Year
                    future.loc[future['ds'] == date, 'is_holiday'] = 1
            
            # School session (simplified: in session Sept-May, summer break June-Aug)
            future['school_in_session'] = ((future['month'] <= 5) | (future['month'] >= 9)).astype(int)
            
            # Seasonal factors
            future['seasonal_factor'] = 0.6 + 0.8 * (np.sin(2 * np.pi * (future['ds'].dt.dayofyear - 80) / 365) + 1)
            
            # Economic features (assume gradual increase)
            future['gas_price'] = avg_gas * (1 + 0.03 * (future.index / 365))  # 3% annual increase
            
            # Engineered features
            future['weekend_holiday'] = (future['is_weekend'] | future['is_holiday']).astype(int)
            future['summer_peak'] = ((future['month'] >= 6) & (future['month'] <= 8)).astype(int)
            future['winter_low'] = ((future['month'] <= 2) | (future['month'] == 12)).astype(int)
        
        # Generate predictions
        forecast = self.model.predict(future)
        
        # Return only future predictions with key columns
        future_predictions = forecast.tail(days_ahead)[
            ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        ].copy()
        
        # Ensure no negative predictions
        future_predictions['yhat'] = future_predictions['yhat'].clip(lower=0)
        future_predictions['yhat_lower'] = future_predictions['yhat_lower'].clip(lower=0)
        future_predictions['yhat_upper'] = future_predictions['yhat_upper'].clip(lower=0)
        
        # Round to whole numbers (can't have partial visitors)
        future_predictions['yhat'] = future_predictions['yhat'].round().astype(int)
        future_predictions['yhat_lower'] = future_predictions['yhat_lower'].round().astype(int)
        future_predictions['yhat_upper'] = future_predictions['yhat_upper'].round().astype(int)
        
        return future_predictions
    
    def save_model(self, model_dir: str = None) -> str:
        """Save the trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save")
            
        if model_dir is None:
            model_dir = config.MODEL_DIR
            
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(
            model_dir, 
            f"{config.MODEL_FILE_PREFIX}_{self.park_id}.joblib"
        )
        
        model_data = {
            'model': self.model,
            'park_id': self.park_id,
            'trained_at': self.trained_at,
            'metrics': self.model_metrics
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"Model saved to {model_path}")
        
        return model_path
    
    def load_model(self, model_path: str) -> bool:
        """Load a trained model from disk."""
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.park_id = model_data['park_id']
            self.trained_at = model_data['trained_at']
            self.model_metrics = model_data.get('metrics')
            
            logger.info(f"Model loaded from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

def train_all_parks() -> Dict[str, Any]:
    """Train models for all parks in the database."""
    parks = db_manager.get_all_parks()
    results = {}
    
    logger.info(f"Training models for {len(parks)} parks")
    
    for park_id in parks:
        try:
            predictor = ParkVisitorPredictor(park_id)
            metrics = predictor.train()
            predictor.save_model()
            
            results[park_id] = {
                'status': 'success',
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to train model for {park_id}: {e}")
            results[park_id] = {
                'status': 'failed',
                'error': str(e)
            }
    
    return results 