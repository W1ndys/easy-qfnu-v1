/**
 * 课程表API模块
 * 处理课程表数据的获取和处理
 */

// API配置
const API_CONFIG = {
    baseURL: null, // 将在运行时从全局配置获取
    endpoints: {
        classtable: '/api/v1/classtable'
    },
    timeout: 10000
};

/**
 * 获取API基础URL
 */
const getBaseURL = () => {
    if (!API_CONFIG.baseURL) {
        API_CONFIG.baseURL = getApp().globalData.apiBaseURL;
    }
    return API_CONFIG.baseURL;
};

/**
 * 获取存储的token
 */
const getToken = () => {
    return uni.getStorageSync('token');
};

/**
 * 创建请求头
 */
const createHeaders = (token) => {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return headers;
};

/**
 * 处理API错误响应
 */
const handleApiError = (statusCode, data, context = '获取课程表') => {
    let message = `${context}失败`;

    switch (statusCode) {
        case 400:
            message = data.detail || data.message || '请求参数错误';
            break;
        case 401:
            message = '登录已过期，请重新登录';
            // 清除token并跳转到登录页
            uni.removeStorageSync('token');
            setTimeout(() => {
                uni.reLaunch({ url: '/pages/index/index' });
            }, 1500);
            break;
        case 403:
            message = '没有权限访问';
            break;
        case 404:
            message = '服务不存在';
            break;
        case 422:
            message = '请求数据格式错误';
            break;
        case 429:
            message = '请求过于频繁，请稍后再试';
            break;
        case 500:
            message = '服务器内部错误，请重新登录';
            uni.removeStorageSync('token');
            setTimeout(() => {
                uni.reLaunch({ url: '/pages/index/index' });
            }, 1500);
            break;
        case 502:
        case 503:
        case 504:
            message = '服务暂时不可用，请稍后重试';
            break;
        default:
            message = data.detail || data.message || `${context}失败`;
    }

    return { message, shouldRetry: [502, 503, 504, 429].includes(statusCode) };
};

/**
 * 验证日期格式
 */
const validateDate = (dateStr) => {
    if (!dateStr) return true; // 允许空值

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateStr)) {
        return false;
    }

    const date = new Date(dateStr);
    return date instanceof Date && !isNaN(date.getTime());
};

/**
 * 格式化日期为API所需格式
 */
const formatDateForApi = (date) => {
    if (!date) return null;

    let dateObj;
    if (typeof date === 'string') {
        dateObj = new Date(date);
    } else {
        dateObj = date;
    }

    if (isNaN(dateObj.getTime())) {
        throw new Error('无效的日期格式');
    }

    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
};

/**
 * 获取日期所在周的标识符
 * 返回格式：YYYY-WW (年-周数)
 * 以周一作为一周的开始，周日和周一之间算新的一周
 */
const getWeekIdentifier = (date) => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) {
        return null;
    }

    // 获取星期几 (0=周日, 1=周一, ..., 6=周六)
    const dayOfWeek = dateObj.getDay();

    // 计算当前周的周一日期（作为一周的起始点）
    let weekStartDate = new Date(dateObj);

    if (dayOfWeek === 0) {
        // 周日，回溯到本周一（6天前）
        weekStartDate.setDate(dateObj.getDate() - 6);
    } else {
        // 周一到周六，回溯到本周一
        weekStartDate.setDate(dateObj.getDate() - (dayOfWeek - 1));
    }

    // 使用周一的日期来计算周标识符
    const year = weekStartDate.getFullYear();
    const startOfYear = new Date(year, 0, 1);

    // 找到年份的第一个周一
    const firstDayOfYear = startOfYear.getDay();
    const daysToFirstMonday = firstDayOfYear === 1 ? 0 : (8 - firstDayOfYear);
    const firstMonday = new Date(year, 0, 1 + daysToFirstMonday);

    // 计算相对于第一个周一的周数
    if (weekStartDate < firstMonday) {
        // 如果在第一个周一之前，属于上一年的最后一周
        return getWeekIdentifier(new Date(year - 1, 11, 31));
    }

    const weekNumber = Math.floor((weekStartDate - firstMonday) / (7 * 24 * 60 * 60 * 1000)) + 1;

    return `${year}-${String(weekNumber).padStart(2, '0')}`;
};

