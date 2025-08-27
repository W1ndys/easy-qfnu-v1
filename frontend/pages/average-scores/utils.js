/**
 * 工具函数模块
 */

/**
 * 格式化时间字符串
 * @param {string} timeStr - 时间字符串
 * @returns {string} 格式化后的时间
 */
export function formatTime(timeStr) {
    if (!timeStr) return "";
    return timeStr.replace("T", " ").split(".")[0];
}

/**
 * 生成错误提示信息
 * @param {Error} error - 错误对象
 * @returns {string} 错误提示信息
 */
export function getErrorMessage(error) {
    let errorMessage = "网络错误，请重试";
    if (error.message) {
        if (error.message.includes("HTTP 422")) {
            errorMessage = "输入参数格式错误，请检查输入内容";
        } else if (error.message.includes("HTTP 400")) {
            errorMessage = "请求参数错误，请检查输入内容";
        } else if (error.message.includes("HTTP 500")) {
            errorMessage = "服务器内部错误，请稍后重试";
        } else if (error.message.includes("HTTP")) {
            errorMessage = `请求失败: ${error.message}`;
        }
    }
    return errorMessage;
}
