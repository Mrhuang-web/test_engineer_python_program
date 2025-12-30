# message_handler.py
from logger import setup_logger
from utils import bytes_to_hex


<<<<<<< HEAD


=======
>>>>>>> f8126fd90caacb3ab48d3cd52149f2be24dd7a3a
class MessageHandler:
    logger = setup_logger('message_handler', 'logs/message_handler.log')

    def __init__(self, response_config=None, heartbeat_sender=None):
        self.response_config = response_config or {}
        self.heartbeat_sender = heartbeat_sender
        self.logger.info("消息处理器初始化完成")

    def extract_messages(self, data, start_byte=0x7e, end_byte=0x0d):
        """
        从接收到的数据中提取以指定字节起始和结尾的报文
        Args:
            data: 接收到的字节数据
            start_byte: 起始字节，默认0x7e
            end_byte: 结尾字节，默认0x0d

        Returns:
            list: 提取到的报文列表，每个元素是一个bytes对象
        """
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
        """
        从报文中提取命令码
        从示例报文 7e3130303138303438323030454630453030303030303030303030464143380d 来看
        46304530 位于字节位置13（包含7e），跳过7e后是位置12（从0开始计数）

        Args:
            data: 接收到的字节数据
            start_offset: 起始偏移量（字节位置，从0开始，不包括7e起始字节）
            length: 要提取的长度（字节数）

        Returns:
            str: 提取的16进制字符串，如果位置超出范围返回None
        """
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
        """
        消息校验函数
        在此处添加您的消息校验逻辑
        示例报文: 7e3130303138303438323030454630453030303030303030303030464143380d
        需要提取46304530位置的字符串来判断请求类型

        Args:
            data: 接收到的字节数据 7e开头 0d结尾 这里需要校验是什么请求以达到不同响应的分发
            response_config: 响应配置字典，包含各种响应消息

        Returns:
            str or None: 校验通过返回响应消息字符串，校验失败返回None
        """
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

<<<<<<< HEAD
    async def generate_response(self, data):
=======
    def generate_response(self, data):
        """
        生成响应消息函数
        Args:
            data: 接收到的字节数据
        Returns:
            bytes: 响应消息的字节流
        """
        # TODO: 在此处添加响应消息生成逻辑
        # 例如：根据接收到的消息内容生成不同的响应
        # 默认返回None，将使用default_message
>>>>>>> f8126fd90caacb3ab48d3cd52149f2be24dd7a3a
        response_msg = self.validate_message(data)
        if response_msg:
            self.logger.info("生成响应消息成功")
            return bytes.fromhex(response_msg)
        else:
            self.logger.warning("生成响应消息失败")
            return None
