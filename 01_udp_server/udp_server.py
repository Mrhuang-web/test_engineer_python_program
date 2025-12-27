# udp_server.py
import argparse
import socket
import sys
import threading
from heartbeat import HeartbeatSender
from message_handler import MessageHandler
from client_request_handler import ClientRequestHandler
from config_loader import ConfigLoader
from logger import setup_logger

logger = setup_logger('udp_server', 'logs/udp_server.log')

def main():
    parser = argparse.ArgumentParser(description='UDP服务器 - 接收请求并响应16进制码流')
    parser.add_argument('-c', '--config', type=str, default='config.json',
                        help='配置文件路径（默认为: config.json）')
    args = parser.parse_args()

    # 加载配置文件
    config_loader = ConfigLoader(args.config)
    config = config_loader.load()
    if not config:
        logger.error("配置文件加载失败，程序退出")
        return

    server_config = config.get('server', {})
    heartbeat_config = config.get('heartbeat', {})
    response_config = config.get('response', {})

    # 初始化消息处理器
    message_handler = MessageHandler(response_config)
    logger.info("消息处理器初始化完成")

    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_config.get('host', '0.0.0.0'), server_config.get('port', 8080)))
    logger.info(f"UDP服务器已启动，监听地址: {server_config.get('host', '0.0.0.0')}:{server_config.get('port', 8080)}")

    # 初始化心跳包发送器
    clients = set()
    heartbeat_sender = HeartbeatSender(sock, clients, heartbeat_config.get('interval', 60), heartbeat_config.get('hex'))
    heartbeat_sender.start()

    # 初始化客户端请求处理器
    client_request_handler = ClientRequestHandler(sock, message_handler)

    while True:
        data, addr = sock.recvfrom(1024)
        # 将客户端地址添加到集合中（用于心跳包发送）
        with threading.Lock():
            clients.add(addr)

        # 为每个客户端请求创建一个独立的线程
        client_thread = threading.Thread(target=client_request_handler.handle_request, args=(data, addr))
        client_thread.start()

if __name__ == '__main__':
    main()