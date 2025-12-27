# udp_server.py
import argparse

import tornado

from udp_server_core import UDPServer
from config_loader import load_config
from message_handler import MessageHandler
from heartbeat import HeartbeatSender
from logger import setup_logger

logger = setup_logger('udp_server', 'logs/udp_server.log')


def initialize_heartbeat_sender(sock, heartbeat_config):
    """
    初始化心跳包发送器
    """
    clients = set()
    heartbeat_sender = HeartbeatSender(sock, clients, heartbeat_config.get('interval', 60), heartbeat_config.get('hex'))
    heartbeat_sender.start()
    return heartbeat_sender


def main():
    parser = argparse.ArgumentParser(description='UDP服务器 - 接收请求并响应16进制码流')
    parser.add_argument('-c', '--config', type=str, default='config.json', help='配置文件路径（默认为: config.json）')
    args = parser.parse_args()

    config = load_config(args.config)
    if not config:
        logger.error("配置文件加载失败，程序退出")
        return

    server_config = config.get('server', {})
    heartbeat_config = config.get('heartbeat', {})
    response_config = config.get('response', {})

    message_handler = MessageHandler(response_config)
    logger.info("消息处理器初始化完成")

    udp_server = UDPServer(
        host=server_config.get('host', '0.0.0.0'),
        port=server_config.get('port', 8081),
        message_handler=message_handler
    )
    udp_server.start()

    heartbeat_sender = initialize_heartbeat_sender(udp_server.sock, heartbeat_config)

    try:
        logger.info("UDP服务器正在运行...")
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logger.info("停止服务器...")
        udp_server.stop()
        heartbeat_sender.stop()


if __name__ == '__main__':
    main()