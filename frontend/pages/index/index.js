// pages/index/index.js
import { decode } from '../../utils/jwt-decode.js';

Page({
  data: {
    studentId: "加载中..."
  },

  /**
   * 页面加载时运行的函数 (生命周期函数)
   * 这是进行页面初始化操作的最佳位置
   */
  onLoad(options) {
    // 1. 检查本地有没有Token
    const token = wx.getStorageSync('token');

    if (!token) {
      // 如果没有Token，说明用户未登录，直接踢回登录页
      wx.showToast({
        title: '请先登录',
        icon: 'none',
        duration: 2000,
        complete: () => {
          setTimeout(() => {
            wx.reLaunch({
              url: '/pages/login/login',
            });
          }, 2000);
        }
      });
    } else {
      // 2. 如果有Token，就解析它来获取用户信息
      try {
        const payload = decode(token);
        // 从payload的'sub'字段获取学号 (这和我们后端生成Token时对应)
        this.setData({
          studentId: payload.sub
        });
      } catch (error) {
        // Token解析失败（可能是无效或篡改的Token）
        console.error("Token解析失败", error);
        wx.showToast({
          title: '凭证无效,请重新登录',
          icon: 'none',
        });
        wx.reLaunch({
          url: '/pages/login/login',
        });
      }
    }
  },

  /**
   * 处理功能按钮点击跳转的函数
   */
  handleNavigate(e) {
    const url = e.currentTarget.dataset.url;
    if (url) {
      wx.navigateTo({ url });
    } else {
      wx.showToast({
        title: '功能正在开发中...',
        icon: 'none'
      });
    }
  },

  /**
   * 处理退出登录的函数
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 用户点击了确定
          // 1. 清除本地缓存的Token
          wx.removeStorageSync('token');
          // 2. 跳转回登录页
          wx.reLaunch({
            url: '/pages/login/login',
          });
        }
        // 如果用户点击取消(res.cancel)，则不执行任何操作
      }
    })
  },

  // onShow 是另一个生命周期函数，每次页面显示时都会调用
  // 你可以把 onLoad 里的逻辑移到这里，这样每次回到首页都会检查登录状态
  onShow() {
    // this.onLoad(); // 可以考虑这样做，但目前 onLoad 已经足够
  }
});