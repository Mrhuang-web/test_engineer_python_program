# data_generator.py
from logger import setup_logger
import random

logger = setup_logger('data_generator', 'logs/data_generator.log')

def generate_random_card_number(length=10):
    """
    生成随机的十进制授权卡号，长度不超过10位。
    """
    card_number = random.randint(1, 10**length - 1)
    return str(card_number).zfill(length)

def generate_protocol_message(card_number):
    """
    根据协议生成完整的报文。
    """
    start_byte = 0x7E  # 协议起始符
    group_address = 0x32  # 组内地址
    address = 0x01  # 地址
    end_byte = 0x0D  # 协议终止符

    # 将授权卡号转换为十六进制字符串
    hex_card_number = hex(int(card_number))[2:].upper().zfill(10)  # 十六进制，10位以内

    # 构造完整的报文
    message = bytes([start_byte, group_address, address]) + bytes.fromhex(hex_card_number) + bytes([end_byte])
    logger.debug(f"生成的报文: {message.hex().upper()}")
    return message