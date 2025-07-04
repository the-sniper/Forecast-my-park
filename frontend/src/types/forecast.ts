export interface Park {
  park_id: string;
  name: string;
  state: string;
  region: string;
  park_type: string;
  has_model: boolean;
  data_available?: boolean;
  last_training?: string;
  latitude?: number;
  longitude?: number;
  visitor_stats?: {
    min_visitors: number;
    max_visitors: number;
    avg_visitors: number;
  };
  metadata?: {
    avg_temperature_high?: number;
    avg_precipitation?: number;
    most_common_weather?: string;
    weekend_ratio?: string;
    holiday_ratio?: string;
    school_session_ratio?: string;
    avg_seasonal_factor?: number;
    most_common_visitor_category?: string;
    total_data_points?: number;
    earliest_date?: string;
    latest_date?: string;
  };
}

export interface PredictionRequest {
  park_id: string;
  start_date: string;
  days_ahead: number;
}

export interface PredictionPoint {
  ds: string; // date string
  yhat: number; // predicted value
  yhat_lower: number; // lower confidence bound
  yhat_upper: number; // upper confidence bound
  temperature_high?: number; // temperature forecast
  weather_condition?: string; // weather condition
  confidence_level?: number; // prediction confidence
}

export interface PredictionResponse {
  predictions: PredictionPoint[];
  park_id: string;
  confidence_level: number;
  model_performance?: {
    mape: number;
    mae: number;
    rmse: number;
  };
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  ml_service_status: string;
  models_loaded: number;
  database_connected: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
} 