# message_handler.py
from logger import setup_logger
from utils import bytes_to_hex




class MessageHandler:
    logger = setup_logger('message_handler', 'logs/message_handler.log')

    def __init__(self, response_config=None, heartbeat_sender=None):
        self.response_config = response_config or {}
        self.heartbeat_sender = heartbeat_sender
        self.logger.info("消息处理器初始化完成")

    def extract_messages(self, data, start_byte=0x7e, end_byte=0x0d):
        messages = []
        data_bytes = bytes(data)
        i = 0
        while i < len(data_bytes):
            if data_bytes[i] == start_byte:
                for j in range(i + 1, len(data_bytes)):
                    if data_bytes[j] == end_byte:
                        message = data_bytes[i:j + 1]
                        messages.append(message)
                        self.logger.debug(f"提取到报文: {bytes_to_hex(message)}")
                        i = j + 1
                        break
                else:
                    i += 1
            else:
                i += 1
        self.logger.info(f"共提取到 {len(messages)} 条报文")
        return messages

    def extract_command_code(self, data, start_offset=12, length=4):
        try:
            data_bytes = bytes(data)
            if len(data_bytes) == 0 or data_bytes[0] != 0x7e:
                self.logger.warning("无法提取命令码，报文格式可能不正确")
                return None
            actual_start = start_offset + 1
            actual_end = actual_start + length
            if actual_end > len(data_bytes):
                self.logger.warning("提取命令码时超出数据范围")
                return None
            extracted_bytes = data_bytes[actual_start:actual_end]
            command_code = bytes_to_hex(extracted_bytes)
            self.logger.info(f"提取到的命令码: {command_code}")
            return command_code
        except Exception as e:
            self.logger.error(f"提取命令码时出错: {e}")
            return None

    def validate_message(self, data):
        command_code = self.extract_command_code(data)
        if not command_code:
            self.logger.warning("无法提取命令码，报文格式可能不正确")
            return None
        response_msg = self.response_config.get(command_code)
        if not response_msg:
            self.logger.warning(f"警告: 命令码 {command_code} 对应的响应消息不存在，使用默认消息")
            response_msg = self.response_config.get('default_message')
            if not response_msg:
                self.logger.error("错误: 默认响应消息也不存在")
                return None
        return response_msg

    async def generate_response(self, data):
        response_msg = self.validate_message(data)
        if response_msg:
            self.logger.info("生成响应消息成功")
            return bytes.fromhex(response_msg)
        else:
            self.logger.warning("生成响应消息失败")
            return None