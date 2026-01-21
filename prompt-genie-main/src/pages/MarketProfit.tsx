import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Store,
  TrendingUp,
  Newspaper,
  MapPin,
  Loader2
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

import { cropDistrictMap } from '@/data/cropDistrictMap';

/* =======================
  District Master List
======================= */

const ALL_DISTRICTS = [
  { value: 'bagalkot', label: 'Bagalkot District' },
  { value: 'ballari', label: 'Ballari District' },
  { value: 'belagavi', label: 'Belagavi District' },
  { value: 'bangalore_city', label: 'Bangalore Urban' },
  { value: 'bangalore_rural', label: 'Bangalore Rural' },
  { value: 'bidar', label: 'Bidar District' },
  { value: 'chamarajanagar', label: 'Chamarajanagar District' },
  { value: 'chikballapur', label: 'Chikballapur District' },
  { value: 'chikkamagaluru', label: 'Chikkamagaluru District' },
  { value: 'chitradurga', label: 'Chitradurga District' },
  { value: 'dakshina_kannada', label: 'Dakshina Kannada District' },
  { value: 'davanagere', label: 'Davanagere District' },
  { value: 'dharwad', label: 'Dharwad District' },
  { value: 'gadag', label: 'Gadag District' },
  { value: 'hassan', label: 'Hassan District' },
  { value: 'haveri', label: 'Haveri District' },
  { value: 'kalaburagi', label: 'Kalaburagi District' },
  { value: 'kodagu', label: 'Kodagu District' },
  { value: 'kolar', label: 'Kolar District' },
  { value: 'koppal', label: 'Koppal District' },
  { value: 'mandya', label: 'Mandya District' },
  { value: 'mysore', label: 'Mysore District' },
  { value: 'raichur', label: 'Raichur District' },
  { value: 'ramanagara', label: 'Ramanagara District' },
  { value: 'shivamogga', label: 'Shivamogga District' },
  { value: 'tumakuru', label: 'Tumakuru District' },
  { value: 'udupi', label: 'Udupi District' },
  { value: 'uttara_kannada', label: 'Uttara Kannada District' },
  { value: 'vijayanagara', label: 'Vijayanagara District' },
  { value: 'vijayapura', label: 'Vijayapura District' },
  { value: 'yadgiri', label: 'Yadgir District' }
];

const MarketProfit: React.FC = () => {
  const { t } = useLanguage();

  const [selectedCrop, setSelectedCrop] = useState('rice');
  const [selectedDistrict, setSelectedDistrict] = useState('mysore');
  const [loading, setLoading] = useState(false);

  const [predictionData, setPredictionData] = useState<any>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);

  /* =======================
     Filter districts by crop
  ======================= */

  const availableDistricts = ALL_DISTRICTS.filter(d =>
    cropDistrictMap[selectedCrop]?.includes(d.value)
  );

  /* =======================
     Auto-fix invalid district
  ======================= */

  useEffect(() => {
    if (!cropDistrictMap[selectedCrop]?.includes(selectedDistrict)) {
      setSelectedDistrict(cropDistrictMap[selectedCrop][0]);
    }
  }, [selectedCrop]);

  /* =======================
     Fetch Data
  ======================= */

  const fetchData = async () => {
    setLoading(true);
    try {
      const predRes = await fetch(
        `http://localhost:5000/predict?district=${selectedDistrict}&commodity=${selectedCrop}`
      );
      setPredictionData(await predRes.json());

      const analysisRes = await fetch(
        `http://localhost:5000/analyze/${selectedCrop}`
      );
      setAnalysisData(await analysisRes.json());
    } catch (error) {
      console.error('Failed to fetch market data', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCrop, selectedDistrict]);

  /* ======================================================
     🔥 SENTIMENT-ADJUSTED PRICE CALCULATION
  ====================================================== */

  const sentimentMultiplier =
    analysisData?.price_impact !== undefined
      ? 1 + analysisData.price_impact
      : 1;

  const chartData = predictionData?.short_term_forecast
    ? Object.entries(predictionData.short_term_forecast).map(
        ([day, price]) => ({
          day,
          price: Math.round((price as number) * sentimentMultiplier)
        })
      )
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">
        {t('nav.marketProfit')}
      </h1>

      {/* =======================
           🔽 FILTER DROPDOWNS
      ======================= */}
      <div className="flex gap-4">
        <div className="flex-1">
          <select
            className="agri-input w-full"
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
          >
            <option value="rice">Rice</option>
            <option value="paddy">Paddy (Dhan)</option>
            <option value="wheat">Wheat</option>
            <option value="arhar">Arhar (Tur)</option>
            <option value="bengal_gram">Bengal Gram</option>
            <option value="green_gram">Green Gram (Moong)</option>
            <option value="black_gram">Black Gram (Urad)</option>
            <option value="maize">Maize</option>
            <option value="jowar">Jowar</option>
            <option value="bajra">Bajra</option>
            <option value="groundnut">Groundnut</option>
            <option value="cotton">Cotton</option>
            <option value="onion">Onion</option>
            <option value="tomato">Tomato</option>
            <option value="sesamum">Sesamum (Til)</option>
          </select>
        </div>

        <div className="flex-1">
          <select
            className="agri-input w-full"
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
          >
            {availableDistricts.map(d => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* =======================
           PRICE TREND
      ======================= */}
      <div className="agri-card">
        <h2 className="font-semibold flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Price Trend (Next 7 Days)
        </h2>

        <div className="h-64">
          {loading ? (
            <Loader2 className="animate-spin" />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#16a34a"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* =======================
           MARKET SENTIMENT
      ======================= */}
      <div className="agri-card">
        <h3 className="font-semibold flex items-center gap-2">
          <Store className="w-5 h-5" />
          Market Sentiment
        </h3>

        <p className="font-bold">
          {analysisData?.signal ?? 'Analyzing'}
        </p>

        <p className="text-sm">
          Impact: {(analysisData?.price_impact * 100)?.toFixed(2)}%
        </p>
      </div>

      {/* =======================
           MARKET NEWS
      ======================= */}
      <div className="agri-card">
        <h3 className="font-semibold flex items-center gap-2">
          <Newspaper className="w-5 h-5" />
          Market News
        </h3>

        {analysisData?.headlines?.map((h: any, i: number) => (
          <div key={i}>
            <p>{h.text}</p>
            <span className="text-xs">{h.source}</span>
          </div>
        ))}
      </div>

      {/* =======================
           NEARBY MARKETS
      ======================= */}
      <div className="agri-card">
        <h3 className="font-semibold flex items-center gap-2">
          <MapPin className="w-5 h-5" />
          Nearby Markets
        </h3>

        <p>
          {selectedDistrict} mandi – ₹{predictionData?.current_price}
        </p>
      </div>
    </div>
  );
};

export default MarketProfit;
