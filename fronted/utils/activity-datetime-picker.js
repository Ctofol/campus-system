/** 跑团活动：日期+时间合并为一个 multiSelector 选择器（纯函数） */

export const pad2 = (n) => String(n).padStart(2, '0');

const getDaysInMonth = (year, month) => new Date(year, month, 0).getDate();

export const getDefaultActivityDateTime = () => {
  const d = new Date();
  d.setMinutes(d.getMinutes() + 30);
  let m = Math.ceil(d.getMinutes() / 15) * 15;
  if (m >= 60) {
    d.setHours(d.getHours() + 1);
    m = 0;
  }
  d.setMinutes(m);
  return {
    date: `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`,
    time: `${pad2(d.getHours())}:${pad2(d.getMinutes())}`
  };
};

export const createDateTimePickerConfig = () => {
  const startYear = new Date().getFullYear();
  const yearCount = 3;
  const years = Array.from({ length: yearCount }, (_, i) => `${startYear + i}年`);
  const months = Array.from({ length: 12 }, (_, i) => `${pad2(i + 1)}月`);
  const hours = Array.from({ length: 24 }, (_, i) => `${pad2(i)}时`);
  const minutes = Array.from({ length: 60 }, (_, i) => `${pad2(i)}分`);

  const buildDayRange = (year, month) => {
    const days = getDaysInMonth(year, month);
    return Array.from({ length: days }, (_, i) => `${pad2(i + 1)}日`);
  };

  const buildRanges = (yi, mi) => [
    years,
    months,
    buildDayRange(startYear + yi, mi + 1),
    hours,
    minutes
  ];

  const indexFromDateTime = (dateStr, timeStr) => {
    const [y, m, d] = dateStr.split('-').map(Number);
    const [hh, mm] = timeStr.split(':').map(Number);
    const yi = Math.max(0, Math.min(y - startYear, yearCount - 1));
    const mi = m - 1;
    const dayRange = buildDayRange(startYear + yi, mi + 1);
    const di = Math.min(Math.max(d - 1, 0), dayRange.length - 1);
    return {
      index: [yi, mi, di, hh, mm],
      ranges: buildRanges(yi, mi)
    };
  };

  const dateTimeFromIndex = (idx, ranges) => {
    const [yi, mi, di, hi, mini] = idx;
    const year = startYear + yi;
    const month = mi + 1;
    const day = di + 1;
    return {
      date: `${year}-${pad2(month)}-${pad2(day)}`,
      time: `${pad2(hi)}:${pad2(mini)}`,
      ranges: buildRanges(yi, mi)
    };
  };

  const adjustIndexOnColumnChange = (column, colVal, currentIndex, currentRanges) => {
    const next = [...currentIndex];
    next[column] = colVal;
    const startYearLocal = startYear;
    if (column === 0 || column === 1) {
      const year = startYearLocal + next[0];
      const month = next[1] + 1;
      const dayRange = buildDayRange(year, month);
      if (next[2] >= dayRange.length) next[2] = dayRange.length - 1;
      return {
        index: next,
        ranges: [years, months, dayRange, hours, minutes]
      };
    }
    return { index: next, ranges: currentRanges };
  };

  return {
    startYear,
    buildRanges,
    indexFromDateTime,
    dateTimeFromIndex,
    adjustIndexOnColumnChange
  };
};
