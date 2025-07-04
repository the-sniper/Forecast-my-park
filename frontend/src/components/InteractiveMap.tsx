"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Park, PredictionResponse } from '@/types/forecast';
import { Sun, Cloud, CloudRain, CloudSnow, Eye, Users, MapPin, Calendar, TrendingUp } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in React Leaflet
delete (L.Icon.Default.prototype as L.Icon.Default & { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface InteractiveMapProps {
  parks: Park[];
  predictions: Record<string, PredictionResponse>;
  selectedDate: string;
  onParkSelect: (park: Park) => void;
  onParkChartView: (park: Park) => void;
  selectedPark?: Park | null;
}

// Enhanced visitor level configuration
const VISITOR_LEVELS = [
  { 
    name: 'Very High', 
    color: '#DC2626', 
    bgColor: '#FEE2E2', 
    textColor: '#991B1B', 
    range: '4,000+', 
    min: 4000,
    icon: '🔴',
    description: 'Extremely crowded - expect long waits'
  },
  { 
    name: 'High', 
    color: '#EA580C', 
    bgColor: '#FED7AA', 
    textColor: '#C2410C', 
    range: '2,500-4,000', 
    min: 2500,
    icon: '🟠',
    description: 'Very busy - plan for crowds'
  },
  { 
    name: 'Medium', 
    color: '#D97706', 
    bgColor: '#FEF3C7', 
    textColor: '#92400E', 
    range: '1,500-2,500', 
    min: 1500,
    icon: '🟡',
    description: 'Moderately busy - comfortable visit'
  },
  { 
    name: 'Low', 
    color: '#65A30D', 
    bgColor: '#DCFCE7', 
    textColor: '#365314', 
    range: '500-1,500', 
    min: 500,
    icon: '🟢',
    description: 'Light crowds - great for exploring'
  },
  { 
    name: 'Very Low', 
    color: '#16A34A', 
    bgColor: '#F0FDF4', 
    textColor: '#14532D', 
    range: '0-500', 
    min: 0,
    icon: '🔵',
    description: 'Very quiet - perfect for peaceful visit'
  },
];

// Enhanced weather icon component
const WeatherIcon: React.FC<{ condition: string; className?: string; temperature?: number }> = ({ 
  condition, 
  className = "w-4 h-4",
  temperature 
}) => {
  const iconMap = {
    'sunny': Sun,
    'clear': Sun,
    'cloudy': Cloud,
    'partly cloudy': Cloud,
    'overcast': Cloud,
    'rainy': CloudRain,
    'rain': CloudRain,
    'snow': CloudSnow,
    'snowy': CloudSnow,
  };
  
  const IconComponent = iconMap[condition?.toLowerCase() as keyof typeof iconMap] || Sun;
  
  // Color based on temperature and condition
  const getIconColor = () => {
    if (condition?.toLowerCase().includes('rain')) return 'text-blue-600';
    if (condition?.toLowerCase().includes('snow')) return 'text-cyan-400';
    if (condition?.toLowerCase().includes('cloud')) return 'text-gray-500';
    
    if (!temperature) return 'text-yellow-500';
    if (temperature >= 80) return 'text-red-500';
    if (temperature >= 65) return 'text-orange-500';
    if (temperature >= 50) return 'text-yellow-500';
    if (temperature >= 32) return 'text-blue-500';
    return 'text-cyan-400';
  };
  
  return <IconComponent className={`${className} ${getIconColor()}`} />;
};

// Custom marker component for parks
const ParkMarker: React.FC<{
  park: Park;
  prediction?: PredictionResponse;
  selectedDate: string;
  isSelected: boolean;
  onSelect: () => void;
  onChartView: () => void;
}> = ({ park, prediction, selectedDate, isSelected, onSelect, onChartView }) => {
  const visitorData = useMemo(() => {
    if (!prediction || !prediction.predictions) {
      return { level: VISITOR_LEVELS[4], visitors: 0, confidence: 0, markerColor: '#6B7280', iconSize: 25 };
    }

    const dayPrediction = prediction.predictions.find(p => p.ds === selectedDate);
    const visitors = dayPrediction?.yhat || 0;
    const confidence = dayPrediction?.confidence_level || prediction.confidence_level || 0;
    
    const level = VISITOR_LEVELS.find(l => visitors >= l.min) || VISITOR_LEVELS[4];
    
    // Enhanced marker sizing
    let size = 30;
    if (visitors > 4000) size = 40;
    else if (visitors > 2500) size = 36;
    else if (visitors > 1500) size = 32;
    else if (visitors > 500) size = 28;
    else size = 24;
    
    return { level, visitors, confidence, markerColor: level.color, iconSize: size };
  }, [prediction, selectedDate]);

  const customIcon = useMemo(() => {
    const svg = `
      <svg width="${visitorData.iconSize}" height="${visitorData.iconSize}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="${visitorData.markerColor}" stroke="white" stroke-width="3"/>
        <text x="12" y="16" text-anchor="middle" fill="white" font-size="8" font-weight="bold">
          ${Math.round(visitorData.visitors / 1000) || '?'}K
        </text>
        ${isSelected ? `<circle cx="12" cy="12" r="11" fill="none" stroke="#3B82F6" stroke-width="4" opacity="0.8"/>` : ''}
        <circle cx="12" cy="12" r="12" fill="none" stroke="rgba(0,0,0,0.1)" stroke-width="1"/>
      </svg>
    `;
    
    return L.divIcon({
      html: svg,
      className: 'enhanced-park-marker',
      iconSize: [visitorData.iconSize, visitorData.iconSize],
      iconAnchor: [visitorData.iconSize / 2, visitorData.iconSize / 2],
    });
  }, [visitorData, isSelected]);

  if (!park.latitude || !park.longitude) {
    return null;
  }

  const dayPrediction = prediction?.predictions?.find(p => p.ds === selectedDate);

  return (
    <Marker
      position={[park.latitude, park.longitude]}
      icon={customIcon}
      eventHandlers={{
        click: onSelect,
      }}
    >
      <Popup>
        <div className="min-w-[320px] p-3">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="font-bold text-xl text-gray-900 mb-2">{park.name}</h3>
              <div className="flex items-center text-sm text-gray-600 mb-3">
                <MapPin className="w-4 h-4 mr-2" />
                {park.state} • {park.park_type}
              </div>
              <div className="flex items-center text-sm mb-2">
                <Calendar className="w-4 h-4 mr-2 text-green-600" />
                <span className="font-medium text-green-900">{selectedDate}</span>
              </div>
            </div>
            {/* <span className="text-3xl ml-3">{visitorData.level.icon}</span> */}
          </div>

          {dayPrediction && (
            <div className="space-y-4">
              {/* Visitor Activity Level */}
              <div 
                className="rounded-xl p-4 border-l-4"
                style={{ 
                  backgroundColor: visitorData.level.bgColor,
                  borderLeftColor: visitorData.level.color
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <Users className="w-5 h-5 mr-2" style={{ color: visitorData.level.color }} />
                    <span className="font-bold text-lg" style={{ color: visitorData.level.textColor }}>
                      {visitorData.level.name} Activity
                    </span>
                  </div>
                </div>
                <div className="text-2xl font-bold mb-1" style={{ color: visitorData.level.textColor }}>
                  {Math.round(visitorData.visitors).toLocaleString()}
                </div>
                <div className="text-sm" style={{ color: visitorData.level.textColor }}>
                  Expected visitors • {visitorData.level.description}
                </div>
              </div>

              {/* Weather Forecast */}
              <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <WeatherIcon 
                      condition={dayPrediction.weather_condition || 'clear'} 
                      className="w-6 h-6 mr-2"
                      temperature={dayPrediction.temperature_high}
                    />
                    <span className="font-bold text-green-900">Weather Forecast</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <div className="text-blue-600 font-medium">Temperature</div>
                    <div className="font-bold text-blue-900 text-lg">
                      {dayPrediction.temperature_high || 70}°F
                    </div>
                  </div>
                  <div>
                    <div className="text-blue-600 font-medium">Conditions</div>
                    <div className="font-bold text-blue-900 capitalize">
                      {dayPrediction.weather_condition || 'Clear'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Confidence */}
              <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2 text-green-600" />
                    <span className="text-sm font-medium text-green-900">Prediction Confidence</span>
                  </div>
                  <span className="font-bold text-green-900 text-lg">
                    {visitorData.confidence}%
                  </span>
                </div>
              </div>

              <button
                onClick={onChartView}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white text-sm py-3 px-4 rounded-lg hover:from-green-700 hover:to-green-800 transition-all duration-200 font-semibold shadow-md"
              >
                View Detailed Forecast & Charts
              </button>
            </div>
          )}

          {!dayPrediction && prediction && (
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
              <div className="flex items-center mb-2">
                <Calendar className="w-5 h-5 mr-2 text-amber-600" />
                <span className="font-semibold text-amber-900">No Data for This Date</span>
              </div>
              <p className="text-sm text-amber-800 mb-3">
                No prediction available for {selectedDate}
              </p>
              <button
                onClick={onChartView}
                className="w-full bg-amber-600 text-white text-sm py-2 px-3 rounded-lg hover:bg-amber-700 transition-colors font-medium"
              >
                🏞️ View Park Information
              </button>
            </div>
          )}

          {!prediction && (
            <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
              <div className="flex items-center mb-2">
                <Eye className="w-5 h-5 mr-2 text-orange-600" />
                <span className="font-semibold text-orange-900">No Prediction Model</span>
              </div>
              <p className="text-sm text-orange-800 mb-3">
                Forecasting model not available for this park
              </p>
              <button
                onClick={onChartView}
                className="w-full bg-orange-600 text-white text-sm py-2 px-3 rounded-lg hover:bg-orange-700 transition-colors font-medium"
              >
                📍 View Park Details
              </button>
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
};

// Component to fit map bounds to markers
const FitBounds: React.FC<{ parks: Park[] }> = ({ parks }) => {
  const map = useMap();

  useEffect(() => {
    if (parks.length > 0) {
      const validParks = parks.filter(park => park.latitude && park.longitude);
      if (validParks.length > 0) {
        const bounds = L.latLngBounds(
          validParks.map(park => [park.latitude!, park.longitude!])
        );
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    }
  }, [parks, map]);

  return null;
};

const InteractiveMap: React.FC<InteractiveMapProps> = ({
  parks,
  predictions,
  selectedDate,
  onParkSelect,
  onParkChartView,
  selectedPark
}) => {
  const [mapKey, setMapKey] = useState(0);

  // Filter parks that have coordinates
  const parksWithCoordinates = useMemo(() => {
    return parks.filter(park => park.latitude && park.longitude);
  }, [parks]);

  // Force re-render when parks change significantly
  useEffect(() => {
    setMapKey(prev => prev + 1);
  }, [parks.length]);

  const mapCenter: [number, number] = useMemo(() => {
    if (selectedPark?.latitude && selectedPark?.longitude) {
      return [selectedPark.latitude, selectedPark.longitude];
    }
    return [39.8283, -98.5795]; // Geographic center of US
  }, [selectedPark]);

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-green-50 to-emerald-100 rounded-xl overflow-hidden shadow-inner">
      {parksWithCoordinates.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="relative">
              <MapPin className="w-16 h-16 text-green-400 mx-auto mb-4 animate-pulse" />
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">🗺️</span>
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Loading National Parks</h3>
            <p className="text-gray-600 mb-4">
              Fetching park location and prediction data...
            </p>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      ) : (
        <>
          <MapContainer
            key={mapKey}
            center={mapCenter}
            zoom={4}
            className="w-full h-full"
            zoomControl={true}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            <FitBounds parks={parksWithCoordinates} />
            
            {parksWithCoordinates.map(park => (
              <ParkMarker
                key={park.park_id}
                park={park}
                prediction={predictions[park.park_id]}
                selectedDate={selectedDate}
                isSelected={selectedPark?.park_id === park.park_id}
                onSelect={() => onParkSelect(park)}
                onChartView={() => onParkChartView(park)}
              />
            ))}
          </MapContainer>

          {/* Enhanced Legend */}
          <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl border border-gray-200 p-5 max-w-sm z-[1000]">
            <div className="flex items-center mb-4">
              <Users className="w-6 h-6 mr-3 text-green-600" />
              <h4 className="font-bold text-gray-900 text-lg">Visitor Activity Levels</h4>
            </div>
            <div className="space-y-3">
              {VISITOR_LEVELS.map((level) => (
                <div key={level.name} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div
                      className="w-8 h-6 rounded-full mr-3 border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold"
                      style={{ backgroundColor: level.color }}
                    >
                      {level.range.includes('+') ? '4K+' : level.range.split('-')[0].charAt(0) + 'K'}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 text-sm">{level.name}</div>
                      <div className="text-xs text-gray-600">{level.description}</div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 font-medium">{level.range}</div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-600 text-center">
              Click markers for detailed predictions
            </div>
          </div>

          {/* Enhanced Park Info Panel */}
          {/* <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl border border-gray-200 px-5 py-4 z-[1000]">
            <div className="flex items-center text-sm mb-2">
              <MapPin className="w-5 h-5 mr-3 text-blue-600" />
              <div>
                <div className="font-bold text-gray-900 text-lg">{parksWithCoordinates.length} National Parks</div>
                <div className="text-xs text-gray-600">Showing predictions for {selectedDate}</div>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t border-gray-200">
              <span>🗺️ Interactive Map</span>
              <span>🤖 AI Predictions</span>
            </div>
          </div> */}
        </>
      )}
    </div>
  );
};

export default InteractiveMap; 