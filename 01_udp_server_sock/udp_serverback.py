#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP服务器
接收UDP客户端请求，响应默认字符串的16进制码流
"""

import socket
import argparse
import sys
import threading
import time
import json
import os
from pathlib import Path


def bytes_to_hex(byte_data):
    """将字节数据转换为16进制字符串"""
    return byte_data.hex().upper()


def string_to_hex_bytes(text):
    """将字符串转换为16进制字节流"""
    return text.encode('utf-8').hex().upper()


def extract_messages(data, start_byte=0x7e, end_byte=0x0d):
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
        # 查找起始字节 0x7e
        if data_bytes[i] == start_byte:
            # 从起始位置开始查找结尾字节 0x0d
            for j in range(i + 1, len(data_bytes)):
                if data_bytes[j] == end_byte:
                    # 提取报文（包含起始和结尾字节）
                    message = data_bytes[i:j + 1]
                    messages.append(message)
                    # 继续从下一个位置查找
                    i = j + 1
                    break
            else:
                # 没有找到结尾字节，跳过这个起始字节
                i += 1
        else:
            i += 1
    
    return messages


def extract_command_code(data, start_offset=12, length=4):
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
        # 确保数据是bytes类型
        data_bytes = bytes(data)
        
        # 检查是否以7e开头
        if len(data_bytes) == 0 or data_bytes[0] != 0x7e:
            return None
        
        # 计算实际位置（跳过7e起始字节，所以+1）
        actual_start = start_offset + 1
        actual_end = actual_start + length
        
        # 检查边界
        if actual_end > len(data_bytes):
            return None
        
        # 提取指定位置的字节
        extracted_bytes = data_bytes[actual_start:actual_end]
        
        # 转换为16进制字符串（大写）
        hex_string = bytes_to_hex(extracted_bytes)
        
        return hex_string
    except Exception as e:
        print(f"提取命令码时出错: {e}")
        return None


def validate_message(data, response_config=None):
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
    # 加载响应配置
    if response_config is None:
        response_config = {}
    
    # 打印可用的响应消息类型
    available_responses = list(response_config.keys())
    if available_responses:
        print(f"可用响应消息类型: {', '.join(available_responses)}")
    
    # 提取命令码（46304530位置，跳过7e后从第12字节开始，长度4字节）
    command_code = extract_command_code(data, start_offset=12, length=4)
    
    if command_code:
        print(f"提取到的命令码: {command_code}")
        if command_code == "46324535":
            response_msg = response_config.get('user_code_message')
        elif command_code == "46324532":
            response_msg = response_config.get('device_event_message')
        elif command_code == "46324537":
            response_msg = response_config.get('door_status_message')
        else:
            response_msg = response_config.get('default_message')
        
        # 检查响应消息是否存在
        if not response_msg:
            print(f"警告: 命令码 {command_code} 对应的响应消息不存在，使用默认消息")
            response_msg = response_config.get('default_message')
            if not response_msg:
                print("错误: 默认响应消息也不存在")
                return None
    else:
        print("无法提取命令码，报文格式可能不正确")
        return None
    
    return response_msg


def generate_response(data):
    """
    生成响应消息函数
    在此处添加您的响应消息生成逻辑
    
    Args:
        data: 接收到的字节数据
        
    Returns:
        bytes: 响应消息的字节流
    """
    # TODO: 在此处添加响应消息生成逻辑
    # 例如：根据接收到的消息内容生成不同的响应
    # 默认返回None，将使用default_message
    return None


def load_config(config_path='config.json'):
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径（相对路径或绝对路径）
        
    Returns:
        dict: 配置字典
    """
    # 如果是相对路径，则相对于脚本所在目录
    if not os.path.isabs(config_path):
        script_dir = Path(__file__).parent
        config_path = script_dir / config_path
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def heartbeat_sender(sock, clients, heartbeat_interval=60, heartbeat_hex=None):
    """
    心跳包发送线程
    定期向所有已连接的客户端发送心跳包
    
    Args:
        sock: UDP socket对象
        clients: 客户端地址集合（线程安全的集合）
        heartbeat_interval: 心跳包发送间隔（秒），默认60秒
        heartbeat_hex: 心跳包16进制码流
    """
    # 心跳包16进制码流
    if heartbeat_hex is None:
        heartbeat_hex = "ff0000000000000000303332303235303330323030313700000000000001020300ed0200eefe"
    heartbeat_bytes = bytes.fromhex(heartbeat_hex)
    
    print(f"心跳包发送线程已启动，间隔: {heartbeat_interval}秒")
    print(f"心跳包16进制码流: {heartbeat_hex}")
    
    while True:
        try:
            time.sleep(heartbeat_interval)
            
            # 复制客户端列表以避免在迭代时修改
            clients_copy = list(clients)
            
            if clients_copy:
                print(f"\n发送心跳包到 {len(clients_copy)} 个客户端...")
                for addr in clients_copy:
                    try:
                        sock.sendto(heartbeat_bytes, addr)
                        print(f"  心跳包已发送到 {addr[0]}:{addr[1]}")
                    except Exception as e:
                        print(f"  发送心跳包到 {addr[0]}:{addr[1]} 失败: {e}")
                        # 如果发送失败，从客户端列表中移除
                        clients.discard(addr)
            else:
                print("没有已连接的客户端，跳过心跳包发送")
                
        except Exception as e:
            print(f"心跳包发送线程错误: {e}", file=sys.stderr)
            time.sleep(heartbeat_interval)


