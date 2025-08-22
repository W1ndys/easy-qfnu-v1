from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from typing import Callable, Any


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False

    def start(self):
        """启动调度器"""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.info("定时器服务已启动")

    def stop(self):
        """停止调度器"""
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("定时器服务已停止")

    def add_job(self, func: Callable, trigger_type: str = "interval", **kwargs):
        """
        添加定时任务

        Args:
            func: 要执行的函数
            trigger_type: 触发器类型 ("interval", "cron", "date")
            **kwargs: 触发器参数
        """
        try:
            if trigger_type == "interval":
                # 间隔执行，例如每5分钟
                job = self.scheduler.add_job(
                    func,
                    trigger=IntervalTrigger(**kwargs),
                    id=f"{func.__name__}_{id(func)}",
                    replace_existing=True,
                )
            elif trigger_type == "cron":
                # 定时执行，例如每天凌晨2点
                job = self.scheduler.add_job(
                    func,
                    trigger=CronTrigger(**kwargs),
                    id=f"{func.__name__}_{id(func)}",
                    replace_existing=True,
                )
            else:
                raise ValueError(f"不支持的触发器类型: {trigger_type}")

            logger.info(f"定时任务已添加: {job.id}")
            return job

        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
            raise

    def remove_job(self, job_id: str):
        """移除定时任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"定时任务已移除: {job_id}")
        except Exception as e:
            logger.error(f"移除定时任务失败: {e}")

    def get_jobs(self):
        """获取所有定时任务"""
        return self.scheduler.get_jobs()

    def pause_job(self, job_id: str):
        """暂停定时任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"定时任务已暂停: {job_id}")
        except Exception as e:
            logger.error(f"暂停定时任务失败: {e}")

    def resume_job(self, job_id: str):
        """恢复定时任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"定时任务已恢复: {job_id}")
        except Exception as e:
            logger.error(f"恢复定时任务失败: {e}")


# 全局调度器实例
scheduler = SchedulerService()

# ========== 主函数使用示例 ==========
if __name__ == "__main__":
    import asyncio

    async def main():
        import time

        def my_job():
            logger.info("定时任务执行：你好，世界！")

        # 添加一个每2秒执行一次的定时任务
        job = scheduler.add_job(my_job, trigger_type="interval", seconds=2)

        scheduler.start()

        logger.info("主函数示例：调度器已启动，等待10秒后停止...")
        await asyncio.sleep(10)

        scheduler.stop()
        logger.info("主函数示例：调度器已停止。")

    asyncio.run(main())
