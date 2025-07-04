import { NextResponse } from 'next/server';
import { Park } from '@/types/forecast';
import { PARK_COORDINATES } from '@/lib/parkCoordinates';

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${ML_SERVICE_URL}/parks`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout
      signal: AbortSignal.timeout(10000)
    });

    if (!response.ok) {
      console.error('ML service error:', response.status, response.statusText);
      
      if (response.status >= 500) {
        return NextResponse.json(
          { error: 'ML service is currently unavailable. Please try again later.' },
          { status: 503 }
        );
      } else {
        const errorText = await response.text();
        return NextResponse.json(
          { error: `ML service error: ${errorText}` },
          { status: response.status }
        );
      }
    }

    const parks: Park[] = await response.json();

    // Add coordinates to parks
    const parksWithCoordinates = parks.map(park => {
      const coordinates = PARK_COORDINATES[park.park_id];
      return {
        ...park,
        latitude: coordinates?.lat,
        longitude: coordinates?.lng
      };
    });

    const parksWithCoords = parksWithCoordinates.filter(park => park.latitude && park.longitude);

    return NextResponse.json({
      parks: parksWithCoordinates,
      total: parksWithCoordinates.length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching parks:', error);
    
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
      { error: 'An unexpected error occurred while fetching parks.' },
      { status: 500 }
    );
  }
} 