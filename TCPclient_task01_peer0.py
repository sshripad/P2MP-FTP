# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 00:18:56 2017

@author: Shriharsha_Shripadaraj &&& Jaspreet Kaur
"""
'''
rfclinkedlist : Linked list to store RFC index
insert        : Function to insert element into the RFC index
rfc_search    : Function to seach an element in RFC list
display       : Function to display elements in the RFC list
get_rfclist   : Function to get elements from the RFC list
ttlupdate     : Function to update TTL field
register      : Function to send Register request to the RS
pquery        : Function to do PQUERY to the RS
leave         : Function to send LEAVE message to the RS
RFC_QUERY     : Function to make RFC query with other peers
get_rfc_list  :  Function to handle RFC query responses.
download_rfc  : Function to request file from peers
keep_alive_send : Function to send keep alive every 30 second to the RS
getuserinput    : I/O for the user
registration_response : Function to handle Registration response
pquery_response  : Function to pquery Registration response
extract_cookie   : Function to extract cookie value from the incoming data 
createRFC_list   : Function to create local RFC list
connection       : Create thread for the TCP server
TCPserver        : Create thread for the TCP server
get_ip_address   : Gets IP addresss of ens33 from ubuntu machine and binds it as TCP socket
leave_response   : Function to handle leave response
ttlloop          : Thread to initiate TTL


'''

import socket
import fcntl
import struct
#import platform
import time
from threading import Thread
import sys
import os

class node(object):
    def __init__(self,data):
        self.data=data
        self.next=None
class rfclinkedlist(object):  
    def __init__(self):
        self.head=None
    def insert(self,temp):
        new_node = node(temp)
        if self.head is None:
            self.head = new_node
            return
        last = self.head
        while (last.next):
            last = last.next
        last.next = new_node
#    
#    def insert(self,item):
#        new_node = node(item)
#        if self.head is None:
#            self.head = new_node
#            return
#        last = self.head
#        while (last.next!=None):
#            last = last.next
#        last.next = new_node
    def search(self,rfc_num,hostname):
        cur=self.head
        status=False
        previous=self.head
        while cur!=None:
            if cur.data[2]==hostname and rfc_num==cur.data[0]:
                status=True
                return(status,previous)
            previous=cur.next
            cur=cur.next
        status=False
        return(status,previous)
    def rfc_search(self,rfc_number):
        cur=self.head
        dest_server=''
        status=False
        while cur!=None:
            if rfc_number==cur.data[0]:
                status=True
                dest_server=cur.data[2]
                return(status,dest_server)
            cur=cur.next
        status=False
        return(status,dest_server)

    def display(self):
        cur=self.head
        while(cur!=None):
            print(cur.data)
            cur=cur.next
            
    def getlist(self,conn,addr):
        cur=self.head
        print("welcome to getlist")
        pquery_list=''
        while cur!=None:
            if cur.data[2]==True:
                if addr[0]==cur.data[0]:
                    cur=cur.next                    
                    continue
#                else:
#                    print("not a match")
                pquery_list=pquery_list+' IP :'+cur.data[0]+': PORT : '+cur.data[4]+' <next> '
            cur=cur.next
        return(pquery_list)
    
    def get_rfclist(self,conn,addr):
        cur=self.head
        print("welcome to get_rfc_list")
        myrfc_list=''
        while cur!=None:
            if int(cur.data[3])!=0:
                myrfc_list=myrfc_list+' RFC_NUM :'+str(cur.data[0])+' : RFC_NAME :'+str(cur.data[1])+' : Hostname :'+str(cur.data[2])+ ' : TTL :'+str(cur.data[3])+' <next> '
            cur=cur.next
        return(myrfc_list)
        
        
    def update(self,previous):
        previous.data[2]=False                   #HAS to CHANGED
        #previous.data[2]=True
        previous.data[3]=40
        return(previous.data)  
        
    def ttlupdate(self,value):
        cur=self.head
        while cur!=None:
            cur.data[3]-=value
            cur=cur.next
        
        
#message=raw_input("")
def register():
    global cookie_num
    global message
    Host_Name=socket.gethostname()
#    OS_Version=platform.platform()
    global server_port
    message='REGISTER / RTP /1.0 Host: '+ str(Host_Name) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 Cookie : "+str(cookie_num)+"Accept-Encoding: none"+"Connection: keep-alive"    
    #print(message)    
    return(message) 
    
def pquery():
    
    global cookie_num
    global message
    Host_Name=socket.gethostname()
#    OS_Version=platform.platform()
    global server_port
    message='PQUERY / RTP /1.0 Host: '+ str(Host_Name) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 Cookie : "+str(cookie_num)+"Accept-Encoding: none"+"Connection: keep-alive"   
    #print(message)    
    return(message)
    
def leave():
    
    global cookie_num
    global message
    Host_Name=socket.gethostname()
#    OS_Version=platform.platform()
    global server_port
    message='LEAVE / RTP /1.0 Host: '+ str(Host_Name) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 Cookie : "+str(cookie_num)+"Accept-Encoding: none"+"Connection: close"  
    #print(message)    
    return(message)  

def RFC_QUERY():
    global host
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host
#    OS_Version=platform.platform()
    global server_port
    message="GET-RFC-INDEX / RTP /1.0 Host: "+ str(server_host) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 "+"Accept-Encoding: none"+"Requesting RFC Index"          
    return(message)


def get_rfc_list():
    global peer_list
    global rfc_list
    if len(peer_list) == 0:
        print("You dont have any active peer. Please Register yourself with RS and get the peer list\n")
        return
    i=0
    for i in range(len(peer_list)):
        rfcserver=socket.socket()
        rfcserver.connect((peer_list[i][0],peer_list[i][1]))
        print("connected to "+ peer_list[i][0])
        message=RFC_QUERY()
        rfcserver.send(message)
        data=rfcserver.recv(9200)
        if 'RFC_QUERY_RESPONSE' in data:
            temp_list=[]
            data=data.split('<cr>')
            data=data[1].split('<next>')
            for i in range(len(data)):
                status=False
                temp_list=data[i].split(':')
                if len(temp_list) > 2:
                    temp=[int(temp_list[1]),temp_list[3],temp_list[5],int(temp_list[7])]
                    status,previous=rfc_list.search(temp[0],temp[2])
                    if status ==False:    
                        rfc_list.insert(temp)
                else: 
                    break
        rfcserver.close()
            
        
 
def download_rfc():
    global host
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host
    global filepath
    print("Please wait.... ")
    get_rfc_list()
    time.sleep(3)
    print("ready to download")
    while True: 
        flag=0
#        RFC_number=int(raw_input("ENTER THE RFC number. "))
        status,dest_server=rfc_list.rfc_search(1)
        dest_port=''
        print(peer_list)
        if status ==False:
            print("We could not find the RFC you are looking for\n\n")
            flag=1
        else:
#            print("We found the RFC you are looking for. Please wait.......")
            for i in range(len(peer_list)):
                print(peer_list[i][0])
                print(peer_list[i][1])
                if (peer_list[i][0] in dest_server) or (dest_server in peer_list[i][0]):
                    dest_port=int(peer_list[i][1])
                    break
            download=socket.socket()
            download.connect((dest_server,dest_port))
            j=8199
            while j<8278: 
                temp_data=''
                item='rfc'+str(j)+'.txt'
                rfc_message="RFC_DOWNLOAD_REQUEST / RTP /1.0 Host: "+ str(server_host) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 "+"Accept-Encoding: none"+"Requesting RFC Index"+ ' <cr>' + item + '<cr> '         
                download.send(rfc_message)
                temp_data = download.recv(9200)
                file_name='RFC_'+str(j)+'.txt'
                download_file = open(file_name,"wb")
                while temp_data:
                    download_file.write(temp_data)
                    temp_data = download.recv(9200)
                print "Download Completed"
                j=j+1
            download.close()
        if flag ==1:
            x=raw_input("Do you want to try again? \n\n 1. Enter Y  to retry\n2.  Enter N to quit")
            if x=='N':
                break
        else:
            x=raw_input("Do you want to download another file? \n\n 1. Enter Y  to download another file\n2.  Enter N to quit")
            if x=='N':
                break
    return()
        
def keep_alive_send(s):
    global host
    global cookie_num
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host
    while True:
        send_data='Keep_Alive / RTP /1.0 Host: '+ str(server_host) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 Cookie : "+str(cookie_num)+"Accept-Encoding: none"+"Connection: keep-alive" 
        s.send(send_data)
        time.sleep(30)

          
def getuserinput(s):
    global host
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host
    user_input=raw_input("\n\nWelcome, You are connected to the server 192.168.159.156 \n\nWhat do you wanna do? Choose one of the following options\nEnter 1 : -->> Register\nEnter 2 : -->> Get peer list\nEnter 3 : -->> Close the connection\nEnter 4 : -->> Download the RFC\nEnter 5 : -->> Quit\nEnter 6 : -->> Get RFC LIST\n\n")
    if user_input== '1':
        register()
        keep=Thread(target=keep_alive_send,args=(s,))
        keep.start()
        return()
    elif user_input == '2':
        pquery()
        return()
    elif user_input == '3':                      #### This is option to leave active peer list group
        leave()
        return()
    elif user_input == '4':
        download_rfc()
    elif user_input == '5':     
        exit()
    elif user_input == '6':
        rfc_list.display()
        getuserinput(s)
    else:
        print("You have entered an invalid option \n\nPLEASE RETRY")
        getuserinput(s)   
    

def registration_response(data,s):

    global cookie_num
    new_data=data.split("<cr>")
    new_data=new_data[1].split(":")
    cookie_num=int(new_data[1])
    print("Cookie value has been updated. YOUR COOKIE is ",cookie_num)
    return

def pquery_response(data,s):
    global peer_list
    peer_list=[]
    new_data=data.split('<cr>')
    new_data=new_data[1].split('<next>')
    for i in range(len(data)):
        temp_list=new_data[i].split(':')
        if len(temp_list) > 2:
            temp=[temp_list[1],int(temp_list[3])]
            peer_list.append(temp)
        else: 
            break
    if len(peer_list)==0:
        print("No active Peer list")
    else:
        print(peer_list)
    return
    

def extract_cookie(data):    
    global cookie_num
    cookie_list=data.split()
    for i in range (len(cookie_list)):
        if(cookie_list[i]=="Cookie"):
            cookie_num=int(cookie_list[i+2])
    return()

def createRFC_list():
    global host
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host
    global filepath
    i=8199
    while i<8278:
        filename='rfc'+str(i)+'.txt'
        for file in os.listdir(filepath):
            if file==filename:
                temp_s=filename
                temp=[i,temp_s,server_host,7200]
                rfc_list.insert(temp)
        i+=1
    return
def connection(conn,addr):
    global host
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host    
    while True:
        client_data=conn.recv(9200)
        if 'GET-RFC-INDEX' in client_data:
            my_rfclist=rfc_list.get_rfclist(conn,addr)
            print(my_rfclist)
            message="OK 4444 / RTP /1.0 Field : RFC_QUERY_RESPONSE / RTP /1.0 Host: "+ str(server_host) +" port : "+str(server_port)+" User-Agent: icewolf 5.0 "+"Accept-Encoding: none"+"Requesting RFC Index "+" <cr> "+ str(my_rfclist) +" <cr>"
            conn.send(message)
        if 'RFC_DOWNLOAD_REQUEST' in client_data:
            data=client_data.split('<cr>')
            filename=data[1]
            found= 0
            for file in os.listdir(filepath):
                if file == filename:
                    found= 1
                    break
            if found == 0:
                print filename+" Not Found On Server"
                conn.send("File_Not_Found_5555")
                break                                           
            else:
                print filename+" File Found"
                UploadFile = open(filepath+filename,"rb")
                fileRead = UploadFile.read()
                while fileRead:
                    conn.send(fileRead)
                    fileRead = UploadFile.read()
                print "Sending Completed"
        break 
    conn.close()

def TCPserver(server_host,server_port):
    serverP1=socket.socket()                              #creating the socket
    serverP1.bind((server_host,server_port))               #binding the port and IP to the server
    serverP1.listen(20) 
    while True:
        try:
            conn, addr = serverP1.accept()
            t=Thread(target=connection,args=(conn,addr))
            t.start()
        except socket.error:
            serverP1.close()            
            break
    


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def leave_response():
    
    print("Connection is succesfully closed")
    return
def ttlloop():
    global rfc_list
    while True:
        rfc_list.ttlupdate(3)
        time.sleep(3)
        
    
host = "192.168.159.167"
port = 65423
message=''
filepath=''
peer_list=[]
rfc_list=rfclinkedlist()
cookie_num=9999
server_host= get_ip_address('ens33')
server_port= 65455
def main():
    global host
    global port
    global message
    global peer_list
    global rfc_list
    global server_port
    global server_host
    global filepath
    filepath=raw_input("Please enter the file path where the RFC are stored.\n\nExample: if file stored in, /home/admin/Document/ folder, enter path as /home/admin/Documents/.  \n(TIP:On terminal, go to RFC folder, use 'pwd' to get path and add '/' at end of it.)\n\n")
    createRFC_list()    
    rfc_list.display()
    s = socket.socket()                   #Client
    s.connect((host,port))
    t1=Thread(target=TCPserver,args=(server_host,server_port))
    t1.start()  
    ttlThread=Thread(target=ttlloop,args=())
    ttlThread.start()
    
    while(1):
        getuserinput(s)
        s.send(message)
        data=s.recv(9200)
        if 'REGISTRATION_RESPONSE' in data:
            registration_response(data,s)
        elif 'PQUERY_RESPONSE' in data:
            pquery_response(data,s)
        elif 'LEAVE_RESPONSE' in data:
            leave_response()

if __name__ =='__main__':
    main()


        
