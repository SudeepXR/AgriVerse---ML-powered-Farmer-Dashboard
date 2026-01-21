import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { useSelectedFarmer } from '@/contexts/FarmerSelectionContext';

import {
  Leaf,
  Beaker,
  FlaskConical,
  CheckCircle,
  AlertCircle,
  Loader2,
  Calendar
} from 'lucide-react';

/* =======================
   API Response Interface
======================= */

interface AnalysisResult {
  success: boolean;
  soil_analysis: {
    [key: string]: { status: string; severity: string; value: number };
  };
  soil_health_score: string;
  recommendations: Array<{
    fertilizer: string;
    dosage: string;
    timing: string;
    benefit: string;
    if_ignored: string | null;
  }>;
  expected_yield_improvement: string;
  confidence_percentage: number;
  sustainability_note: string;
  created_at?: string;
}

/* =======================
   Component
======================= */

const SoilHealth: React.FC = () => {
  const { t } = useLanguage();
  const { user, role } = useAuth();
  const { selectedFarmer } = useSelectedFarmer();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResult | null>(null);

  /* =======================
     Form State
  ======================= */

  const [formData, setFormData] = useState({
    nitrogen: 180,
    phosphorus: 25,
    potassium: 220,
    ph: 6.8,
    temperature: 25.0,
    humidity: 60.0,
    rainfall: 100.0
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  };

  /* =======================
     Submit Handler
  ======================= */

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!user?.id) {
      setError('You must be logged in as a farmer to analyze soil health.');
      setLoading(false);
      return;
    }
    
    const farmerId = role === 'farmer' ? user.id : selectedFarmer?.id;

    if (!farmerId) {
      setError('Please select a farmer first.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/nutrient', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          farmer_id: farmerId
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze soil');
      }

      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /* =======================
     Helpers
  ======================= */

  const formatDateTime = (dateString: string | undefined) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  /* =======================
     Initial Load / Fetch Latest
  ======================= */

  const activeFarmerId = role === 'farmer' ? user?.id : selectedFarmer?.id;

  useEffect(() => {
    const fetchLatestReport = async () => {
      if (!activeFarmerId) return;

      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5000/soil-report/latest/${activeFarmerId}`);
        const data = await response.json();

        if (response.ok && data.success) {
          setResults(data);
          setFormData(prev => ({
            ...prev,
            nitrogen: data.soil_analysis.nitrogen.value,
            phosphorus: data.soil_analysis.phosphorus.value,
            potassium: data.soil_analysis.potassium.value,
            // Fallback to current state if backend doesn't provide env vars
            ph: data.ph || prev.ph, 
            temperature: data.temperature || prev.temperature,
            humidity: data.humidity || prev.humidity,
            rainfall: data.rainfall || prev.rainfall
          }));
        }
      } catch (err) {
        console.error("Error fetching latest report:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestReport();
  }, [activeFarmerId]);

  /* =======================
     Render
  ======================= */

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.soilHealth')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Analyze soil nutrients and get AI-powered fertilizer recommendations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ================= Input Form ================= */}
        <div className="agri-card h-fit">
          <h2 className="text-lg font-display font-semibold text-foreground mb-4 flex items-center gap-2">
            <Beaker className="w-5 h-5 text-primary" />
            Soil & Environment Parameters
          </h2>

          <form onSubmit={handleAnalyze} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nitrogen (N) kg/acre</label>
                <input
                  type="number"
                  name="nitrogen"
                  className="agri-input"
                  value={formData.nitrogen}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Phosphorus (P) kg/acre</label>
                <input
                  type="number"
                  name="phosphorus"
                  className="agri-input"
                  value={formData.phosphorus}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Potassium (K) kg/acre</label>
                <input
                  type="number"
                  name="potassium"
                  className="agri-input"
                  value={formData.potassium}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Soil pH</label>
                <input
                  type="number"
                  step="0.1"
                  name="ph"
                  className="agri-input"
                  value={formData.ph}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium mb-1">Temp (°C)</label>
                <input
                  type="number"
                  name="temperature"
                  className="agri-input"
                  value={formData.temperature}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">Humidity (%)</label>
                <input
                  type="number"
                  name="humidity"
                  className="agri-input"
                  value={formData.humidity}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">Rainfall (mm)</label>
                <input
                  type="number"
                  name="rainfall"
                  className="agri-input"
                  value={formData.rainfall}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="agri-btn-primary w-full flex justify-center items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Soil Health'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-destructive/10 text-destructive text-sm rounded-lg flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </div>

        {/* ================= Results Column ================= */}
        <div className="space-y-4">
          
          {/* Header Banner for Previous Reports */}
          {results?.created_at && (
            <div className="bg-primary/10 border-2 border-primary/20 p-4 rounded-xl flex flex-col gap-1 items-center text-center shadow-sm animate-in fade-in slide-in-from-top-4">
              <div className="flex items-center gap-2 text-primary">
                <Calendar className="w-5 h-5" />
                <span className="text-sm font-bold uppercase tracking-wider">
                  Previous Soil Health Report
                </span>
              </div>
              <p className="text-xs text-muted-foreground font-medium">
                Generated on: {formatDateTime(results.created_at)}
              </p>
            </div>
          )}

          {!results && !loading && (
            <div className="agri-card flex flex-col items-center justify-center py-12 text-center text-muted-foreground border-dashed border-2">
              <FlaskConical className="w-12 h-12 mb-2 opacity-20" />
              <p>Enter soil data and click analyze to see recommendations.</p>
            </div>
          )}

          {results && (
            <div className="space-y-4 animate-fade-in">
              {/* Health Score Section */}
              <div className="agri-card bg-gradient-to-br from-primary/5 to-card border-l-4 border-primary">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                      <Leaf className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Overall Soil Health</p>
                      <p className="text-2xl font-display font-bold text-foreground">
                        {results.soil_health_score}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Confidence</p>
                    <p className="font-mono font-bold text-lg">
                      {results.confidence_percentage}%
                    </p>
                  </div>
                </div>
              </div>

              {/* N, P, K Values Grid */}
              <div className="agri-card">
                <h3 className="font-semibold mb-3 text-sm flex items-center gap-2">
                  <Beaker className="w-4 h-4 text-primary" />
                  Nutrient Levels (N, P, K)
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(results.soil_analysis).map(([key, data]) => (
                    <div key={key} className="p-3 rounded-xl bg-secondary/50 border border-border text-center">
                      <p className="capitalize text-[10px] text-muted-foreground font-black uppercase tracking-widest">{key}</p>
                      <p className="text-xl font-display font-bold text-foreground mt-1">{data.value}</p>
                      <p className={`text-[10px] font-bold uppercase mt-1 px-2 py-0.5 rounded inline-block text-white ${
                        data.status.toLowerCase() === 'low' ? 'bg-destructive' : 
                        data.status.toLowerCase() === 'high' ? 'bg-warning' :
                        'bg-success'
                      }`}>
                        {data.status}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations Section */}
              <div className="agri-card">
                <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2 text-success">
                  <CheckCircle className="w-5 h-5" />
                  Recommended Action
                </h3>
                <div className="space-y-3">
                  {results.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-secondary rounded-xl border border-border"
                    >
                      <div className="flex justify-between items-start mb-1">
                        <p className="font-bold text-primary">{rec.fertilizer}</p>
                        <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                          {rec.dosage}
                        </span>
                      </div>
                      <p className="text-xs text-foreground mb-1">
                        <strong>Timing:</strong> {rec.timing}
                      </p>
                      <p className="text-xs text-muted-foreground italic">
                        "{rec.benefit}"
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-4 p-3 bg-success/10 rounded-lg">
                  <p className="text-sm font-medium text-success text-center">
                    Expected Yield Gain: {results.expected_yield_improvement}
                  </p>
                </div>
              </div>

              {/* Sustainability Footer */}
              <div className="p-3 text-xs text-muted-foreground bg-secondary/30 rounded-lg flex gap-2">
                <span>💡</span>
                {results.sustainability_note}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SoilHealth;