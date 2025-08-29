import { decode } from "../../utils/jwt-decode.js";

// ==================== Profile Management ====================
class ProfileCache {
    static CACHE_KEY = "user_profile_cache";
    static CACHE_EXPIRE_TIME = 30 * 60 * 1000; // 30分钟过期时间

    // 获取当前用户的唯一标识
    static getCurrentUserKey() {
        const token = uni.getStorageSync("token");
        if (!token) return null;

        try {
            const payload = decode(token);
            return payload.sub || payload.user_id || payload.id || token.substring(0, 32);
        } catch (error) {
            return token.substring(0, 32);
        }
    }

    // 保存个人信息到缓存
    static save(profileData) {
        try {
            const userKey = this.getCurrentUserKey();
            if (!userKey) {
                console.warn("无法获取用户标识，跳过缓存");
                return;
            }
            const cacheData = {
                profile: profileData,
                timestamp: Date.now(),
                version: "1.1",
                userKey: userKey,
                tokenHash: this.getTokenHash()
            };
            uni.setStorageSync(this.CACHE_KEY, JSON.stringify(cacheData));
        } catch (error) {
            console.error("缓存个人信息失败", error);
        }
    }

    static getTokenHash() {
        const token = uni.getStorageSync("token");
        if (!token) return null;
        let hash = 0;
        for (let i = 0; i < token.length; i++) {
            const char = token.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash.toString();
    }

    static get() {
        try {
            const cacheString = uni.getStorageSync(this.CACHE_KEY);
            if (!cacheString) return null;
            const cacheData = JSON.parse(cacheString);
            if (this.isExpired(cacheData.timestamp) || this.userKeyChanged(cacheData) || this.tokenChanged(cacheData)) {
                this.clear();
                return null;
            }
            return cacheData.profile;
        } catch (error) {
            this.clear();
            return null;
        }
    }

    static isExpired(timestamp) {
        return Date.now() - timestamp > this.CACHE_EXPIRE_TIME;
    }

    static userKeyChanged(cacheData) {
        return cacheData.userKey !== this.getCurrentUserKey();
    }

    static tokenChanged(cacheData) {
        return cacheData.tokenHash && cacheData.tokenHash !== this.getTokenHash();
    }

    static isValid() {
        const cacheString = uni.getStorageSync(this.CACHE_KEY);
        if (!cacheString) return false;
        try {
            const cacheData = JSON.parse(cacheString);
            return !this.isExpired(cacheData.timestamp) && !this.userKeyChanged(cacheData) && !this.tokenChanged(cacheData);
        } catch {
            return false;
        }
    }

    static clear() {
        uni.removeStorageSync(this.CACHE_KEY);
    }

    static clearAll() {
        uni.removeStorageSync(this.CACHE_KEY);
    }
}

export const ProfileAPI = {
    isProfileAvailable: () => ProfileCache.isValid(),
    getProfile: () => ProfileCache.get(),
    getStudentId: () => ProfileCache.get()?.student_id || "加载中...",
    getStudentName: () => ProfileCache.get()?.student_name || "W1ndys",
    getCollege: () => ProfileCache.get()?.college || "曲奇学院",
    getMajor: () => ProfileCache.get()?.major || "曲奇专业",
    getClassName: () => ProfileCache.get()?.class_name || "22曲奇班",
    saveProfile: (profileData) => ProfileCache.save(profileData),
    clearProfile: () => ProfileCache.clear(),
};

export { ProfileCache };
