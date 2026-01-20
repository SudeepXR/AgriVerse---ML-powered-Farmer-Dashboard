import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Wheat, User, Users, ArrowRight, Loader2 } from 'lucide-react';

type LoginStep = 'role' | 'credentials';
type Role = 'farmer' | 'village_head';

const Login: React.FC = () => {
  const { user } = useAuth();
  const [step, setStep] = useState<LoginStep>('role');
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { t, language, setLanguage } = useLanguage();
  const { login } = useAuth();
  const navigate = useNavigate();
  const displayName =
  user && 'full_name' in user
    ? user.full_name || user.username
    : user?.username;


  const handleRoleSelect = (role: Role) => {
    setSelectedRole(role);
    setStep('credentials');
    setError('');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole) return;

    setLoading(true);
    setError('');

    const endpoint =
      selectedRole === 'farmer'
        ? 'http://localhost:5000/api/auth/farmer/login'
        : 'http://localhost:5000/api/auth/head/login';

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: email,
          password
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Login failed');
      }

      // Fixed: Handle farmer response correctly
      if (selectedRole === 'farmer') {
        login('farmer', data.farmer);
      } else {
        login('head', data.head);
      }


      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-muted flex items-center justify-center p-4">
      {/* Language Toggle */}
      <div className="absolute top-6 right-6">
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
      </div>

      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="w-20 h-20 rounded-2xl bg-primary mx-auto mb-4 flex items-center justify-center shadow-glow">
            <Wheat className="w-12 h-12 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">
            {t('login.title')}
          </h1>
          <p className="text-muted-foreground mt-2">{t('login.subtitle')}</p>
        </div>

        {/* Card */}
        <div className="agri-card animate-fade-in">
          {step === 'role' ? (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-center mb-6">
                Choose how you want to login
              </h2>

              <button
                onClick={() => handleRoleSelect('farmer')}
                className="w-full p-5 rounded-xl border-2 border-border bg-card hover:border-primary hover:bg-secondary/50 transition flex items-center gap-4"
              >
                <User className="w-7 h-7 text-leaf" />
                <span className="flex-1 text-left">{t('login.asFarmer')}</span>
                <ArrowRight />
              </button>

              <button
                onClick={() => handleRoleSelect('village_head')}
                className="w-full p-5 rounded-xl border-2 border-border bg-card hover:border-primary hover:bg-secondary/50 transition flex items-center gap-4"
              >
                <Users className="w-7 h-7 text-primary" />
                <span className="flex-1 text-left">{t('login.asVillageHead')}</span>
                <ArrowRight />
              </button>
            </div>
          ) : (
            <form onSubmit={handleLogin} className="space-y-5">
              <button
                type="button"
                onClick={() => setStep('role')}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                ← Back
              </button>

              <div>
                <label className="block text-sm mb-2">
                  Email / Username
                </label>
                <input
                  className="agri-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-sm mb-2">Password</label>
                <input
                  type="password"
                  className="agri-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              {error && (
                <p className="text-sm text-red-500 text-center">{error}</p>
              )}

              <button
                type="submit"
                className="agri-btn-primary w-full flex justify-center gap-2"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin w-4 h-4" />
                    Logging in...
                  </>
                ) : (
                  <>
                    {t('login.continue')}
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <p className="text-center text-sm text-muted-foreground mt-4">
                Don't have an account?{' '}
                <span
                  onClick={() => navigate('/signup')}
                  className="text-primary cursor-pointer hover:underline font-medium"
                >
                  Create one
                </span>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Login;
