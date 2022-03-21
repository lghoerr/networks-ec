import mimetypes

class FileReader:

    def __init__(self):
        pass

    def get(self, filepath, cookies):
        requestHead = self.head(filepath, 'bleh') #don't use cookies
        import os
        #Collab: in Python3 it is very important to use binary strings (often denoted as b'') when working with files and data from clients
        tail = b'' #binary string
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                #If your server receives a request for a directory, and that directory exists, it should return a simple HTML document with the requested path to that directory:
                #<html><body><h1>/requested/directory/path</h1></body></html>
                tail = b'<html><body><h1>' + filepath.encode(encoding="ascii") + b'</h1></body></html>'
                return requestHead, tail
            #read from the binary file in python
            else:
                file=open(filepath, mode='rb')
                tail = file.read()
        return requestHead, tail

    def head(self, filepath, cookies):
        import os
        response = "HTTP/1.1 "
        if os.path.exists(filepath) == False:
            response = response + "404 Not Found\r\n"
        if os.path.exists(filepath):
            response = response + "200 OK\r\n" + "Content-Length: " + str(os.stat(filepath).st_size + 4) + "\r\n"
            #https://docs.python.org/3/library/os.path.html
            #If your server receives a request for a file, and that file exists, it should return the contents of that file with the correct MIME-type
            mimetype = "text/html" #directory
            if not os.path.isdir(filepath):
                #https://docs.python.org/3/library/mimetypes.html
                mimetype, encoding = mimetypes.guess_type(filepath, strict=True)
            response = response + "Content-Type: " + mimetype + "\r\n"
        return response.encode(encoding='ascii')