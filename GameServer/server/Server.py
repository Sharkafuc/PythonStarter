#coding=utf-8

from DataStructs import *
import socket
import select
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import json
import time
import random

#origindata = {"netease1":{"pwd":"123","time":0.0},"netease2":{"pwd":"123","time":0.0},"netease3":{"pwd":"123","time":0.0},"netease4":{"pwd":"123","time":0.0}}

class Server:
    def __init__(self,host=HOST, port=PORT):
        # server类的成员 服务器socket:serverSock,所有连接的socks字典:allConnectSocks({sock:SockAgent})
        # select读列表:input_list,简之,读完命令直接解析,直接处理返回,没通过消息队列和select写列表
        # 所有在线玩家字典:online_players({name:player}),所有在线房间列表:online_rooms(大厅是第1个房间,[0] = Room("lobby",0)),
        # 存在本地的操作指令Msg
        # 注册玩家的账号密码时间字典 playersDict({"name":{pwd,time}})
        # 游戏发题的时间 questionime
        # 是否在游戏的抢答时间里 Competing

        # 服务器socket
        self.serverSock = None
        try:
            self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSock.bind((host,port))
            self.serverSock.listen(MaxConnect)
            self.serverSock.setblocking(False)
            print "服务端就绪等待连接"
        except Exception as e:
            print e.message
            if self.serverSock:
                self.serverSock.close()
                self.serverSock = None
            print "服务器socket出错"
            sys.exit(1)

        # 所有连接的socks
        self.allConnectSocks = {}
        self.allConnectSocks[self.serverSock] = SocketAgent(self.serverSock,HOST)

        # select读列表
        self.input_list = []
        self.input_list.append(self.serverSock)

        # 所有在线玩家字典
        self.online_players = {}
        # 所有在线房间字典
        self.online_rooms = []
        self.online_rooms.append(Room("lobby",0))
        #初始化大厅为房间第一个字典元素,不需要初始化其他房间

        #其他初始化的操作
        #如本地信息helpMsg等的读取
        self.getMsg()
        self.playersDict = {}
        self.loadPlayersData()
        #print self.playersDict
        self.questionTime = 0.0
        self.Competing = False

    def loadPlayersData(self):
        # 读取玩家信息的存档
        # with open("players.data","w") as f:
        #     f.write(json.dumps(origindata))

        with open("players.data","r") as f:
            try:
                jsonstr = f.read()
                self.playersDict = json.loads(jsonstr)
            except Exception as e:
                print "读取注册用户数据出错"

    def getMsg(self):
        # 本地信息如helpMsg等的读取
        with open('Msg.txt','r') as f:
            msg = f.read().split('......')
        self.helpMsg =  msg[0]
        self.guideMsg = msg[1]
        self.rqirName = msg[2]
        self.rqirPwd = msg[3]
        self.rqirPwd2 = msg[4]
        self.nameNotExistRqir = msg[5]
        self.nameExistRqir = msg[6]
        self.pwdWrong = msg[7]
        self.helpstr = msg[8]
        self.notInroom = msg[9]
        self.roomNotInRange = msg[10]
        self.illegalExpr = msg[11]

    def dealWithStr(self,RecvSock,RecvStr):
        # 对客户端请求的处理
        print "Receive the message from %s: %s" % (self.allConnectSocks[RecvSock].addr,RecvStr)
        # print RecvStr in self.playersDict
        # 断开连接
        if RecvStr == 'quit':
            print '客户端请求离开,切断来自 %s 的连接' % (self.allConnectSocks[RecvSock].addr)
            self.disConnectSock(RecvSock)

        SA = self.allConnectSocks[RecvSock]

        # 客户端还未登录的请求处理
        if SA.task == TaskState.unlogin:
            if RecvStr == 'login':
                RecvSock.sendall(self.rqirName.encode('utf-8'))
                SA.task = TaskState.loginName
                return
            elif RecvStr == 'signup':
                RecvSock.sendall(self.rqirName.encode('utf-8'))
                SA.task = TaskState.signName
                return
            else:
                RecvSock.sendall(self.guideMsg.encode('utf-8'))
                return

        # 客户端需要注册的请求
        elif SA.task == TaskState.signName:
            if RecvStr in self.playersDict:
                RecvSock.sendall(self.nameExistRqir.encode('utf-8'))
                return
            else:
                if len(RecvStr) > 0 and ord(RecvStr[0]) > 32 and ord(RecvStr[0]) < 127:
                    RecvSock.sendall(self.rqirPwd.encode('utf-8'))
                    SA.task = TaskState.signPwd1
                    SA.name = RecvStr
                    return
                else:
                    RecvSock.sendall(self.rqirName.encode('utf-8'))
                    return
        elif SA.task == TaskState.signPwd1:
            if len(RecvStr) > 0 and ord(RecvStr[0]) > 32 and ord(RecvStr[0]) < 127:
                RecvSock.sendall(self.rqirPwd2.encode('utf-8'))
                SA.task = TaskState.signPwd2
                SA.pwd = RecvStr
                return
            else:
                RecvSock.sendall(self.pwdWrong.encode('utf-8'))
                SA.name = ''
                SA.task = TaskState.unlogin
                RecvSock.sendall(self.guideMsg.encode('utf-8'))
                return
        elif SA.task == TaskState.signPwd2:
            if RecvStr == SA.pwd:
                RecvSock.sendall(('注册成功,Hi! '+SA.name+' 欢迎登录大厅\nhelp: 查看帮助文档\n').encode('utf-8'))
                SA.task = TaskState.lobby
                self.online_players[SA.name] = Player(SA.name,SA.pwd,0,SA.sock)
                self.playersDict[SA.name] = {"pwd":SA.pwd,"time":0}
                self.online_rooms[0].addPlayer(self.online_players[SA.name])
                return
            else:
                RecvSock.sendall(self.pwdWrong.encode('utf-8'))
                SA.name = ''
                SA.pwd = ''
                SA.task = TaskState.unlogin
                RecvSock.sendall(self.guideMsg.encode('utf-8'))
                return

        # 客户端需要登录的请求
        elif SA.task == TaskState.loginName:
            if RecvStr in self.playersDict:
                RecvSock.sendall(self.rqirPwd.encode('utf-8'))
                SA.task = TaskState.loginPwd
                SA.name = RecvStr
                return
            else:
                RecvSock.sendall(self.nameNotExistRqir.encode('utf-8'))
                SA.task = TaskState.unlogin
                RecvSock.sendall(self.guideMsg.encode('utf-8'))
                return
        elif SA.task == TaskState.loginPwd:
            if RecvStr == self.playersDict[SA.name]['pwd']:
                if SA.name in self.online_players:
                    lastsock = self.online_players[SA.name].sock
                    lastsock.sendall('您正在通过其他设备登录,此次游戏下线\n'.encode('utf-8'))
                    print '切断来自 %s 的连接' % self.allConnectSocks[lastsock].addr
                    self.disConnectSock(lastsock)
                RecvSock.sendall(('Hi! '+SA.name+' 欢迎回到大厅\nhelp: 查看帮助文档\n').encode('utf-8'))
                SA.task = TaskState.lobby
                self.online_players[SA.name] = Player(SA.name,self.playersDict[SA.name]['pwd'],self.playersDict[SA.name]['time'],SA.sock)
                self.online_rooms[0].addPlayer(self.online_players[SA.name])
                return
            else:
                RecvSock.sendall(self.pwdWrong.encode('utf-8'))
                SA.name = ''
                SA.task = TaskState.unlogin
                RecvSock.sendall(self.guideMsg.encode('utf-8'))
                return

        # 进入大厅后的请求
        elif SA.task == TaskState.lobby:
            # 帮助文档
            if RecvStr == 'help':
                RecvSock.sendall(self.helpMsg.encode('utf-8'))
                return
            # 服务器时间
            elif RecvStr == 'when':
                timestr = "当前服务器时间为: "+time.asctime(time.localtime(time.time()))
                RecvSock.sendall(timestr.encode('utf-8'))
                return
            # 玩家信息
            elif RecvStr == 'me':
                self.playersDict[SA.name]['time'] += time.time()-self.online_players[SA.name].logintime
                self.dumpPlayerData()
                seconds = self.playersDict[SA.name]['time']
                hour = int(seconds//3600)
                minute = int((seconds-hour*3600)//60)
                second = int(seconds-hour*3600-minute*60)
                timestr = str(hour)+"小时"+str(minute)+"分钟"+str(second)+"秒"
                sockPlayer = self.online_players[SA.name]
                roomInfo = "玩家位置:游戏大厅"
                if sockPlayer.roomid != 0:
                    roomInfo = "玩家位置:"+str(sockPlayer.roomid)+"号房间,"+self.online_rooms[sockPlayer.roomid].name
                playerInfo = "姓名:"+sockPlayer.name+"     在线时间:"+timestr+"     "+roomInfo+"\n"
                #RecvSock.sendall(playerInfo.encode('utf-8'))
                sockPlayer.sendMsg(playerInfo)
                return
            # 查看大厅玩家
            elif RecvStr == 'playersInLobby':
                PILstr = ''
                for name in self.online_players:
                    if self.online_players[name].roomid == 0:
                        PILstr += name+"\t"
                if PILstr == '':
                    PILstr = '此时大厅没有人在走动'
                RecvSock.sendall((PILstr+"\n").encode('utf-8'))
                return
            # 切换账户
            elif RecvStr == 'changeAccount':
                self.playersDict[SA.name]['time'] += time.time()-self.online_players[SA.name].logintime
                self.dumpPlayerData()
                self.online_players.pop(SA.name)
                SA.name = ''
                SA.pwd = ''
                SA.task = TaskState.unlogin
                RecvSock.sendall(self.guideMsg.encode('utf-8'))
                return
            # 对所有人讲话
            elif len(RecvStr)>8 and RecvStr[:8] == 'chatAll ':
                chatStr = SA.name+" 在大厅里发言:"+RecvStr[8:]+"\n"
                RecvSock.sendall(chatStr.encode('utf-8'))
                for name,player in self.online_players.items():
                    if player.name != SA.name:
                        #self.online_players[name].sock.sendall(chatStr.encode('utf-8'))
                        player.sendMsg(chatStr)
                return
            # 私聊
            elif RecvStr.split(' ')[0] == 'chatTo':
                sendName = RecvStr.split(' ')[1]
                start = len('chatTo')+len(sendName)+2
                if sendName in self.online_players and len(RecvStr)>start:
                    content = RecvStr[start:]
                    senderStr = '你对 '+sendName+' 私聊:'+content+"\n"
                    readerStr = SA.name+' 对你私聊:'+content+"\n"
                    RecvSock.sendall(senderStr.encode('utf-8'))
                    #self.online_players[sendName].sock.sendall(readerStr.encode('utf-8'))
                    self.online_players[sendName].sendMsg(readerStr)
                    return
                else:
                    RecvSock.sendall(("聊天对象不存在,或"+self.helpstr).encode('utf-8'))
                    return
            # 创建房间
            elif len(RecvStr)>11 and RecvStr[:11] == 'createRoom ':
                roomname = RecvStr[11:]
                exist = False
                for room in self.online_rooms:
                    if roomname == room.name:
                        exist = True
                if exist:
                    RecvSock.sendall("该房间名已存在,请重新创建\n".encode('utf-8'))
                    return
                else:
                    roomid = len(self.online_rooms)
                    newRoom = Room(roomname,roomid)
                    self.online_rooms.append(newRoom)
                    oldRoom = self.online_rooms[self.online_players[SA.name].roomid]
                    oldRoom.removePlayer(SA.name)
                    newRoom.addPlayer(self.online_players[SA.name])
                    return
            # 查看大厅内的房间
            elif RecvStr == 'listRooms':
                roomInfo = ''
                for room in self.online_rooms:
                    if room.id != 0:
                        roomInfo += str(room.id)+' 号房:'+room.name+"\n"
                if roomInfo == '':
                    roomInfo = '大厅还未创建新房间'
                RecvSock.sendall((roomInfo+"\n").encode('utf-8'))
                return
            # 查看房间内的玩家
            elif RecvStr == 'playersInRoom':
                roomid = self.online_players[SA.name].roomid
                if roomid == 0:
                    RecvSock.sendall(self.notInroom.encode('utf-8'))
                    return
                else:
                    PIRstr = ''
                    for player in self.online_rooms[roomid].players:
                        PIRstr += player.name+'\t'
                    PIRstr += "\n"
                    RecvSock.sendall(PIRstr.encode('utf-8'))
                    return
            # 房间内发言
            elif len(RecvStr)>9 and RecvStr[:9] == "chatRoom ":
                roomid = self.online_players[SA.name].roomid
                if roomid == 0:
                    RecvSock.sendall(self.notInroom.encode('utf-8'))
                    return
                else:
                    content = SA.name+" 在本房间说:"+RecvStr[9:]+"\n"
                    self.online_rooms[roomid].sendMsg(content)
                    return
            # 从房间返回大厅
            elif RecvStr == "lobby":
                roomid = self.online_players[SA.name].roomid
                if roomid == 0:
                    RecvSock.sendall("您已在大厅中\n".encode('utf-8'))
                    return
                else:
                    self.online_rooms[roomid].removePlayer(SA.name)
                    RecvSock.sendall("欢迎回到大厅\n".encode('utf-8'))
                    return
            # 进入房间
            elif len(RecvStr)>6 and RecvStr[:6] == "enter ":
                roomstr = RecvStr[6:]
                try:
                    int(roomstr)
                except ValueError:
                    RecvSock.sendall(self.roomNotInRange.encode('utf-8'))
                    return
                else:
                    roomnum = int(roomstr)
                    if roomnum >=1 and roomnum<len(self.online_rooms):
                        newRoom = self.online_rooms[roomnum]
                        oldRoom = self.online_rooms[self.online_players[SA.name].roomid]
                        oldRoom.removePlayer(SA.name)
                        newRoom.addPlayer(self.online_players[SA.name])
                        return
                    else:
                        RecvSock.sendall(self.roomNotInRange.encode('utf-8'))
                        return
            # 参与房间内的21点游戏
            elif len(RecvStr)>7 and RecvStr[:7] == '21game ':
                roomid = self.online_players[SA.name].roomid
                if roomid == 0:
                    RecvSock.sendall("您正在大厅中,请进入房间答题\n".encode('utf-8'))
                    return

                if self.online_rooms[roomid].winner != '':
                    RecvSock.sendall(("该房间游戏已结束,获胜者是 "+self.online_rooms[roomid].winner+" \n").encode('utf-8'))
                    return

                if not self.Competing:
                    if len(self.online_rooms[roomid].questionNums)>0:
                        RecvSock.sendall(("该房间游戏已结束,没有获胜者\n").encode('utf-8'))
                    else:
                        RecvSock.sendall(("游戏还未开始\n").encode('utf-8'))
                    return

                if len(RecvStr)>=7+4+3 and len(RecvStr) < 40:
                    expr = RecvStr[7:]
                    unary = ['++','--','**','//']
                    GameRoom = self.online_rooms[roomid]
                    GameNumstr = [str(GameRoom.questionNums[0]),str(GameRoom.questionNums[1]),
                                 str(GameRoom.questionNums[2]),str(GameRoom.questionNums[3])]
                    for each in unary:
                        if each in expr:
                            RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                            return
                    for i in range(len(expr)):
                        c = expr[i]
                        if c == '1' and i<len(expr)-1 and expr[i+1] == '0' and '10' in GameNumstr:
                            continue
                        if c == '0' and i>0 and expr[i-1] == '1' and '10' in GameNumstr:
                            continue
                        if c not in ['+','-','*','/','(',')',' ',GameNumstr[0],GameNumstr[1],GameNumstr[2],GameNumstr[3]]:
                            RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                            return
                        if c in GameNumstr:
                            if c == '1' and '10' in GameNumstr:
                                if expr.count(c)-GameNumstr.count('10') > GameNumstr.count(c):
                                    RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                                    return
                            elif expr.count(c) > GameNumstr.count(c):
                                RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                                return
                        if c >='1' and c<='9' and i<len(expr)-1 and expr[i+1] >='1' and expr[i+1] <='9':
                            RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                            return
                        if c >='1' and c<='9' and i>0 and expr[i-1] >='0' and expr[i-1] <='9':
                            RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                            return

                    try:
                        thisScore = eval(expr)
                    except Exception as e:
                        print e.message
                        RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                        return

                    if thisScore > 21:
                        RecvSock.sendall("计算结果大于21点\n".encode('utf-8'))
                        return

                    curtime = time.time()
                    if curtime-self.questionTime <= 0.00001+Game21rushAnswerTime:
                        if thisScore == 21:
                            self.online_rooms[roomid].sendMsg("本次游戏获胜者是 "+SA.name+"     答案为 "+expr+" \n")
                            self.online_rooms[roomid].winner = SA.name
                            return
                        else:
                            if thisScore not in self.online_rooms[roomid].answers:
                                self.online_rooms[roomid].answers[thisScore] = SA.name
                            RecvSock.sendall(("结果为"+str(thisScore)+" ,等待其他人的结果\n").encode('utf-8'))
                            return
                else:
                    RecvSock.sendall(self.illegalExpr.encode('utf-8'))
                    return
            # 查看房间内的21点题目
            elif RecvStr == 'question':
                roomid = self.online_players[SA.name].roomid
                if roomid == 0:
                    RecvSock.sendall("您正在大厅中,请进入房间查看题目\n".encode('utf-8'))
                    return
                GameRoom = self.online_rooms[roomid]
                question = str(GameRoom.id)+'号房间,'+GameRoom.name+' 的21点题目是: '
                for num in GameRoom.questionNums:
                    question += str(num)+' '
                question += '\n'
                if len(GameRoom.questionNums) == 0:
                    RecvSock.sendall("本房间还未出题\n".encode('utf-8'))
                else:
                    RecvSock.sendall(question.encode('utf-8'))
                return

            elif RecvStr == 'modifyInfo' or RecvStr[:11] == 'reNameRoom ':
                RecvSock.sendall("该功能 Coming Soon,敬请关注\nhelp:查看帮助文档\n".encode('utf-8'))
                return
            else:
                RecvSock.sendall(self.helpstr.encode('utf-8'))
                return

    def run(self):
        self.Competing = True
        self.questionTime = time.time()
        self.questionTime -= self.questionTime %Game21timeSpan
        while True:
            curtime = time.time()
            # 抢答时间已过,结算房间内的获胜者
            if self.Competing and curtime-self.questionTime >= 0.00001+Game21rushAnswerTime:
                self.balanceGame21()
                self.Competing = False

            # 到时间发布新题目
            if curtime-self.questionTime >= 0.00001+Game21timeSpan:
                self.questionTime = curtime
                self.questionForRooms()

            try:
                # 响应客户端的请求
                r_list, w_list, e_list = select.select(self.input_list,[], self.input_list, 2)#2s Select处理一次
                # print r_list
                # select读 处理
                for r in r_list:
                    if r is self.serverSock:
                        # 新连接加入
                        conn, addr = self.serverSock.accept()
                        conn.setblocking(False)
                        self.input_list.append(conn)
                        self.allConnectSocks[conn] = SocketAgent(conn,addr)
                        conn.sendall(self.guideMsg.encode('utf-8'))
                    else:
                        # 接收老客户端发来的消息
                        try:
                            recv_data = r.recv(ReadBufferSize)
                            #print recv_data
                            if recv_data:
                                recv_str = recv_data.decode('utf-8')
                                self.dealWithStr(r,recv_str)
                            else:
                                print '客户端消息格式出错,切断来自 %s 的连接' % (self.allConnectSocks[r].addr)
                                self.disConnectSock(r)
                        except Exception as e:
                            print e.message
                            print '接收消息出错,切断来自 %s 的连接' % (self.allConnectSocks[r].addr)
                            self.disConnectSock(r)

            except Exception as e:
                print e.message
                print "select读写的socket已断开"

    # 玩家信息存档
    def dumpPlayerData(self):
        with open("players.data","w") as f:
            f.write(json.dumps(self.playersDict))

    # 发布新题目
    def questionForRooms(self):
        for room in self.online_rooms:
            if room.id != 0:
                room.winner = ''
                room.answers = {}
                room.questionNums = []
                for i in range(4):
                    room.questionNums.append(random.randint(1, 10))
                question = str(room.id)+'号房间,'+room.name+' 的21点题目是: '
                for num in room.questionNums:
                    question += str(num)+' '
                question += '\n'
                room.sendMsg(question)
        self.Competing = True

    # 结算房间内的获胜者
    def balanceGame21(self):
        for room in self.online_rooms:
            if room.id != 0 and room.winner == '':
                maxScore = 0
                maxName = ''
                for score,name in room.answers.items():
                    if score > maxScore:
                        maxScore = score
                        maxName = name
                if maxName == '':
                    if len(room.questionNums)>0:
                        room.sendMsg("本次游戏没有获胜者\n")
                else:
                    room.sendMsg("本次游戏获胜者为: "+maxName+"     结果为:"+str(maxScore)+" \n")
                    room.winner = maxName

    # 断开客户端的连接
    def disConnectSock(self,clientsock):
        #代表player的客户端下线
        sockname = self.allConnectSocks[clientsock].name
        if sockname in self.online_players:
            self.playersDict[sockname]['time'] += time.time()-self.online_players[sockname].logintime
            self.dumpPlayerData()

            sockroomid = self.online_players[sockname].roomid
            self.online_rooms[sockroomid].removePlayer(sockname)

            self.online_players.pop(sockname)

        self.allConnectSocks.pop(clientsock)
        self.input_list.remove(clientsock)
        clientsock.close()

    def destruct(self):
        if self.serverSock:
            self.serverSock.close()
        print "关闭服务端"

if __name__ == "__main__":
    server = Server()
    server.run()
    server.destruct()

