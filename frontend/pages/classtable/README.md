# 课程表模块

这是一个完整的课程表前端模块，采用模块化设计，包含以下组件：

## 📁 文件结构

```
pages/classtable/
├── classtable.vue          # 主页面（整合所有组件）
├── api.js                  # API模块（数据获取和处理）
├── DateSelector.vue        # 日期选择器组件
├── DateSelector.js         # 日期选择器逻辑
├── DateSelector.scss       # 日期选择器样式
├── CourseCard.vue          # 课程卡片组件
├── CourseCard.js           # 课程卡片逻辑
├── CourseCard.scss         # 课程卡片样式
├── DaySchedule.vue         # 单天课程排列组件
├── DaySchedule.js          # 单天课程排列逻辑
├── DaySchedule.scss        # 单天课程排列样式
└── README.md               # 说明文档
```

## 🚀 功能特性

### 1. 日期选择器 (DateSelector)

- ✅ 前一天/后一天快速切换
- ✅ 日期选择器弹窗
- ✅ 今日标识
- ✅ 中文日期显示

### 2. 课程卡片 (CourseCard)

- ✅ 课程基本信息展示（名称、地点、时间）
- ✅ 课程类型标签（必修、选修等）
- ✅ 统一主题色设计
- ✅ 课程状态指示（进行中、即将开始、已结束）
- ✅ 点击查看详情

### 3. 单天课程排列 (DaySchedule)

- ✅ 按时间段排列课程
- ✅ 空课程状态显示
- ✅ 当前课程高亮
- ✅ 课程统计信息
- ✅ 今日/非今日区分显示

### 4. 数据管理 (API)

- ✅ 课程表数据获取
- ✅ 数据缓存机制（10 分钟缓存）
- ✅ 错误处理和重试
- ✅ 日期验证和格式化
- ✅ 数据预处理和优化

### 5. 主页面功能

- ✅ 组件集成和状态管理
- ✅ 加载状态和错误处理
- ✅ 课程详情弹窗
- ✅ 数据统计卡片

## 🎨 设计特色

### 视觉设计

- 🎨 现代化卡片设计
- 🎯 统一主题色系统
- 📱 移动端优化布局
- ✨ 流畅的动画效果

### 交互体验

- 👆 直观的手势操作
- ⚡ 快速的日期切换
- 📋 详细的课程信息
- 🔄 智能缓存机制

## 📋 API 接口

### 获取课程表

```javascript
GET /api/v1/classtable?date=2025-01-15
```

### 响应数据结构

```javascript
{
  "success": true,
  "message": "课程表获取成功",
  "data": {
    "week_info": {
      "current_week": 1,
      "total_weeks": 20
    },
    "time_slots": [
      {
        "period": 1,
        "name": "第一大节",
        "time": "08:00-09:40",
        "slots": [1, 2]
      }
    ],
    "courses": [
      {
        "id": "course_1",
                 "name": "网络管理",
        "location": "嵌入式实验室204",
        "credits": "3",
        "course_type": "任选",
        "time_info": {
          "weekday": 1,
          "weekday_name": "星期一",
          "period": 1,
          "start_time": "08:00",
          "end_time": "09:40"
        },
        "style": {
          "color": "#3498db"
        }
      }
    ],
    "stats": {
      "total_courses": 1,
      "total_hours": 2
    }
  }
}
```

## 🔧 使用方法

### 1. 直接使用主页面

```vue
<template>
  <classtable />
</template>
```

### 2. 单独使用组件

#### 日期选择器

```vue
<template>
  <DateSelector v-model="selectedDate" @change="onDateChange" />
</template>
```

#### 课程卡片

```vue
<template>
  <CourseCard
    :course="courseData"
    :current-time="currentTime"
    @click="onCourseClick" />
</template>
```

#### 单天课程排列

```vue
<template>
  <DaySchedule
    :selected-date="selectedDate"
    :courses="courses"
    :time-slots="timeSlots"
    @course-click="onCourseClick" />
</template>
```

### 3. API 调用

```javascript
import { fetchClassTable } from "./api.js";

// 获取指定日期的课程表
const data = await fetchClassTable("2025-01-15");

// 获取今日课程表
const todayData = await fetchClassTable();
```

## 📱 界面预览

### 主界面

- 顶部：日期选择器（前一天/后一天按钮 + 日期显示 + 日期选择按钮）
- 中部：当前课程指示器（如有进行中的课程）
- 主体：课程卡片列表（按时间排序）
- 底部：统计信息卡片（可选）

### 课程卡片

- 头部：课程名称 + 时间 + 类型标签
- 主体：地点、班级信息
- 底部：学分信息

### 空状态

- 无课程时显示友好的空状态提示
- 提供休息建议和学习建议

## 🛠️ 技术实现

### 前端技术栈

- Vue 3 Composition API
- SCSS 样式预处理
- Uni-app 跨平台框架

### 核心特性

- 响应式数据管理
- 组件化架构
- 智能缓存系统
- 错误边界处理
- 性能优化

### 浏览器兼容

- 支持现代浏览器
- 移动端优化
- 小程序兼容

## 🔮 扩展功能

可以在此基础上扩展：

- 📅 周视图课程表
- 📋 课程详情页面
- 🔔 课程提醒功能
- 📊 学习统计分析
- 🎯 课程搜索功能
- 📤 课程分享功能

## 🐛 常见问题

### Q: 如何自定义课程颜色？

A: 课程卡片统一使用主题色设计，如需修改可在 CourseCard.scss 中调整 .course-header 的背景色

### Q: 如何调整缓存时间？

A: 在 api.js 中修改 CACHE_CONFIG.maxAge 配置

### Q: 如何添加新的课程状态？

A: 在 CourseCard.vue 中扩展 courseStatus 计算属性和对应样式

### Q: 如何自定义时间段？

A: 在 api.js 中修改 getDefaultTimeSlots 函数返回的时间段配置
