<template>
    <transition name="modal">
        <view v-if="showModal" class="modal-overlay" @click.self="$emit('close')">
            <view class="modal-container">
                <view class="modal-header">
                    <text class="modal-title">成绩分析与GPA分析提示</text>
                </view>
                <view class="modal-content">
                    <text>
                        因不同专业或不同目标院校的要求不同，保研所需要的绩点要求不同，如有需求，请前往底部自定义GPA计算自行计算
                    </text>
                </view>
                <view class="modal-footer">
                    <button class="modal-btn" @click="$emit('close')">我已知晓</button>
                </view>
            </view>
        </view>
    </transition>
</template>

<script>
import NoticeModalScript from './NoticeModal.js'
export default NoticeModalScript
</script>

<style lang="scss" scoped>
@import './NoticeModal.scss';
</style>
