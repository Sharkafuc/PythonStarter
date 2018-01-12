#coding=utf-8

import os
import sys
from enum import Enum
import time

#服务器的ip,端口,最大监听数
HOST = '127.0.0.1'
PORT = 54131
MaxConnect = 512

#客户端服务器传递消息的大小
ReadBufferSize = 1024

#游戏抢答时间
Game21rushAnswerTime = 15
#游戏出题时间
Game21timeSpan = 60

#客户端在服务器上的状态枚举
class TaskState(Enum):
    unlogin = 0
    loginName = 1
    loginPwd = 2
    lobby = 3
    signName = 4
    signPwd1 = 5
    signPwd2 = 6

#玩家登录之前是连接
class SocketAgent:
    def __init__(self,sock,addr):
        self.sock = sock
        self.addr = str(addr)
        self.task = TaskState.unlogin
        self.name = ''
        self.pwd = ''

#玩家
class Player:
    def __init__(self,name,pwd,t,sock):
        self.sock = sock
        self.time = t
        self.name = name
        self.pwd = pwd
        self.logintime = time.time()
        self.roomid = 0
    def sendMsg(self,msg):
        self.sock.sendall(msg.encode('utf-8'))

#房间
class Room:
    def __init__(self,name,id):
        self.name = name
        self.id = id
        self.players = []
        self.questionNums = []
        self.host = None
        self.winner = ''
        self.answers = {}
    def sendMsg(self,msg):
        for player in self.players:
            player.sendMsg(msg)

    def oneSendMsg(self,msg):
        pass

    def removePlayer(self,name):
        for player in self.players:
            if player.name == name:
                if self.id != 0:
                    player.roomid = 0
                    player.sendMsg("您已离开"+str(self.id)+"号房间,"+self.name)
                self.players.remove(player)
        if self.id != 0:
            self.sendMsg("玩家 "+name+" 已离开本房间")
    def addPlayer(self,newPlayer):
        newPlayer.roomid = self.id
        if self.id != 0:
            self.sendMsg("玩家 "+newPlayer.name+" 加入本房间")
            newPlayer.sendMsg("您已加入"+str(self.id)+"号房间,"+self.name)
        self.players.append(newPlayer)


