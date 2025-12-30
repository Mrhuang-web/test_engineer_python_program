import asyncio
from logger import setup_logger
from utils import bytes_to_hex
import time
import hashlib

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
        self.transport, protocol = await loop.create_datagram_endpoint(
            lambda: DatagramHandler(self.message_handler, self.client_request_handler),
            local_addr=(self.host, self.port)
        )
        logger.info(f"UDP服务器已启动，监听地址: {self.host}:{self.port}")

    async def stop(self):
        if self.transport:
            self.transport.close()
        logger.info("UDP服务器已停止")

    async def stop(self):
        if self.transport:
            self.transport.close()
        logger.info("UDP服务器已停止")


class DatagramHandler:
    def __init__(self, message_handler, client_request_handler):
        self.message_handler = message_handler
        self.client_request_handler = client_request_handler
        self.processed_requests = {}  # 用于记录已处理的请求
        self.request_timeout = 1.0  # 设置请求去重的时间窗口为1秒

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        current_time = time.time()
        # 清理过期的请求记录
        self.processed_requests = {k: v for k, v in self.processed_requests.items() if
                                   current_time - v < self.request_timeout}

        request_key = hashlib.md5(data + str(addr).encode()).hexdigest()
        if request_key not in self.processed_requests:
            self.processed_requests[request_key] = current_time
            asyncio.create_task(self.handle_request(data, addr))
        else:
            logger.info(f"重复请求被忽略: {addr[0]}:{addr[1]}")

    async def handle_request(self, data, addr):
        logger.info(f"\n收到来自 {addr[0]}:{addr[1]} 的请求")
        logger.info(f"接收到的数据 (原始): {data}")
        hex_data = await bytes_to_hex(data)
        logger.info(f"接收到的数据 (16进制): {hex_data}")

        # 提取报文
        extracted_messages = self.message_handler.extract_messages(data)
        if extracted_messages:
            logger.info(f"\n提取到 {len(extracted_messages)} 个报文 (7e起始0d结尾):")
            for idx, msg in enumerate(extracted_messages, 1):
                logger.info(f"  报文 {idx}:")
                logger.info(f"    原始数据: {msg}")
                logger.info(f"    16进制: {await bytes_to_hex(msg)}")
                logger.info(f"    长度: {len(msg)} 字节")
        else:
            logger.info("未找到7e起始0d结尾的报文")

        # 消息校验和响应生成
        response = await self.client_request_handler.handle_request(data, addr)
        if response:
            self.transport.sendto(response, addr)
            logger.info(f"已发送响应: {await bytes_to_hex(response)}")
        else:
            logger.warning("消息校验失败，未发送响应")
