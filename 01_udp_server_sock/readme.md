基础知识说明：
    socker -> 即sock
        sock 是一个 套接字（Socket）对象 - 用于在不同设备之间进行网络通信（比如本地脚本创建sock - 就可通过这个sock去传和接收某个服务）
            sock.sendto(data, address)
                sendto 方法可以将数据发送到指定的地址（IP 地址和端口）
            data, address = sock.recvfrom(buffer_size)
                recvfrom 方法可以接收来自任意设备的数据，并获取发送方的地址
    clients 是一个 集合（set），用于存储所有需要接收心跳包的客户端地址 -> 即想要传递的目标地址     


大致梳理当前场景：    
        sock 是服务端的套接字，用于发送和接收数据
        clients 是服务端维护的客户端地址集合，服务端通过 sock 向这些客户端发送心跳包
        当前应用场景中：
            （前提要客户端先下行过来，这样才会回给client）
            服务端通过 sock 向 clients 中的每个客户端发送心跳包，以检测客户端是否仍然在线
        疑问：
            那客户端也需要给服务端发送心跳包吗？
                客户端需要给服务端发送心跳包，以告知服务端它仍然在线。服务端通过接收客户端的心跳包来判断客户端是否仍然在线。
            当前fsu - 就是sock （clients -> 服务端需要维护的客户端地址集合）


logger.py
    功能：提供异步日志记录功能，避免日志操作阻塞主线程。
    核心：使用 aiologger，支持异步写入文件和控制台日志。
config_loader.py
    功能：异步加载 JSON 配置文件。
    核心：使用 aiofiles 异步读取文件内容并解析为 JSON。
utils.py
    功能：提供字节和十六进制的转换工具。
    核心：支持异步日志记录，记录转换过程。
heartbeat.py
    功能：定时发送心跳包。
    核心：使用 Tornado 的 PeriodicCallback 实现异步定时任务。
message_handler.py
    功能：解析客户端请求并生成响应消息。
    核心：支持异步消息处理，包括报文提取、命令码提取、消息校验和响应生成。
client_request_handler.py(引用message_hanlder的构造)
    功能：接收 UDP socket 和消息处理器对象，用于后续处理客户端请求
udp_server.py
    功能：UDP 服务器的具体实现逻辑，包括监听端口、接收数据、处理请求和发送响应
    核心：只负责 UDP 服务器的运行逻辑，不涉及配置加载、心跳包发送等其他功能
    扩展：需要扩展服务器功能（例如支持更多协议或更复杂的客户端管理），可以直接在这个类中添加方法或修改现有逻辑
udp_server.py
    功能：负责初始化和启动整个 UDP 服务器系统。它加载配置文件、初始化消息处理器、启动 UDP 服务器和心跳包发送器
    核心：主程序模块只负责初始化和启动流程，不涉及具体的业务逻辑
    扩展：增加新功能（如支持更多协议或更复杂的客户端管理），可以直接在 UDPServer 类中扩展，而不需要修改主程序逻辑


业务逻辑（重点）：
    读取配置
    建立udp（含处理逻辑类） -> 建立心跳机制（事件循环 -> 需要又）





udp说明：
    UDP 是无连接的 - 
        因此需要定期发送心跳包，检测对端是否仍然在线（一定时间内没有收到，则离线或出现故障）
        防止连接被防火墙或 NAT 设备关闭


版本：
    aiologger==0.6.0 
    aiofiles==23.1.0 
    tornado==6.3.3



框架代码解释：
    udp_server -> tornado.ioloop.IOLoop.current().start()
        tornado.ioloop.IOLoop:
            IOLoop 是 Tornado 中的事件循环类，它负责监听文件描述符（如套接字）和定时器事件，并调度回调函数来处理这些事件
            事件循环是异步编程的核心，它允许程序在单个线程中高效地处理多个并发任务
        IOLoop.current():
            返回当前线程中正在使用的 IOLoop 实例
            当前线程中没有正在使用的 IOLoop，它会创建一个新的实例并返回
            大多数情况下，你只需要一个全局的 IOLoop 实例，因此通常使用 IOLoop.current() 来获取它
        IOLoop.start():
            启动事件循环，开始监听和处理事件
            一旦调用 start()，事件循环会进入一个无限循环，等待事件发生并调度回调函数
            事件循环会一直运行，直到显式调用 IOLoop.stop() 方法
        事件循环的作用:
            监听文件描述符（如套接字）:事件循环会监听文件描述符（如 UDP 或 TCP 套接字）上的读写事件
            处理定时器事件:事件循环会管理定时器事件，例如周期性任务（PeriodicCallback）
            调度回调函数:事件循环会调度和执行各种回调函数，这些回调函数通常是由用户定义的异步任务
            举例：
                import tornado.ioloop
                import tornado.web
                
                class MainHandler(tornado.web.RequestHandler):
                    def get(self):
                        self.write("Hello, world")
                
                def make_app():
                    return tornado.web.Application([
                        (r"/", MainHandler),
                    ])
                
                if __name__ == "__main__":
                    app = make_app()
                    app.listen(8888)
                    print("Server is running on http://localhost:8888")
                    tornado.ioloop.IOLoop.current().start()        
                Tornado Web 应用程序，监听 HTTP 请求
                调用 app.listen(8888) 将应用绑定到端口 8888
                调用 tornado.ioloop.IOLoop.current().start() 启动事件循环，开始监听和处理 HTTP 请求
    本项目
        初始化 UDP 服务器和心跳包发送器
        调用 tornado.ioloop.IOLoop.current().start() 启动事件循环，开始监听 UDP 数据并处理心跳任务
        tornado.ioloop.IOLoop.current().start() 是启动 Tornado 事件循环的方法