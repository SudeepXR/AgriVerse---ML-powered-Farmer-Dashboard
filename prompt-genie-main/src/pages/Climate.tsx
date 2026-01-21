import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Cloud, Droplets, Thermometer, Wind, Sun, CloudRain, AlertTriangle, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useSelectedFarmer } from '@/contexts/FarmerSelectionContext';

// Helper to map Open-Meteo codes to your icons
const getWeatherIcon = (code: number) => {
  if (code <= 1) return Sun;
  if (code <= 3) return Cloud;
  return CloudRain;
};

const Climate: React.FC = () => {
  const { t } = useLanguage();
  const [weatherData, setWeatherData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user, role } = useAuth();
  const { selectedFarmer } = useSelectedFarmer();
  const farmerId =
  role === 'farmer'
    ? user?.id
    : selectedFarmer?.id;
    
  if (!farmerId && role === 'head') {
    return (
      <div className="flex items-center justify-center min-h-[300px] text-muted-foreground">
        Please select a farmer from the top bar to view climate data.
      </div>
    );
  }

  if (!farmerId) {
    setLoading(false);
    return;
  }

  useEffect(() => {
  const fetchWeather = async () => {
    if (!farmerId) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:5000/api/weather?farmer_id=${farmerId}`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch weather');
      }

      setWeatherData(data);
    } catch (error) {
      console.error("Failed to fetch weather:", error);
    } finally {
      setLoading(false);
    }
  };

  fetchWeather();
}, [farmerId]);


  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // Fallback to static risks if your API doesn't provide them yet
  const risks = [
    {
      type: 'Drought Risk',
      level: 'Low',
      color: 'success',
      explanation: 'Adequate rainfall expected in the coming weeks.',
      action: 'Maintain regular irrigation schedule.',
    },
    {
      type: 'Flood Risk',
      level: weatherData?.seven_day_forecast.some((d: any) => d.precipitation > 10) ? 'Moderate' : 'Low',
      color: weatherData?.seven_day_forecast.some((d: any) => d.precipitation > 10) ? 'warning' : 'success',
      explanation: 'Rainfall levels are being monitored daily.',
      action: 'Ensure proper drainage channels are clear.',
    },
    {
      type: 'Heat Stress',
      level: weatherData?.current_weather.temperature > 35 ? 'High' : 'Low',
      color: weatherData?.current_weather.temperature > 35 ? 'destructive' : 'success',
      explanation: 'Temperatures are within typical ranges for your crops.',
      action: 'No immediate action needed.',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.climate')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Weather forecasts and climate risk alerts for your farm
        </p>
      </div>

      {/* Current Weather */}
      <div className="agri-card bg-gradient-to-r from-sky/10 to-card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Current Weather</p>
            <p className="text-4xl font-display font-bold text-foreground mt-1">
              {Math.round(weatherData?.current_weather.temperature)}°C
            </p>
            <p className="text-lg text-foreground">Live Conditions</p>
          </div>
          <div className="flex gap-8">
            <div className="text-center">
              <Droplets className="w-6 h-6 mx-auto text-sky mb-1" />
              <p className="text-lg font-semibold text-foreground">{weatherData?.current_weather.humidity}%</p>
              <p className="text-xs text-muted-foreground">Humidity</p>
            </div>
            <div className="text-center">
              <Wind className="w-6 h-6 mx-auto text-muted-foreground mb-1" />
              <p className="text-lg font-semibold text-foreground">{weatherData?.current_weather.wind_speed} km/h</p>
              <p className="text-xs text-muted-foreground">Wind</p>
            </div>
            <div className="text-center">
              <CloudRain className="w-6 h-6 mx-auto text-sky mb-1" />
              <p className="text-lg font-semibold text-foreground">
                {weatherData?.seven_day_forecast[0]?.precipitation??0} mm
              </p>
              <p className="text-xs text-muted-foreground">Rainfall</p>
            </div>
          </div>
        </div>
      </div>

      {/* 7-Day Forecast */}
      <div className="agri-card">
        <h2 className="text-lg font-display font-semibold text-foreground mb-4 flex items-center gap-2">
          <Cloud className="w-5 h-5 text-primary" />
          7-Day Weather Forecast
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
          {weatherData?.seven_day_forecast.map((day: any, index: number) => {
            // Determine day name (Today, Tue, etc.)
            const date = new Date(day.date);
            const dayName = index === 0 ? 'Today' : date.toLocaleDateString('en-US', { weekday: 'short' });
            
            // Basic icon logic based on precipitation
            const Icon = day.precipitation > 0.5 ? CloudRain : Sun;
            const isRainy = day.precipitation > 0.5;

            return (
              <div
                key={index}
                className={`p-4 rounded-xl text-center transition-all ${
                  index === 0 
                    ? 'bg-primary text-primary-foreground' 
                    : isRainy 
                      ? 'bg-sky/10' 
                      : 'bg-secondary'
                }`}
              >
                <p className={`text-sm font-medium ${index === 0 ? '' : 'text-foreground'}`}>
                  {dayName}
                </p>
                <Icon className={`w-8 h-8 mx-auto my-3 ${
                  index === 0 ? '' : isRainy ? 'text-sky' : 'text-orange-400'
                }`} />
                <p className={`text-lg font-bold ${index === 0 ? '' : 'text-foreground'}`}>
                  {Math.round(day.temp_max)}°
                </p>
                <p className={`text-xs mt-1 ${index === 0 ? 'opacity-80' : 'text-muted-foreground'}`}>
                  {day.precipitation}mm
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Climate Risks */}
      <div>
        <h2 className="text-lg font-display font-semibold text-foreground mb-4">Climate Risk Assessment</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {risks.map((risk, index) => (
            <div
              key={index}
              className={`agri-card border-l-4 ${
                risk.color === 'success' 
                  ? 'border-green-500' 
                  : risk.color === 'warning' 
                    ? 'border-yellow-500' 
                    : 'border-red-500'
              }`}
            >
              <div className="flex items-start gap-3 mb-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  risk.color === 'success' ? 'bg-green-50' : risk.color === 'warning' ? 'bg-yellow-50' : 'bg-red-50'
                }`}>
                  <AlertTriangle className={`w-5 h-5 ${
                    risk.color === 'success' ? 'text-green-600' : risk.color === 'warning' ? 'text-yellow-600' : 'text-red-600'
                  }`} />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{risk.type}</h3>
                  <span className={`text-sm font-medium ${
                    risk.color === 'success' ? 'text-green-600' : risk.color === 'warning' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {risk.level}
                  </span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-3">{risk.explanation}</p>
              <div className="p-2 bg-secondary rounded-lg">
                <p className="text-xs text-foreground">
                  <strong>Action:</strong> {risk.action}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
    
  );
};

export default Climate;