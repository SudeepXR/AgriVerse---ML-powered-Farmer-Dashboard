import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useSelectedFarmer } from '@/contexts/FarmerSelectionContext';
import { useEffect, useState } from 'react';

import { 
  ArrowRight,
  Droplets,
  Thermometer,
  Wind,
  User,
  MapPin,
  Loader2
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const { user, role } = useAuth();
  const { selectedFarmer } = useSelectedFarmer();
  const navigate = useNavigate();
  
  const [weather, setWeather] = useState<any>(null);
  const [farmerDetails, setFarmerDetails] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const farmerId = role === 'farmer' ? user?.id : selectedFarmer?.id;

  useEffect(() => {
    if (!farmerId) {
      setWeather(null);
      setFarmerDetails(null);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch Weather
        const weatherRes = await fetch(`http://localhost:5000/api/weather?farmer_id=${farmerId}`);
        if (weatherRes.ok) {
          const weatherData = await weatherRes.json();
          setWeather(weatherData);
        }

        // Fetch Farmer Details
        const detailsRes = await fetch(`http://localhost:5000/api/farmer-details?farmer_id=${farmerId}`);
        if (detailsRes.ok) {
          const detailsData = await detailsRes.json();
          setFarmerDetails(detailsData);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [farmerId]);

  const actionCards = [
    {
      title: t('dashboard.checkSoil'),
      description: 'Analyze soil nutrients and get fertilizer recommendations',
      path: '/soil-health',
      color: 'bg-leaf/10 hover:bg-leaf/20',
    },
    {
      title: t('dashboard.checkMarket'),
      description: 'View current prices and market predictions',
      path: '/market-profit',
      color: 'bg-wheat/10 hover:bg-wheat/20',
    },
    {
      title: t('dashboard.askAI'),
      description: 'Get personalized farming advice from AI',
      path: '/ai-assistant',
      color: 'bg-primary/10 hover:bg-primary/20',
    },
  ];

  const weatherData = weather ? [
    { icon: Thermometer, label: 'Temp', value: `${Math.round(weather.current_weather.temperature)}${weather.current_weather.unit}` },
    { icon: Droplets, label: 'Humidity', value: `${weather.current_weather.humidity}%` },
    { icon: Wind, label: 'Wind', value: `${weather.current_weather.wind_speed} km/h` },
  ] : [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('dashboard.welcome')}, {user?.username}! 👋
        </h1>
        <p className="text-muted-foreground mt-1">
          {role === 'head' && selectedFarmer 
            ? `Viewing dashboard for ${selectedFarmer.full_name}` 
            : "Here's the latest data for your farm."}
        </p>
      </div>

      {/* Farmer Profile Card */}
      {loading ? (
        <div className="agri-card flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Fetching profile details...</span>
        </div>
      ) : farmerDetails && (
        <div className="agri-card border-l-4 border-primary bg-primary/5 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-white rounded-xl shadow-sm">
                <User className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-xs font-bold text-primary/60 uppercase tracking-widest">Farmer Name</p>
                <p className="text-lg font-bold text-foreground">{farmerDetails.full_name}</p>
                <p className="text-sm text-muted-foreground">@{farmerDetails.username}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 border-t md:border-t-0 md:border-l border-primary/10 pt-4 md:pt-0 md:pl-6">
              <div className="p-3 bg-white rounded-xl shadow-sm">
                <MapPin className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-xs font-bold text-primary/60 uppercase tracking-widest">Location</p>
                <p className="text-md font-medium text-foreground">
                  {farmerDetails.village}, {farmerDetails.district}
                </p>
                <p className="text-sm text-muted-foreground">{farmerDetails.state}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {role === 'head' && !selectedFarmer && (
        <div className="agri-card border-l-4 border-warning bg-warning/5">
          <p className="text-sm text-muted-foreground">Please select a farmer from the navigation bar to view specific data.</p>
        </div>
      )}

      {/* Weather Card */}
      <div className="agri-card-highlight shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-medium text-muted-foreground">Today's Weather</h3>
            <p className="text-2xl font-display font-bold text-foreground mt-1">
              {weather ? (weather.current_weather.temperature > 25 ? 'Warm Conditions' : 'Cool Conditions') : 'Updating...'}
            </p>
          </div>
          <div className="flex gap-8">
            {weatherData.length > 0 ? weatherData.map((item) => (
              <div key={item.label} className="text-center">
                <item.icon className="w-5 h-5 mx-auto text-primary mb-1" />
                <p className="text-lg font-semibold text-foreground">{item.value}</p>
                <p className="text-xs text-muted-foreground">{item.label}</p>
              </div>
            )) : (
                <p className="text-sm text-muted-foreground">Weather details loading...</p>
            )}
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
              className={`agri-card ${card.color} transition-all duration-300 text-left group border border-transparent hover:border-primary/20 hover:shadow-md`}
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