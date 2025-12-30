模块描述
    client_config_loader.py
        功能：加载客户端配置文件（如服务器地址、端口、发送间隔等）。
        作用：提供配置管理功能，确保客户端可以根据配置文件动态调整行为，无需修改代码。
    data_generator.py
        功能：生成随机字节数据，用于模拟客户端发送的数据。
        作用：为客户端提供数据生成逻辑，支持灵活的数据格式和长度调整。
    udp_client_core.py
        功能：实现 UDP 客户端的核心功能，包括发送数据和接收服务器响应。
        作用：封装了与服务器通信的核心逻辑，便于复用和扩展。
    udp_client_runner.py
        功能：控制客户端的运行逻辑，如循环发送数据和处理异常。
        作用：管理客户端的运行流程，确保数据能够按照配置的间隔持续发送。 
    main.py
        功能：作为客户端的主入口，加载配置并启动客户端。
        作用：提供程序的启动点，协调各模块的功能，确保客户端能够正确运行。 
    logger.py
        功能：设置和管理日志记录功能。
        作用：为所有模块提供统一的日志记录机制，便于调试和监控。
    client_config.json  --> 配置文件
        功能：存储客户端的配置信息，如服务器地址、端口和发送间隔。
        作用：以文件形式存储配置，便于修改和维护，无需修改代码即可调整客户端行为。


逻辑走向：
    main.py -> client_config_loader.py -> udp_client_runner.py -> udp_client_core.py -> data_generator.py
    启动程序：
        用户运行 main.py。
    加载配置：
        main.py 调用 client_config_loader.py 加载配置文件。
    初始化客户端：
        main.py 根据配置信息调用 udp_client_runner.py 启动客户端。
    运行客户端：
        udp_client_runner.py 创建 UDPClient 实例。
    在循环中：
        调用 data_generator.py 生成数据。
        调用 UDPClient 的 send_data 方法发送数据并接收响应。
        按配置的间隔等待。
    停止客户端：
        用户通过 Ctrl+C 停止程序。
        udp_client_runner.py 调用 UDPClient 的 close 方法关闭套接字。
    日志记录：
        每个模块通过 logger.py 记录运行过程中的信息、警告和错误。