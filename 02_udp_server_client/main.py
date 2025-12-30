# main.py
from client_config_loader import load_client_config
from udp_client_runner import run_client
from logger import setup_logger

logger = setup_logger('main', 'logs/main.log')


def main():
    # 加载客户端配置
    config = load_client_config("client_config.json")
    if not config:
        logger.error("配置文件加载失败，程序退出")
        return

    server_host = config.get("server", {}).get("host", "127.0.0.1")
    server_port = config.get("server", {}).get("port", 8081)  # 端口号修改为 18080
    interval = config.get("interval", 2)

    logger.info(f"启动UDP客户端，目标服务器: {server_host}:{server_port}, 发送间隔: {interval}秒")
    run_client(server_host, server_port, interval)


if __name__ == "__main__":
    main()
