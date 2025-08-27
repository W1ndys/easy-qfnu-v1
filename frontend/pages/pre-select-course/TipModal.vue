<template>
    <view v-if="show" class="tip-modal-overlay" :class="{ closing: isClosing }" @click="onOverlayClick">
        <view class="tip-modal" @click.stop>
            <view class="tip-header">
                <text class="tip-title">使用提示</text>
                <view class="tip-close" @click="handleClose">
                    <uni-icons type="close" size="20" color="#868e96" />
                </view>
            </view>
            <view class="tip-content" style="flex-direction: row; flex-wrap: wrap; justify-content: center;">
                <view class="tip-text" style="text-align: left; line-height: 1.8; font-size: 28rpx;">
                    <view style="margin-bottom: 18rpx; color: #d03050; font-weight: bold;">
                        很遗憾，我高估了这个功能的可用性。从理论上讲，我的实现是完全可以做到提前预知选课模块的，但是由于教务系统的隔离性（暂且这么命名），以及系统内某种设定和其他系统内可能的原因，导致搜索结果与预期相差很大，有很多课是本应搜到但实际搜不到的，这一点我也无能为力，敬请谅解。
                    </view>
                    <view style="margin-bottom: 18rpx; color: #198754; font-weight: bold;">
                        不过，目前已经想到一种基于统计的办法来平替此功能，实用性还有待测试，敬请期待后续实践效果。
                    </view>
                    本数据基于
                    <text style="font-weight: bold; color: #7F4515;">你个人的学生身份</text>
                    和
                    <text style="font-weight: bold; color: #7F4515;">当前开放的</text>
                    选课年级库进行搜索，如果搜索没有结果，但你从夫子校园或其他地方搜到了开课数据，说明当前教务系统的开课数据对你
                    <text style="font-weight: bold; color: #f56c6c;">不开放</text>
                    搜索权限。由于教学安排和教务系统限制，本页面搜索结果不保证准确。
                    <text style="font-weight: bold; color: #f56c6c;">仅供参考</text>
                    ，请以实际为准。<br />
                    <text style="font-weight: bold; color: #198754;">公选课数据一般是准确的</text>，因为本模块与培养方案无关，公选课开放情况以教务系统为准。
                </view>
                <view class="search-tip"
                    style="margin: 12rpx 0 0 0; color: #868e96; font-size: 24rpx; line-height: 1.7;">
                    <view>支持模糊搜索，建议使用课程代码，速度更快，结果更精准。</view>
                    <view>如果课余量显示-，大概率是选修课，原因是选修课模块教务系统后端没有提供课余量数据，请使用我们的友情网站 <a href="http://xk.s.fz.z-xin.net"
                            target="_blank" rel="noopener" style="color:#007aff;text-decoration:underline;">夫子校园</a>
                        辅助查询</view>
                </view>
            </view>
            <view class="tip-footer">
                <button class="tip-btn" @click="handleClose">我已知晓</button>
            </view>
        </view>
    </view>
    <view v-else />
</template>

<script setup>
import { defineProps, defineEmits } from "vue";

const props = defineProps({
    show: { type: Boolean, default: false },
    isClosing: { type: Boolean, default: false },
});
const emit = defineEmits(["close"]);

function handleClose() {
    emit("close");
}
function onOverlayClick() {
    handleClose();
}
</script>

<style lang="scss" scoped>
/* 保持与原页面一致的样式（仅弹窗相关） */
.tip-modal-overlay {
    position: fixed;
    inset: 0;
    box-sizing: border-box;
    padding: 40rpx env(safe-area-inset-right) 40rpx env(safe-area-inset-left);
    display: grid;
    place-items: center;
    z-index: 9999;
    background: rgba(0, 0, 0, 0);
    animation: fadeIn 0.3s ease-out forwards;
}

.tip-modal {
    background: #fff;
    border-radius: 20rpx;
    width: 100%;
    max-width: 600rpx;
    max-height: 80vh;
    overflow: auto;
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.2);
    transform: scale(0.92);
    opacity: 0;
    animation: slideIn 0.28s ease-out 0.08s forwards;
}

.tip-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx 30rpx 20rpx;
    border-bottom: 1rpx solid #f1f3f5;
}

.tip-title {
    font-size: 32rpx;
    font-weight: 700;
    color: var(--text-primary);
}

.tip-close {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #f8f9fa;
    cursor: pointer;
    transition: all 0.2s ease;

    &:active {
        background: #e9ecef;
        transform: scale(0.95);
    }
}

.tip-content {
    padding: 30rpx;
    min-height: 200rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.tip-text {
    font-size: 28rpx;
    color: var(--text-primary);
    line-height: 1.6;
    text-align: center;
}

.tip-footer {
    padding: 20rpx 30rpx 30rpx;
    border-top: 1rpx solid #f1f3f5;
}

.tip-btn {
    width: 100%;
    height: 80rpx;
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #fff;
    border: none;
    border-radius: 12rpx;
    font-size: 28rpx;
    font-weight: 600;
    transition: all 0.3s ease;
    transform: translateY(0);

    &::after {
        border: none;
    }

    &:active {
        transform: translateY(2rpx) scale(0.98);
        box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.3);
    }
}

@keyframes fadeIn {
    from {
        background: rgba(0, 0, 0, 0);
    }

    to {
        background: rgba(0, 0, 0, 0.5);
    }
}

@keyframes slideIn {
    from {
        transform: scale(0.92);
        opacity: 0;
    }

    to {
        transform: scale(1);
        opacity: 1;
    }
}

.tip-modal-overlay.closing {
    animation: fadeOut 0.2s ease-in forwards;
}

.tip-modal-overlay.closing .tip-modal {
    animation: slideOut 0.2s ease-in forwards;
}

@keyframes slideOut {
    from {
        transform: scale(1) translateY(0);
        opacity: 1;
    }

    to {
        transform: scale(0.8) translateY(40rpx);
        opacity: 0;
    }
}
</style>
