// 仪表盘页面模块化组件统一导出

// Vue 组件导出
export { default as ProfileCard } from './ProfileCard.vue';
export { default as NoticeBar } from './NoticeBar.vue';
export { default as FeatureGrid } from './FeatureGrid.vue';
export { default as SystemActions } from './SystemActions.vue';
export { default as SupportCard } from './SupportCard.vue';
export { default as NoticeModal } from './NoticeModal.vue';
export { default as CalendarModal } from './CalendarModal.vue';

// 业务逻辑导出
export { useDashboard } from './dashboard.js';

// 单独组件逻辑导出（如需要）
export { default as ProfileCardLogic } from './ProfileCard.js';
export { default as NoticeBarLogic } from './NoticeBar.js';
export { default as FeatureGridLogic } from './FeatureGrid.js';
export { default as SystemActionsLogic } from './SystemActions.js';
export { default as SupportCardLogic } from './SupportCard.js';
export { default as NoticeModalLogic } from './NoticeModal.js';
export { default as CalendarModalLogic } from './CalendarModal.js';
