// ProfileCard 组件的业务逻辑
import { ref, onMounted } from "vue";
import { decode } from "../../utils/jwt-decode.js";

// 个人信息缓存管理
class ProfileCache {
    static CACHE_KEY = "user_profile_cache";
    static CACHE_EXPIRE_TIME = 30 * 60 * 1000; // 30分钟过期时间

    // 保存个人信息到缓存
    static save(profileData) {
        try {
            const cacheData = {
                profile: profileData,
                timestamp: Date.now(),
                version: "1.0"
            };
            uni.setStorageSync(this.CACHE_KEY, JSON.stringify(cacheData));
            console.log("个人信息已缓存", profileData);
        } catch (error) {
            console.error("缓存个人信息失败", error);
        }
    }

    // 从缓存读取个人信息
    static get() {
        try {
            const cacheString = uni.getStorageSync(this.CACHE_KEY);
            if (!cacheString) {
                return null;
            }

            const cacheData = JSON.parse(cacheString);

            // 检查缓存是否过期
            if (this.isExpired(cacheData.timestamp)) {
                console.log("个人信息缓存已过期，清除缓存");
                this.clear();
                return null;
            }

            console.log("从缓存读取个人信息", cacheData.profile);
            return cacheData.profile;
        } catch (error) {
            console.error("读取个人信息缓存失败", error);
            this.clear(); // 清除损坏的缓存
            return null;
        }
    }

    // 检查缓存是否过期
    static isExpired(timestamp) {
        return Date.now() - timestamp > this.CACHE_EXPIRE_TIME;
    }

    // 清除缓存
    static clear() {
        try {
            uni.removeStorageSync(this.CACHE_KEY);
            console.log("个人信息缓存已清除");
        } catch (error) {
            console.error("清除个人信息缓存失败", error);
        }
    }

    // 更新缓存（仅更新特定字段）
    static update(updates) {
        const currentProfile = this.get();
        if (currentProfile) {
            const updatedProfile = { ...currentProfile, ...updates };
            this.save(updatedProfile);
            return updatedProfile;
        }
        return null;
    }

    // 检查缓存是否存在且有效
    static isValid() {
        try {
            const cacheString = uni.getStorageSync(this.CACHE_KEY);
            if (!cacheString) return false;

            const cacheData = JSON.parse(cacheString);
            return !this.isExpired(cacheData.timestamp);
        } catch (error) {
            return false;
        }
    }
}

// 提供给其他模块使用的个人信息访问接口
export const ProfileAPI = {
    // 获取缓存的个人信息（供其他API使用）
    getCachedProfile() {
        return ProfileCache.get();
    },

    // 获取学号（最常用的信息）
    getStudentId() {
        const profile = ProfileCache.get();
        return profile ? profile.student_id : null;
    },

    // 获取学生姓名
    getStudentName() {
        const profile = ProfileCache.get();
        return profile ? profile.student_name : null;
    },

    // 获取学院信息
    getCollege() {
        const profile = ProfileCache.get();
        return profile ? profile.college : null;
    },

    // 获取专业信息
    getMajor() {
        const profile = ProfileCache.get();
        return profile ? profile.major : null;
    },

    // 获取班级信息
    getClassName() {
        const profile = ProfileCache.get();
        return profile ? profile.class_name : null;
    },

    // 检查个人信息是否可用
    isProfileAvailable() {
        return ProfileCache.isValid();
    },

    // 清除个人信息缓存
    clearProfile() {
        ProfileCache.clear();
    }
};

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

    // 从缓存加载个人信息
    const loadFromCache = () => {
        const cachedProfile = ProfileCache.get();
        if (cachedProfile) {
            profile.value = { ...cachedProfile };
            console.log("从缓存加载个人信息成功", profile.value);
            return true;
        }
        return false;
    };

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

                // 缓存个人信息
                ProfileCache.save(profile.value);

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
            // 首先尝试从缓存加载
            const cacheLoaded = loadFromCache();

            if (!cacheLoaded) {
                // 缓存不存在或过期，从服务器获取
                console.log("缓存不可用，从服务器获取个人信息");
                fetchProfile();
            } else {
                // 缓存加载成功，但如果数据是默认值则仍需要从服务器获取
                if (profile.value.student_name === "W1ndys" ||
                    profile.value.student_id === "加载中...") {
                    console.log("缓存数据不完整，从服务器重新获取");
                    fetchProfile();
                }
            }
        }
    };

    // 强制从服务器刷新并更新缓存
    const forceRefreshProfile = async () => {
        console.log("强制刷新个人信息");
        // 清除旧缓存
        ProfileCache.clear();
        // 从服务器获取最新数据
        await fetchProfile();
    };

    return {
        // 数据
        profile,
        loading,

        // 方法
        fetchProfile,
        refreshProfile,
        initProfile,
        forceRefreshProfile,
        loadFromCache,

        // 缓存管理方法
        clearProfileCache: ProfileCache.clear,
        getCachedProfile: ProfileCache.get,
        isProfileCacheValid: ProfileCache.isValid
    };
}

// 使用示例：在其他API模块中如何使用个人信息缓存
/*
// 在其他文件中导入
import { ProfileAPI } from "../dashboard/ProfileCard.js";

// 使用示例
const useOtherAPI = () => {
    const callSomeAPI = async () => {
        // 检查个人信息是否可用
        if (!ProfileAPI.isProfileAvailable()) {
            console.warn("个人信息缓存不可用，请先登录或刷新个人信息");
            return;
        }

        // 获取学号用于API请求
        const studentId = ProfileAPI.getStudentId();
        if (!studentId) {
            console.error("无法获取学号");
            return;
        }

        // 使用学号调用其他API
        const response = await uni.request({
            url: `${baseURL}/api/v1/some-endpoint`,
            method: "POST",
            data: {
                student_id: studentId,
                // 其他参数...
            }
        });

        // 也可以获取完整的个人信息
        const fullProfile = ProfileAPI.getCachedProfile();
        console.log("当前用户信息", fullProfile);
    };
};
*/