/**
 * 判断两个日期是否在同一周
 */
const isSameWeek = (date1, date2) => {
    const week1 = getWeekIdentifier(date1);
    const week2 = getWeekIdentifier(date2);
    return week1 === week2 && week1 !== null && week2 !== null;
};

/**
 * 处理课程表数据
 */
const processClassTableData = (rawData) => {
    if (!rawData || !rawData.data) {
        throw new Error('课程表数据格式错误');
    }

    const { data } = rawData;

    // 验证必要字段
    if (!data.courses || !Array.isArray(data.courses)) {
        console.warn('课程数据格式异常，使用空数组');
        data.courses = [];
    }

    if (!data.time_slots || !Array.isArray(data.time_slots)) {
        console.warn('时间段数据格式异常，使用默认配置');
        data.time_slots = getDefaultTimeSlots();
    }

    if (!data.weekdays || !Array.isArray(data.weekdays)) {
        console.warn('星期数据格式异常，使用默认配置');
        data.weekdays = getDefaultWeekdays();
    }

    // 处理课程数据
    const processedCourses = data.courses.map(course => {
        // 确保课程有唯一ID
        if (!course.id) {
            course.id = `course_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }

        // 确保时间信息完整
        if (course.time_info) {
            // 修正星期格式（后端可能返回0-6，前端需要1-7）
            if (course.time_info.weekday === 0) {
                course.time_info.weekday = 7; // 周日转为7
            }
        }

        // 确保样式信息（简化设计，统一颜色）
        if (!course.style) {
            course.style = {
                color: '#7f4515', // 统一使用主题色
                row: 1,
                col: 1,
                row_span: 1,
                col_span: 1
            };
        }

        return course;
    });

    // 处理统计数据
    const processedStats = {
        total_courses: processedCourses.length,
        total_hours: processedCourses.reduce((sum, course) => {
            const slots = course.time_info?.time_slots || [];
            return sum + slots.length;
        }, 0),
        courses_by_day: data.stats?.courses_by_day || {}
    };

    return {
        ...data,
        courses: processedCourses,
        stats: processedStats,
        processed_at: new Date().toISOString()
    };
};

/**
 * 获取课程颜色（简化版，统一使用主题色）
 */
const getCourseColor = () => {
    return '#7f4515'; // 统一使用主题色，简洁设计
};

/**
 * 获取默认时间段配置
 */
const getDefaultTimeSlots = () => {
    return [
        {
            period: 1,
            name: '第一大节',
            time: '08:00-09:40',
            slots: [1, 2]
        },
        {
            period: 2,
            name: '第二大节',
            time: '10:00-11:40',
            slots: [3, 4]
        },
        {
            period: 3,
            name: '第三大节',
            time: '14:00-15:40',
            slots: [5, 6]
        },
        {
            period: 4,
            name: '第四大节',
            time: '16:00-17:40',
            slots: [7, 8]
        },
        {
            period: 5,
            name: '第五大节',
            time: '19:00-20:40',
            slots: [9, 10]
        }
    ];
};

/**
 * 获取默认星期配置
 */
const getDefaultWeekdays = () => {
    return [
        { id: 1, name: '星期一', short: '周一' },
        { id: 2, name: '星期二', short: '周二' },
        { id: 3, name: '星期三', short: '周三' },
        { id: 4, name: '星期四', short: '周四' },
        { id: 5, name: '星期五', short: '周五' },
        { id: 6, name: '星期六', short: '周六' },
        { id: 7, name: '星期日', short: '周日' }
    ];
};

/**
 * 获取课程表数据
 * @param {string|Date} date - 查询日期，格式：YYYY-MM-DD 或 Date对象
 * @returns {Promise<Object>} 课程表数据
 */
export const fetchClassTable = async (date = null) => {
    try {
        // 验证并格式化日期
        let formattedDate = null;
        if (date) {
            if (!validateDate(date)) {
                throw new Error('日期格式错误，请使用 YYYY-MM-DD 格式');
            }
            formattedDate = formatDateForApi(date);
        }

        // 获取token
        const token = getToken();
        if (!token) {
            throw new Error('用户未登录');
        }

        // 构建URL
        const baseURL = getBaseURL();
        let url = `${baseURL}${API_CONFIG.endpoints.classtable}`;

        // 添加查询参数
        if (formattedDate) {
            url += `?date=${formattedDate}`;
        }

        console.log(`正在请求课程表数据: ${url}`);

        // 发起请求
        const response = await uni.request({
            url,
            method: 'GET',
            header: createHeaders(token),
            timeout: API_CONFIG.timeout
        });

        const { statusCode, data } = response;

        // 处理响应
        if (statusCode === 200) {
            if (data.success || data.code === 200) {
                console.log('课程表数据获取成功');
                return processClassTableData(data);
            } else {
                throw new Error(data.detail || data.message || '获取课程表失败');
            }
        } else {
            const errorInfo = handleApiError(statusCode, data, '获取课程表');
            throw new Error(errorInfo.message);
        }

    } catch (error) {
        console.error('获取课程表失败:', error);

        // 网络错误处理
        if (error.errMsg) {
            if (error.errMsg.includes('timeout')) {
                throw new Error('请求超时，请检查网络连接');
            } else if (error.errMsg.includes('fail')) {
                throw new Error('网络连接失败，请检查网络设置');
            }
        }

        throw error;
    }
};

/**
 * 获取本周课程表
 * @returns {Promise<Object>} 本周课程表数据
 */
export const fetchWeekClassTable = async () => {
    const today = new Date();
    return await fetchClassTable(today);
};

/**
 * 获取指定日期范围的课程表
 * @param {string|Date} startDate - 开始日期
 * @param {string|Date} endDate - 结束日期  
 * @returns {Promise<Array>} 多天课程表数据数组
 */
export const fetchDateRangeClassTable = async (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const results = [];

    const current = new Date(start);
    while (current <= end) {
        try {
            const data = await fetchClassTable(current);
            results.push({
                date: formatDateForApi(current),
                data
            });
        } catch (error) {
            console.warn(`获取 ${formatDateForApi(current)} 的课程表失败:`, error.message);
            results.push({
                date: formatDateForApi(current),
                error: error.message,
                data: null
            });
        }

        current.setDate(current.getDate() + 1);
    }

    return results;
};

/**
 * 缓存管理 - 基于周的缓存策略
 */
const CACHE_CONFIG = {
    key: 'classtable_week_cache',
    maxAge: 30 * 60 * 1000, // 30分钟缓存
};

/**
 * 获取缓存的课程表数据 - 基于周缓存
 */
export const getCachedClassTable = (date) => {
    try {
        const cache = uni.getStorageSync(CACHE_CONFIG.key);
        if (!cache) return null;

        // 检查缓存是否过期
        if (Date.now() - cache.timestamp > CACHE_CONFIG.maxAge) {
            console.log('课程表缓存已过期');
            return null;
        }

        // 检查请求的日期是否在缓存的周内
        if (cache.weekId && isSameWeek(date, cache.requestDate)) {
            console.log(`使用缓存的课程表数据，周标识: ${cache.weekId}`);
            return cache.data;
        }

        console.log('请求日期不在缓存周内，需要重新获取');
        return null;
    } catch (error) {
        console.warn('读取课程表缓存失败:', error);
        return null;
    }
};

/**
 * 缓存课程表数据 - 基于周缓存
 */
export const setCachedClassTable = (date, data) => {
    try {
        const weekId = getWeekIdentifier(date);
        if (!weekId) {
            console.warn('无法获取日期的周标识，跳过缓存');
            return;
        }

        const cache = {
            data,
            weekId,
            requestDate: formatDateForApi(date),
            timestamp: Date.now()
        };

        uni.setStorageSync(CACHE_CONFIG.key, cache);
        console.log(`课程表数据已缓存，周标识: ${weekId}, 请求日期: ${cache.requestDate}`);

    } catch (error) {
        console.warn('缓存课程表数据失败:', error);
    }
};

/**
 * 清理课程表缓存
 */
export const clearClassTableCache = () => {
    try {
        uni.removeStorageSync(CACHE_CONFIG.key);
        console.log('课程表缓存已清理');
    } catch (error) {
        console.warn('清理课程表缓存失败:', error);
    }
};

// 导出常量和函数
export {
    API_CONFIG,
    CACHE_CONFIG,
    validateDate,
    formatDateForApi,
    getDefaultTimeSlots,
    getDefaultWeekdays,
    getWeekIdentifier,
    isSameWeek
};
