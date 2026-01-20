import React, { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { TrendingUp, Calendar, Sliders, ArrowUp, ArrowDown } from 'lucide-react';

const YieldPlanning: React.FC = () => {
  const { t } = useLanguage();
  const [fertilizerAmount, setFertilizerAmount] = useState(100);
  const [sowingDelay, setSowingDelay] = useState(0);

  const baseYield = 45;
  const fertilizerEffect = (fertilizerAmount - 100) * 0.05;
  const delayEffect = sowingDelay * -0.8;
  const predictedYield = Math.max(0, baseYield + fertilizerEffect + delayEffect).toFixed(1);
  const lastSeasonYield = 42;
  const comparison = ((parseFloat(predictedYield) - lastSeasonYield) / lastSeasonYield * 100).toFixed(1);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.yieldPlanning')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Predict your crop yield and plan for optimal results
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-4">
          <div className="agri-card">
            <h2 className="text-lg font-display font-semibold text-foreground mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary" />
              Crop Selection
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Select Crop
                </label>
                <select className="agri-input">
                  <option value="rice">Rice (Paddy)</option>
                  <option value="wheat">Wheat</option>
                  <option value="maize">Maize</option>
                  <option value="cotton">Cotton</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Sowing Date
                </label>
                <input
                  type="date"
                  className="agri-input"
                  defaultValue="2024-06-15"
                />
              </div>
            </div>
          </div>

          {/* What-If Sliders */}
          <div className="agri-card">
            <h2 className="text-lg font-display font-semibold text-foreground mb-4 flex items-center gap-2">
              <Sliders className="w-5 h-5 text-primary" />
              What-If Analysis
            </h2>

            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-foreground">
                    Fertilizer Amount
                  </label>
                  <span className="text-sm font-medium text-primary">{fertilizerAmount}%</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="150"
                  value={fertilizerAmount}
                  onChange={(e) => setFertilizerAmount(parseInt(e.target.value))}
                  className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>50%</span>
                  <span>100% (Recommended)</span>
                  <span>150%</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-foreground">
                    Sowing Delay (Days)
                  </label>
                  <span className="text-sm font-medium text-primary">{sowingDelay} days</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="30"
                  value={sowingDelay}
                  onChange={(e) => setSowingDelay(parseInt(e.target.value))}
                  className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>On time</span>
                  <span>15 days</span>
                  <span>30 days late</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          {/* Main Prediction */}
          <div className="agri-card bg-gradient-to-br from-success/10 to-card">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Predicted Yield</p>
              <p className="text-5xl font-display font-bold text-success">
                {predictedYield}
              </p>
              <p className="text-lg text-foreground mt-1">quintals per acre</p>
              
              <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-success/15 rounded-full">
                <span className="text-sm font-medium text-success">
                  High Confidence
                </span>
              </div>
            </div>
          </div>

          {/* Comparison */}
          <div className="agri-card">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Season Comparison
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-secondary rounded-xl text-center">
                <p className="text-sm text-muted-foreground">Last Season</p>
                <p className="text-2xl font-bold text-foreground">{lastSeasonYield}</p>
                <p className="text-xs text-muted-foreground">quintals/acre</p>
              </div>
              <div className="p-4 bg-secondary rounded-xl text-center">
                <p className="text-sm text-muted-foreground">Change</p>
                <p className={`text-2xl font-bold flex items-center justify-center gap-1 ${
                  parseFloat(comparison) >= 0 ? 'text-success' : 'text-destructive'
                }`}>
                  {parseFloat(comparison) >= 0 ? (
                    <ArrowUp className="w-5 h-5" />
                  ) : (
                    <ArrowDown className="w-5 h-5" />
                  )}
                  {Math.abs(parseFloat(comparison))}%
                </p>
                <p className="text-xs text-muted-foreground">vs last season</p>
              </div>
            </div>
          </div>

          {/* Tips */}
          <div className="agri-card bg-primary/5">
            <h3 className="font-semibold text-foreground mb-2">💡 Optimization Tips</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>• Sow within the recommended window for best results</li>
              <li>• Apply fertilizer in split doses for better absorption</li>
              <li>• Monitor weather forecasts for irrigation planning</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YieldPlanning;
