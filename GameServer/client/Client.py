#coding=utf-8

from DataStructs import *
import socket
import threading
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import os

class Client:
    def __init__(self,host=HOST, port=PORT):
        # client类的成员 客户端socket:clientSock,客户端读写正常标志:RightSocket

        # 客户端读写正常标志
        self.RightSocket = True
        # 客户端socket
        self.clientSock = None
        try:
            self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSock.connect((HOST,PORT))
            print "客户端就绪连接服务端"
        except Exception as e:
            print e.message
            if self.clientSock:
                self.clientSock.close()
                self.clientSock = None
            print "客户端socket出错"
            sys.exit(1)
        print "客户端连接成功"
        try:
            # 连接成功后服务器会发送引导语
            guideline = self.clientSock.recv(ReadBufferSize)
            print guideline.decode('utf-8')
        except Exception as e:
            print e.message
            print "客户端读引导语错误"
            if not self.clientSock:
                sys.exit(1)

    # 客户端读线程,负责接收服务器的消息
    def clientRead(self,sock,addr):
        while True:
            try:
                readData = self.clientSock.recv(ReadBufferSize)
                if readData:
                    print readData.decode('utf-8')
                else:
                    raise Exception
            except Exception as e:
                print e.message
                print "已断开与服务器的连接"
                self.RightSocket = False
                break
        self.destruct()

    # 客户端写线程,负责发送玩家的请求
    def clientWrite(self,sock,addr):
        while True:
            try:
                inpstr = raw_input()

                if inpstr == 'clear':
                    os.system('clear')
                    continue

                sock.sendall(inpstr.encode('utf-8'))
            except Exception as e:
                print e.message
                print "客户端写错误"
                self.RightSocket = False
                break
        self.destruct()

    def run(self):

        #客户端跑读写两个线程
        tR = threading.Thread(target=self.clientRead, args=(self.clientSock, HOST))
        tR.start()

        tW = threading.Thread(target=self.clientWrite, args=(self.clientSock, HOST))
        tW.start()

    def destruct(self):
        #读写线程任意一个发生异常就断开与服务器的连接
        if self.clientSock:
            self.clientSock.close()
        print "关闭客户端"
        os._exit(0)

if __name__ == "__main__":
    client = Client()
    client.run()