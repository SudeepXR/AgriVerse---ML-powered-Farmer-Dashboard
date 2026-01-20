import React, { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import {
  Leaf,
  Beaker,
  FlaskConical,
  CheckCircle,
  AlertCircle,
  Loader2
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
}

/* =======================
   Component
======================= */

const SoilHealth: React.FC = () => {
  const { t } = useLanguage();
  const { user, role } = useAuth();

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

    // Safety check
    if (!user?.id || role !== 'farmer') {
      setError('You must be logged in as a farmer to analyze soil health.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/nutrient', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          farmer_id: user.id
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'low':
        return 'bg-destructive';
      case 'moderate':
        return 'bg-warning';
      default:
        return 'bg-success';
    }
  };

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
                <label className="block text-sm font-medium mb-1">
                  Nitrogen (N) kg/acre
                </label>
                <input
                  type="number"
                  name="nitrogen"
                  className="agri-input"
                  value={formData.nitrogen}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Phosphorus (P) kg/acre
                </label>
                <input
                  type="number"
                  name="phosphorus"
                  className="agri-input"
                  value={formData.phosphorus}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Potassium (K) kg/acre
                </label>
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
                <label className="block text-xs font-medium mb-1">
                  Temp (°C)
                </label>
                <input
                  type="number"
                  name="temperature"
                  className="agri-input"
                  value={formData.temperature}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">
                  Humidity (%)
                </label>
                <input
                  type="number"
                  name="humidity"
                  className="agri-input"
                  value={formData.humidity}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-xs font-medium mb-1">
                  Rainfall (mm)
                </label>
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

        {/* ================= Results ================= */}
        <div className="space-y-4">
          {!results && !loading && (
            <div className="agri-card flex flex-col items-center justify-center py-12 text-center text-muted-foreground border-dashed border-2">
              <FlaskConical className="w-12 h-12 mb-2 opacity-20" />
              <p>Enter soil data and click analyze to see recommendations.</p>
            </div>
          )}

          {results && (
            <div className="space-y-4 animate-fade-in">
              {/* Health Indicator */}
              <div className="agri-card bg-gradient-to-br from-primary/5 to-card border-l-4 border-primary">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                      <Leaf className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Overall Soil Health
                      </p>
                      <p className="text-xl font-display font-bold text-foreground">
                        {results.soil_health_score}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Confidence</p>
                    <p className="font-mono font-bold">
                      {results.confidence_percentage}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Nutrient Status */}
              <div className="agri-card">
                <h3 className="font-semibold mb-3">Nutrient Status</h3>
                <div className="space-y-3">
                  {Object.entries(results.soil_analysis).map(
                    ([key, data]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between p-2 rounded-lg bg-secondary/50"
                      >
                        <span className="capitalize text-sm font-medium">
                          {key}
                        </span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-muted-foreground">
                            {data.value} kg/acre
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] text-white font-bold uppercase ${getStatusColor(
                              data.status
                            )}`}
                          >
                            {data.status}
                          </span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Recommendations */}
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
                        <p className="font-bold text-primary">
                          {rec.fertilizer}
                        </p>
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
                  <p className="text-sm font-medium text-success">
                    Expected Yield Gain:{' '}
                    {results.expected_yield_improvement}
                  </p>
                </div>
              </div>

              {/* Sustainability */}
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
