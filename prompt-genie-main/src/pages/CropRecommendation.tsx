import React, { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Sprout, TrendingUp, Shield, Star, Check,
  Loader2, AlertCircle, AlertTriangle, ChevronDown
} from 'lucide-react';

// Types
interface Recommendation {
  crop_name: string;
  rank: number;
  feasibility_score: number;
  confidence_level: 'High' | 'Medium' | 'Low';
  reasoning: string[];
  warnings: string[];
}

interface ResponseMetadata {
  data_coverage: 'high' | 'medium' | 'low';
  used_imputed_soil_data: boolean;
  disclaimer: string;
}

interface ApiResponse {
  status: string;
  model_version: string;
  meta: ResponseMetadata;
  recommendations: Recommendation[];
}

interface SoilData {
  nitrogen: string;
  phosphorus: string;
  potassium: string;
  ph: string;
}

// Constants
const SEASONS = ['Whole Year', 'Kharif', 'Rabi', 'Autumn', 'Summer'];

const CropRecommendation: React.FC = () => {
  const { t } = useLanguage();

  // Form state
  const [regionId, setRegionId] = useState('');
  const [season, setSeason] = useState('Whole Year');
  const [includeSoilData, setIncludeSoilData] = useState(false);
  const [soilData, setSoilData] = useState<SoilData>({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: ''
  });

  // API state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null);
  const [metadata, setMetadata] = useState<ResponseMetadata | null>(null);

  // Form validation
  const isRegionValid = regionId.trim().length >= 2;

  const isSoilDataValid = !includeSoilData || (
    soilData.nitrogen !== '' &&
    soilData.phosphorus !== '' &&
    soilData.potassium !== '' &&
    soilData.ph !== '' &&
    parseFloat(soilData.nitrogen) >= 0 && parseFloat(soilData.nitrogen) <= 300 &&
    parseFloat(soilData.phosphorus) >= 0 && parseFloat(soilData.phosphorus) <= 300 &&
    parseFloat(soilData.potassium) >= 0 && parseFloat(soilData.potassium) <= 300 &&
    parseFloat(soilData.ph) >= 0 && parseFloat(soilData.ph) <= 14
  );

  const isFormValid = isRegionValid && isSoilDataValid;

  // API submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload: Record<string, unknown> = {
      region_id: regionId.trim()
    };

    if (season !== 'Whole Year') {
      payload.season = season;
    }

    if (includeSoilData) {
      payload.soil_data = {
        nitrogen: parseFloat(soilData.nitrogen),
        phosphorus: parseFloat(soilData.phosphorus),
        potassium: parseFloat(soilData.potassium),
        ph: parseFloat(soilData.ph)
      };
    }

    try {
      const response = await fetch('http://localhost:5000/api/crop-recommendation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get recommendations');
      }

      if (data.status === 'success') {
        setRecommendations(data.recommendations);
        setMetadata(data.meta);
      } else {
        throw new Error(data.error || 'Unexpected response from server');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setRecommendations(null);
      setMetadata(null);
    } finally {
      setLoading(false);
    }
  };

  // Helper for confidence badge color
  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'High': return 'bg-success/15 text-success';
      case 'Medium': return 'bg-warning/15 text-warning';
      case 'Low': return 'bg-muted text-muted-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  // Helper for data coverage badge
  const getCoverageColor = (coverage: string) => {
    switch (coverage) {
      case 'high': return 'text-success';
      case 'medium': return 'text-warning';
      case 'low': return 'text-muted-foreground';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.cropRecommendation')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Get crop feasibility insights based on regional historical data and soil profiles
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="agri-card">
        <div className="space-y-4">
          {/* Region ID */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Region <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={regionId}
              onChange={(e) => setRegionId(e.target.value)}
              placeholder="e.g., Satara, Maharashtra"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              required
            />
            <p className="text-xs text-muted-foreground mt-1">
              Enter district and state (e.g., "Mysuru, Karnataka")
            </p>
          </div>

          {/* Season Dropdown */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Season
            </label>
            <div className="relative">
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground appearance-none focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                {SEASONS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            </div>
          </div>

          {/* Soil Data Toggle */}
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={includeSoilData}
                onChange={(e) => setIncludeSoilData(e.target.checked)}
                className="w-4 h-4 rounded border-border text-primary focus:ring-primary/50"
              />
              <span className="text-sm font-medium text-foreground">
                Include soil data (optional)
              </span>
            </label>
          </div>

          {/* Soil Data Fields */}
          {includeSoilData && (
            <div className="grid grid-cols-2 gap-4 p-4 bg-secondary/50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Nitrogen (kg/ha)
                </label>
                <input
                  type="number"
                  value={soilData.nitrogen}
                  onChange={(e) => setSoilData({ ...soilData, nitrogen: e.target.value })}
                  placeholder="0-300"
                  min="0"
                  max="300"
                  step="0.1"
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Phosphorus (kg/ha)
                </label>
                <input
                  type="number"
                  value={soilData.phosphorus}
                  onChange={(e) => setSoilData({ ...soilData, phosphorus: e.target.value })}
                  placeholder="0-300"
                  min="0"
                  max="300"
                  step="0.1"
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Potassium (kg/ha)
                </label>
                <input
                  type="number"
                  value={soilData.potassium}
                  onChange={(e) => setSoilData({ ...soilData, potassium: e.target.value })}
                  placeholder="0-300"
                  min="0"
                  max="300"
                  step="0.1"
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  pH Level
                </label>
                <input
                  type="number"
                  value={soilData.ph}
                  onChange={(e) => setSoilData({ ...soilData, ph: e.target.value })}
                  placeholder="0-14"
                  min="0"
                  max="14"
                  step="0.1"
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!isFormValid || loading}
            className="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing conditions...
              </>
            ) : (
              <>
                <Sprout className="w-5 h-5" />
                Get Recommendations
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error State */}
      {error && (
        <div className="agri-card border-destructive/50 bg-destructive/5">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-destructive">Error</h3>
              <p className="text-sm text-destructive/80 mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-destructive/60 hover:text-destructive"
            >
              &times;
            </button>
          </div>
        </div>
      )}

      {/* Empty State (no results yet) */}
      {!loading && !error && !recommendations && (
        <div className="agri-card bg-secondary/50 text-center py-8">
          <Sprout className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <h3 className="font-medium text-foreground mb-1">Ready to analyze</h3>
          <p className="text-sm text-muted-foreground">
            Enter your region and optionally add soil data to get crop feasibility insights
          </p>
        </div>
      )}

      {/* Results Display */}
      {recommendations && recommendations.length > 0 && metadata && (
        <>
          {/* Metadata Banner */}
          <div className="agri-card bg-secondary/50">
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Data coverage:</span>
                <span className={`font-medium capitalize ${getCoverageColor(metadata.data_coverage)}`}>
                  {metadata.data_coverage}
                </span>
              </div>
              {metadata.used_imputed_soil_data && (
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-warning" />
                  <span className="text-warning text-xs">Using regional soil averages</span>
                </div>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {metadata.disclaimer}
            </p>
          </div>

          {/* Top Recommendation */}
          <div className="agri-card border-2 border-success bg-gradient-to-br from-success/10 to-card">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 rounded-2xl bg-success/20 flex items-center justify-center flex-shrink-0">
                <Star className="w-8 h-8 text-success" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-3 py-1 bg-success text-success-foreground text-xs font-medium rounded-full">
                    Best Choice
                  </span>
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getConfidenceColor(recommendations[0].confidence_level)}`}>
                    {recommendations[0].confidence_level} Confidence
                  </span>
                </div>
                <h2 className="text-2xl font-display font-bold text-foreground">
                  {recommendations[0].crop_name}
                </h2>
                <div className="flex items-center gap-6 mt-3">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-success" />
                    <span className="text-foreground font-medium">
                      {Math.round(recommendations[0].feasibility_score * 100)}%
                    </span>
                    <span className="text-sm text-muted-foreground">feasibility</span>
                  </div>
                </div>
                {/* Feasibility Score Bar */}
                <div className="mt-3 w-full bg-secondary rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-success h-full rounded-full transition-all duration-500"
                    style={{ width: `${recommendations[0].feasibility_score * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="font-semibold text-foreground mb-3">Why this aligns with your conditions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {recommendations[0].reasoning.map((reason, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-foreground">{reason}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Warnings */}
            {recommendations[0].warnings && recommendations[0].warnings.length > 0 && (
              <div className="mt-4 p-3 bg-warning/10 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-warning">
                    {recommendations[0].warnings.map((warning, i) => (
                      <p key={i}>{warning}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Alternative Options */}
          {recommendations.length > 1 && (
            <div>
              <h2 className="text-lg font-display font-semibold text-foreground mb-4">
                Alternative Options
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.slice(1).map((rec) => (
                  <div key={rec.rank} className="agri-card">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center flex-shrink-0">
                        <Sprout className="w-6 h-6 text-leaf" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-display font-bold text-foreground">{rec.crop_name}</h3>
                        <div className="flex items-center gap-4 mt-2">
                          <span className="text-sm text-foreground font-medium">
                            {Math.round(rec.feasibility_score * 100)}% feasibility
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${getConfidenceColor(rec.confidence_level)}`}>
                            {rec.confidence_level}
                          </span>
                        </div>
                        {/* Mini progress bar */}
                        <div className="mt-2 w-full bg-secondary rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              rec.confidence_level === 'High' ? 'bg-success' :
                              rec.confidence_level === 'Medium' ? 'bg-warning' : 'bg-muted-foreground'
                            }`}
                            style={{ width: `${rec.feasibility_score * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-border">
                      <ul className="space-y-1">
                        {rec.reasoning.slice(0, 2).map((reason, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                            <Check className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
                            {reason}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Warnings for alternatives */}
                    {rec.warnings && rec.warnings.length > 0 && (
                      <div className="mt-3 flex items-start gap-1.5 text-xs text-warning">
                        <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                        <span>{rec.warnings[0]}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* No Results State */}
      {recommendations && recommendations.length === 0 && (
        <div className="agri-card bg-warning/5 border-warning/30 text-center py-8">
          <AlertTriangle className="w-12 h-12 text-warning mx-auto mb-3" />
          <h3 className="font-medium text-foreground mb-1">No suitable crops found</h3>
          <p className="text-sm text-muted-foreground">
            Based on the provided conditions, no crops from our database show strong alignment.
            Try adjusting your region or season selection.
          </p>
        </div>
      )}
    </div>
  );
};

export default CropRecommendation;
