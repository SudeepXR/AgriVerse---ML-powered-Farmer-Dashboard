    import React, { useState } from 'react';
    import { useNavigate } from 'react-router-dom';
    import { useLanguage } from '@/contexts/LanguageContext';
    import { Wheat, User, Users, ArrowRight, Loader2 } from 'lucide-react';

    type SignupStep = 'role' | 'details';
    type Role = 'farmer' | 'village_head';

    const Signup: React.FC = () => {
    const [step, setStep] = useState<SignupStep>('role');
    const [selectedRole, setSelectedRole] = useState<Role | null>(null);
    const { t, language, setLanguage } = useLanguage();
    const [form, setForm] = useState<any>({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleRoleSelect = (role: Role) => {
        setSelectedRole(role);
        setStep('details');
        setError('');
    };

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedRole) return;

        setLoading(true);
        setError('');

        const endpoint =
        selectedRole === 'farmer'
            ? 'http://localhost:5000/api/auth/farmer/signup'
            : 'http://localhost:5000/api/auth/head/signup';

        const payload =
        selectedRole === 'farmer'
            ? {
                username: form.email,
                password: form.password,
                full_name: form.full_name,
                village: form.village,
                district: form.district
            }
            : {
                username: form.email,
                password: form.password,
                full_name: form.full_name
            };

        try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Signup failed');

        navigate('/login');
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
                {t('Welcome to Agri Verse') ?? 'Create Account'}
            </h1>
            <p className="text-muted-foreground mt-2">
                {t('Signup to join the AgriVerse Community') ?? 'Join the farming dashboard'}
            </p>
            </div>

            {/* Card */}
            <div className="agri-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
            {step === 'role' ? (
                <div className="space-y-4">
                <h2 className="text-lg font-display font-semibold text-center text-foreground mb-6">
                    Choose account type
                </h2>

                {/* Farmer */}
                <button
                    onClick={() => handleRoleSelect('farmer')}
                    className="w-full p-5 rounded-xl border-2 border-border bg-card hover:border-primary hover:bg-secondary/50 transition-all duration-300 flex items-center gap-4 group"
                >
                    <div className="w-14 h-14 rounded-xl bg-leaf/15 flex items-center justify-center group-hover:bg-leaf/25 transition-colors">
                    <User className="w-7 h-7 text-leaf" />
                    </div>
                    <div className="text-left flex-1">
                    <h3 className="font-semibold text-foreground">Farmer</h3>
                    <p className="text-sm text-muted-foreground">Manage your own farm</p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary" />
                </button>

                {/* Village Head */}
                <button
                    onClick={() => handleRoleSelect('village_head')}
                    className="w-full p-5 rounded-xl border-2 border-border bg-card hover:border-primary hover:bg-secondary/50 transition-all duration-300 flex items-center gap-4 group"
                >
                    <div className="w-14 h-14 rounded-xl bg-primary/15 flex items-center justify-center group-hover:bg-primary/25 transition-colors">
                    <Users className="w-7 h-7 text-primary" />
                    </div>
                    <div className="text-left flex-1">
                    <h3 className="font-semibold text-foreground">Village Head</h3>
                    <p className="text-sm text-muted-foreground">Oversee multiple farmers</p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary" />
                </button>
                </div>
            ) : (
                <form onSubmit={handleSignup} className="space-y-5">
                <button
                    type="button"
                    onClick={() => setStep('role')}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                    ← Back to role selection
                </button>

                {/* Common fields */}
                <div>
                    <label className="block text-sm font-medium mb-2">Full Name</label>
                    <input
                    className="agri-input"
                    placeholder="Enter full name"
                    name="full_name"
                    value={form.full_name || ''}
                    onChange={handleChange}
                    required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Email / Username</label>
                    <input
                    className="agri-input"
                    placeholder="Enter email or username"
                    name="email"
                    value={form.email || ''}
                    onChange={handleChange}
                    required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Password</label>
                    <input
                    type="password"
                    className="agri-input"
                    placeholder="Create password"
                    name="password"
                    value={form.password || ''}
                    onChange={handleChange}
                    required
                    />
                </div>

                {/* Farmer-only fields */}
                {selectedRole === 'farmer' && (
                    <>
                    <div>
                        <label className="block text-sm font-medium mb-2">Village</label>
                        <input
                        className="agri-input"
                        placeholder="Village name"
                        name="village"
                        value={form.village || ''}
                        onChange={handleChange}
                        required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">District</label>
                        <input
                        className="agri-input"
                        placeholder="District name"
                        name="district"
                        value={form.district || ''}
                        onChange={handleChange}
                        required
                        />
                    </div>
                    </>
                )}

                {/* Error message */}
                {error && (
                    <p className="text-sm text-red-500 text-center bg-red-50 p-3 rounded-lg">
                    {error}
                    </p>
                )}

                {/* Submit button */}
                <button
                    type="submit"
                    disabled={loading}
                    className="agri-btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Creating account...
                    </>
                    ) : (
                    <>
                        Create Account
                        <ArrowRight className="w-4 h-4" />
                    </>
                    )}
                </button>

                <p className="text-center text-sm text-muted-foreground">
                    Already have an account?{' '}
                    <span
                    onClick={() => navigate('/login')}
                    className="text-primary cursor-pointer hover:underline font-medium"
                    >
                    Login
                    </span>
                </p>
                </form>
            )}
            </div>
        </div>
        </div>
    );
    };

    export default Signup;
