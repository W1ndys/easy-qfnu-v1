# Easy-QFNU

> 曲阜师范大学第三方教务辅助工具

Easy-QFNU 是一个专为曲阜师范大学学生设计的第三方教务辅助系统，包含微信小程序前端和 FastAPI 后端，提供便捷的教务信息查询和数据分析服务。

## 📱 项目特性

### 🎯 核心功能

- **快速查询**: 成绩查询、课表查询、课余量查询
- **数据增强**: 自动计算 GPA、绩点统计、成绩分析
- **智能统计**: 课程历史平均分、班内排名分析
- **教师推荐**: 基于历史数据的选课参考
- **众包模式**: 用户贡献数据，共建数据生态

### 🔒 安全保障

- **不存储密码**: 仅用于获取官网 Session，不在服务器存储
- **HTTPS 加密**: 全站 HTTPS，保护数据传输安全
- **JWT 认证**: 无状态身份验证，安全可靠
- **隐私保护**: 严格遵守最小必要原则，保护用户隐私

### 🏗️ 技术架构

- **前端**: 微信原生小程序 (WXML, WXSS, JavaScript)
- **后端**: Python + FastAPI 框架
- **数据库**: SQLite 轻量级数据库
- **部署**: 云服务器 + Nginx + Uvicorn

## 📁 项目结构

```
EasyQFNUJW/
├── backend/                 # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 核心模块
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── data/           # 数据存储
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── README.md           # 后端文档
├── frontend/               # 微信小程序前端
│   ├── pages/              # 页面文件
│   ├── components/         # 自定义组件
│   ├── utils/              # 工具函数
│   ├── images/             # 图片资源
│   ├── app.js              # 应用逻辑
│   ├── app.json            # 应用配置
│   ├── app.wxss            # 全局样式
│   └── README.md           # 前端文档
├── 设计文档.md              # 项目设计文档
├── LICENSE                 # 开源协议
└── README.md               # 项目总览
```

## 🚀 快速开始

### 后端部署

1. **环境准备**

```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境**

```bash
cp env.example .env
# 编辑 .env 文件，修改相关配置
```

3. **启动服务**

```bash
python main.py
```

4. **访问 API 文档**

- 访问 http://localhost:8000/docs 查看 API 文档

### 前端开发

1. **安装微信开发者工具**

   - 下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

2. **导入项目**

   - 打开微信开发者工具
   - 导入 `frontend` 目录

3. **配置后端地址**

   - 在 `frontend/app.js` 中修改 `apiBase` 配置

4. **开始开发**
   - 在开发者工具中预览和调试

## 🎨 功能展示

### 📊 成绩查询模块

- **个人成绩**: 按学期查看完整成绩单
- **GPA 计算**: 自动计算总 GPA、学期 GPA
- **成绩统计**: 挂科统计、优秀课程统计
- **趋势分析**: 成绩变化趋势图表

### 📅 课表查询模块

- **周视图课表**: 清晰展示时间、地点、教师
- **今日课程**: 快速查看当天课程安排
- **课余量查询**: 实时查询课程剩余名额
- **智能提醒**: 上课时间提醒功能

### 📈 数据统计模块

- **历史参考数据**: 授权的历史平均分数据
- **实时众包数据**: 用户贡献的成绩统计
- **班内排名分析**: 个人可见的排名和百分位
- **教师推荐系统**: 基于历史评价的选课参考

### 👤 用户中心模块

- **个人信息管理**: 基本信息展示和设置
- **数据贡献设置**: 灵活的隐私控制
- **应用设置**: 个性化功能配置
- **意见反馈**: 便捷的问题报告渠道

## 🛡️ 隐私与合规

### 用户协议与隐私政策

- 登录前明确告知并获得用户同意
- 详细说明数据使用目的和范围
- 提供隐私设置选项

### 数据贡献授权

- **一次性弹窗授权**: 单独获取数据贡献同意
- **匿名化处理**: 贡献数据完全匿名
- **可撤回授权**: 用户可随时修改贡献设置

### 安全措施

- **密码不存储**: 仅用于获取 Session，不在服务器保存
- **Session 加密**: 采用安全的序列化和加密存储
- **最小必要原则**: 仅收集必要的数据信息

## 🔧 API 接口

### 认证接口

- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户退出
- `GET /api/verify` - 令牌验证

### 成绩接口

- `GET /api/grades` - 获取成绩列表
- `GET /api/grades/summary` - 获取成绩摘要

### 课表接口

- `GET /api/schedule` - 获取课程表
- `GET /api/schedule/today` - 今日课程
- `GET /api/courses/{id}/capacity` - 课余量查询

### 统计接口

- `GET /api/stats/course/` - 课程统计分析
- `POST /api/stats/grades/contribute` - 贡献成绩数据
- `GET /api/stats/class_rank/` - 班内排名分析

详细的 API 文档请查看：http://localhost:8000/docs

## 🎯 开发路线图

### ✅ 阶段一：MVP 核心功能 (已完成)

- [x] 用户登录认证系统
- [x] 个人成绩查询功能
- [x] 课程表查询功能
- [x] 基础数据统计功能

### 🚧 阶段二：数据增强 (进行中)

- [ ] 历史平均分数据导入
- [ ] 实时众包数据收集
- [ ] 班内排名分析功能
- [ ] 教师推荐系统

### 📋 阶段三：体验优化 (计划中)

- [ ] 界面 UI/UX 优化
- [ ] 性能优化和缓存
- [ ] 离线数据支持
- [ ] 推送通知功能

### 🌟 阶段四：生态建设 (未来)

- [ ] 社群功能集成
- [ ] 第三方服务对接
- [ ] 数据可视化增强
- [ ] AI 智能分析

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循现有的代码风格
- 添加适当的注释和文档
- 确保所有测试通过
- 更新相关文档

### 问题报告

- 使用 GitHub Issues 报告 bug
- 提供详细的复现步骤
- 包含相关的错误日志

## 📜 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## ⚠️ 免责声明

- 本项目为**第三方**教务辅助工具，与曲阜师范大学官方**无任何关联**
- 请遵守学校相关规定和政策使用本工具
- 开发者不对使用本工具产生的任何后果承担责任
- 本工具仅供学习交流使用，禁止商业用途

## 📞 联系我们

- **GitHub Issues**: [提交问题](https://github.com/W1ndys/EasyQFNUJW/issues)
- **Email**: support@example.com
- **QQ 群**: 123456789

---

### 🌟 Star History

如果这个项目对你有帮助，请给我们一个 Star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=W1ndys/EasyQFNUJW&type=Date)](https://star-history.com/#W1ndys/EasyQFNUJW&Date)

---

**感谢您使用 Easy-QFNU！** 🎉
