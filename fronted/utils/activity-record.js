/** 运动记录列表：状态文案与阳光跑有效判定（与后端 is_valid 对齐） */

export const mapRecordStatus = (item) => {
  if (!item) return { statusText: '—', statusColor: '#999' };
  if (item.type !== 'run') {
    const ok = !!item.metrics?.qualified;
    return { statusText: ok ? '达标' : '未达标', statusColor: ok ? '#20C997' : '#d81e06' };
  }
  if (item.is_valid === true) {
    return { statusText: '有效', statusColor: '#20C997' };
  }
  const reason = (item.fail_reason || '').trim();
  if (reason.includes('里程')) return { statusText: '里程不足', statusColor: '#d81e06' };
  if (reason.includes('配速')) return { statusText: '配速未达标', statusColor: '#d81e06' };
  if (reason.includes('人脸')) return { statusText: '人脸未通过', statusColor: '#d81e06' };
  if (reason) return { statusText: '未达标', statusColor: '#d81e06' };
  return { statusText: '未达标', statusColor: '#d81e06' };
};

export const isValidSunshineRun = (item) =>
  item &&
  item.type === 'run' &&
  item.is_valid === true;
