# client_request_handler.py
from utils import bytes_to_hex
from logger import setup_logger

logger = setup_logger('client_request_handler', 'logs/client_request_handler.log')

class ClientRequestHandler:
    def __init__(self, sock, message_handler):
        """
        初始化客户端请求处理器。
        :param sock: UDP socket对象
        :param message_handler: 消息处理器对象
        """
        self.sock = sock
        self.message_handler = message_handler
        logger.info("客户端请求处理器初始化完成")

    def handle_request(self, data, addr):
        """
        处理客户端请求。
        :param data: 接收到的字节数据
        :param addr: 客户端地址
        """
        logger.info(f"收到来自 {addr[0]}:{addr[1]} 的请求")
        logger.debug(f"接收到的数据 (原始): {data}")
        logger.debug(f"接收到的数据 (16进制): {bytes_to_hex(data)}")

        # 调用消息处理器处理消息
        response = self.message_handler.generate_response(data)
        if response:
            self.sock.sendto(response, addr)
            logger.info(f"已发送响应: {bytes_to_hex(response)}")
        else:
            logger.warning("消息校验失败，未发送响应")