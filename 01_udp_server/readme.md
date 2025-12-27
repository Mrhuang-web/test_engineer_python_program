utils.py（工具函数）
message_handler.py（类封装 - 负责消息的提取、命令码的解析、消息校验以及响应生成 - 通用的消息处理逻辑，适用于所有消息的处理）
ClientRequestHandler(专门用于处理客户端请求 - 处理来自客户端的请求，包括接收数据、调用消息处理逻辑、发送响应)
heartbeat.py（类封装）
udp_server.py（主程序）
config_loader.py（配置加载）


udp说明：
    UDP 是无连接的 - 
        因此需要定期发送心跳包，检测对端是否仍然在线（一定时间内没有收到，则离线或出现故障）
        防止连接被防火墙或 NAT 设备关闭
    