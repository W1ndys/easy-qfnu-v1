/**
 * 日期工具函数
 */

/**
 * 格式化日期为 YYYY-MM-DD 格式
 * @param {Date} date - 日期对象
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}

/**
 * 解析日期字符串
 * @param {string} dateStr - 日期字符串 YYYY-MM-DD
 * @returns {Date} 日期对象
 */
export function parseDate(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
}

/**
 * 获取当前日期
 * @returns {string} 当前日期字符串 YYYY-MM-DD
 */
export function getCurrentDate() {
    return formatDate(new Date());
}

/**
 * 获取一周的日期范围
 * @param {string} dateStr - 基准日期字符串 YYYY-MM-DD
 * @returns {Array<string>} 一周的日期数组
 */
export function getWeekDates(dateStr) {
    const date = parseDate(dateStr);
    const dayOfWeek = date.getDay(); // 0 = Sunday, 1 = Monday, ...
    const monday = new Date(date);

    // 调整到周一
    monday.setDate(date.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));

    const weekDates = [];
    for (let i = 0; i < 7; i++) {
        const currentDay = new Date(monday);
        currentDay.setDate(monday.getDate() + i);
        weekDates.push(formatDate(currentDay));
    }

    return weekDates;
}

/**
 * 获取日期的星期几
 * @param {string} dateStr - 日期字符串 YYYY-MM-DD
 * @returns {number} 星期几 (1-7, 1表示周一)
 */
export function getWeekday(dateStr) {
    const date = parseDate(dateStr);
    const day = date.getDay();
    return day === 0 ? 7 : day; // 将周日从0转换为7
}

/**
 * 添加天数到日期
 * @param {string} dateStr - 日期字符串 YYYY-MM-DD
 * @param {number} days - 要添加的天数
 * @returns {string} 新的日期字符串
 */
export function addDays(dateStr, days) {
    const date = parseDate(dateStr);
    date.setDate(date.getDate() + days);
    return formatDate(date);
}

/**
 * 计算两个日期之间的天数差
 * @param {string} date1 - 日期1 YYYY-MM-DD
 * @param {string} date2 - 日期2 YYYY-MM-DD
 * @returns {number} 天数差
 */
export function daysDifference(date1, date2) {
    const d1 = parseDate(date1);
    const d2 = parseDate(date2);
    const timeDiff = d2.getTime() - d1.getTime();
    return Math.ceil(timeDiff / (1000 * 3600 * 24));
}

/**
 * 检查是否为今天
 * @param {string} dateStr - 日期字符串 YYYY-MM-DD
 * @returns {boolean} 是否为今天
 */
export function isToday(dateStr) {
    return dateStr === getCurrentDate();
}

/**
 * 检查是否为本周
 * @param {string} dateStr - 日期字符串 YYYY-MM-DD
 * @returns {boolean} 是否为本周
 */
export function isThisWeek(dateStr) {
    const weekDates = getWeekDates(getCurrentDate());
    return weekDates.includes(dateStr);
}
