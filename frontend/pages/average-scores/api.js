/**
 * 平均分查询API模块
 */

/**
 * 检查登录状态
 * @returns {boolean} 是否已登录
 */
export function checkLoginStatus() {
    const token = uni.getStorageSync("token");
    if (!token) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
        return false;
    }
    return true;
}

/**
 * 查询平均分数据
 * @param {Object} params - 查询参数
 * @param {string} params.course - 课程名称或代码
 * @param {string} [params.teacher] - 教师姓名（可选）
 * @returns {Promise} 返回查询结果
 */
export function queryAverageScores(params) {
    const baseURL = getApp().globalData.apiBaseURL;
    const token = uni.getStorageSync("token");

    if (!token) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
        return Promise.reject(new Error("未登录"));
    }

    return new Promise((resolve, reject) => {
        uni.request({
            url: `${baseURL}/api/v1/average-scores`,
            method: "GET",
            data: params,
            header: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            success: (res) => {
                if (res.statusCode === 401) {
                    uni.removeStorageSync("token");
                    uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
                    setTimeout(() => {
                        uni.reLaunch({ url: "/pages/index/index" });
                    }, 1500);
                    return;
                }
                if (res.statusCode !== 200) {
                    reject(new Error(`HTTP ${res.statusCode}: ${res.data?.message || "请求失败"}`));
                    return;
                }
                resolve(res.data);
            },
            fail: (err) => reject(err),
        });
    });
}
