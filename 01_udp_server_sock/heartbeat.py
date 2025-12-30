from logger import setup_logger
from tornado.ioloop import PeriodicCallback
import asyncio

logger = setup_logger('heartbeat', 'logs/heartbeat.log')


class HeartbeatSender:
    """
        心跳包发送线程
        定期向所有已连接的客户端发送心跳包

        Args:
        sock: UDP socket对象
        clients: 客户端地址集合（线程安全的集合）
        heartbeat_interval: 心跳包发送间隔（秒），默认60秒
        heartbeat_hex: 心跳包16进制码流
    """
    def __init__(self, clients, interval=60, heartbeat_hex=None):
        self.clients = clients
        self.interval = interval
        self.heartbeat_hex = heartbeat_hex or "01020304"
        self.heartbeat_bytes = bytes.fromhex(self.heartbeat_hex)
        logger.info("心跳包发送器初始化完成")

    async def _send_heartbeat(self):
        while True:
            clients_copy = list(self.clients)
            for addr in clients_copy:
                try:
                    logger.info(f"心跳包已发送到 {addr[0]}:{addr[1]}")
                except Exception as e:
                    logger.error(f"发送心跳包失败: {e}")
                    self.clients.discard(addr)
            await asyncio.sleep(self.interval)

    def start(self):
        self.task = asyncio.create_task(self._send_heartbeat())
        logger.info("心跳包发送器已启动")

    def stop(self):
        if self.task:
            self.task.cancel()
        logger.info("心跳包发送器已停止")