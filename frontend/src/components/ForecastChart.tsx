'use client';

import { useMemo } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart
} from 'recharts';
import { PredictionPoint } from '@/types/forecast';
import { formatShortDate, formatNumber } from '@/lib/utils';

interface ForecastChartProps {
  predictions: PredictionPoint[];
  title?: string;
  showConfidenceInterval?: boolean;
  height?: number;
}

interface ChartDataPoint {
  date: string;
  dateFormatted: string;
  predicted: number;
  lowerBound: number;
  upperBound: number;
  confidenceRange: [number, number];
}

export default function ForecastChart({
  predictions,
  title = 'Visitor Forecast',
  showConfidenceInterval = true,
  height = 400
}: ForecastChartProps) {
  const chartData: ChartDataPoint[] = useMemo(() => {
    return predictions.map((pred) => ({
      date: pred.ds,
      dateFormatted: formatShortDate(pred.ds),
      predicted: pred.yhat,
      lowerBound: pred.yhat_lower,
      upperBound: pred.yhat_upper,
      confidenceRange: [pred.yhat_lower, pred.yhat_upper] as [number, number]
    }));
  }, [predictions]);

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: ChartDataPoint; value: number; dataKey: string; color: string }>; label?: string }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{formatShortDate(data.date)}</p>
          <p className="text-green-600">
            <span className="font-medium">Predicted:</span> {formatNumber(data.predicted)} visitors
          </p>
          {showConfidenceInterval && (
            <p className="text-gray-600 text-sm">
              Range: {formatNumber(data.lowerBound)} - {formatNumber(data.upperBound)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (!predictions || predictions.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-center">
          {/* <div className="text-gray-400 text-lg mb-2"></div> */}
          <p className="text-gray-600">No prediction data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">
          {predictions.length} day forecast • {showConfidenceInterval ? 'With' : 'Without'} confidence intervals
        </p>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          
          <XAxis
            dataKey="dateFormatted"
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: '#e0e0e0' }}
            axisLine={{ stroke: '#e0e0e0' }}
          />
          
          <YAxis
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: '#e0e0e0' }}
            axisLine={{ stroke: '#e0e0e0' }}
            tickFormatter={(value) => formatNumber(value)}
          />

          {showConfidenceInterval && (
            <Area
              type="monotone"
              dataKey="confidenceRange"
              fill="#16a34a"
              fillOpacity={0.1}
              stroke="none"
            />
          )}

          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#16a34a"
            strokeWidth={3}
            dot={{ fill: '#16a34a', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#16a34a', strokeWidth: 2, fill: '#ffffff' }}
          />

          {showConfidenceInterval && (
            <>
              <Line
                type="monotone"
                dataKey="lowerBound"
                stroke="#86efac"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="upperBound"
                stroke="#86efac"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
              />
            </>
          )}

          <Tooltip content={<CustomTooltip />} />
          
          {/* <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
            formatter={(value) => {
              if (value === 'predicted') return 'Predicted Visitors';
              if (value === 'lowerBound') return 'Lower Bound (80%)';
              if (value === 'upperBound') return 'Upper Bound (80%)';
              return value;
            }}
          /> */}
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-sm text-green-600 font-medium">Peak Day</p>
          <p className="text-lg font-bold text-green-900">
            {formatNumber(Math.max(...predictions.map(p => p.yhat)))}
          </p>
        </div>
        <div className="bg-teal-50 p-3 rounded-lg">
          <p className="text-sm text-teal-600 font-medium">Average</p>
          <p className="text-lg font-bold text-teal-900">
            {formatNumber(predictions.reduce((sum, p) => sum + p.yhat, 0) / predictions.length)}
          </p>
        </div>
        <div className="bg-orange-50 p-3 rounded-lg">
          <p className="text-sm text-orange-600 font-medium">Low Day</p>
          <p className="text-lg font-bold text-orange-900">
            {formatNumber(Math.min(...predictions.map(p => p.yhat)))}
          </p>
        </div>
      </div>
    </div>
  );
} 