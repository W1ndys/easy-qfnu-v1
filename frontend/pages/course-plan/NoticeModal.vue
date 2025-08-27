<template>
    <transition name="modal" appear>
        <view v-if="visible" class="modal-overlay" @click="handleClose">
            <view class="modal-container" @click.stop>
                <view class="modal-header">
                    <uni-icons type="info-filled" size="24" color="#1890ff" />
                    <text class="modal-title">培养方案说明</text>
                </view>

                <view class="modal-content">
                    <text class="notice-text">
                        本页面由教务系统培养方案表格直接生成，大部分专业的应修是160或170或175，该培养方案总和大部分都不足够（22级是），少的那些分就是你应该选的公选课的分。如果不够，请及时与对应负责老师沟通。
                    </text>
                    <text class="notice-text" style="margin-top: 24rpx">
                        根据教务处官方规定：培养方案毕业学分原则上145-170学分，其中人文社会科学类专业毕业学分≤160学分，理科类专业毕业学分≤165学分，工科类专业毕业学分≤170学分，辅修学士学位专业毕业学分70学分左右。
                    </text>
                    <view style="margin-top: 16rpx;">
                        <text class="notice-text" style="font-size: 24rpx; color: #8c8c8c">来源：</text>
                        <text class="link-text" @click="openLink">https://jwc.qfnu.edu.cn/info/1068/7039.htm</text>
                    </view>
                </view>

                <view class="modal-actions">
                    <button class="action-btn primary-btn" @click="handleConfirm"
                        style="background-color: #834A1A; color: white;">我已阅读</button>
                </view>
            </view>
        </view>
    </transition>
</template>

<script setup>
const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close', 'confirm']);

const handleClose = () => {
    emit('close');
};

const handleConfirm = () => {
    emit('confirm');
};

const openLink = () => {
    // #ifdef H5
    window.open('https://jwc.qfnu.edu.cn/info/1068/7039.htm', '_blank');
    // #endif

    // #ifdef MP-WEIXIN
    uni.setClipboardData({
        data: 'https://jwc.qfnu.edu.cn/info/1068/7039.htm',
        success: () => {
            uni.showToast({
                title: '链接已复制到剪贴板',
                icon: 'success'
            });
        }
    });
    // #endif

    // #ifdef APP-PLUS
    plus.runtime.openURL('https://jwc.qfnu.edu.cn/info/1068/7039.htm');
    // #endif
};
</script>

<style lang="scss" scoped>
@import './NoticeModal.scss';

.link-text {
    font-size: 24rpx;
    color: #1890ff;
    text-decoration: underline;
    cursor: pointer;
    transition: color 0.3s ease;
}

.link-text:hover {
    color: #40a9ff;
}

.link-text:active {
    color: #096dd9;
}
</style>
