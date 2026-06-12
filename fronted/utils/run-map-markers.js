/**
 * 跑步轨迹起终点：微信地图原生 label 圆标（避免 PNG 白底贴图）
 * 起点蓝「起」、终点红「终」
 */

const START_COLOR = '#2196F3';
const END_COLOR = '#E53935';

/**
 * @param {object} opts
 * @param {number} opts.id
 * @param {number} opts.latitude
 * @param {number} opts.longitude
 * @param {'start'|'end'} opts.type
 */
export const createRunEndpointMarker = ({ id, latitude, longitude, type }) => {
  const isStart = type === 'start';
  return {
    id,
    latitude,
    longitude,
    title: isStart ? '起点' : '终点',
    iconPath: '/static/marker-anchor.png',
    width: 1,
    height: 1,
    anchor: { x: 0.5, y: 1 },
    zIndex: isStart ? 80 : 81,
    label: {
      content: isStart ? '起' : '终',
      color: '#FFFFFF',
      fontSize: 14,
      bgColor: isStart ? START_COLOR : END_COLOR,
      borderColor: '#FFFFFF',
      borderWidth: 2,
      borderRadius: 18,
      padding: 5,
      anchorX: 0,
      anchorY: -24,
      textAlign: 'center'
    }
  };
};

/** 根据轨迹点批量生成起终点 markers */
export const buildRunRouteMarkers = (points) => {
  if (!Array.isArray(points) || points.length < 1) return [];
  const markers = [
    createRunEndpointMarker({
      id: 2,
      latitude: points[0].latitude,
      longitude: points[0].longitude,
      type: 'start'
    })
  ];
  if (points.length >= 2) {
    const last = points[points.length - 1];
    markers.push(
      createRunEndpointMarker({
        id: 3,
        latitude: last.latitude,
        longitude: last.longitude,
        type: 'end'
      })
    );
  }
  return markers;
};
