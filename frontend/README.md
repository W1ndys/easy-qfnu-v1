# Easy-QFNUJW 微信小程序

## TabBar 图标解决方案

目前使用了 **文字+Emoji** 的方案来避免图标文件缺失问题。如果您需要使用真实的图标，有以下几种选择：

### 方案一：使用 Emoji（当前方案）
- ✅ 无需额外文件
- ✅ 简洁美观
- ✅ 兼容性好

### 方案二：创建真实图标
如果您想使用真实的图标文件，请：

1. **准备图标文件**
   - 普通状态：81x81 像素
   - 选中状态：81x81 像素
   - 格式：PNG，大小不超过 40KB

2. **创建以下图标文件**
   ```
   frontend/images/tab/
   ├── home.png          # 首页-普通状态
   ├── home-active.png   # 首页-选中状态
   ├── grades.png        # 成绩-普通状态
   ├── grades-active.png # 成绩-选中状态
   ├── schedule.png      # 课表-普通状态
   ├── schedule-active.png # 课表-选中状态
   ├── stats.png         # 统计-普通状态
   ├── stats-active.png  # 统计-选中状态
   ├── profile.png       # 我的-普通状态
   └── profile-active.png # 我的-选中状态
   ```

3. **修改 app.json**
   ```json
   "tabBar": {
     "list": [
       {
         "pagePath": "pages/index/index",
         "iconPath": "images/tab/home.png",
         "selectedIconPath": "images/tab/home-active.png",
         "text": "首页"
       }
       // ... 其他页面
     ]
   }
   ```

### 方案三：图标资源推荐

可以从以下渠道获取图标：
- **IconFont**: https://www.iconfont.cn/
- **Feather Icons**: https://feathericons.com/
- **Heroicons**: https://heroicons.com/
- **微信官方图标库**: 微信开发者文档

### 当前配置

目前 TabBar 配置为文字+Emoji模式：
- 🏠 首页
- 📊 成绩  
- 📅 课表
- 📈 统计
- 👤 我的

这种方式简洁美观，无需额外的图标文件，推荐在开发阶段使用。

## 页面功能

### 登录页面 (`pages/login/`)
- 学号密码登录
- 表单验证
- 隐私协议
- 安全提示

### 首页 (`pages/index/`)
- 个人信息展示
- 今日课程
- 成绩摘要
- 快捷操作

### 成绩查询 (`pages/grades/`)
- 学期成绩列表
- GPA 计算
- 成绩统计
- 筛选排序

### 课程表 (`pages/schedule/`)
- 周视图课表
- 今日课程
- 课程详情
- 课余量查询

### 数据统计 (`pages/stats/`)
- 课程平均分
- 班内排名
- 成绩贡献
- 数据可视化

### 个人中心 (`pages/profile/`)
- 个人信息
- 应用设置
- 意见反馈
- 关于我们

## 开发指南

### 快速开始

1. **安装微信开发者工具**
2. **导入项目** - 选择 `frontend` 目录
3. **配置后端地址** - 修改 `app.js` 中的 `apiBase`
4. **开始调试**

### 配置后端

在 `app.js` 中修改：
```javascript
globalData: {
  apiBase: 'https://your-backend-domain.com/api'
}
```

### 项目结构

```
frontend/
├── pages/           # 页面文件
├── components/      # 自定义组件
├── utils/          # 工具函数
├── images/         # 图片资源
├── app.js          # 应用逻辑
├── app.json        # 应用配置
├── app.wxss        # 全局样式
└── sitemap.json    # 站点地图
```

## 注意事项

- 本应用为第三方教务辅助工具
- 请确保后端API地址正确
- 开发时可关闭域名校验
- 发布前需要配置合法域名

---

**提示**: 如果遇到其他问题，请查看微信开发者工具的调试控制台获取详细错误信息。
