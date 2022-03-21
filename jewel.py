#!/usr/bin/env python3
import socket
import sys
import select
from urllib import response

from file_reader import FileReader

class Jewel:

    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(1)
        s.bind(('0.0.0.0', port))

        s.listen(5)
        clientdict = {}
        wdict = {}
        #https://docs.python.org/3/library/select.html
        rlist = [s] #wait until ready for reading (rready)
        wlist = [] #wait until ready for writing (wready)
        xlist = [] #wait for an exceptional condition

        while True:
            #Select.select() docs: https://docs.python.org/3/library/select.html
            #select.select(rlist, wlist, xlist[, timeout])
            rready, wready, xcondition = select.select(rlist, wlist, xlist)
            #The return value is a triple of lists of objects that are ready: subsets of the first three arguments. When the time-out is reached without a file descriptor becoming ready, three empty lists are returned.
           
            #Loop through list of objects ready for reading
            for readable in rready:
                if readable == s:
                    (client, address) = s.accept() #from collab document
                    client.setblocking(0)
                    #When a client connects. Your server should log: [CONN] Connection from <ip address> on port <port number>
                    print("[CONN] Connection from ", address[0], " on port ", port)
                    clientdict[client] = address  #set address to socket
                    rlist.append(client) #add to readable list
                    wlist.append(client) #add to writable list
                    wdict[client] = [] #add to writable dict
                else:
                        data = readable.recv(1024)

                        request_fields = str.splitlines(data.decode(encoding='ascii'))
                        request_type = request_fields[0].split()
                            #When a request is received. Your server should log: [REQU] [<address>:<port>] <request type> request for <request path>
                        print("[REQU] [",clientdict[readable][0],":",port,"]" ,request_type[0], "request for",request_type[1])
                        if request_type[0] == "GET": 
                            head, body = file_reader.get(file_path+request_type[1],request_fields[1:len(request_fields)-1])
                            if body != "":
                                wdict[readable].append(head+b"\r\n"+body+b"\r\n\r\n")
                            else:
                                wdict[readable].append(head)
                        elif request_type[0] == "HEAD":
                            wdict[readable].append(file_reader.head(file_path+request_type[1],request_fields[1:len(request_fields)-1])+b"\r\n")
                        else:
                            wdict[readable].append(b"HTTP/1.1 501 Method Unimplemented\r\n\r\n")
           
            for writable in wready:
                if wdict[writable]:
                    msg = wdict[writable].pop()
                    #print("message", msg)
                    response_code = str.splitlines(msg[9:12].decode(encoding='ascii'))  
                    #b'HTTP/1.1 200 OK\r\nContent-Length: 61822\r\nContent-Type: image/jpeg                
                    if response_code[0] != '200':
                        #When a request results in an error. Your server should log: [ERRO] [<address>:<port>] <request type> request returned error <error number>
                        print("[ERRO] [",clientdict[writable][0],":",port,"]",request_type[0],"request returned error",response_code[0])
                    writable.send(msg)
                    rlist.remove(writable)
                    wlist.remove(writable)
                    writable.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    file_path = sys.argv[2]

    FR = FileReader()

    J = Jewel(port, file_path, FR)
