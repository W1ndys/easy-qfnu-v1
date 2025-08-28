// dashboard 页面的主要业务逻辑
import { ref, nextTick } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import { decode } from "../../utils/jwt-decode.js";
import { ProfileAPI } from "./ProfileCard.js";

export function useDashboard() {
    // 弹窗引用
    const noticeModalRef = ref(null);
    const calendarModalRef = ref(null);

    // ==================== 公告机制 ====================
    const noticeData = ref({
        version: "7",
        title: "重要通知：请加用户群防走丢！",
        content: `<div style="line-height: 1.6;">
            <p style="margin-bottom: 16rpx;">我们新增了用户QQ群，欢迎加入</p>
            <p style="margin-bottom: 16rpx;">后期很有可能会推出QQ号强绑定，需要加群使用，请尽快加群，群额度有限</p>
            <p style="margin-bottom: 16rpx; color: red;">仪表盘下方新增了分享本站功能，欢迎分享给朋友</p>
            <p style="margin-bottom: 16rpx;">时间紧张，本网站即将面临四个月的暂停开发，2025年12月后左右恢复开发进度</p>
            <p style="margin-bottom: 16rpx; color: red;">开学快乐！</p>
        </div>`,
        timestamp: Date.now(),
        forceShow: false
    });

    const NOTICE_READ_KEY = "notice_read_version";

    const checkNoticeUpdate = () => {
        const remoteNotice = noticeData.value;
        const lastReadVersion = uni.getStorageSync(NOTICE_READ_KEY);
        console.log(`当前公告版本: ${remoteNotice.version}, 已读版本: ${lastReadVersion}`);

        if (remoteNotice.version !== lastReadVersion || remoteNotice.forceShow) {
            console.log("检测到新公告或强制公告，准备弹窗。");
            nextTick(() => {
                openNoticeModal();
            });
        }
    };

    const openNoticeModal = () => {
        if (noticeModalRef.value) {
            noticeModalRef.value.openModal();
        }
    };

    const handleNoticePopupChange = (e) => {
        if (!e.show) {
            uni.setStorageSync(NOTICE_READ_KEY, noticeData.value.version);
            console.log(`公告版本 ${noticeData.value.version} 已通过关闭操作标记为已读。`);
        }
    };

    // ==================== ProfileCard 引用 ====================
    const profileCardRef = ref(null);

    const features = ref([
        { text: "今日课表", description: "实时查看今日课表", icon: "calendar", url: "/pages/classtable/classtable" },
        { text: "成绩分析", description: "查看成绩与GPA分析", icon: "paperplane", url: "/pages/grades/grades" },
        { text: "平均分查询", description: "查看课程平均分数据", icon: "bars", url: "/pages/average-scores/average-scores" },
        { text: "选课推荐", description: "智能推荐选课方案", icon: "star", url: "https://doc.easy-qfnu.top/EasySelectCourse/CourseSelectionRecommendation/", external: true },
        { text: "培养方案", description: "查看模块完成进度", icon: "list", url: "/pages/course-plan/course-plan" },
        { text: "选课查询", description: "支持选课模块探测", icon: "checkmarkempty", url: "/pages/pre-select-course/pre-select-course" },
        { text: "查看校历", description: "查看最新校历", icon: "calendar", url: "calendar", external: false },
        { text: "无课教室", description: "查询空闲教室", icon: "home", url: "" },
        { text: "无考教室", description: "查询无考试教室", icon: "compose", url: "" },
        { text: "排名查询", description: "即将推出", icon: "medal", url: "" },
        { text: "更多功能", description: "敬请期待", icon: "gear", url: "" },
    ]);



    const checkLoginStatus = () => {
        const token = uni.getStorageSync("token");
        if (!token) {
            uni.showToast({ title: "请先登录", icon: "none" });
            uni.reLaunch({ url: "/pages/index/index" });
            return;
        } else {
            try {
                const payload = decode(token);
                console.log("Token验证成功", payload);
            } catch (error) {
                console.error("Token解析失败", error);
                uni.removeStorageSync("token");
                uni.showToast({ title: "凭证无效,请重新登录", icon: "none" });
                uni.reLaunch({ url: "/pages/index/index" });
                return;
            }
        }
    };

    // ==================== 事件处理 ====================
    const handleNavigate = (index) => {
        const targetPage = features.value[index];
        if (targetPage.url) {
            if (targetPage.url === "calendar") {
                if (calendarModalRef.value) {
                    calendarModalRef.value.openModal();
                }
            } else if (targetPage.external) {
                if (typeof window !== 'undefined') window.open(targetPage.url, "_blank");
                else if (typeof plus !== 'undefined') plus.runtime.openURL(targetPage.url);
                else uni.setClipboardData({ data: targetPage.url, success: () => uni.showToast({ title: "外链已复制,请在浏览器中打开", icon: "success", duration: 3000 }) });
            } else {
                uni.navigateTo({ url: targetPage.url });
            }
        } else {
            uni.showToast({ title: "功能正在开发中...", icon: "none" });
        }
    };

    const handleRefresh = () => {
        // 通过 ProfileCard 组件刷新用户资料
        if (profileCardRef.value && profileCardRef.value.refreshProfile) {
            profileCardRef.value.refreshProfile();
        } else {
            uni.showToast({ title: "刷新功能暂不可用", icon: "none" });
        }
    };

    const handleLogout = () => {
        uni.showModal({
            title: "确认退出", content: "确定要退出登录吗？", confirmColor: "#7F4515",
            success: (res) => {
                if (res.confirm) {
                    // 清除token
                    uni.removeStorageSync("token");

                    // 清除个人信息缓存
                    ProfileAPI.clearAllProfiles();

                    uni.showToast({ title: "已退出登录", icon: "success" });
                    setTimeout(() => { uni.reLaunch({ url: "/pages/index/index" }); }, 1000);
                }
            },
        });
    };

    const handleClearCache = () => {
        uni.showModal({
            title: "清除缓存", content: "确定要清除所有本地缓存数据吗？这将清除除登录凭证外的所有本地数据。",
            confirmText: "清除", cancelText: "取消", confirmColor: "#ff4d4f",
            success: (res) => {
                if (res.confirm) {
                    try {
                        const token = uni.getStorageSync("token");
                        uni.clearStorageSync();
                        if (token) {
                            uni.setStorageSync("token", token);
                            // 清除个人信息缓存（因为可能包含旧数据）
                            ProfileAPI.clearProfile();
                        }
                        uni.showToast({ title: "缓存已清除", icon: "success", duration: 2000 });
                    } catch (e) {
                        uni.showToast({ title: "清除缓存失败", icon: "error" });
                    }
                }
            },
        });
    };

    const handleUserAgreement = () => {
        const url = "https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf";
        handleExternalLink("用户协议", url);
    };

    const handleChangelog = () => {
        const url = "https://cq4hqujcxu3.feishu.cn/docx/BO2od7OI8omtmTxGkB0cn305nFl";
        handleExternalLink("更新日志", url);
    };

    const handleContact = () => {
        const qqAddUrl = "https://qm.qq.com/q/WBCJEU82A2";
        handleExternalLink("添加QQ好友", qqAddUrl);
    };

    const handleFeedback = () => {
        const feedbackUrl = "https://cq4hqujcxu3.feishu.cn/share/base/form/shrcnojLq3xgJ5m5Gzn5V87poHZ";
        handleExternalLink("意见建议反馈", feedbackUrl);
    };

    const handleSponsorList = () => {
        const sponsorUrl = "https://cq4hqujcxu3.feishu.cn/docx/DE9Ed1l5iofB0exEYZncwMeenvd";
        handleExternalLink("赞赏名单", sponsorUrl);
    };

    const handleShareSite = () => {
        const shareText = `我发现一个超级好用的曲师大教务工具，你也来看看吧
多维度成绩分析、历史平均分查询、选课推荐、培养方案解析、选课查询，各种功能~
地址：https://easy-qfnu.top`;

        uni.setClipboardData({
            data: shareText,
            success: () => {
                uni.showToast({
                    title: "分享内容已复制到剪贴板",
                    icon: "success",
                    duration: 2000
                });
            },
            fail: () => {
                uni.showToast({
                    title: "复制失败，请手动复制",
                    icon: "none"
                });
            }
        });
    };

    const handleExternalLink = (title, url) => {
        if (typeof window !== 'undefined') window.open(url, "_blank");
        else if (typeof plus !== 'undefined') plus.runtime.openURL(url);
        else uni.setClipboardData({ data: url, success: () => uni.showToast({ title: "外链已复制,请在浏览器中打开", icon: "success", duration: 3000 }) });
    };

    const handleImageError = () => { uni.showToast({ title: "赞赏码加载失败", icon: "none" }); };
    const handleImageLoad = () => { console.log("赞赏码加载成功"); };

    const handleCalendarImageError = () => { uni.showToast({ title: "校历图片加载失败", icon: "none" }); };
    const handleCalendarImageLoad = () => { console.log("校历图片加载成功"); };

    // ==================== 生命周期 ====================
    const initDashboard = () => {
        onLoad(() => {
            checkLoginStatus();
            checkNoticeUpdate();
            console.log("用户进入仪表盘页面");
        });

        onShow(() => {
            const token = uni.getStorageSync("token");
            if (token) {
                checkLoginStatus();
            }
        });
    };

    return {
        // 数据
        noticeModalRef,
        calendarModalRef,
        profileCardRef,
        noticeData,
        features,

        // 方法
        openNoticeModal,
        handleNoticePopupChange,
        handleNavigate,
        handleRefresh,
        handleLogout,
        handleUserAgreement,
        handleClearCache,
        handleChangelog,
        handleContact,
        handleFeedback,
        handleSponsorList,
        handleShareSite,
        handleImageError,
        handleImageLoad,
        handleCalendarImageError,
        handleCalendarImageLoad,

        // 初始化
        initDashboard
    };
}
