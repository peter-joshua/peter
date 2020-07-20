#!/usr/bin/python3

from socket import *
from select import *
import re

class WebServer:
    def __init__(self, html=None,host=None,port=None):
        self.webserver_socket = socket()
        self.host=host
        self.port=port
        self.html = html
        # 为IO多路复用并发做准备
        self.__p=poll()
        self.__p.register(self.webserver_socket,EPOLLIN)
        self.__map={self.webserver_socket.fileno():self.webserver_socket}

    def create_socket(self):
        self.webserver_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.webserver_socket.bind((self.host,self.port))

    def start(self):
        while True:
            self.webserver_socket.listen(5)
            self.webserver_socket.setblocking(False)
            events = self.__p.poll()
            for sock, event in events:
                if self.webserver_socket.fileno() == sock:
                    connfd, addr = self.webserver_socket.accept()
                    self.__p.register(connfd, EPOLLIN)
                    self.__map[connfd.fileno()] = connfd
                elif event == EPOLLIN:#写法2 event & EPOLLIN &---过滤作用：如果包含EPOLLIN则执行以下操作
                    data = self.__map[sock].recv(1024)
                    pattern = '[A-Z]+\s+(?P<info>/\S*)'
                    result = re.match(pattern, data.decode())  # 提取请求头
                    if result:
                        info = result.group('info')
                        self.do_reponse(self.__map[sock], info)
                    else:
                        # 没有获取到请求头，断开客户端连接
                        self.__map[sock].close()
                        self.__p.unregister(sock)
                        del self.__map[sock]
    def do_reponse(self,sock,info):
        print(info)
        #处理客户端请求
        if info=='/':
            filename=self.html+'/index.html'
            print(filename)
        else:
            filename=self.html+info
            print(filename)
        try:
            f=open(filename,'rb')
        except:
            reponse = '''HTTP/1.1 404 Not Found
            Content-Type:text/html

            <h1>网页出错啦！</h1>'''
            reponse=reponse.encode(encoding="GBK")
            sock.send(reponse)
            self.__p.unregister(sock)
            del self.__map[sock.fileno()]
        else:
            data=f.read()
            reponse="HTTP/1.1 200 OK\r\n"
            reponse+="Content-Type:text/html\r\n"
            reponse+="\r\n"
            reponse=reponse.encode()+data
            sock.send(reponse)
            self.__p.unregister(sock)
            del self.__map[sock.fileno()]



def main():
    s1 = WebServer(html='/home/peter',host='0.0.0.0', port=8888)
    s1.create_socket()
    s1.start()


if __name__ == '__main__':
    main()
