import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { 
  LayoutDashboard, 
  Leaf, 
  Stethoscope, 
  TrendingUp, 
  Store, 
  Cloud, 
  Sprout, 
  MessageSquare,
  LogOut,
  Wheat
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, labelKey: 'nav.dashboard' },
  { path: '/soil-health', icon: Leaf, labelKey: 'nav.soilHealth' },
  { path: '/crop-doctor', icon: Stethoscope, labelKey: 'nav.cropDoctor' },
  { path: '/yield-planning', icon: TrendingUp, labelKey: 'nav.yieldPlanning' },
  { path: '/market-profit', icon: Store, labelKey: 'nav.marketProfit' },
  { path: '/climate', icon: Cloud, labelKey: 'nav.climate' },
  { path: '/crop-recommendation', icon: Sprout, labelKey: 'nav.cropRecommendation' },
  { path: '/ai-assistant', icon: MessageSquare, labelKey: 'nav.aiAssistant' },
];

const Sidebar: React.FC = () => {
  const { t } = useLanguage();
  const { logout } = useAuth();
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-sidebar flex flex-col">
      {/* Logo */}
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-sidebar-primary flex items-center justify-center">
            <Wheat className="w-6 h-6 text-sidebar-primary-foreground" />
          </div>
          <span className="text-xl font-display font-bold text-sidebar-foreground">
            AgriVerse
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-2 overflow-y-auto">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{t(item.labelKey)}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-sidebar-border">
        <button 
          onClick={logout}
          className="sidebar-nav-item w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">{t('nav.logout')}</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
