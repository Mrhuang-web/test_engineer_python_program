from logger import setup_logger
from utils import bytes_to_hex

logger = setup_logger('client_request_handler', 'logs/client_request_handler.log')


class ClientRequestHandler:
    def __init__(self, sock, message_handler):
        self.sock = sock
        self.message_handler = message_handler
        logger.info("客户端请求处理器初始化完成")

    async def handle_request(self, data, addr):
        logger.info(f"收到来自 {addr[0]}:{addr[1]} 的请求")
        logger.debug(f"接收到的数据 (原始): {data}")
        hex_data = await bytes_to_hex(data)
        logger.debug(f"接收到的数据 (16进制): {hex_data}")

        # 将新客户端地址添加到心跳包发送器的客户端集合中
        if self.message_handler.heartbeat_sender is not None:
            if addr not in self.message_handler.heartbeat_sender.clients:
                self.message_handler.heartbeat_sender.clients.add(addr)
                logger.info(f"新客户端 {addr[0]}:{addr[1]} 已添加到心跳包发送列表")
        else:
            logger.warning("心跳包发送器未正确初始化")

        # 调用消息处理器处理消息
        response = await self.message_handler.generate_response(data)
        if response is None:
            logger.warning("消息校验失败，未生成响应")
            return None
        return response