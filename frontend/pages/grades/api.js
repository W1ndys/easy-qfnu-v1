// API服务模块 - 处理成绩相关的数据请求
import { ProfileAPI } from "../dashboard/ProfileCard.js";

/**
 * 获取成绩数据
 * @returns {Promise} 成绩数据的Promise对象
 */
export const fetchGradesData = async () => {
    const API_BASE_URL = getApp().globalData.apiBaseURL
    const API_GRADES_URL = `${API_BASE_URL}/api/v1/grades`

    // 检查个人信息是否可用（用于日志记录）
    if (ProfileAPI.isProfileAvailable()) {
        const studentId = ProfileAPI.getStudentId();
        const studentName = ProfileAPI.getStudentName();
        console.log(`正在为学生 ${studentName}(${studentId}) 获取成绩数据`);
    }

    try {
        const { statusCode, data } = await uni.request({
            url: API_GRADES_URL,
            method: "GET",
            header: { Authorization: "Bearer " + uni.getStorageSync("token") },
        })

        if (statusCode === 200 && data.success) {
            return {
                success: true,
                data: {
                    allCourses: data.data || [],
                    gpaAnalysis: data.basic_gpa,
                    semesterGpa: data.semester_gpa,
                    yearlyGpa: data.yearly_gpa,
                    effectiveGpa: data.effective_gpa,
                }
            }
        } else if (statusCode === 401) {
            uni.removeStorageSync("token")
            uni.showToast({ title: "登录已过期，请重新登录", icon: "none" })
            setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500)
            return { success: false, error: "登录已过期" }
        } else {
            uni.showToast({ title: data.detail || "获取成绩失败", icon: "none" })
            return { success: false, error: data.detail || "获取成绩失败" }
        }
    } catch (error) {
        console.error("请求失败", error)
        uni.showToast({ title: "服务器连接失败", icon: "none" })
        return { success: false, error: "服务器连接失败" }
    }
}

/**
 * 计算自定义GPA
 * @param {Array} selectedIndices 选中的课程索引数组
 * @returns {Promise} 计算结果的Promise对象
 */
export const calculateCustomGPA = async (selectedIndices) => {
    const API_BASE_URL = getApp().globalData.apiBaseURL
    const API_GPA_CALCULATE_URL = `${API_BASE_URL}/api/v1/gpa/calculate`

    // 可以在请求中包含学生信息用于服务端日志记录
    const payload = {
        include_indices: selectedIndices.map(String), // 确保索引是字符串
        remove_retakes: true
    };

    // 如果个人信息可用，添加到payload中（可选）
    if (ProfileAPI.isProfileAvailable()) {
        const studentId = ProfileAPI.getStudentId();
        console.log(`正在为学生 ${studentId} 计算自定义GPA`);
        // payload.student_id = studentId; // 根据API需求决定是否添加
    }

    try {
        const { statusCode, data } = await uni.request({
            url: API_GPA_CALCULATE_URL,
            method: "POST",
            header: {
                Authorization: "Bearer " + uni.getStorageSync("token"),
                "Content-Type": "application/json"
            },
            data: payload
        })

        if (statusCode === 200 && data.success) {
            uni.showToast({ title: "GPA计算完成", icon: "success" })
            return { success: true, data: data.data }
        } else {
            uni.showToast({ title: data.detail || "GPA计算失败", icon: "none" })
            return { success: false, error: data.detail || "GPA计算失败" }
        }
    } catch (error) {
        console.error("GPA计算请求失败", error)
        uni.showToast({ title: "网络连接失败", icon: "none" })
        return { success: false, error: "网络连接失败" }
    }
}

/**
 * 将成绩按学期分组
 * @param {Array} grades 成绩数组
 * @returns {Array} 按学期分组的成绩数据
 */
export const groupGradesBySemester = (grades) => {
    if (!grades || grades.length === 0) return []

    const semesterMap = grades.reduce((acc, grade) => {
        (acc[grade.semester] = acc[grade.semester] || []).push(grade)
        return acc
    }, {})

    return Object.keys(semesterMap)
        .map(name => ({ semesterName: name, grades: semesterMap[name] }))
        .sort((a, b) => b.semesterName.localeCompare(a.semesterName))
}

/**
 * 检查登录状态
 * @returns {boolean} 是否已登录
 */
export const checkLoginStatus = () => {
    if (!uni.getStorageSync("token")) {
        uni.showToast({ title: "请先登录", icon: "none" })
        uni.reLaunch({ url: "/pages/index/index" })
        return false
    }
    return true
}

/**
 * 获取当前学生的基本信息（用于其他API调用）
 * @returns {Object|null} 学生基本信息或null
 */
export const getCurrentStudentInfo = () => {
    if (!ProfileAPI.isProfileAvailable()) {
        console.warn("个人信息缓存不可用");
        return null;
    }

    return {
        studentId: ProfileAPI.getStudentId(),
        studentName: ProfileAPI.getStudentName(),
        college: ProfileAPI.getCollege(),
        major: ProfileAPI.getMajor(),
        className: ProfileAPI.getClassName()
    };
}

/**
 * 检查是否有足够的学生信息进行API调用
 * @returns {boolean} 是否有足够信息
 */
export const hasRequiredStudentInfo = () => {
    const studentId = ProfileAPI.getStudentId();
    return studentId && studentId !== "加载中...";
}
