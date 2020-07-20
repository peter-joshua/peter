#!/usr/bin/python3

from select import *
from socket import *
class WebServer_v1:
    def __init__(self,HOST='0.0.0.0',PORT=8888,path_target=None):
        self.host=HOST
        self.port=PORT
        self.html=None
        self.path_target=path_target
        self.webserver_sock=socket()
        self.__map={self.webserver_sock.fileno():self.webserver_sock}
    def create_socket(self):
        '''
        创建服务端套接字
        :return:
        '''
        self.webserver_sock.bind((self.host,self.port))#绑定服务端IP
        self.webserver_sock.listen(5)#建立监听
        self.webserver_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)#设置IP地址重用
        #建立IO监控
        self.p=epoll()
        self.p.register(self.webserver_sock,EPOLLIN)#关注服务端套接字的写事件
        events=self.p.poll()
        while True:
            for sock,event in events:
                if self.webserver_sock.fileno()==sock:
                    # self.p.register(self.webserver_sock,EPOLLIN)
                    connfd,addr=self.webserver_sock.accept()#服务端接收请求
                    self.register_(connfd)
                    self.html='HTTP/1.1 200 OK\r\n'
                    self.html+='Conternt-Type:test/html\r\n'
                    self.html+='\r\n'
                    data=self.html
                    self.open_file(self.path_target,connfd,data)
                    self.register_(connfd)#将客户端IO读事件注册到系统监控事件中
    def register_(self,sock):
        self.p.register(sock)
        self.__map[sock.fileno()]=sock
    def open_file(self,path,sock,html):
        reponse=html.encode()
        try:
            with open(path,'rb') as f:
                data=f.read()
                reponse+=data
            f.close()
        except:
            reponse='''HTTP/1.1 404 Not Found\r\n
            Content-Type:text/html\r\n
            
            <h1>网页出错啦！</h1>
            '''
        finally:
            sock.send(reponse)
            self.p.unregister(sock)
            del self.__map[sock.fileno()]


    def register_(self,sock):
        self.p.register(sock,EPOLLIN)
        self.__map[sock.fileno()]=sock



if __name__ == '__main__':
    web=WebServer_v1(path_target='/home/peter/index.html')
    web.create_socket()
