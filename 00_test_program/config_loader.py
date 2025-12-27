# config_loader.py
import json
from pathlib import Path
from logger import setup_logger

logger = setup_logger('config_loader', 'logs/config_loader.log')

class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            # 如果是相对路径，相对于当前文件的目录
            self.config_path = Path(__file__).parent / self.config_path
        logger.info(f"配置文件路径初始化为: {self.config_path}")

    def load(self):
        try:
            if self.config_path.suffix == ".json":
                return self._load_json()
            else:
                logger.error(f"不支持的配置文件格式: {self.config_path.suffix}")
                return None
        except FileNotFoundError as e:
            logger.error(f"错误: 配置文件未找到 - {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"错误: 配置文件格式错误 - {e}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None

    def _load_json(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info("配置文件加载成功")
            return data