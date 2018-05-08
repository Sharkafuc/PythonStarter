import socket

host,port = "127.0.0.1",25001
data = "0,5,0"  #the vector for positioning the red cube

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    sock.connect((host,port))
    sock.sendall(data.encode("utf-8"))
    data = sock.recv(1024).decode("utf-8")
    print data;
finally:
    sock.close()
