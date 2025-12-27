# udp_server.py
import argparse
import socket
import tornado.ioloop
from heartbeat import HeartbeatSender
from message_handler import MessageHandler
from client_request_handler import ClientRequestHandler
from config_loader import ConfigLoader
from logger import setup_logger

logger = setup_logger('udp_server', 'logs/udp_server.log')

clients = set()  # 全局变量，存储当前连接的客户端地址
last_request = None  # 全局变量，存储最近一次请求的信息

def start_udp_server():
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
    global clients
    heartbeat_sender = HeartbeatSender(sock, clients, heartbeat_config.get('interval', 60), heartbeat_config.get('hex'))
    heartbeat_sender.start()

    # 初始化客户端请求处理器
    client_request_handler = ClientRequestHandler(sock, message_handler)

    def handle_request(data, addr):
        global last_request
        last_request = {"data": data, "addr": addr}
        client_request_handler.handle_request(data, addr)

    # 使用 Tornado 的 IOLoop 来处理 UDP 请求
    def udp_server_callback(fileno, event):
        data, addr = sock.recvfrom(1024)
        with tornado.locks.Lock():
            clients.add(addr)
        tornado.ioloop.IOLoop.current().spawn_callback(handle_request, data, addr)

    tornado.ioloop.IOLoop.current().add_handler(sock.fileno(), udp_server_callback, tornado.ioloop.IOLoop.READ)

# 封装为函数，便于在 Tornado 中调用
def initialize_udp_server():
    start_udp_server()