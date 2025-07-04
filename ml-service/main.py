import logging
import sys
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from app.config import config
from app.predictor import prediction_service
from app.model_trainer import train_all_parks
from app.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ml_service.log')
    ]
)

logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class PredictionRequest(BaseModel):
    park_id: str = Field(..., description="Park identifier")
    start_date: str = Field(..., description="Start date for predictions (YYYY-MM-DD)")
    days_ahead: int = Field(30, ge=1, le=365, description="Number of days to predict (1-365)")
    
    @validator('start_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class PredictionResponse(BaseModel):
    success: bool
    park_id: str
    prediction_start: Optional[str] = None
    days_predicted: Optional[int] = None
    predictions: Optional[List[dict]] = None
    model_info: Optional[dict] = None
    park_stats: Optional[dict] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None

class ParkInfo(BaseModel):
    park_id: str
    name: str
    state: str
    region: str
    park_type: str
    has_model: bool
    data_available: Optional[bool] = None
    visitor_stats: Optional[dict] = None
    metadata: Optional[dict] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database_connected: bool
    models_available: int

# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        parks = db_manager.get_all_parks()
        db_connected = len(parks) >= 0
    except Exception:
        db_connected = False
    
    available_parks = prediction_service.get_available_parks()
    models_count = sum(1 for park in available_parks if park['has_model'])
    
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        timestamp=datetime.now().isoformat(),
        version=config.API_VERSION,
        database_connected=db_connected,
        models_available=models_count
    )

@app.get("/parks", response_model=List[ParkInfo])
async def get_parks():
    """Get list of all available parks with their model status."""
    try:
        parks = prediction_service.get_available_parks()
        return [ParkInfo(**park) for park in parks]
    except Exception as e:
        logger.error(f"Error fetching parks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch parks")

@app.post("/predict", response_model=PredictionResponse)
async def predict_visitors(request: PredictionRequest):
    """
    Generate visitor predictions for a specific park.
    
    - **park_id**: Identifier for the park
    - **start_date**: Start date for predictions (YYYY-MM-DD format)
    - **days_ahead**: Number of days to predict (1-365)
    """
    try:
        result = prediction_service.predict_visitors(
            park_id=request.park_id,
            start_date=request.start_date,
            days_ahead=request.days_ahead
        )
        
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/predict/{park_id}")
async def quick_predict(
    park_id: str,
    days_ahead: int = Query(30, ge=1, le=365, description="Number of days to predict"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD), defaults to tomorrow")
):
    """
    Quick prediction endpoint with URL parameters.
    """
    if start_date is None:
        start_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    request = PredictionRequest(
        park_id=park_id,
        start_date=start_date,
        days_ahead=days_ahead
    )
    
    return await predict_visitors(request)

@app.get("/parks/{park_id}/stats")
async def get_park_stats(park_id: str):
    """Get statistical information for a specific park."""
    try:
        stats = db_manager.get_park_stats(park_id)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Park {park_id} not found")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats for {park_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch park stats")

@app.post("/models/train/{park_id}")
async def retrain_model(park_id: str, background_tasks: BackgroundTasks):
    """
    Retrain the model for a specific park.
    This operation runs in the background.
    """
    try:
        # Validate park exists
        parks = db_manager.get_all_parks()
        if park_id not in parks:
            raise HTTPException(status_code=404, detail=f"Park {park_id} not found")
        
        # Add retraining to background tasks
        background_tasks.add_task(prediction_service.retrain_model, park_id)
        
        return {
            "message": f"Model retraining started for park {park_id}",
            "park_id": park_id,
            "status": "training_started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training for {park_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start model training")

@app.post("/models/train-all")
async def retrain_all_models(background_tasks: BackgroundTasks):
    """
    Retrain models for all parks.
    This operation runs in the background.
    """
    try:
        background_tasks.add_task(train_all_parks)
        
        parks_count = len(db_manager.get_all_parks())
        return {
            "message": f"Model retraining started for all {parks_count} parks",
            "status": "training_started",
            "parks_count": parks_count
        }
        
    except Exception as e:
        logger.error(f"Error starting bulk training: {e}")
        raise HTTPException(status_code=500, detail="Failed to start bulk model training")

@app.get("/models/{park_id}/performance")
async def get_model_performance(park_id: str):
    """Get performance metrics for a park's model."""
    try:
        performance = prediction_service.get_model_performance(park_id)
        
        if not performance['success']:
            raise HTTPException(status_code=404, detail=performance['error'])
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching performance for {park_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model performance")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ML Service...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 