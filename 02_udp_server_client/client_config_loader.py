from logger import setup_logger
from pathlib import Path
import json

logger = setup_logger('client_config_loader', 'logs/client_config_loader.log')

def load_client_config(config_path):
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = Path(__file__).parent / config_path

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"客户端配置文件加载成功: {config_path}")
            return config
    except FileNotFoundError as e:
        logger.error(f"错误: 配置文件未找到 - {e}")
    except json.JSONDecodeError as e:
        logger.error(f"错误: 配置文件格式错误 - {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
    return None