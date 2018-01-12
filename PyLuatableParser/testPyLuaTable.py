#coding=utf-8

from PyLuaTblParser import PyLuaTblParser
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
