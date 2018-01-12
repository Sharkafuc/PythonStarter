#coding=utf-8


class PyLuaTblParser:
    
    def __init__(self):
        self.table = {}  #table用来存储luatable数据
        self.removeStart = 0
        self.comentStart = 0

    def __getUnicode(self,strInput):
        #从文件读入或者输入的strinput,不管什么格式的编码,都统一转换为unicode
        if isinstance(strInput,unicode):
            returnStr = strInput
            return returnStr
        try:
            returnStr = strInput.decode("utf8")
            return returnStr
        except:
            pass

        try:
            returnStr = strInput.decode("gbk")
            return returnStr
        except:
            pass

    def __removeSpan(self,s):
        #清除字符串中的空白格,返回的字符串不包含能够被清除的字符
        newstr = ''
        ssize = len(s)
        for i in range(ssize):
            if not self.__removeSig(s,i,self.removeStart):
                newstr += s[i]
        return newstr

    def __removeSig(self,s,pos,start):
        #判断字符串s中的第pos个字符是否能够被清除,能够清除的是不在引号里的空白格,引号有可能被\转义,引号前的\也可能被\转义
        if s[pos].isspace():
            sig = ''
            count = 0
            for i in range(start,pos):
                if s[i] == '"' and sig == '':
                    sig = '"'
                    count = count+1
                elif s[i] == "'" and sig =='':
                    sig = "'"
                    count = count+1
                elif s[i] == '"' and sig == '"' and s[i-1] != '\\':
                    count = count-1
                    if count == 0:
                        sig = ''
                elif s[i] == "'" and sig == "'" and s[i-1] != '\\':
                    count = count-1
                    if count == 0:
                        sig = ''
                elif s[i] == '"' and sig == '"' and i<=2 and s[i-1] == '\\' and s[i-2] == '\\':
                    count = count-1
                    if count == 0:
                        sig = ''
                elif s[i] == "'" and sig == "'" and i<=2 and s[i-1] == '\\' and s[i-2] == '\\':
                    count = count-1
                    if count == 0:
                        sig = ''
                elif s[i] == '"' and sig == '"' and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                    count = count-1
                    if count == 0:
                        sig = ''
                elif s[i] == "'" and sig == "'" and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                    count = count-1
                    if count == 0:
                        sig = ''
            if count == 0:
                self.removeStart = pos
                return True
            else:
                return False
        else:
            return False

    def __isNotInString(self,s,pos):
        #判断字符串s的第pos个字符是否在引号中,引号有可能被\转义,引号前的\也可能被\转义
        sig = ''
        count = 0
        for i in range(pos):
            if s[i] == '"' and sig == '':
                sig = '"'
                count = count+1
            elif s[i] == "'" and sig =='':
                sig = "'"
                count = count+1
            elif s[i] == '"' and sig == '"' and s[i-1] != '\\':
                count = count-1
                if count == 0:
                    sig = ''
            elif s[i] == "'" and sig == "'" and s[i-1] != '\\':
                count = count-1
                if count == 0:
                    sig = ''
            elif s[i] == '"' and sig == '"' and i<=2 and s[i-1] == '\\' and s[i-2] == '\\':
                count = count-1
                if count == 0:
                    sig = ''
            elif s[i] == "'" and sig == "'" and i<=2 and s[i-1] == '\\' and s[i-2] == '\\':
                count = count-1
                if count == 0:
                    sig = ''
            elif s[i] == '"' and sig == '"' and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                count = count-1
                if count == 0:
                    sig = ''
            elif s[i] == "'" and sig == "'" and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                count = count-1
                if count == 0:
                    sig = ''
        if count == 0:
            return True
        else:
            return False

    def __splitTableWithComma(self,s):
        #用逗号分割luatable字符串,可以作为分割符的逗号,是不在引号里,且只在最外层{}内的逗号
        ssize = len(s)
        substrs = []
        braces = 0
        i = 1
        while i < ssize-1:
            j = i
            while j <= ssize-1:
                if s[j] == '{':
                    braces = braces+1
                if s[j] == '}':
                    braces = braces-1
                if s[j] == ',' and self.__isNotInString(s,j) and braces == 0 and i <= j-1 :
                    substrs.append(s[i:j])
                    i = j
                    break
                if j == ssize-1 and i <= j-1:
                    substrs.append(s[i:j])
                    i = j
                j = j+1
            i = i+1
        return substrs

    def __isStrInt(self,s):
        #判断s字符串的内容是否是整数
        try:
            int(s)
        except ValueError:
            return False
        else:
            return True

    def __isStrFloat(self,s):
        #判断s字符串的内容是否是小数
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True

    def __isStr(self,s):
        #判断s字符串的内容是否是字符串
        flag = False
        if s[0] == '"' and s[-1] == '"':
            flag = True
            for i in range(1,len(s)-1):
                if s[i] == '"' and i<=2 and s[i-1] == '\\' and s[i-2] == '\\':
                    flag = False
                    break
                if s[i] == '"' and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                    flag = False
                    break
                if s[i] == '"' and s[i-1] != '\\':
                    flag = False
                    break

        if s[0] == "'" and s[-1] == "'":
            flag = True
            for i in range(1,len(s)-1):
                if s[i] == "'" and i<=2 and s[i-1] == '\\' and s[i-2] == '\\':
                    flag = False
                    break
                if s[i] == "'" and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                    flag = False
                    break
                if s[i] == "'" and s[i-1] != "\\":
                    flag = False
                    break
        return flag

    def __isTable(self,s):
        #判断s字符串的内容是否是luatable
        if s[0] == '{' and s[-1] == '}':
            return True
        return False

    def __isDict(self,s):
        #判断s字符串的内容是否是字典,在最外层{}中有=,且=不在引号内的是字典,如果是字典返回=的位置.
        ssize = len(s)
        braces = 0
        i = 1
        while i < ssize-1:
            if s[i] == '{':
                braces = braces+1
            if s[i] == '}':
                braces = braces-1
            if s[i] == '=' and self.__isNotInString(s,i) and braces == 0:
                return i
            i = i+1
        return False

    def __parseString(self,text):
        #读luatable到内存需要对字符串进行转义
        s = ""
        ssize = len(text)
        i = 0
        d = {'a': '\a', 'r': '\r', 'b': '\b', 'f': '\f', 'n': '\n', 't': '\t', '\'': '\'', '"': '"', 'v': '\v','\\': '\\'}
        while i < ssize:
            if text[i] != '\\':
                s = s+text[i]
            else:
                if i+1 == ssize:
                    s = s+'\\'
                else:
                    if text[i+1] in d:
                        s = s+d[text[i+1]]
                        i = i+1
                    else:
                        s = s+'\\'
            i = i+1
        return s

    def __deParseString(self,s):
        #写内存到文件中的luatable需要对字符串反转义
        d = {'\a': '\\a', '\r': '\\r', '\b': '\\b', '\f': '\\f', '\n': '\\n', '\t': '\\t', '\'': '\\\'', '"': '\\"', '\v': '\\v','\\': '\\\\'}
        s2 = ""
        for each in s:
            if each in d:
                s2 += d[each]
            else:
                s2 += each
        return s2

    def __parseStr2table(self,s):
        #将luatable字符串转变为类的self.table
        ssize = len(s)
        #这里的s是去除过空白格的字符串,luatable至少要有{和}两个字符,以{开头,}结尾
        if ssize < 2:
            print "table format error, size too small"
            raise Exception("table format error, size too small")
        if s[0] != '{' or s[-1] != '}':
            print "table format error, it should be like {}"
            raise Exception("table format error, it should be like {}")
        #逗号将luatable分割成多个子部分
        substrs = self.__splitTableWithComma(s)
        keys = []
        values = []
        valueCount = 0
        defualtKey = 0
        for i,eachstr in enumerate(substrs):
            #逐个判断子部分的内容,valuecount记数不是字典的个数,小于子部分的个数说明存在字典,则self.table是字典,否则,self.table是列表
            defualtKey = defualtKey+1
            if eachstr == "nil":
                keys.append(defualtKey)
                values.append(None)
                valueCount = valueCount+1
            elif eachstr == "true":
                keys.append(defualtKey)
                values.append(True)
                valueCount = valueCount+1
            elif eachstr == "false":
                keys.append(defualtKey)
                values.append(False)
                valueCount = valueCount+1
            elif self.__isStrInt(eachstr):
                keys.append(defualtKey)
                values.append(int(eachstr))
                valueCount = valueCount+1
            elif self.__isStrFloat(eachstr):
                keys.append(defualtKey)
                values.append(float(eachstr))
                valueCount = valueCount+1
            elif self.__isStr(eachstr):
                keys.append(defualtKey)
                values.append(self.__parseString(eachstr[1:-1]))
                valueCount = valueCount+1
            elif self.__isTable(eachstr):
                #如果子部分是luatable,递归返回这部分代表的字典或列表
                try:
                    table = self.__parseStr2table(eachstr)
                except Exception:
                    print "subTable format error"
                    raise Exception("subTable format error")
                else:
                    keys.append(defualtKey)
                    values.append(table)
                    valueCount = valueCount+1
            elif self.__isDict(eachstr):
                defualtKey = defualtKey-1
                #如果子部分是字典,用=分割字典的key和value,value如果是table或者字典就递归返回它们
                eaqualPos = self.__isDict(eachstr)
                keyStr = eachstr[0:eaqualPos]
                valueStr = eachstr[eaqualPos+1:]
                keyValid = False
                valueValid = False
                eachstrKey = keyStr
                eachstrValue = valueStr

                if keyStr[0] == '[' and keyStr[-1] == ']':
                    eachstrKey = keyStr[1:-1]
                    if self.__isStrInt(eachstrKey):
                        eachstrKey = int(eachstrKey)
                        keyValid = True
                    elif self.__isStrFloat(eachstrKey):
                        eachstrKey = float(eachstrKey)
                        keyValid = True
                    elif self.__isStr(eachstrKey):
                        eachstrKey = self.__parseString(eachstrKey[1:-1])
                        keyValid = True
                elif self.__isStr(keyStr):
                    eachstrKey = self.__parseString(keyStr[1:-1])
                    keyValid = True
                else:
                    keyValid = True
                
                if valueStr == "nil":
                    eachstrValue = None
                    valueValid = True
                elif valueStr == "true":
                    eachstrValue = True
                    valueValid = True
                elif valueStr == "false":
                    eachstrValue = False
                    valueValid = True
                elif self.__isStrInt(valueStr):
                    eachstrValue = int(valueStr)
                    valueValid = True
                elif self.__isStrFloat(valueStr):
                    eachstrValue = float(valueStr)
                    valueValid = True
                elif self.__isStr(valueStr):
                    eachstrValue = self.__parseString(eachstrValue[1:-1])
                    valueValid = True
                elif self.__isTable(valueStr):
                    try:
                        table = self.__parseStr2table(valueStr)
                    except Exception:
                        print "value table format error"
                        raise Exception("value table format error")
                    else:
                        eachstrValue = table
                        valueValid = True

                if keyValid:
                    if valueValid:
                        keys.append(eachstrKey)
                        values.append(eachstrValue)
                    else:
                        #解析不出的value说明是变量
                        keys.append(eachstrKey)
                        values.append(None)
                else:
                    #解析不出的key说明格式错误
                    print "key format error"
                    raise Exception("key format error")
            else:
                #不是已知的类型不能解析
                print "unknown type format error"
                raise Exception("unknown type format error")
        
        if valueCount == len(substrs):
            #没有字典,self.table是列表
            return values
        else:
            #有字典,self.table是字典,缺失的key是value所占的位置
            diction = {}
            try:
                for i in range(len(keys)):
                    if values[i] != None:
                        diction[keys[i]] = values[i]
            except Exception:
                print "dict format error"
                raise Exception("dict format error")
            return diction
    
    
    def __parseKey2Str(self,item):
        #将键转变为字符串
        s = ""
        if isinstance(item,int) or isinstance(item,float):
            s += "["+str(item)+"]"
        else:
            s += '["'+self.__deParseString(item)+'"]'
        return s

    def __parseValue2Str(self,item):
        #将值转变为字符串
        s = ""
        if item == None:
            s += "nil"
        elif item == True and isinstance(item,bool):
            s += "true"
        elif item == False and isinstance(item,bool):
            s += "false"
        elif isinstance(item,int) or isinstance(item,float):
            s += str(item)
        elif isinstance(item,str):
            s += '"'+self.__deParseString(item)+'"'
        else:
            s += self.__parseTable2Str(item)
        return s

    def __parseTable2Str(self,table):
        #将self.table转变为字符串
        s = "{"
        if isinstance(table,list):
            size = len(table)
            for i,item in enumerate(table):
                s += self.__parseValue2Str(item)
                if i != size-1:
                    s += ','
        else:
            size = len(table)
            i = 0
            for key,value in table.items():
                s += self.__parseKey2Str(key) + "=" + self.__parseValue2Str(value)
                if i != size -1:
                    s += ','
                i = i+1
        s += "}"
        return s

    def __lightfulKeyInput(self,key):
        #判断key的类型是否是luatable需要的key
        if (isinstance(key,int) or isinstance(key,float) or isinstance(key,str)) and not isinstance(key,bool):
            return True
        else:
            return False

    def __lightfulValueInput(self,value):
        #判断value的类型是否是luatable需要的value
        if value == None or isinstance(value,bool) or isinstance(value,int) or isinstance(value,float) or isinstance(value,str):
            return True
        else:
            return False

    def __lightfulCollectInput(self,d):
        #判断传入字典或列表,以及它的子部分,的类型是否是luatable需要的
        if isinstance(d,dict):
            for key,value in d.items():
                if self.__lightfulKeyInput(key) == False:
                    return False
                flag = True
                if isinstance(value,list) or isinstance(value,dict):
                    flag = self.__lightfulCollectInput(value)
                else:
                    flag = self.__lightfulValueInput(value)
                if flag == False:
                    return False
            return True
        else:
            for item in d:
                flag = True
                if isinstance(item,list) or isinstance(item,dict):
                    flag = self.__lightfulCollectInput(item)
                else:
                    flag = self.__lightfulValueInput(item)
                if flag == False:
                    return False
            return True

    def __removeComent(self,s):
        #去luatable字符串中的注释
        ssize = len(s)
        i = 0
        while i < ssize:
            i,s = self.__StartLineComent(s,i)
        return s

    def __StartLineComent(self,s,index):
        ssize = len(s)
        if index+2 < ssize and s[index:index+2] == '--' and self.__isNotInString(s,index):
            if index+8 < ssize and s[index:index+4] == '--[[':
                #multiLine
                start = index
                i = index +1
                while i < ssize:
                    if i+4 < ssize and s[i:i+2] == '--':
                        j = i+2
                        while j < ssize:
                            if s[j].isspace():
                                j = j+1
                            else:
                                if j+2<ssize and s[j:j+2] == ']]':
                                    end = j+2
                                    s = s[:start]+s[end:]
                                    return start,s
                                else:
                                    return index+1,s
                    i = i+1
            else:
                #singleLine
                i = index +2
                while i<ssize:
                    if s[i] == '\n':
                        s = s[:index]+s[i+1:]
                        return index,s
                    i = i+1
                if i==ssize:
                    return ssize,s[:index]
        return index+1,s

    def load(self,s):
        #s = str(self.__getUnicode(s))#将任意编码的s转换成python内部的str类型
        if isinstance(s,str):
            s = self.__removeComent(s)#去注释
            s = self.__removeSpan(s)#去空格
            self.table = self.__parseStr2table(s)#转变为self.table
            # try:
            #     self.table = self.__parseStr2table(s)#转变为self.table
            # except Exception:
            #     print "LuaTable struct error"
            #     raise Exception("loadError")
            # else:
            #     print "read LuaTable str successful"
        else:
            print "not LuaTable str"

    def dump(self):
        return self.__parseTable2Str(self.table)

    def loadLuaTable(self,f):
        try:
            TableFile = open(f,'r')
        except Exception:
            print "open file error"
        else:
            allText = TableFile.read()
            self.load(allText) 
            print "load LuaTable from file successful"
        finally:
            if TableFile:
                TableFile.close()

    def dumpLuaTable(self,f):
        try:
            TableFile = open(f,'w')
        except Exception:
            print "open file error"
        else:
            text = self.dump()
            TableFile.write(text)
            print "write LuaTable to file successful"
        finally:
            if TableFile:
                TableFile.close()

    def loadDict(self,d):
        #判断传入字典,以及它的子部分,的类型是否是luatable需要的,如果是的话,就用它来替换self.table
        if isinstance(d,dict):
            newdict = {}
            for key,value in d.items():
                if self.__lightfulKeyInput(key):
                    flag = True
                    if isinstance(value,list) or isinstance(value,dict):
                        flag = self.__lightfulCollectInput(value)
                    else:
                        flag = self.__lightfulValueInput(value)
                    if flag:
                        newdict[key] = value
                    else:
                        print "dict key or value not right struct"
                        return
                else:
                    print "key:"+str(key)+",not int or str,ignore"
            self.table = newdict
            print "read successfull"
        else:
            print "d is not dict"

    def __copyList(self,l):
        #列表的深拷贝
        if isinstance(l,list):
            newlist = []
            for item in l:
                if isinstance(item,dict):
                    newlist.append(self.__copyDict(item))
                elif isinstance(item,list):
                    newlist.append(self.__copyList(item))
                else:
                    newlist.append(item)
            return newlist

    def __copyDict(self,d):
        #字典的深拷贝
        if isinstance(d,dict):
            newdict = {}
            for key,value in d.items():
                if isinstance(value,dict):
                    newdict[key] = self.__copyDict(value)
                elif isinstance(value,list):
                    newdict[key] = self.__copyList(value)
                else:
                    newdict[key] = value
            return newdict

    def dumpDict(self):
        #返回存储self.table内部数据的字典
        print "dump class data to dict"
        if isinstance(self.table,list):
            newdict = {}
            for i,item in enumerate(self.table):
                newdict[i+1] = item
            return newdict
        else:
            from copy import deepcopy
            return deepcopy(self.table)
            #return self.__copyDict(self.table)

    def update(self,d):
        #判断传入字典,以及它的子部分,的类型是否是luatable需要的,如果是的话,就用它来更新self.table
        if isinstance(d,dict):
            if self.__lightfulCollectInput(d):
                newdict = self.dumpDict()
                for key,value in d.items():
                    newdict[key] = value
                self.table = newdict
            else:
                print "dict loaded not right struct"
                return
            print "update data successful"
        else:
            print "data loaded is not dict"

    def __getitem__(self,index):
        #重载[]读,判断参数是否类型是luatable需要的,如果self.table是列表是否越界,如果是字典是否有键
        if isinstance(self.table,dict):
            if self.table.has_key(index):
                return self.table[index]
            else:
                print "not exist key:"+str(index)
                raise KeyError
        else:
            if isinstance(index,int):
                tableSize = len(self.table)
                if index >= 0 and index<tableSize:
                    return self.table[index]
                else:
                    print "index range error"
                    raise IndexError
            else:
                print "index should be integger or string"
                raise TypeError

    def __lightfulKeyAndValue(self,key,value):
        #判断参数key和value是否类型是luatable需要的
        if self.__lightfulKeyInput(key):
            flag = True
            if isinstance(value,list) or isinstance(value,dict):
                flag = self.__lightfulCollectInput(value)
            else:
                flag = self.__lightfulValueInput(value)
            return flag
        else:
            return False

    def __setitem__(self,key,value):
        #重载[]写,判断参数key和value是否类型是luatable需要的,如果self.table是列表是否越界
        if self.__lightfulKeyAndValue(key,value):
            if isinstance(key,int):
                if isinstance(self.table,list):
                    tableSize = len(self.table)
                    if key >= 0 and key<tableSize:
                        self.table[key] = value
                    else:
                        print "index range error"
                        raise IndexError
                else:
                    self.table[key] = value
            else:
                newdict = self.dumpDict()
                newdict[key] = value
                self.table = newdict
        else:
            print "key or value type not right"
            raise TypeError
        print "assign successful"

if __name__ == "__main__":
    
    a1 = PyLuaTblParser()
    a2 = PyLuaTblParser()
    a3 = PyLuaTblParser()

    file_path = "case.txt"
    a1.loadLuaTable(file_path)
    #print a1.table

    d1 = a1.dumpDict()

    #print d1
    a2.loadDict(d1)
    #print a2.table


    a2.dumpLuaTable("dumpfile.txt")
    a3.loadLuaTable("dumpfile.txt")

    #print a3.table
    d2 = a3.dumpDict()
    print "d2:\n",d2['root']
    d2['root'] = True
    print d2['root']
