// NoticeModal 组件的业务逻辑
import { ref } from "vue";

export default {
    name: 'NoticeModal',

    props: {
        noticeData: {
            type: Object,
            required: true,
            default: () => ({
                content: "",
                version: "1"
            })
        }
    },

    emits: ['close', 'popupChange'],

    setup(props, { emit }) {
        const noticePopup = ref(null);

        const openModal = () => {
            if (noticePopup.value) {
                noticePopup.value.open();
            }
        };

        const closeNoticeModal = () => {
            if (noticePopup.value) {
                noticePopup.value.close();
            }
        };

        const handleNoticePopupChange = (e) => {
            emit('popupChange', e);
        };

        const copyQQNumber = () => {
            const qqNumber = "1053240065";
            uni.setClipboardData({
                data: qqNumber,
                success: () => {
                    uni.showToast({
                        title: `QQ号 ${qqNumber} 已复制`,
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

        const openOfficialGroupLink = () => {
            const url = 'https://qm.qq.com/q/jKCk6GtL1e';
            // #ifdef H5
            window.open(url, '_blank');
            // #endif
            // #ifndef H5
            uni.setClipboardData({
                data: url,
                success: () => {
                    uni.showToast({ title: '已复制群链接，请在浏览器打开', icon: 'none' });
                }
            });
            // #endif
        };

        const openDevQQGroupLink = () => {
            const url = 'https://qm.qq.com/q/BBYFdHBDEc';
            // #ifdef H5
            window.open(url, '_blank');
            // #endif
            // #ifndef H5
            uni.setClipboardData({
                data: url,
                success: () => {
                    uni.showToast({ title: '已复制群链接，请在浏览器打开', icon: 'none' });
                }
            });
            // #endif
        };

        return {
            noticePopup,
            openModal,
            closeNoticeModal,
            handleNoticePopupChange,
            copyQQNumber,
            openOfficialGroupLink,
            openDevQQGroupLink
        };
    }
};
