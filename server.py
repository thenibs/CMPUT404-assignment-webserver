#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    # html template portion of response
    def htmlResponse(self, CODE):
        body = "<!DOCTYPE html>\n<head><meta charset='UTF-8'></head>\n<html>\n<body>\n" + str(CODE) + ":"
        if CODE == 404:
            body += "Page Not Found\n</body>\n</html>" 

        elif CODE == 405:
            body += "Method Not Allowed\n</body>\n</html>" 

        return body

    # html response header and html display content
    def createResponse(self, CODE):
        response = "HTTP/1.1 "+ str(CODE) + " "
        if CODE == 404:
            body = self.htmlResponse(404)
            response += "Not Found\r\nContent-Length: " + str(len(body)) + \
                "\r\nContent-Type: text/html\r\nConnection: Closed\r\n\r\n" + body
    
        elif CODE == 405:
            body = self.htmlResponse(405)
            response += "Method Not Allowed\r\nConnection: Closed\r\n\r\n" + body
        
        print(str(CODE) + " RESPONSE: " + response)
        return response

    # valid response html header and content
    def validResponse(self, pathName, fileTypeName):
        f = open(pathName, 'r')
        content = f.read()
        response = "HTTP/1.1 200 OK\r\nContent-Type: " + fileTypeName + \
                "\r\nContent-Length: " + str(len(content)) + "\r\nConnection Closed\r\n\r\n" + content
        f.close()

        return response

    # perm moved response html header and redirect to correct location
    def permMovedResponse(self, newPathName):
        response = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + newPathName[3:] + "\r\n\r\n"
        return response

    # main handling class function
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data) # for testing to see what request received

        # decode request data and get extract relevant variables
        decodedData = self.data.decode('utf-8')
        fullHeader = decodedData.split("\r\n")[0]
        header = fullHeader.split(" ")

        # if unsupported header type, throw error 405
        if header[0] != "GET":
            response405 = self.createResponse(405)
            self.request.sendall(bytearray(response405, 'utf-8'))
            return
        
        path = header[1]

        # add index.html if base/directory and then verify existence in later step
        if path[0] == "/" and path[-1] == "/":
            path += "index.html"

        # get full path
        path = "www" + path

        # check if valid path or throw not found
        if not os.path.exists(path):
            response404 = self.createResponse(404)
            self.request.sendall(bytearray(response404, 'utf-8'))
            return

        # check if file
        if os.path.isfile(path):
            # ensure valid type or throw not found
            fileTypeName = ""
            if path.endswith("html"):
                fileTypeName = "text/html"

            elif path.endswith(".css"):
                fileTypeName = "text/css"
            
            else:
                response404 = self.createResponse(404)
                self.request.sendall(bytearray(response404, 'utf-8'))
                return
            
            # send valid response
            filePathResponse = self.validResponse(path, fileTypeName)
            self.request.sendall(bytearray(filePathResponse, 'utf-8'))

        # check if directory
        if os.path.isdir(path):
            # redirect if directory missing ending char '/'
            if path[-1] != "/":
                redirectPathResponse = self.permMovedResponse(path+"/")
                self.request.sendall(bytearray(redirectPathResponse, 'utf-8'))

        self.request.sendall(bytearray("OK\r\n",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    print("Server listening on http://{}:{}".format(
        HOST,
        PORT
    ))

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
