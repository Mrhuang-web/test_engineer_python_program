# heartbeat.py
import threading
import time
from logger import setup_logger

logger = setup_logger('heartbeat', 'logs/heartbeat.log')

class HeartbeatSender:
    def __init__(self, sock, clients, interval=60, heartbeat_hex=None):
        self.sock = sock
        self.clients = clients
        self.interval = interval
        self.heartbeat_hex = heartbeat_hex or "默认心跳包16进制码流"
        self.heartbeat_bytes = bytes.fromhex(self.heartbeat_hex)
        self.running = True
        logger.info("心跳包发送器初始化完成")

    def start(self):
        thread = threading.Thread(target=self._send_heartbeat, daemon=True)
        thread.start()
        logger.info("心跳包发送线程已启动")

    def _send_heartbeat(self):
        while self.running:
            time.sleep(self.interval)
            clients_copy = list(self.clients)
            for addr in clients_copy:
                try:
                    self.sock.sendto(self.heartbeat_bytes, addr)
                    logger.info(f"心跳包已发送到 {addr[0]}:{addr[1]}")
                except Exception as e:
                    logger.error(f"发送心跳包失败: {e}")
                    self.clients.discard(addr)

    def stop(self):
        self.running = False
        logger.info("心跳包发送器已停止")