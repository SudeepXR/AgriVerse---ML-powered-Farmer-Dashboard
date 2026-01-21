import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { ChevronDown, User } from 'lucide-react';
import { useSelectedFarmer } from '@/contexts/FarmerSelectionContext';
import { useEffect, useState } from 'react';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const TopBar: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();
  const { user, role, logout } = useAuth();
  const { setSelectedFarmer } = useSelectedFarmer();
  const [farmers, setFarmers] = useState<any[]>([]);
  const { selectedFarmer } = useSelectedFarmer();

  useEffect(() => {
    if (role === 'head' && user?.id) {
      fetch(`http://localhost:5000/api/head/farmers/${user.id}`)
        .then(res => res.json())
        .then(data => setFarmers(data.farmers));
    }
  }, [role, user]);

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
      {/* Left Side */}
      <div className="flex items-center gap-4">
        {/* Farm Selector (ONLY for Head) */}
        {/* Farm Selector (ONLY for Head) */}
{/* Farm Selector (ONLY for Head) */}
{role === 'head' && (
  <DropdownMenu>
    <DropdownMenuTrigger className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-medium hover:bg-primary/90 transition-colors">
      {selectedFarmer
        ? selectedFarmer.full_name || 'Selected Farmer'
        : t('common.selectFarm')}
      <ChevronDown className="w-4 h-4" />
    </DropdownMenuTrigger>

    <DropdownMenuContent className="bg-card border-border">
      {farmers.length === 0 && (
        <DropdownMenuItem disabled>
          No farmers assigned
        </DropdownMenuItem>
      )}

      {farmers.map(farmer => (
        <DropdownMenuItem
          key={farmer.id}
          onClick={() => setSelectedFarmer(farmer)}
          className="cursor-pointer"
        >
          {farmer.full_name || farmer.username} – {farmer.village}
        </DropdownMenuItem>
      ))}
    </DropdownMenuContent>
  </DropdownMenu>
)}
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-4">
        {/* Language Toggle */}
        <div className="lang-toggle">
          <button
            onClick={() => setLanguage('en')}
            className={`lang-toggle-btn ${language === 'en' ? 'active' : ''}`}
          >
            English
          </button>
          <button
            onClick={() => setLanguage('kn')}
            className={`lang-toggle-btn ${language === 'kn' ? 'active' : ''}`}
          >
            ಕನ್ನಡ
          </button>
        </div>

        {/* User Profile */}
        <DropdownMenu>
          <DropdownMenuTrigger className="flex items-center gap-2 cursor-pointer">
            <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center">
              <User className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="text-left hidden md:block">
              <p className="text-sm font-medium text-foreground">
                {user?.username}
              </p>
              <p className="text-xs text-muted-foreground">
                {role === 'farmer'
                  ? t('common.farmer')
                  : t('common.villageHead')}
              </p>
            </div>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" className="w-56 bg-card border-border">
            <DropdownMenuLabel>
              <span className="font-medium">{user?.username}</span>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer">
              {t('common.profile')}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={logout}
              className="cursor-pointer text-destructive"
            >
              {t('common.signOut')}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default TopBar;
