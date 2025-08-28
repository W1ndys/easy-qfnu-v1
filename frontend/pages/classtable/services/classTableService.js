/**
 * 课程表API服务
 */

const API_BASE_URL = () => getApp().globalData.apiBaseURL;

/**
 * 获取授权令牌
 */
function getAuthToken() {
    return uni.getStorageSync("token");
}

/**
 * 处理API响应
 */
function handleApiResponse(statusCode, data) {
    if (statusCode === 200 && (data.success || data.code === 200)) {
        return data.data;
    } else if (statusCode === 401) {
        uni.removeStorageSync("token");
        uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
        setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500);
        throw new Error("登录已过期");
    } else {
        throw new Error(data.detail || data.message || "请求失败");
    }
}

/**
 * 课程表服务类
 */
class ClassTableService {
    /**
     * 获取课程表数据
     * @param {string} date - 查询日期，格式：YYYY-MM-DD
     * @returns {Promise<Object>} 课程表数据
     */
    async getClassTable(date = null) {
        const token = getAuthToken();
        if (!token) {
            throw new Error("未登录");
        }

        const url = `${API_BASE_URL()}/api/v1/classtable${date ? `?date=${date}` : ''}`;

        try {
            const { statusCode, data } = await uni.request({
                url,
                method: "GET",
                header: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            return handleApiResponse(statusCode, data);
        } catch (error) {
            console.error("获取课程表失败:", error);
            throw new Error(error.message || "网络连接失败");
        }
    }
}

// 导出单例实例
export const classTableService = new ClassTableService();
