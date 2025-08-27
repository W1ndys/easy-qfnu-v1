// 格式化更新时间
export const formatUpdateTime = (timeStr) => {
    if (!timeStr) return "未知";
    try {
        const date = new Date(timeStr);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / 86400000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffMinutes = Math.floor(diffMs / 60000);
        if (diffDays > 0) return `${diffDays}天前`;
        if (diffHours > 0) return `${diffHours}小时前`;
        if (diffMinutes > 0) return `${diffMinutes}分钟前`;
        return "刚刚";
    } catch (error) {
        return "未知";
    }
};

// 格式化数字
export const formatNumber = (n) => {
    const v = Number(n);
    if (isNaN(v)) return "0";
    return v % 1 === 0 ? String(v) : v.toFixed(1);
};

// 计算已修学时
export const calculateCompletedHours = (module) => {
    if (!module.courses?.length) return { total: 0 };
    return module.courses.filter(course => !!course.completion_status?.includes("已修")).reduce((acc, course) => {
        if (course.hours && typeof course.hours === "object") {
            for (const [key, value] of Object.entries(course.hours)) {
                acc[key] = (acc[key] || 0) + (Number(value) || 0);
            }
        }
        return acc;
    }, {});
};

// 格式化学时信息
export const formatHours = (hours) => {
    if (!hours || typeof hours !== "object") return [];
    const hourTypes = {
        lecture: "讲授",
        practice: "实践",
        seminar: "研讨",
        experiment: "实验",
        design: "设计",
        computer: "上机",
        discussion: "讨论",
        extracurricular: "课外",
        online: "在线",
    };
    return Object.entries(hours)
        .filter(([key, value]) => key !== "total" && Number(value) > 0)
        .map(([key, value]) => `${hourTypes[key] || key}: ${value}`);
};
