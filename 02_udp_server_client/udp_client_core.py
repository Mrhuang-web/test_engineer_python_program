# udp_client_core.py
import socket
from logger import setup_logger
from data_generator import generate_random_card_number, generate_protocol_message

logger = setup_logger('udp_client_core', 'logs/udp_client_core.log')

class UDPClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)  # 设置超时时间为 5 秒
        logger.info(f"UDP客户端初始化完成，目标服务器: {server_host}:{server_port}")

    def send_data(self):
        """
        生成符合协议的报文并发送到服务器。
        """
        card_number = generate_random_card_number()  # 生成随机授权卡号
        message = generate_protocol_message(card_number)  # 生成符合协议的报文

        logger.info(f"发送数据: {message.hex().upper()}")
        self.sock.sendto(message, (self.server_host, self.server_port))

        try:
            response, address = self.sock.recvfrom(65536)
            logger.info(f"收到来自 {address[0]}:{address[1]} 的响应: {response.hex().upper()}")
        except socket.timeout:
            logger.warning("未收到服务器响应，超时！")

    def close(self):
        """
        关闭客户端套接字。
        """
        self.sock.close()
        logger.info("UDP客户端已关闭。")