def main():
    parser = argparse.ArgumentParser(description='UDP服务器 - 接收请求并响应16进制码流')
    parser.add_argument('-c', '--config', type=str, default='config.json',
                        help='配置文件路径（默认为: config.json）')
    
    args = parser.parse_args()
    
    # 加载配置文件
    try:
        config = load_config(args.config)
        print(f"已加载配置文件: {args.config}")
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 从配置文件读取配置
    server_config = config.get('server', {})
    heartbeat_config = config.get('heartbeat', {})
    response_config = config.get('response', {})
    
    port = server_config.get('port', 8080)
    host = server_config.get('host', '0.0.0.0')
    heartbeat_interval = heartbeat_config.get('interval', 60)
    heartbeat_hex = heartbeat_config.get('hex', 'ff0000000000000000303332303235303330323030313700000000000001020300ed0200eefe')
    default_message = response_config.get('default_message', 'Hello UDP Client')
    
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 客户端地址集合（使用线程安全的集合）
    clients = set()
    clients_lock = threading.Lock()
    
    try:
        # 绑定到指定端口
        sock.bind((host, port))
        print(f"UDP服务器已启动，监听地址: {host}:{port}")
        print(f"默认响应消息: {default_message}")
        print(f"响应16进制码流: {string_to_hex_bytes(default_message)}")
        print(f"心跳包间隔: {heartbeat_interval}秒")
        print("等待UDP客户端连接...")
        print("-" * 50)
        
        # 启动心跳包发送线程
        heartbeat_thread = threading.Thread(
            target=heartbeat_sender,
            args=(sock, clients, heartbeat_interval, heartbeat_hex),
            daemon=True
        )
        heartbeat_thread.start()
        
        while True:
            # 接收数据
            data, addr = sock.recvfrom(1024)
            
            # 打印接收到的信息
            print(f"\n收到来自 {addr[0]}:{addr[1]} 的请求")
            print(f"接收到的数据 (原始): {data}")
            print(f"接收到的数据 (16进制): {bytes_to_hex(data)}")
            
            # ========== 提取7e起始0d结尾的报文 ==========
            extracted_messages = extract_messages(data, start_byte=0x7e, end_byte=0x0d)
            if extracted_messages:
                print(f"\n提取到 {len(extracted_messages)} 个报文 (7e起始0d结尾):")
                for idx, msg in enumerate(extracted_messages, 1):
                    print(f"  报文 {idx}:")
                    print(f"    原始数据: {msg}")
                    print(f"    16进制: {bytes_to_hex(msg)}")
                    print(f"    长度: {len(msg)} 字节")
            else:
                print("未找到7e起始0d结尾的报文")
            
            # 将客户端地址添加到集合中（用于心跳包发送）
            with clients_lock:
                clients.add(addr)
                print(f"当前已连接客户端数量: {len(clients)}")
            
            # ========== 消息校验和响应消息获取 ==========
            # 使用提取后的报文进行校验（如果有的话），否则使用原始数据
            message_to_validate = extracted_messages[0] if extracted_messages else data
            response_msg = validate_message(message_to_validate, response_config)
            
            if response_msg is None:
                print("消息校验失败，忽略此请求")
                print("-" * 50)
                continue
            
            print("消息校验通过")
            print(f"选择的响应消息类型: {response_msg[:50]}..." if len(response_msg) > 50 else f"选择的响应消息: {response_msg}")
            
            # ========== 生成响应消息 ==========
            # 优先使用validate_message返回的响应消息
            if response_msg:
                # 将响应消息（16进制字符串）转换为字节流
                try:
                    response_bytes = bytes.fromhex(response_msg.replace(' ', ''))
                    response_hex = bytes_to_hex(response_bytes)
                    response_message = f"配置响应消息 (16进制: {response_hex[:50]}...)" if len(response_hex) > 50 else f"配置响应消息 (16进制: {response_hex})"
                except ValueError as e:
                    print(f"响应消息格式错误: {e}")
                    # 如果格式错误，尝试使用generate_response函数
                    response_bytes = generate_response(data)
                    if response_bytes is None:
                        # 使用默认消息
                        response_hex = string_to_hex_bytes(default_message)
                        response_bytes = bytes.fromhex(response_hex)
                        response_message = default_message
                    else:
                        response_hex = bytes_to_hex(response_bytes)
                        response_message = f"自定义响应 (16进制: {response_hex})"
            else:
                # 如果没有响应消息，尝试使用generate_response函数
                response_bytes = generate_response(data)
                if response_bytes is None:
                    # 使用默认消息
                    response_hex = string_to_hex_bytes(default_message)
                    response_bytes = bytes.fromhex(response_hex)
                    response_message = default_message
                else:
                    response_hex = bytes_to_hex(response_bytes)
                    response_message = f"自定义响应 (16进制: {response_hex})"
            
            # 发送响应
            sock.sendto(response_bytes, addr)
            print(f"已发送响应: {response_message}")
            print(f"响应16进制码流: {response_hex}")
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\n\n服务器正在关闭...")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        sock.close()
        print("UDP服务器已关闭")


if __name__ == '__main__':
    main()

