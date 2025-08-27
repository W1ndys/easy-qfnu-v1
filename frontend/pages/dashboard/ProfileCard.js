// ProfileCard 组件的业务逻辑
import { ref, onMounted } from "vue";
import { decode } from "../../utils/jwt-decode.js";

export function useProfileCard() {
    // 用户资料数据
    const profile = ref({
        student_name: "W1ndys",
        student_id: "加载中...",
        college: "曲奇学院",
        major: "曲奇专业",
        class_name: "22曲奇班",
    });

    // 加载状态
    const loading = ref(false);

    // 获取用户资料
    const fetchProfile = async () => {
        const token = uni.getStorageSync("token");
        if (!token) {
            console.warn("未找到登录凭证");
            return;
        }

        loading.value = true;
        const baseURL = getApp().globalData.apiBaseURL;

        try {
            const res = await new Promise((resolve, reject) => {
                uni.request({
                    url: `${baseURL}/api/v1/profile`,
                    method: "GET",
                    header: { Authorization: `Bearer ${token}` },
                    success: resolve,
                    fail: reject,
                });
            });

            if (res.statusCode === 200 && res.data.success) {
                const serverData = res.data.data;

                // 获取学号，优先从服务器数据，其次从token解析
                const studentId = serverData.student_id || (() => {
                    try {
                        const payload = decode(token);
                        return payload.sub;
                    } catch (e) {
                        console.error("Token解析失败", e);
                        return profile.value.student_id;
                    }
                })();

                // 更新用户资料
                profile.value = {
                    student_name: serverData.student_name || profile.value.student_name,
                    student_id: studentId,
                    college: serverData.college || profile.value.college,
                    major: serverData.major || profile.value.major,
                    class_name: serverData.class_name || profile.value.class_name,
                };

                console.log("用户资料获取成功", profile.value);
            } else {
                const errorMsg = res.data.message || `获取信息失败 (${res.statusCode})`;
                console.error("获取用户资料失败", errorMsg);

                uni.showToast({
                    title: errorMsg,
                    icon: "none"
                });

                // 处理认证失败
                if (res.statusCode === 401) {
                    uni.removeStorageSync("token");
                    setTimeout(() => {
                        uni.reLaunch({ url: "/pages/index/index" });
                    }, 1500);
                }
            }
        } catch (err) {
            console.error("获取个人信息请求失败", err);
            uni.showToast({
                title: "网络请求失败，请稍后重试",
                icon: "none"
            });
        } finally {
            loading.value = false;
        }
    };

    // 刷新用户资料
    const refreshProfile = async () => {
        uni.showLoading({ title: "正在刷新..." });
        try {
            await fetchProfile();
            uni.showToast({
                title: "资料已刷新",
                icon: "success"
            });
        } finally {
            uni.hideLoading();
        }
    };

    // 检查并初始化用户资料
    const initProfile = () => {
        const token = uni.getStorageSync("token");
        if (token) {
            // 如果用户信息为默认值或加载中状态，则获取最新数据
            if (!profile.value.student_name ||
                profile.value.student_name === "W1ndys" ||
                profile.value.student_id === "加载中...") {
                fetchProfile();
            }
        }
    };

    return {
        // 数据
        profile,
        loading,

        // 方法
        fetchProfile,
        refreshProfile,
        initProfile
    };
}
