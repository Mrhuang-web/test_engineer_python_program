import socket
import tornado.ioloop
from utils import bytes_to_hex
from logger import setup_logger

logger = setup_logger('udp_server_core', 'logs/udp_server_core.log')


class UDPServer:
    def __init__(self, host, port, message_handler):
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.sock = None

    def start(self):
        """
        启动 UDP 服务器
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        logger.info(f"UDP服务器已启动，监听地址: {self.host}:{self.port}")

        # 使用 tornado 的 IOLoop 来周期性地接收数据
        tornado.ioloop.IOLoop.current().add_callback(self.receive_data)

    def receive_data(self):
        """
        周期性地接收数据
        """
        try:
            data, addr = self.sock.recvfrom(65536)  # 接收最大 64KB 数据
            self.handle_request(data, addr)
        except Exception as e:
            logger.error(f"接收数据时出错: {e}")
        finally:
            # 继续接收数据
            tornado.ioloop.IOLoop.current().add_callback(self.receive_data)

    def handle_request(self, data, addr):
        """
        处理接收到的请求
        """
        logger.info(f"收到来自 {addr[0]}:{addr[1]} 的请求")
        logger.debug(f"接收到的数据 (原始): {data}")
        logger.debug(f"接收到的数据 (16进制): {bytes_to_hex(data)}")

        response = self.message_handler.generate_response(data)
        if response:
            self.sock.sendto(response, addr)
            logger.info(f"已发送响应: {bytes_to_hex(response)}")
        else:
            logger.warning("消息校验失败，未发送响应")

    def stop(self):
        """
        停止 UDP 服务器
        """
        if self.sock:
            self.sock.close()
        logger.info("UDP服务器已停止")