import { NextResponse } from 'next/server';
import { HealthResponse } from '@/types/forecast';

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

export async function GET() {
  const startTime = Date.now();
  let mlServiceStatus = 'unknown';
  let mlModelsLoaded = 0;
  let dbConnected = false;

  try {
    const response = await fetch(`${ML_SERVICE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000) // 5 second timeout for health checks
    });

    if (response.ok) {
      const mlHealth: HealthResponse = await response.json();
      mlServiceStatus = mlHealth.status;
      mlModelsLoaded = mlHealth.models_loaded || 0;
      dbConnected = mlHealth.database_connected || false;
    } else {
      mlServiceStatus = 'error';
    }

  } catch (error) {
    mlServiceStatus = 'unavailable';
  }

  const responseTime = Date.now() - startTime;

  const healthData = {
    status: mlServiceStatus === 'healthy' ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    frontend: {
      status: 'healthy',
      version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'
    },
    ml_service: {
      status: mlServiceStatus,
      url: ML_SERVICE_URL,
      models_loaded: mlModelsLoaded,
      database_connected: dbConnected
    },
    response_time_ms: responseTime,
    environment: process.env.NODE_ENV || 'development'
  };

  // Return appropriate status code
  const statusCode = mlServiceStatus === 'healthy' ? 200 : 503;

  return NextResponse.json(healthData, { status: statusCode });
} 