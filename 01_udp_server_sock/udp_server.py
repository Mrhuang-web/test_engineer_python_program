import argparse
import asyncio
from udp_server_core import UDPServer
from config_loader import load_config
from message_handler import MessageHandler
from heartbeat import HeartbeatSender
from client_request_handler import ClientRequestHandler
from logger import setup_logger

logger = setup_logger('udp_server', 'logs/udp_server.log')

async def main():
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

    clients = set()
    heartbeat_sender = HeartbeatSender(
        clients=clients,
        interval=heartbeat_config.get('interval', 60),
        heartbeat_hex=heartbeat_config.get('hex')
    )

    message_handler = MessageHandler(response_config=response_config, heartbeat_sender=heartbeat_sender)
    client_request_handler = ClientRequestHandler(None, message_handler)

    udp_server = UDPServer(
        host=server_config.get('host', '0.0.0.0'),
        port=server_config.get('port', 8081),
        message_handler=message_handler,
        client_request_handler=client_request_handler
    )

    await udp_server.start()
    heartbeat_sender.start()

    try:
        logger.info("UDP服务器正在运行...")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("停止服务器...")
        await udp_server.stop()
        heartbeat_sender.stop()

if __name__ == '__main__':
    asyncio.run(main())