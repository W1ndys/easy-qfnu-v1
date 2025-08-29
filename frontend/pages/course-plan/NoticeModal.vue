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
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 32rpx;
    animation: fadeIn 0.3s ease-out;
}

.modal-container {
    background: #ffffff;
    border-radius: 20rpx;
    max-width: 600rpx;
    width: 100%;
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
    animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes slideUp {
    from {
        transform: translateY(100rpx);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 退出动画关键帧 */
@keyframes fadeOut {
    from {
        opacity: 1;
    }

    to {
        opacity: 0;
    }
}

@keyframes slideDown {
    from {
        transform: translateY(0);
        opacity: 1;
    }

    to {
        transform: translateY(100rpx);
        opacity: 0;
    }
}

/* overlay 的离场动画 */
.modal-leave-active {
    animation: fadeOut 0.25s ease-in forwards;
}

/* 弹窗容器的离场动画（配合 overlay 一起） */
.modal-leave-active .modal-container {
    animation: slideDown 0.25s ease-in forwards;
}

.modal-header {
    display: flex;
    align-items: center;
    gap: 10rpx;
    padding: 24rpx 24rpx 16rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
    font-size: 32rpx;
    font-weight: 600;
}

.modal-content {
    padding: 24rpx;
}

.notice-text {
    font-size: 28rpx;
    line-height: 1.6;
    color: var(--text-secondary);
}

.modal-actions {
    display: flex;
    padding: 16rpx 24rpx 24rpx;
    justify-content: flex-end;
}

.action-btn {
    padding: 12rpx 24rpx;
    border-radius: 8rpx;
    font-size: 28rpx;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

.primary-btn {
    background-color: #834A1A;
    color: white;
}

.primary-btn:active {
    transform: translateY(2rpx);
    box-shadow: 0 2rpx 8rpx rgba(131, 74, 26, 0.3);
}

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
