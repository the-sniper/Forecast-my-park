import { NextRequest, NextResponse } from 'next/server';
import { PredictionRequest, PredictionResponse } from '@/types/forecast';

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

interface MLServicePrediction {
  date: string;
  predicted_visitors: number;
  lower_bound: number;
  upper_bound: number;
  confidence_interval: string;
}

interface MLServiceResponse {
  success: boolean;
  park_id: string;
  predictions: MLServicePrediction[] | null;
  error?: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: PredictionRequest = await request.json();
    
    // Validate request
    if (!body.park_id || !body.start_date || !body.days_ahead) {
      return NextResponse.json(
        { error: 'Missing required fields: park_id, start_date, days_ahead' },
        { status: 400 }
      );
    }

    if (body.days_ahead < 1 || body.days_ahead > 365) {
      return NextResponse.json(
        { error: 'days_ahead must be between 1 and 365' },
        { status: 400 }
      );
    }

    const response = await fetch(`${ML_SERVICE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30000) // 30 second timeout for ML operations
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('ML service prediction error:', response.status, errorText);
      
      if (response.status >= 500) {
        return NextResponse.json(
          { error: 'ML service is currently unavailable. Please try again later.' },
          { status: 503 }
        );
      } else {
        return NextResponse.json(
          { error: `ML service error: ${errorText}` },
          { status: response.status }
        );
      }
    }

    const mlResponse: MLServiceResponse = await response.json();
    
    // Handle ML service errors
    if (!mlResponse.success || !mlResponse.predictions) {
      console.error('ML service returned error:', mlResponse.error);
      return NextResponse.json(
        { error: mlResponse.error || 'Failed to generate predictions' },
        { status: 400 }
      );
    }

    // Transform ML service format to frontend format
    const predictions = mlResponse.predictions.map(pred => ({
      ds: pred.date,
      yhat: pred.predicted_visitors,
      yhat_lower: pred.lower_bound,
      yhat_upper: pred.upper_bound
    }));



    const response_data: PredictionResponse = {
      predictions,
      park_id: body.park_id,
      confidence_level: 80,
      model_performance: {
        mape: 0, // Will be updated when ML service provides this
        mae: 0,
        rmse: 0
      }
    };

    return NextResponse.json({
      ...response_data,
      timestamp: new Date().toISOString(),
      request_params: body
    });

  } catch (error) {
    console.error('Error generating predictions:', error);
    
    // Check if it's a network/connection error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        { error: 'Unable to connect to ML service. Please check if the service is running.' },
        { status: 503 }
      );
    }
    
    // Check if it's a timeout error
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'ML service request timed out. Please try again.' },
        { status: 504 }
      );
    }

    return NextResponse.json(
      { error: 'An unexpected error occurred while generating predictions.' },
      { status: 500 }
    );
  }
} 