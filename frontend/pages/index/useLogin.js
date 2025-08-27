import { ref, watch } from "vue";
import { isTokenValid } from "../../utils/jwt-decode.js";

export function useLogin() {
    // 响应式数据
    const formData = ref({
        studentId: "",
        password: "",
    });
    const isLoading = ref(false);
    const agreed = ref(false);

    // 学号格式验证正则
    const STUDENT_ID_REGEX = /^\d{8,11}$/;

    // 学号输入时自动清洗：只保留数字，并截断到 11 位
    watch(
        () => formData.value.studentId,
        (val) => {
            const digits = (val || "").replace(/\D/g, "").slice(0, 11);
            if (digits !== val) formData.value.studentId = digits;
        }
    );

    // 检查登录状态函数
    const checkLoginStatus = () => {
        const token = uni.getStorageSync("token");

        if (token) {
            console.log("检测到缓存的token，开始验证有效性");

            try {
                if (isTokenValid(token)) {
                    console.log("Token验证通过，准备跳转到dashboard");
                    uni.reLaunch({
                        url: "/pages/dashboard/dashboard",
                    });
                } else {
                    console.log("Token无效，清除并停留在登录页");
                    uni.removeStorageSync("token");
                    uni.showToast({
                        title: "登录已过期，请重新登录",
                        icon: "none",
                    });
                }
            } catch (error) {
                console.error("Token验证过程中出错:", error);
                uni.removeStorageSync("token");
                uni.showToast({
                    title: "登录状态异常，请重新登录",
                    icon: "none",
                });
            }
        }
    };

    // 同意协议处理
    const onAgreeChange = (e) => {
        try {
            agreed.value = Array.isArray(e.detail.value) && e.detail.value.includes("agree");
        } catch (err) {
            agreed.value = false;
        }
    };

    // 登录处理函数
    const handleLogin = async (rememberPassword, saveCachedCredentials) => {
        // 简单的输入校验
        if (!formData.value.studentId || !formData.value.password) {
            uni.showToast({ title: "学号和密码不能为空", icon: "none" });
            return;
        }

        // 学号格式校验
        const sid = (formData.value.studentId || "").trim();
        if (!STUDENT_ID_REGEX.test(sid)) {
            uni.showToast({ title: "学号格式不正确", icon: "none" });
            return;
        }

        if (!agreed.value) {
            uni.showToast({ title: "请先阅读并同意用户协议", icon: "none" });
            return;
        }

        isLoading.value = true;

        try {
            const res = await uni.request({
                url: `${getApp().globalData.apiBaseURL}/api/v1/login`,
                method: "POST",
                data: {
                    student_id: sid,
                    password: formData.value.password,
                },
            });

            if (res.statusCode === 200 && res.data.access_token) {
                console.log("登录成功, Token:", res.data.access_token);

                // 保存账号密码到缓存（在登录成功后）
                if (saveCachedCredentials) {
                    saveCachedCredentials();
                }

                uni.showToast({ title: "登录成功", icon: "success" });
                uni.setStorageSync("token", res.data.access_token);

                // 延时后跳转
                setTimeout(() => {
                    uni.reLaunch({
                        url: "/pages/dashboard/dashboard",
                    });
                }, 1500);
            } else {
                const errorMessage = res.data.detail || "学号或密码错误";
                uni.showToast({ title: errorMessage, icon: "none" });
            }
        } catch (error) {
            console.error("请求失败", error);
            uni.showToast({ title: "服务器连接失败", icon: "none" });
        } finally {
            isLoading.value = false;
        }
    };

    // 下拉刷新处理
    const onPullRefresh = () => {
        console.log("下拉刷新");
        checkLoginStatus();
        uni.stopPullDownRefresh();
    };

    return {
        formData,
        isLoading,
        agreed,
        checkLoginStatus,
        onAgreeChange,
        handleLogin,
        onPullRefresh
    };
}
