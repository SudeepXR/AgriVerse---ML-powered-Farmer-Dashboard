import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useSelectedFarmer } from '@/contexts/FarmerSelectionContext';
import { useEffect, useState } from 'react';

import { 
  Heart, 
  Leaf, 
  TrendingUp, 
  Store, 
  AlertTriangle,
  ArrowRight,
  Droplets,
  Thermometer,
  Wind
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const { user, role } = useAuth();
  const { selectedFarmer } = useSelectedFarmer();
  const navigate = useNavigate();
  
  const [weather, setWeather] = useState<any>(null);
  const [weatherError, setWeatherError] = useState<string | null>(null);
  const farmerId =
    role === 'farmer'
      ? user?.id
      : selectedFarmer?.id;

  useEffect(() => {
    if (!farmerId) {
      setWeather(null);
      return;
    }

    const fetchWeather = async () => {
      try {
        const response = await fetch(
          `http://localhost:5000/api/weather?farmer_id=${farmerId}`
        );
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch weather');
        }

        setWeather(data);
        setWeatherError(null);
      } catch (err: any) {
        setWeather(null);
        setWeatherError(err.message);
      }
    };

    fetchWeather();
  }, [farmerId]);

  const statusCards = [
    {
      title: t('dashboard.farmHealth'),
      value: t('dashboard.good'),
      status: 'good' as const,
      icon: Heart,
      description: 'All systems operating normally',
    },
    {
      title: t('dashboard.soilHealth'),
      value: t('dashboard.moderate'),
      status: 'moderate' as const,
      icon: Leaf,
      description: 'Nitrogen levels need attention',
    },
    {
      title: t('dashboard.expectedYield'),
      value: '+12%',
      status: 'good' as const,
      icon: TrendingUp,
      description: 'Above average expected',
    },
    {
      title: t('dashboard.marketOutlook'),
      value: 'Positive',
      status: 'good' as const,
      icon: Store,
      description: 'Prices trending upward',
    },
  ];

  const actionCards = [
    {
      title: t('dashboard.checkSoil'),
      description: 'Analyze soil nutrients and get fertilizer recommendations',
      path: '/soil-health',
      color: 'bg-leaf/10 hover:bg-leaf/20',
      iconColor: 'text-leaf',
    },
    {
      title: t('dashboard.checkMarket'),
      description: 'View current prices and market predictions',
      path: '/market-profit',
      color: 'bg-wheat/10 hover:bg-wheat/20',
      iconColor: 'text-wheat',
    },
    {
      title: t('dashboard.askAI'),
      description: 'Get personalized farming advice from AI',
      path: '/ai-assistant',
      color: 'bg-primary/10 hover:bg-primary/20',
      iconColor: 'text-primary',
    },
  ];

  const weatherData = weather
  ? [
      {
        icon: Thermometer,
        label: 'Temperature',
        value: `${Math.round(weather.current_weather.temperature)}${weather.current_weather.unit}`,
      },
      {
        icon: Droplets,
        label: 'Humidity',
        value: `${weather.current_weather.humidity}%`,
      },
      {
        icon: Wind,
        label: 'Wind',
        value: `${weather.current_weather.wind_speed} km/h`,
      },
    ]
  : [];



  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">
              {t('dashboard.welcome')},{' '}
              {user && (
                'full_name' in user
                  ? user.full_name || user.username
                  : user.username
              )}! 👋
            </h1>

          <p className="text-muted-foreground mt-1">
            Here's what's happening on your farm today
          </p>
        </div>
      </div>

      {role === 'head' && !selectedFarmer && (
        <div className="agri-card border-l-4 border-warning bg-warning/5">
          <p className="text-sm text-muted-foreground">
            Please select a farmer from the top bar to view weather data.
          </p>
        </div>
      )}

      {/* Weather Summary Card */}
      <div className="agri-card-highlight">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-1">Today's Weather</h3>
            <p className="text-2xl font-display font-bold text-foreground">
              {weather
                ? weather.current_weather.humidity > 70
                  ? 'Humid Conditions'
                  : weather.current_weather.temperature > 30
                  ? 'Hot Weather'
                  : 'Pleasant Weather'
                : weatherError
                ? 'Weather unavailable'
                : 'Loading...'}

            </p>

            <p className="text-sm text-muted-foreground mt-1">Perfect for field work</p>
          </div>
          <div className="flex gap-6">
            {weatherData.map((item) => (
              <div key={item.label} className="text-center">
                <item.icon className="w-6 h-6 mx-auto text-primary mb-1" />
                <p className="text-lg font-semibold text-foreground">{item.value}</p>
                <p className="text-xs text-muted-foreground">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Status Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statusCards.map((card) => (
          <div key={card.title} className="agri-card">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                card.status === 'good' ? 'bg-success/15' : 
                card.status === 'moderate' ? 'bg-warning/15' : 'bg-destructive/15'
              }`}>
                <card.icon className={`w-5 h-5 ${
                  card.status === 'good' ? 'text-success' : 
                  card.status === 'moderate' ? 'text-warning' : 'text-destructive'
                }`} />
              </div>
            </div>
            <h3 className="text-sm font-medium text-muted-foreground">{card.title}</h3>
            <p className={`text-xl font-display font-bold mt-1 ${
              card.status === 'good' ? 'text-success' : 
              card.status === 'moderate' ? 'text-warning' : 'text-destructive'
            }`}>
              {card.value}
            </p>
            <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
          </div>
        ))}
      </div>

      {/* Climate Alert (conditional) */}
      <div className="agri-card border-l-4 border-warning bg-warning/5">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-warning/15 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-5 h-5 text-warning" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{t('dashboard.climateAlert')}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Light rain expected in 3 days. Consider completing harvesting activities before then.
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-display font-semibold text-foreground mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {actionCards.map((card) => (
            <button
              key={card.title}
              onClick={() => navigate(card.path)}
              className={`agri-card ${card.color} transition-all duration-300 text-left group`}
            >
              <h3 className="font-semibold text-foreground flex items-center justify-between">
                {card.title}
                <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
              </h3>
              <p className="text-sm text-muted-foreground mt-2">{card.description}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
