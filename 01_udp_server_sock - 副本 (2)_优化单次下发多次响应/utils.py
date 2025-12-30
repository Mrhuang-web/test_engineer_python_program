# utils.py
from logger import setup_logger

logger = setup_logger('utils', 'logs/utils.log')

async def bytes_to_hex(byte_data):
    """
    将字节数据转换为16进制字符串。
    """
    hex_string = byte_data.hex().upper()
    logger.debug(f"字节数据转换为16进制字符串: {hex_string}")
    return hex_string

async def string_to_hex_bytes(text):
    """
    将字符串转换为16进制字节流。
    """
    hex_bytes = text.encode('utf-8').hex().upper()
    logger.debug(f"字符串转换为16进制字节流: {hex_bytes}")
    return hex_bytes