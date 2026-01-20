import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Sprout, TrendingUp, Shield, Star, Check } from 'lucide-react';

const recommendations = [
  {
    crop: 'Rice (Paddy)',
    recommended: true,
    profitEstimate: '₹45,000/acre',
    riskLevel: 'Low',
    reasons: [
      'Optimal soil conditions for paddy cultivation',
      'Good water availability expected',
      'Strong market demand in coming months',
      'Government MSP support available',
    ],
  },
  {
    crop: 'Maize',
    recommended: false,
    profitEstimate: '₹38,000/acre',
    riskLevel: 'Medium',
    reasons: [
      'Suitable soil type',
      'Shorter growth period',
      'Moderate water requirement',
    ],
  },
  {
    crop: 'Groundnut',
    recommended: false,
    profitEstimate: '₹42,000/acre',
    riskLevel: 'Medium',
    reasons: [
      'Good export potential',
      'Nitrogen-fixing benefits soil',
      'Lower input costs',
    ],
  },
];

const CropRecommendation: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.cropRecommendation')}
        </h1>
        <p className="text-muted-foreground mt-1">
          AI-powered crop recommendations based on your soil, climate, and market conditions
        </p>
      </div>

      {/* Farm Context */}
      <div className="agri-card bg-secondary/50">
        <p className="text-sm text-muted-foreground">
          Based on: <span className="text-foreground font-medium">5 acres in Mysore District</span> • 
          <span className="text-foreground font-medium"> Loamy soil</span> • 
          <span className="text-foreground font-medium"> Kharif Season 2024</span>
        </p>
      </div>

      {/* Best Recommendation */}
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
            </div>
            <h2 className="text-2xl font-display font-bold text-foreground">
              {recommendations[0].crop}
            </h2>
            <div className="flex items-center gap-6 mt-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <span className="text-foreground font-medium">{recommendations[0].profitEstimate}</span>
                <span className="text-sm text-muted-foreground">expected profit</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-success" />
                <span className="text-foreground font-medium">{recommendations[0].riskLevel} Risk</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="font-semibold text-foreground mb-3">Why this recommendation?</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {recommendations[0].reasons.map((reason, index) => (
              <div key={index} className="flex items-start gap-2">
                <Check className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <span className="text-sm text-foreground">{reason}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alternative Options */}
      <div>
        <h2 className="text-lg font-display font-semibold text-foreground mb-4">Alternative Options</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.slice(1).map((rec, index) => (
            <div key={index} className="agri-card">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center flex-shrink-0">
                  <Sprout className="w-6 h-6 text-leaf" />
                </div>
                <div className="flex-1">
                  <h3 className="font-display font-bold text-foreground">{rec.crop}</h3>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-sm text-foreground font-medium">{rec.profitEstimate}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      rec.riskLevel === 'Low' 
                        ? 'bg-success/15 text-success' 
                        : rec.riskLevel === 'Medium'
                          ? 'bg-warning/15 text-warning'
                          : 'bg-destructive/15 text-destructive'
                    }`}>
                      {rec.riskLevel} Risk
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-border">
                <ul className="space-y-1">
                  {rec.reasons.slice(0, 2).map((reason, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <Check className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparison */}
      <div className="agri-card">
        <h3 className="font-semibold text-foreground mb-4">Profit & Risk Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 font-medium text-muted-foreground">Crop</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Profit Estimate</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Risk Level</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Water Requirement</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border bg-success/5">
                <td className="py-3 font-medium text-foreground">Rice (Paddy) ⭐</td>
                <td className="py-3 text-success font-medium">₹45,000</td>
                <td className="py-3"><span className="px-2 py-0.5 bg-success/15 text-success rounded">Low</span></td>
                <td className="py-3 text-foreground">High</td>
              </tr>
              <tr className="border-b border-border">
                <td className="py-3 font-medium text-foreground">Groundnut</td>
                <td className="py-3 text-foreground">₹42,000</td>
                <td className="py-3"><span className="px-2 py-0.5 bg-warning/15 text-warning rounded">Medium</span></td>
                <td className="py-3 text-foreground">Low</td>
              </tr>
              <tr>
                <td className="py-3 font-medium text-foreground">Maize</td>
                <td className="py-3 text-foreground">₹38,000</td>
                <td className="py-3"><span className="px-2 py-0.5 bg-warning/15 text-warning rounded">Medium</span></td>
                <td className="py-3 text-foreground">Medium</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CropRecommendation;
