# udp_client_runner.py
import time
from udp_client_core import UDPClient
from logger import setup_logger

logger = setup_logger('udp_client_runner', 'logs/udp_client_runner.log')

def run_client(server_host, server_port, interval=2):
    """
    启动客户端，循环发送符合协议的报文。
    """
    client = UDPClient(server_host, server_port)
    try:
        while True:
            client.send_data()
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("客户端模拟器停止运行。")
    finally:
        client.close()