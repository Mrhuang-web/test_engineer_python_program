# udp_server_core.py
import asyncio
from logger import setup_logger
from utils import bytes_to_hex

logger = setup_logger('udp_server_core', 'logs/udp_server_core.log')


class UDPServer:
    def __init__(self, host, port, message_handler, client_request_handler):
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.client_request_handler = client_request_handler
        self.transport = None

    async def start(self):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: DatagramHandler(self.message_handler, self.client_request_handler),
            local_addr=(self.host, self.port)
        )
        logger.info(f"UDP服务器已启动，监听地址: {self.host}:{self.port}")

    async def stop(self):
        if self.transport:
            self.transport.close()
        logger.info("UDP服务器已停止")


class DatagramHandler:
    def __init__(self, message_handler, client_request_handler):
        self.message_handler = message_handler
        self.client_request_handler = client_request_handler

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.create_task(self.handle_request(data, addr))

    async def handle_request(self, data, addr):
        logger = setup_logger('udp_server_core', 'logs/udp_server_core.log')
        logger.info(f"收到来自 {addr[0]}:{addr[1]} 的请求")
        logger.debug(f"接收到的数据 (原始): {data}")
        hex_data = await bytes_to_hex(data)  # 使用 await 调用 bytes_to_hex
        logger.debug(f"接收到的数据 (16进制): {hex_data}")

        response = await self.client_request_handler.handle_request(data, addr)  # 使用 await 调用 handle_request
        if response is not None:
            self.transport.sendto(response, addr)
            logger.info(f"已发送响应: {hex_data}")
        else:
            logger.warning("消息校验失败，未发送响应")