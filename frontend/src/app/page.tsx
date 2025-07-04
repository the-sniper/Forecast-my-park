"use client";

import { useState, useEffect, useCallback } from "react";
import {
  CalendarIcon,
  TrendingUpIcon,
  AlertCircleIcon,
  RefreshCwIcon,
  MapIcon,
  BarChartIcon,
} from "lucide-react";
import ParkSelector from "@/components/ParkSelector";
import ForecastChart from "@/components/ForecastChart";
import dynamic from "next/dynamic";

const InteractiveMap = dynamic(() => import("@/components/InteractiveMap"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <RefreshCwIcon className="h-8 w-8 text-green-600 animate-spin mx-auto mb-4" />
        <p className="text-lg font-medium text-gray-900">Loading Map...</p>
      </div>
    </div>
  ),
});
import { Park, PredictionResponse, PredictionRequest } from "@/types/forecast";
import { getToday, formatDate, addDaysToDate } from "@/lib/utils";

type ViewMode = "map" | "chart";

export default function Dashboard() {
  // View state
  const [viewMode, setViewMode] = useState<ViewMode>("map");

  // State management
  const [parks, setParks] = useState<Park[]>([]);
  const [selectedPark, setSelectedPark] = useState<Park | null>(null);
  const [startDate, setStartDate] = useState<string>(getToday());
  const [daysAhead, setDaysAhead] = useState<number>(14);
  const [predictions, setPredictions] = useState<PredictionResponse | null>(
    null
  );
  const [mapPredictions, setMapPredictions] = useState<
    Record<string, PredictionResponse>
  >({});
  const [selectedMapDate, setSelectedMapDate] = useState<string>(
    addDaysToDate(getToday(), 1)
  );

  // Loading states
  const [parksLoading, setParksLoading] = useState(true);
  const [predictionsLoading, setPredictionsLoading] = useState(false);
  const [mapPredictionsLoading, setMapPredictionsLoading] = useState(false);

  // Error states
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);

  // Load parks on component mount
  useEffect(() => {
    loadParks();
  }, []);

  // Generate chart predictions when park or date parameters change
  useEffect(() => {
    if (selectedPark && startDate && daysAhead > 0 && viewMode === "chart") {
      generatePredictions();
    }
  }, [selectedPark, startDate, daysAhead, viewMode]);

  // Load map predictions when switching to map view
  useEffect(() => {
    if (viewMode === "map" && parks.length > 0) {
      loadMapPredictions();
    }
  }, [viewMode, parks, selectedMapDate]);

  const loadParks = useCallback(async () => {
    try {
      setParksLoading(true);
      setError(null);

      const response = await fetch("/api/parks");
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to load parks");
      }

      setParks(data.parks || []);
      setWarning(null);

      // Auto-select first park with a model for chart view
      const parkWithModel = (data.parks || []).find(
        (park: Park) => park.has_model
      );
      if (parkWithModel && !selectedPark) {
        setSelectedPark(parkWithModel);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load parks");
    } finally {
      setParksLoading(false);
    }
  }, [selectedPark]);

  const generatePredictions = useCallback(async () => {
    if (!selectedPark) return;

    try {
      setPredictionsLoading(true);
      setError(null);

      const request: PredictionRequest = {
        park_id: selectedPark.park_id,
        start_date: startDate,
        days_ahead: daysAhead,
      };

      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to generate predictions");
      }

      setPredictions(data);
      setWarning(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate predictions"
      );
      setPredictions(null);
    } finally {
      setPredictionsLoading(false);
    }
  }, [selectedPark, startDate, daysAhead]);

  const loadMapPredictions = useCallback(async () => {
    try {
      setMapPredictionsLoading(true);
      setError(null);

      // Load predictions for all parks with models
      const parksWithModels = parks.filter((park) => park.has_model);

      // Calculate days ahead from the base date (July 4th, 2025)
      const baseDate = "2025-07-04";
      const selectedDateTime = new Date(selectedMapDate);
      const baseDateTime = new Date(baseDate);
      const daysFromBase = Math.ceil(
        (selectedDateTime.getTime() - baseDateTime.getTime()) /
          (1000 * 60 * 60 * 24)
      );

      const predictionPromises = parksWithModels.map(async (park) => {
        try {
          // Always request from base date with enough days to include the selected date
          const request: PredictionRequest = {
            park_id: park.park_id,
            start_date: baseDate,
            days_ahead: Math.max(1, daysFromBase + 1), // Ensure we get the selected date
          };

          const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(request),
          });

          if (response.ok) {
            const data = await response.json();

            // Filter predictions to only include the selected date
            if (data.predictions) {
              data.predictions = data.predictions.filter(
                (pred: any) => pred.ds === selectedMapDate
              );
            }

            return { park_id: park.park_id, data };
          }
          return null;
        } catch (err) {
          return null;
        }
      });

      const results = await Promise.all(predictionPromises);
      const newMapPredictions: Record<string, PredictionResponse> = {};

      results.forEach((result) => {
        if (result) {
          newMapPredictions[result.park_id] = result.data;
        }
      });

      setMapPredictions(newMapPredictions);
    } catch (err) {
      setError("Failed to load some predictions for map view");
    } finally {
      setMapPredictionsLoading(false);
    }
  }, [parks, selectedMapDate]);

  const handleRefresh = () => {
    if (viewMode === "chart" && selectedPark) {
      generatePredictions();
    } else if (viewMode === "map") {
      loadMapPredictions();
    }
    loadParks();
  };

  const handleViewModeChange = (mode: ViewMode) => {
    setViewMode(mode);
    setError(null); // Clear any previous errors
  };

  const handleMapParkSelect = (park: Park) => {
    setSelectedPark(park);
    // Only switch to chart view when user clicks the button in the popup
    // The popup will handle showing the details first
  };

  const handleParkChartView = (park: Park) => {
    setSelectedPark(park);
    setViewMode("chart"); // Switch to chart view for detailed analysis
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <TrendingUpIcon className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Forecast My Park
                </h1>
                <p className="text-sm text-gray-500">
                  AI-powered visitor predictions for National Parks
                </p>
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => handleViewModeChange("map")}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    viewMode === "map"
                      ? "bg-white text-green-600 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  <MapIcon className="h-4 w-4 mr-2" />
                  Map View
                </button>
                <button
                  onClick={() => handleViewModeChange("chart")}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    viewMode === "chart"
                      ? "bg-white text-green-600 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  <BarChartIcon className="h-4 w-4 mr-2" />
                  Chart View
                </button>
              </div>

              <button
                onClick={handleRefresh}
                disabled={
                  parksLoading || predictionsLoading || mapPredictionsLoading
                }
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCwIcon
                  className={`h-4 w-4 mr-2 ${
                    parksLoading || predictionsLoading || mapPredictionsLoading
                      ? "animate-spin"
                      : ""
                  }`}
                />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error/Warning Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircleIcon className="h-5 w-5 text-red-400 mt-0.5" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {warning && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex">
              <AlertCircleIcon className="h-5 w-5 text-yellow-400 mt-0.5" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Note</h3>
                <p className="text-sm text-yellow-700 mt-1">{warning}</p>
              </div>
            </div>
          </div>
        )}

        {viewMode === "map" ? (
          // Map View Layout
          <div className="space-y-6">
            {/* Map Controls */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 flex items-center">
                  <MapIcon className="h-5 w-5 text-gray-400 mr-2" />
                  National Parks Visitor Predictions
                </h3>
                {/* {mapPredictionsLoading && (
                  <div className="flex items-center text-sm text-blue-600">
                    <RefreshCwIcon className="h-4 w-4 mr-2 animate-spin" />
                    Loading predictions for {formatDate(selectedMapDate)}...
                  </div>
                )} */}
              </div>

              <div className="mapDateSelection flex items-center space-x-4 mb-4">
                <div>
                  <label
                    htmlFor="map-date"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Select Date
                  </label>
                  <input
                    type="date"
                    id="map-date"
                    value={selectedMapDate}
                    onChange={(e) => setSelectedMapDate(e.target.value)}
                    min="2025-07-04"
                    max="2026-07-03"
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                  />
                </div>
                <div className="text-sm text-gray-600">
                  Showing predictions for{" "}
                  <span className="font-medium">
                    {formatDate(selectedMapDate)}
                  </span>
                </div>
              </div>
            </div>

            {/* Map Container */}
            <div
              className="bg-white rounded-lg shadow overflow-hidden relative"
              style={{ height: "600px" }}
            >
              {/* Loading Overlay */}
              {mapPredictionsLoading && (
                <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-[2000] loading-overlay">
                  <div className="bg-white rounded-xl shadow-2xl border border-gray-200 p-8 max-w-sm mx-4 overflow-hidden">
                    <div className="text-center">
                      <div className="relative mb-6">
                        <RefreshCwIcon className="w-12 h-12 text-green-600 animate-spin mx-auto" />
                        <div className="absolute -inset-2 bg-green-100 rounded-full animate-ping opacity-75"></div>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Updating Predictions
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">
                        Loading visitor forecasts for{" "}
                        <span className="font-medium text-green-600">
                          {formatDate(selectedMapDate)}
                        </span>
                      </p>
                      <div className="flex items-center justify-center space-x-2">
                        <div className="w-2 h-2 bg-green-600 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-green-600 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-green-600 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <InteractiveMap
                parks={parks}
                predictions={mapPredictions}
                selectedDate={selectedMapDate}
                onParkSelect={handleMapParkSelect}
                onParkChartView={handleParkChartView}
                selectedPark={selectedPark}
              />
            </div>
          </div>
        ) : (
          // Chart View Layout
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Controls Panel */}
            <div className="lg:col-span-1 space-y-6">
              {/* Park Selection */}
              <div className="bg-white rounded-lg shadow p-6">
                <ParkSelector
                  parks={parks}
                  selectedPark={selectedPark}
                  onParkChange={setSelectedPark}
                  loading={parksLoading}
                />
              </div>

              {/* Date Controls */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                  Forecast Settings
                </h3>

                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="start-date"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Start Date
                    </label>
                    <input
                      type="date"
                      id="start-date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      min={getToday()}
                      max={addDaysToDate(getToday(), 365)}
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="days-ahead"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      Forecast Days ({daysAhead})
                    </label>
                    <input
                      type="range"
                      id="days-ahead"
                      min="1"
                      max="90"
                      value={daysAhead}
                      onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>1 day</span>
                      <span>90 days</span>
                    </div>
                  </div>

                  {selectedPark && (
                    <div className="pt-4 border-t border-gray-200">
                      <p className="text-sm text-gray-600">
                        Forecasting{" "}
                        <span className="font-medium">{daysAhead} days</span>{" "}
                        starting from{" "} <br/>
                        <span className="font-medium">
                          {formatDate(startDate)}
                        </span>
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Model Performance */}
              {/* {predictions?.model_performance && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Model Performance
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">
                        Accuracy (MAPE)
                      </span>
                      <span className="text-sm font-medium">
                        {predictions.model_performance.mape.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">
                        Avg Error (MAE)
                      </span>
                      <span className="text-sm font-medium">
                        {predictions.model_performance.mae.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Confidence</span>
                      <span className="text-sm font-medium">
                        {predictions.confidence_level}%
                      </span>
                    </div>
                  </div>
                </div>
              )} */}
            </div>

            {/* Chart Panel */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow p-6">
                {predictionsLoading ? (
                  <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                      <RefreshCwIcon className="h-8 w-8 text-green-600 animate-spin mx-auto mb-4" />
                      <p className="text-lg font-medium text-gray-900">
                        Generating Predictions...
                      </p>
                      <p className="text-sm text-gray-600">
                        This may take a few moments
                      </p>
                    </div>
                  </div>
                ) : predictions && selectedPark ? (
                  <ForecastChart
                    predictions={predictions.predictions}
                    title={`${selectedPark.name} Visitor Forecast`}
                    showConfidenceInterval={true}
                    height={500}
                  />
                ) : selectedPark ? (
                  <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                      <TrendingUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-medium text-gray-900">
                        Ready to Generate Forecast
                      </p>
                      <p className="text-sm text-gray-600">
                        Adjust settings and predictions will appear here
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                      <TrendingUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-medium text-gray-900">
                        Select a Park
                      </p>
                      <p className="text-sm text-gray-600">
                        Choose a park from the dropdown to begin
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
