import React, { createContext, useContext, useState, ReactNode } from 'react';

type Language = 'en' | 'kn';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.soilHealth': 'Soil Health',
    'nav.cropDoctor': 'Crop Doctor',
    'nav.yieldPlanning': 'Yield & Planning',
    'nav.marketProfit': 'Market & Profit',
    'nav.climate': 'Climate',
    'nav.cropRecommendation': 'Crop Recommendation',
    'nav.aiAssistant': 'AI Farming Assistant',
    'nav.logout': 'Logout',
    
    // Dashboard
    'dashboard.title': 'Farm Overview',
    'dashboard.welcome': 'Welcome back',
    'dashboard.farmHealth': 'Farm Health',
    'dashboard.soilHealth': 'Soil Health',
    'dashboard.expectedYield': 'Expected Yield',
    'dashboard.marketOutlook': 'Market Outlook',
    'dashboard.climateAlert': 'Climate Alert',
    'dashboard.checkSoil': 'Check Soil Health',
    'dashboard.checkMarket': 'Check Market Prices',
    'dashboard.askAI': 'Ask AI Assistant',
    'dashboard.good': 'Good',
    'dashboard.moderate': 'Moderate',
    'dashboard.poor': 'Poor',
    
    // Common
    'common.search': 'Search by Field, Crop, Metric',
    'common.selectFarm': 'Select Farm',
    'common.weather': 'Weather',
    'common.profile': 'Profile',
    'common.signOut': 'Sign Out',
    'common.farmer': 'Farmer',
    'common.villageHead': 'Village Head',
    
    // Login
    'login.title': 'Welcome to AgriVerse',
    'login.subtitle': 'Your AI-powered farming assistant',
    'login.asFarmer': 'Login as Farmer',
    'login.asVillageHead': 'Login as Village Head',
    'login.email': 'Email',
    'login.password': 'Password',
    'login.continue': 'Continue',
  },
  kn: {
    // Navigation
    'nav.dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
    'nav.soilHealth': 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ',
    'nav.cropDoctor': 'ಬೆಳೆ ವೈದ್ಯ',
    'nav.yieldPlanning': 'ಇಳುವರಿ ಮತ್ತು ಯೋಜನೆ',
    'nav.marketProfit': 'ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಲಾಭ',
    'nav.climate': 'ಹವಾಮಾನ',
    'nav.cropRecommendation': 'ಬೆಳೆ ಶಿಫಾರಸು',
    'nav.aiAssistant': 'AI ಕೃಷಿ ಸಹಾಯಕ',
    'nav.logout': 'ಲಾಗ್ ಔಟ್',
    
    // Dashboard
    'dashboard.title': 'ಕೃಷಿ ಅವಲೋಕನ',
    'dashboard.welcome': 'ಮರಳಿ ಸ್ವಾಗತ',
    'dashboard.farmHealth': 'ಕೃಷಿ ಆರೋಗ್ಯ',
    'dashboard.soilHealth': 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ',
    'dashboard.expectedYield': 'ನಿರೀಕ್ಷಿತ ಇಳುವರಿ',
    'dashboard.marketOutlook': 'ಮಾರುಕಟ್ಟೆ ಮುನ್ನೋಟ',
    'dashboard.climateAlert': 'ಹವಾಮಾನ ಎಚ್ಚರಿಕೆ',
    'dashboard.checkSoil': 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಪರಿಶೀಲಿಸಿ',
    'dashboard.checkMarket': 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ',
    'dashboard.askAI': 'AI ಸಹಾಯಕನನ್ನು ಕೇಳಿ',
    'dashboard.good': 'ಉತ್ತಮ',
    'dashboard.moderate': 'ಮಧ್ಯಮ',
    'dashboard.poor': 'ಕಳಪೆ',
    
    // Common
    'common.search': 'ಕ್ಷೇತ್ರ, ಬೆಳೆ, ಮೆಟ್ರಿಕ್ ಮೂಲಕ ಹುಡುಕಿ',
    'common.selectFarm': 'ಕೃಷಿ ಆಯ್ಕೆಮಾಡಿ',
    'common.weather': 'ಹವಾಮಾನ',
    'common.profile': 'ಪ್ರೊಫೈಲ್',
    'common.signOut': 'ಸೈನ್ ಔಟ್',
    'common.farmer': 'ರೈತ',
    'common.villageHead': 'ಗ್ರಾಮ ಮುಖ್ಯಸ್ಥ',
    
    // Login
    'login.title': 'AgriVerse ಗೆ ಸ್ವಾಗತ',
    'login.subtitle': 'ನಿಮ್ಮ AI-ಚಾಲಿತ ಕೃಷಿ ಸಹಾಯಕ',
    'login.asFarmer': 'ರೈತನಾಗಿ ಲಾಗಿನ್',
    'login.asVillageHead': 'ಗ್ರಾಮ ಮುಖ್ಯಸ್ಥನಾಗಿ ಲಾಗಿನ್',
    'login.email': 'ಇಮೇಲ್',
    'login.password': 'ಪಾಸ್‌ವರ್ಡ್',
    'login.continue': 'ಮುಂದುವರಿಸಿ',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
