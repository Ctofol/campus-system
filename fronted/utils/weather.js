import { request } from '@/utils/request.js';
import { getCurrentLocation } from '@/utils/location.js';

const WEATHER_CACHE_KEY = 'home_weather_cache';
const CACHE_TTL_MS = 30 * 60 * 1000;
const LAST_LOC_KEY = 'lastLocation';

const resolveLatLng = async () => {
  const last = uni.getStorageSync(LAST_LOC_KEY);
  const ts = last?.ts ? Number(last.ts) : 0;
  if (last?.lat != null && last?.lng != null && Date.now() - ts < CACHE_TTL_MS) {
    return { lat: last.lat, lng: last.lng };
  }
  const loc = await getCurrentLocation({ fastFix: true, timeout: 10000 });
  if (loc?.success && loc.latitude != null && loc.longitude != null) {
    uni.setStorageSync(LAST_LOC_KEY, {
      lat: loc.latitude,
      lng: loc.longitude,
      ts: Date.now()
    });
    return { lat: loc.latitude, lng: loc.longitude };
  }
  return null;
};

/**
 * 经后端代理获取实时天气（腾讯 Key 仅存服务端）
 */
export const fetchWeather = async (options = {}) => {
  if (!options.force) {
    const cached = uni.getStorageSync(WEATHER_CACHE_KEY);
    if (cached?.weather && cached.ts && Date.now() - cached.ts < CACHE_TTL_MS) {
      return { ok: true, weather: cached.weather, fromCache: true };
    }
  }

  let latLng = null;
  if (options.lat != null && options.lng != null) {
    latLng = { lat: options.lat, lng: options.lng };
  } else {
    latLng = await resolveLatLng();
  }

  if (!latLng) {
    return { ok: false, weather: null, error: 'no_location' };
  }

  try {
    const res = await request({
      url: '/student/weather',
      method: 'GET',
      data: { lat: latLng.lat, lng: latLng.lng }
    });
    const weather = res?.weather;
    if (res?.ok && weather) {
      const normalized = {
        temp: weather.temp,
        condition: weather.condition,
        aqiLabel: weather.aqi_label || weather.aqiLabel || '',
        humidity: weather.humidity != null ? weather.humidity : null,
        icon: weather.icon || 'default'
      };
      uni.setStorageSync(WEATHER_CACHE_KEY, { weather: normalized, ts: Date.now() });
      return { ok: true, weather: normalized, fromCache: false };
    }
    return { ok: false, weather: null, error: res?.error || 'empty' };
  } catch (e) {
    console.warn('[weather] backend request failed', e);
    return { ok: false, weather: null, error: 'network', message: e?.message };
  }
};

/** @deprecated 使用 fetchWeather */
export const fetchTencentWeather = fetchWeather;
