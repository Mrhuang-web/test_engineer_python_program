# client_request_handler.py
from logger import setup_logger
from utils import bytes_to_hex

class ClientRequestHandler:
    def __init__(self, sock, message_handler):
        """
        初始化客户端请求处理器。
        :param sock: UDP socket对象
        :param message_handler: 消息处理器对象
        """
        self.sock = sock
        self.message_handler = message_handler
        self.logger = setup_logger('client_request_handler', 'logs/client_request_handler.log')
        self.logger.info("客户端请求处理器初始化完成")

    async def handle_request(self, data, addr):
        """
        处理客户端请求。
        :param data: 接收到的字节数据
        :param addr: 客户端地址
        """
        self.logger.info(f"收到来自 {addr[0]}:{addr[1]} 的请求")
        self.logger.debug(f"接收到的数据 (原始): {data}")
        self.logger.debug(f"接收到的数据 (16进制): {await bytes_to_hex(data)}")

        # 调用消息处理器处理消息
        response = await self.message_handler.generate_response(data)
        if response:
            self.sock.sendto(response, addr)
            self.logger.info(f"已发送响应: {await bytes_to_hex(response)}")
        else:
            self.logger.warning("消息校验失败，未发送响应")