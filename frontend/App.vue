<script>
export default {
  globalData: {
    apiBaseURL: "https://api.easy-qfnu.top",
  },
  onLaunch: function () {
    console.log("App Launch");
    // 使用条件编译，仅在 H5 平台生效
    // #ifdef H5
    // uni-app 的 onAppRoute API 可以监听到所有页面的跳转
    uni.onAppRoute(function (res) {
      console.log('当前路由切换到：', res.path)

      // 确保 window.gtag 已被加载
      if (typeof window.gtag === 'function') {
        window.gtag('config', 'G-CVQBSTF9X6', {
          // uni-app 的 res.path 不带前导斜杠，手动补上
          'page_path': '/' + res.path,
          // 你也可以从 res.meta 中获取页面标题等信息
          // 'page_title': res.meta.title || '默认标题'
        });
      }
    })
    // #endif
  },
  onShow: function () {
    console.log("App Show");
  },
  onHide: function () {
    console.log("App Hide");
  },
};
</script>

<style>
/*每个页面公共css */
</style>
