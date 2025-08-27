// 外部链接管理组合式函数
export function useExternalLinks() {
    const AGREEMENT_URL = "https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf";
    const ACTIVATION_URL = "http://ids.qfnu.edu.cn/retrieve-password/activationMobile/index.html";

    // 打开用户协议
    const openAgreement = () => {
        uni.showModal({
            title: "用户协议",
            content: `即将跳转到用户协议页面：\n${AGREEMENT_URL}\n\n是否继续？`,
            confirmText: "前往",
            cancelText: "复制链接",
            confirmColor: "#7F4515",
            success: (res) => {
                if (res.confirm) {
                    // 用户选择前往
                    openExternalUrl(AGREEMENT_URL, "链接已复制，请在浏览器中打开");
                } else if (res.cancel) {
                    // 用户选择复制链接
                    uni.setClipboardData({
                        data: AGREEMENT_URL,
                        success() {
                            uni.showToast({
                                title: "协议链接已复制到剪贴板",
                                icon: "success",
                                duration: 2000,
                            });
                        },
                    });
                }
            },
        });
    };

    // 打开账号激活页面
    const openActivationPage = () => {
        uni.showModal({
            title: "账号激活",
            content: `即将跳转到账号激活页面：\n${ACTIVATION_URL}\n\n是否继续？`,
            confirmText: "前往",
            cancelText: "复制链接",
            confirmColor: "#7F4515",
            success: (res) => {
                if (res.confirm) {
                    // 用户选择前往
                    openExternalUrl(ACTIVATION_URL, "链接已复制，请在浏览器中打开");
                } else if (res.cancel) {
                    // 用户选择复制链接
                    uni.setClipboardData({
                        data: ACTIVATION_URL,
                        success() {
                            uni.showToast({
                                title: "激活链接已复制到剪贴板",
                                icon: "success",
                                duration: 2000,
                            });
                        },
                    });
                }
            },
        });
    };

    // 通用的外部链接打开函数
    const openExternalUrl = (url, fallbackMessage) => {
        // #ifdef H5
        if (typeof window !== "undefined" && window.open) {
            window.open(url, "_blank");
        } else {
            uni.setClipboardData({
                data: url,
                success() {
                    uni.showToast({
                        title: fallbackMessage,
                        icon: "success",
                        duration: 3000,
                    });
                },
            });
        }
        // #endif

        // #ifdef APP-PLUS
        plus.runtime.openURL(url);
        // #endif

        // #ifdef MP
        uni.setClipboardData({
            data: url,
            success() {
                uni.showToast({
                    title: fallbackMessage,
                    icon: "success",
                    duration: 3000,
                });
            },
        });
        // #endif
    };

    return {
        openAgreement,
        openActivationPage
    };
}
