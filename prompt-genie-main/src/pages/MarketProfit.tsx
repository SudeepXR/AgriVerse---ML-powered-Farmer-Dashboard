import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Store, TrendingUp, TrendingDown, Newspaper, MapPin, Loader2, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const MarketProfit: React.FC = () => {
  const { t } = useLanguage();
  
  // States
  const [selectedCrop, setSelectedCrop] = useState('rice');
  const [selectedDistrict, setSelectedDistrict] = useState('mysore'); // Added to support /predict
  const [loading, setLoading] = useState(false);
  
  // Data States for the two different backend calls
  const [predictionData, setPredictionData] = useState<any>(null); // From /predict
  const [analysisData, setAnalysisData] = useState<any>(null);     // From /analyze

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Call your Prediction Backend (District + Commodity)
      const predRes = await fetch(`http://localhost:5000/predict?district=${selectedDistrict}&commodity=${selectedCrop}`);
      const predJson = await predRes.json();
      setPredictionData(predJson);

      // 2. Call your Analysis Backend (Sentiment + News)
      const analysisRes = await fetch(`http://localhost:5000/analyze/${selectedCrop}`);
      const analysisJson = await analysisRes.json();
      setAnalysisData(analysisJson);

    } catch (error) {
      console.error("Failed to fetch market data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCrop, selectedDistrict]);

  // Transform prediction short_term_forecast for the LineChart (Next 7 Days)
  const chartData = predictionData?.short_term_forecast 
    ? Object.entries(predictionData.short_term_forecast).map(([day, price]) => ({
        day: day,
        price: Math.round(price as number)
      }))
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.marketProfit')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Track market prices and get profit predictions (All prices in ₹ per quintal)
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <select 
            className="agri-input w-full" 
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
          >
            <option value="rice">Rice (Paddy)</option>
            <option value="wheat">Wheat</option>
            <option value="cotton">Cotton</option>
          </select>
        </div>
        <div className="flex-1">
          <select 
            className="agri-input w-full"
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
          >
            <option value="mysore">Mysore District</option>
            <option value="bangalore">Bangalore Rural</option>
            <option value="mandya">Mandya District</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          
          {/* Price Chart: Next 7 Days Prediction */}
          <div className="agri-card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-display font-semibold text-foreground flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                Price Trend (Next 7 Days Prediction)
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-success">
                  ₹{predictionData?.current_price?.toLocaleString() || '---'}
                </span>
                <span className="text-xs text-muted-foreground">/ quintal</span>
              </div>
            </div>

            <div className="h-64">
              {loading ? (
                <div className="h-full flex items-center justify-center"><Loader2 className="animate-spin text-primary" /></div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} domain={['auto', 'auto']} />
                    <Tooltip 
                      formatter={(val) => [`₹${val}`, 'Predicted Price']}
                      contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '12px' }} 
                    />
                    <Line type="monotone" dataKey="price" stroke="hsl(var(--success))" strokeWidth={3} dot={{ fill: 'hsl(var(--success))', strokeWidth: 2 }} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* 3-Month Price Prediction (Dynamic from Backend) */}
          <div className="agri-card">
            <h3 className="font-semibold text-foreground mb-4">3-Month Price Forecast (₹ per quintal)</h3>
            <div className="grid grid-cols-3 gap-4">
              {['Month +1', 'Month +2', 'Month +3'].map((m) => (
                <div key={m} className="p-4 bg-secondary rounded-xl text-center">
                  <p className="text-sm text-muted-foreground">{m}</p>
                  <p className="text-xl font-bold text-foreground">
                    ₹{predictionData?.medium_term_forecast?.[m] ? Math.round(predictionData.medium_term_forecast[m]).toLocaleString() : '---'}
                  </p>
                </div>
              ))}
            </div>
            
            {/* Dynamic Advisory Section */}
            <div className="mt-4 p-3 bg-success/10 rounded-xl border border-success/20">
              <p className="text-sm text-foreground flex flex-col gap-1">
                <strong>Advisory:</strong>
                {predictionData?.farmer_advisory?.map((adv: string, i: number) => (
                  <span key={i}>• {adv}</span>
                )) || "Analyzing market conditions..."}
              </p>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          
          {/* Market Sentiment (DYNAMIC from /analyze) */}
          <div className="agri-card relative">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Store className="w-5 h-5 text-primary" />
              Market Sentiment
            </h3>
            {loading ? (
              <div className="flex justify-center py-8"><Loader2 className="animate-spin text-primary" /></div>
            ) : (
              <div className="text-center mb-4">
                <div className={`w-20 h-20 rounded-full mx-auto flex items-center justify-center ${analysisData?.current_sentiment >= 0 ? 'bg-success/15' : 'bg-destructive/15'}`}>
                  <span className={`text-xl font-bold ${analysisData?.current_sentiment >= 0 ? 'text-success' : 'text-destructive'}`}>
                    {analysisData?.current_sentiment || '0.0'}
                  </span>
                </div>
                <p className={`mt-2 text-sm font-bold uppercase tracking-wider ${analysisData?.current_sentiment >= 0 ? 'text-success' : 'text-destructive'}`}>
                  {analysisData?.signal || 'Analyzing...'}
                </p>
              </div>
            )}
          </div>

          {/* Market News (DYNAMIC from /analyze) */}
          <div className="agri-card">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Newspaper className="w-5 h-5 text-primary" />
              Market News
            </h3>
            <div className="space-y-3">
              {loading ? (
                <p className="text-xs text-center text-muted-foreground">Fetching latest headlines...</p>
              ) : analysisData?.headlines?.length > 0 ? (
                analysisData.headlines.map((news: any, index: number) => (
                  <div key={index} className="p-3 bg-secondary rounded-xl">
                    <p className="text-sm text-foreground font-medium leading-tight">{news.text}</p>
                    <p className="text-[10px] text-primary uppercase font-bold mt-2">{news.source}</p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-center text-muted-foreground">No recent news found for this crop.</p>
              )}
            </div>
          </div>

          {/* Nearby Markets (Placeholder) */}
          <div className="agri-card">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-primary" />
              Nearby Markets
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-2 bg-secondary rounded-lg">
                <span className="text-sm text-foreground capitalize">{selectedDistrict} Mandi</span>
                <span className="text-sm font-medium text-success">₹{predictionData?.current_price || '---'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketProfit;