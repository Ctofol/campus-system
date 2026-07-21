// Convert the Android native WGS84 location to the GCJ02 coordinates used by
// the UniApp/Tencent map. This is a coordinate-system conversion only.
const PI = Math.PI;
const A = 6378245.0;
const EE = 0.00669342162296594323;

const outsideChina = (lng, lat) => lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271;

const transformLat = (lng, lat) => {
  let value = -100 + 2 * lng + 3 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng));
  value += (20 * Math.sin(6 * lng * PI) + 20 * Math.sin(2 * lng * PI)) * 2 / 3;
  value += (20 * Math.sin(lat * PI) + 40 * Math.sin(lat / 3 * PI)) * 2 / 3;
  return value + (160 * Math.sin(lat / 12 * PI) + 320 * Math.sin(lat * PI / 30)) * 2 / 3;
};

const transformLng = (lng, lat) => {
  let value = 300 + lng + 2 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng));
  value += (20 * Math.sin(6 * lng * PI) + 20 * Math.sin(2 * lng * PI)) * 2 / 3;
  value += (20 * Math.sin(lng * PI) + 40 * Math.sin(lng / 3 * PI)) * 2 / 3;
  return value + (150 * Math.sin(lng / 12 * PI) + 300 * Math.sin(lng / 30 * PI)) * 2 / 3;
};

export const wgs84ToGcj02 = (latitude, longitude) => {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude) || outsideChina(longitude, latitude)) {
    return { latitude, longitude };
  }
  const dLat = transformLat(longitude - 105, latitude - 35);
  const dLng = transformLng(longitude - 105, latitude - 35);
  const radLat = latitude / 180 * PI;
  const magic = 1 - EE * Math.sin(radLat) * Math.sin(radLat);
  const sqrtMagic = Math.sqrt(magic);
  const adjustedLat = (dLat * 180) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI);
  const adjustedLng = (dLng * 180) / (A / sqrtMagic * Math.cos(radLat) * PI);
  return { latitude: latitude + adjustedLat, longitude: longitude + adjustedLng };
};
