    import { useEffect, useState } from 'react';

    export interface CurrentWeather {
    temperature: number;
    humidity: number;
    wind_speed: number;
    unit: string;
    }

    const WEATHER_CACHE_KEY = 'weather_cache';
    const CACHE_TTL = 10 * 60 * 1000; // 10 minutes

    export const useWeather = () => {
    const [weather, setWeather] = useState<CurrentWeather | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadWeather = async () => {
        try {
            // 1️⃣ Check localStorage
            const cached = localStorage.getItem(WEATHER_CACHE_KEY);
            if (cached) {
            const parsed = JSON.parse(cached);
            const isFresh = Date.now() - parsed.timestamp < CACHE_TTL;

            if (isFresh) {
                setWeather(parsed.data);
                setLoading(false);
                return; // ✅ stop here
            }
            }

            // 2️⃣ Fetch from backend if no cache / expired
            const res = await fetch('http://localhost:5000/api/weather');
            const data = await res.json();

            const current = data.current_weather;

            // 3️⃣ Save to localStorage
            localStorage.setItem(
            WEATHER_CACHE_KEY,
            JSON.stringify({
                data: current,
                timestamp: Date.now(),
            })
            );

            setWeather(current);
        } catch (err) {
            console.error('Weather fetch failed', err);
        } finally {
            setLoading(false);
        }
        };

        loadWeather();
    }, []);

    return { weather, loading };
    };
