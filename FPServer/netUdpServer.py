#coding=utf-8

import socket
import select
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

host,port = "127.0.0.1",25001
udpBufferSize = 1024

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((host,port))

while True:
    conn_list = [sock]
    rlist, wlist, elist = select.select(conn_list, [], [])
    for fd in rlist:
        if fd == sock:
            data,addr = fd.recvfrom(udpBufferSize)
            print u'服务器收到消息：',data
            #判断data要如何处理，再返回处理的消息
            fd.sendto(data,addr)




