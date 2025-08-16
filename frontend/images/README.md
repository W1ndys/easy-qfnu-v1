# 图片资源说明

## Logo 解决方案

目前使用了 **Emoji Logo** 的方案（🎓）来避免图片文件缺失问题。

### 当前方案：文字Logo
- ✅ 无需图片文件
- ✅ 加载速度快
- ✅ 支持所有设备
- ✅ 易于维护

### 如果需要真实Logo图片

如果您想使用真实的logo图片，请：

#### 1. 准备Logo文件
- **文件名**: `logo.png`
- **尺寸**: 建议 256x256 像素或 512x512 像素
- **格式**: PNG（支持透明背景）
- **大小**: 建议小于 100KB

#### 2. 放置文件
将logo文件放置在：
```
frontend/images/logo.png
```

#### 3. 修改登录页面代码
将 `frontend/pages/login/login.wxml` 中的：
```xml
<view class="logo">🎓</view>
```

改为：
```xml
<image class="logo" src="/images/logo.png" mode="aspectFit"></image>
```

#### 4. 更新样式
将 `frontend/pages/login/login.wxss` 中的logo样式改为：
```css
.logo {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 30rpx;
}
```

## Logo 设计建议

### 设计要素
- **简洁明了**: 在小尺寸下仍然清晰可辨
- **符合主题**: 体现教务辅助工具的特点
- **色彩搭配**: 与应用整体色调协调
- **品牌识别**: 具有一定的记忆点

### 推荐图标元素
- 📚 书本（学习）
- 🎓 学士帽（教育）
- 📊 图表（数据统计）
- 🏫 学校建筑
- ⚡ 闪电（快速）
- 💡 灯泡（智能）

### 在线Logo制作工具
- **Canva**: https://www.canva.com/
- **LogoMaker**: https://www.logomaker.com/
- **Hatchful**: https://hatchful.shopify.com/
- **Tailor Brands**: https://www.tailorbrands.com/

### 免费图标资源
- **IconFont**: https://www.iconfont.cn/
- **Flaticon**: https://www.flaticon.com/
- **Icons8**: https://icons8.com/
- **Feather Icons**: https://feathericons.com/

## 其他图片资源

如果需要添加其他图片资源，请：

1. **创建对应目录**
   ```
   frontend/images/
   ├── logo.png          # 应用logo
   ├── icons/            # 图标文件夹
   ├── backgrounds/      # 背景图片
   └── illustrations/    # 插图
   ```

2. **优化图片**
   - 压缩图片大小
   - 使用合适的格式
   - 考虑不同屏幕密度

3. **注意事项**
   - 图片路径以 `/` 开头表示根目录
   - 小程序对图片大小有限制
   - 考虑网络加载速度

## 当前状态

目前所有需要图片的地方都已经用替代方案处理：
- ✅ **应用Logo**: 使用Emoji 🎓
- ✅ **TabBar图标**: 使用文字+Emoji
- ✅ **功能图标**: 使用Emoji表情

这种方案简洁高效，无需额外的图片文件，推荐在开发和测试阶段使用。

---

**提示**: 如果您准备发布正式版本，建议设计专业的Logo和图标以提升用户体验和品牌形象。
