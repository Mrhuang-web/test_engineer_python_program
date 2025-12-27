# tornado_server.py
import os
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import logging
from udp_server import clients, last_request, initialize_udp_server
from logger import setup_logger

logger = setup_logger('tornado_server', 'logs/tornado_server.log')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logger.info("WebSocket连接已打开")
        self.write_message("连接成功！")

    def on_message(self, message):
        try:
            data = json.loads(message)
            if data.get("type") == "get_status":
                status = {
                    "clients": list(clients),  # 当前连接的客户端
                    "last_request": last_request,  # 最近一次请求的信息
                }
                self.write_message(json.dumps({"type": "status", "data": status}))
            elif data.get("type") == "get_logs":
                logs = read_logs()
                self.write_message(json.dumps({"type": "logs", "data": logs}))
        except Exception as e:
            logger.error(f"处理 WebSocket 消息时出错: {e}")
            self.write_message(json.dumps({"type": "error", "message": "处理请求时出错"}))

    def on_close(self):
        logger.info("WebSocket连接已关闭")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

def read_logs():
    try:
        with open("logs/udp_server.log", "r") as f:
            return f.readlines()[-10:]  # 返回最后 10 行日志
    except Exception as e:
        logger.error(f"读取日志文件失败: {e}")
        return []

def make_app():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(root_dir, "templates")
    static_path = os.path.join(root_dir, "static")

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", WebSocketHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
    ], template_path=template_path)

if __name__ == "__main__":
    initialize_udp_server()  # 初始化 UDP 服务器
    app = make_app()
    app.listen(8888)
    logger.info("Tornado服务器已启动，监听端口 8888")
    tornado.ioloop.IOLoop.current().start()