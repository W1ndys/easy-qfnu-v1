import { ref } from "vue";

export function useCredentialsCache() {
    // 响应式数据
    const rememberPassword = ref(false);
    const hasCachedCredentials = ref(false);

    // 加载缓存的账号密码
    const loadCachedCredentials = (formData) => {
        try {
            const cachedCredentials = uni.getStorageSync("cached_credentials");
            if (cachedCredentials) {
                const { studentId, password, remember } = JSON.parse(cachedCredentials);
                formData.value.studentId = studentId || "";
                formData.value.password = password || "";
                rememberPassword.value = remember || false;
                hasCachedCredentials.value = !!(studentId || password);

                console.log("已加载缓存的账号信息", {
                    studentId: studentId ? "***" + studentId.slice(-4) : "",
                    hasPassword: !!password,
                    remember,
                });
            }
        } catch (error) {
            console.error("加载缓存账号密码失败:", error);
        }
    };

    // 保存账号密码到缓存
    const saveCachedCredentials = (formData) => {
        try {
            if (rememberPassword.value) {
                const credentials = {
                    studentId: formData.value.studentId,
                    password: formData.value.password,
                    remember: true,
                    saveTime: new Date().getTime(),
                };
                uni.setStorageSync("cached_credentials", JSON.stringify(credentials));
                console.log("账号密码已保存到缓存");
            } else {
                // 如果不记住密码，清除缓存
                uni.removeStorageSync("cached_credentials");
                console.log("已清除账号密码缓存");
            }
        } catch (error) {
            console.error("保存账号密码到缓存失败:", error);
        }
    };

    // 清除缓存的账号密码
    const clearCachedCredentials = (formData) => {
        uni.showModal({
            title: "确认清除",
            content: "确定要清除缓存的账号密码吗？",
            success: (res) => {
                if (res.confirm) {
                    try {
                        uni.removeStorageSync("cached_credentials");
                        formData.value.studentId = "";
                        formData.value.password = "";
                        rememberPassword.value = false;
                        hasCachedCredentials.value = false;
                        uni.showToast({ title: "缓存已清除", icon: "success" });
                        console.log("用户手动清除了账号密码缓存");
                    } catch (error) {
                        console.error("清除缓存失败:", error);
                        uni.showToast({ title: "清除缓存失败", icon: "none" });
                    }
                }
            },
        });
    };

    // 记住密码选项变化
    const onRememberChange = (e) => {
        try {
            rememberPassword.value =
                Array.isArray(e.detail.value) && e.detail.value.includes("remember");
        } catch (err) {
            rememberPassword.value = false;
        }
    };

    return {
        rememberPassword,
        hasCachedCredentials,
        loadCachedCredentials,
        saveCachedCredentials,
        clearCachedCredentials,
        onRememberChange
    };
}
