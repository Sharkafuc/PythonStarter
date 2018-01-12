def removeSpan(s):

    newstr = ''
    for i,chr in enumerate(s):
        if not removeSig(s,i):
            newstr += chr
        print i,chr,removeSig(s,i)
    return newstr

def removeSig(s,pos):
    if s[pos].isspace():
        sig = ''
        count = 0
        for i in range(pos):
            chr = s[i]
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
            elif s[i] == '"' and sig == '"' and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                count = count-1
                if count == 0:
                    sig = ''
            elif s[i] == "'" and sig == "'" and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
                count = count-1
                if count == 0:
                    sig = ''
        print count
        if count == 0:
            return True
        else:
            return False
    else:
        return False

removestart = 0

def isNotInString(s,pos,start):
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
        elif s[i] == '"' and sig == '"' and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
            count = count-1
            if count == 0:
                sig = ''
        elif s[i] == "'" and sig == "'" and i>2 and s[i-1] == '\\' and s[i-2] == '\\' and s[i-3] != '\\':
            count = count-1
            if count == 0:
                sig = ''
    if count == 0:
        removestart = pos
        return True
    else:
        return False

def removeComent(s):
    ssize = len(s)
    i = 0
    while i < ssize:
        i,s = StartLineComent(s,i)
    return s

def StartLineComent(s,index):
    ssize = len(s)
    if index+2 < ssize and s[index:index+2] == '--' and isNotInString(s,index,removestart):
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


with open("case.txt","r") as f:
    text = f.read()
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

    with open("teststr.txt","w") as g:
        d = {'\a': '\\a', '\r': '\\r', '\b': '\\b', '\f': '\\f', '\n': '\\n', '\t': '\\t', '\'': '\\\'', '"': '\\"', '\v': '\\v','\\': '\\\\'}
        s2 = ""
        for each in s:
            if each in d:
                s2 += d[each]
            else:
                s2 += each
        g.write(s2)

