# heartbeat.py
from logger import setup_logger
from tornado.ioloop import PeriodicCallback

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
        self.heartbeat_hex = heartbeat_hex or "01020304"  # 提供一个默认的十六进制字符串
        try:
            self.heartbeat_bytes = bytes.fromhex(self.heartbeat_hex)
        except ValueError:
            self.logger = setup_logger('heartbeat', 'logs/heartbeat.log')
            self.logger.error(f"无效的心跳包十六进制码流: {self.heartbeat_hex}，使用默认值: 01020304")
            self.heartbeat_bytes = bytes.fromhex("01020304")  # 使用默认值
        self.periodic_callback = None
        self.logger = setup_logger('heartbeat', 'logs/heartbeat.log')
        self.logger.info("心跳包发送器初始化完成")

    def start(self):
        self.periodic_callback = PeriodicCallback(self._send_heartbeat, self.interval * 1000)
        self.periodic_callback.start()
        self.logger.info("心跳包发送器已启动")

    def _send_heartbeat(self):
        clients_copy = list(self.clients)
        for addr in clients_copy:
            try:
                self.heartbeat_bytes = bytes.fromhex(self.heartbeat_hex)
                self.logger.info(f"心跳包已发送到 {addr[0]}:{addr[1]}")
            except Exception as e:
                self.logger.error(f"发送心跳包失败: {e}")
                self.clients.discard(addr)

    def stop(self):
        if self.periodic_callback:
            self.periodic_callback.stop()
        self.logger.info("心跳包发送器已停止")