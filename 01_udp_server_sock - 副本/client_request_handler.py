# client_request_handler.py
from logger import setup_logger
from utils import bytes_to_hex

class ClientRequestHandler:
    def __init__(self, sock, message_handler):
        self.sock = sock
        self.message_handler = message_handler
        self.logger = setup_logger('client_request_handler', 'logs/client_request_handler.log')
        self.logger.info("客户端请求处理器初始化完成")

    async def handle_request(self, data, addr):
        self.logger.info(f"收到来自 {addr[0]}:{addr[1]} 的请求")
        self.logger.debug(f"接收到的数据 (原始): {data}")
        hex_data = await bytes_to_hex(data)  # 使用 await 调用 bytes_to_hex
        self.logger.debug(f"接收到的数据 (16进制): {hex_data}")

        # 将新客户端地址添加到心跳包发送器的客户端集合中
        if addr not in self.message_handler.heartbeat_sender.clients:
            self.message_handler.heartbeat_sender.clients.add(addr)
            self.logger.info(f"新客户端 {addr[0]}:{addr[1]} 已添加到心跳包发送列表")

        # 调用消息处理器处理消息
        response = await self.message_handler.generate_response(data)  # 使用 await
        if response is None:
            self.logger.warning("消息校验失败，未生成响应")
            return None  # 如果生成响应失败，返回 None

        return response