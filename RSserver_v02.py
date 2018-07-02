
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 00:18:56 2017

@author: Shriharsha_Shripadaraj &&& Jaspreet Kaur
"""


###################################################################################################################################################################
#Follwing code snippet is for Registration server.                                                                                                                #
#                                                                                                                                                                 #
#Registration server performs following task                                                                                                                      #
#                                                                                                                                                                 #
#1. Creates a TCP server socket on port 65423 and IP of physical port 'ENS33'.                                                                                    #
#2. Waits for connections from any client.                                                                                                                        #
#3. On recieving registration request from client, adds the hostname, port number (peer server), TTL, counter, flag, time and cookie value in to its peer list.   #
#4. On recieving PQUERY request, RS sends list of all active peers                                                                                                #
#5. On recieving Keep-Alive message, RS resets the TTL value of that perticular peer to 7200 and sets flag to True and time to most recent value.                 #
#6. On Recieving LEAVE message from peer, RS sets flag to False and TTL to 0.                                                                                     #
###################################################################################################################################################################

"""
linkedlist		: Linked list to store Peer list
insert			: Insert new node into the peer list
search			: Search a node in the peer list
display			: Display the nodes in peer list
getlist			: Extract nodes from the peer list
update			: Update flag, TTL and count in the peer list
ttlupdate		: Update TTL value of the peer list
new_peer		: Add new peer in to the linked list
register		: Handle registration request from the peers
replyphrase		: Create reply phrase 
pquery			: Handles pquery requests from peers
leave			: Handles LEAVE requests from the peers
keep_alive		: Handles Keep-alive updates from the peers
extracter		: Extracts cookie value from the incoming data
connection		: Creates a thread to handle incoming messages
get_ip_address	: To get 'ens33' ip from Ubuntu machine
ttlloop			: Creates thread to initiate TTL updates

"""

from threading import Thread
import socket
import time
import datetime
import fcntl
import struct

class node(object):
    def __init__(self,data):
        self.data=data
        self.next=None
class linkedlist(object):  
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

    def search(self,hostname):
        cur=self.head
        status=False
        previous=self.head
        while cur!=None:
            if cur.data[0]==hostname:
                status=True
                return(status,previous)
            previous=cur.next
            cur=cur.next
        status=False
        return(status,previous)

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
                pquery_list=pquery_list+' IP :'+cur.data[0]+': PORT :'+cur.data[4]+'<next>'
            cur=cur.next
        return(pquery_list)
    def update(self,previous,switch,re_entry_switch):
        if switch==True:
			if re_entry_switch==True:
				previous.data[2]=True
				previous.data[3]=7200
				previous.data[5]+=1
			else:
				previous.data[2]=True
				previous.data[3]=7200
        else:
			previous.data[2]=False                   #HAS to CHANGED
			previous.data[3]=0
        
        return(previous.data)
    def ttlupdate(self,value):
        cur=self.head
        while cur!=None:
            cur.data[3]-=value
            cur=cur.next
        
        
def new_peer(client_data,addr,cookie_val):  
    global global_cookie
    global peer_list
    cur_time=str(datetime.datetime.now())
    flag=True
    counter=1
    port_number=0
    new_list=client_data.split()
    for i in range(len(new_list)):
        if new_list[i]=="port":
            port_number=new_list[i+2]
    cur_ttl=7200
    temp=[addr[0],cookie_val,flag,cur_ttl,port_number,counter,cur_time]      
    peer_list.insert(temp)         
    item='cookie : '+str(cookie_val)
    status_code='OK 4444'
    reply_of='REGISTRATION_RESPONSE'
    message=replyphrase(client_data,item,status_code,cookie_val,reply_of)    
    return(message)
    
def register(client_data, addr,conn):
    global global_cookie
    global peer_list
    status=False
    status,previous=peer_list.search(str(addr[0]))
    if status==True:
        switch = True
        re_entry_switch=True	                                                              #re_entry_switch determines if the update is because of keep-alive or becasue of re-registration
        updated_data=peer_list.update(previous,switch,re_entry_switch)                        #Switch determines, if the update is to leave the peer or re-registration.  
        cookie_val=updated_data[1]
        item=' You are already registed \n your details are :'+str(cookie_val)
        status_code='OK 4444'
        reply_of='REGISTRATION_RESPONSE'
        message=replyphrase(client_data,item,status_code,cookie_val,reply_of)
        conn.send(message)
    else:
        global_cookie=global_cookie+1
        cookie_val=global_cookie         
        message=new_peer(client_data,addr,cookie_val)
        conn.send(message)
    return(message)

def replyphrase(client_data,item,status_code,cookie_val,reply_of):
    global host
    global port
    if cookie_val==9999:
        #Client_IP,Client_port,Client_cookie=extractphrase(client_data)
        Client_cookie=100
    else: 
        Client_cookie=cookie_val
    if '4444' in status_code:        
        message= status_code+" Field: "+reply_of+" / RTP /1.0 Host: "+ host +" port : "+ str(port)+" User-Agent: icewolf 5.0 Cookie : "+str(Client_cookie)+" Accept-Encoding: none Connection: keep-alive "+" <cr> "+ item +" <cr>"
    elif '5555' in status_code:
        message= status_code  # have to be edited
    return(message)
def pquery(client_data,conn,addr):    
    global peer_list   
    pquery_list=peer_list.getlist(conn,addr)
    status_code='OK 4444'
    reply_of='PQUERY_RESPONSE'
    cookie_extract=client_data.split()
    for i in range(len(cookie_extract)):
        if cookie_extract[i]=='Cookie':
            cookie_val=cookie_extract[i+2]
            break
    pquery_string=replyphrase(client_data,pquery_list,status_code,cookie_val,reply_of) 
    conn.send(pquery_string)
    return
def leave(client_data,conn,addr):
    global host
    global port
    global peer_list
    global global_cookie
    item='GOOD BYEEE'
    status_code='OK 4444'
    Client_cookie=extracter(client_data)
    message=status_code+"/ RTP /1.0 Field: LEAVE_RESPONSE Host: "+ host +" port : "+ str(port)+" User-Agent: icewolf 5.0 Cookie : "+str(Client_cookie)+"Accept-Encoding: none Connection: keep-alive "+" <cr> "+ item +" <cr> " 
    conn.send(message) 
    status,previous=peer_list.search(str(addr[0]))
    switch=False
    re_entry_switch=False
    peer_list.update(previous,switch,re_entry_switch)
    conn.close()
    
def keep_alive(client_data,conn,addr):
    global host
    global port
    global peer_list
    global global_cookie
    status,previous=peer_list.search(str(addr[0]))
    if status==True:
        switch = True
        re_entry_switch=False
        peer_list.update(previous,switch,re_entry_switch)
    return
	
def extracter(client_data):
    lists=client_data.split()
    for i in range(len(lists)):
        if lists[i]=='Cookie':
            Cookie_val=lists[i+2]
    
    return(Cookie_val)
 
def connection(conn,addr):
    global host
    global port
    global peer_list
    global global_cookie
    while True:
        client_data=conn.recv(1024)
        if 'REGISTER' in client_data:
            register(client_data,addr,conn)
        elif 'PQUERY' in client_data:
            pquery(client_data,conn,addr)
        elif 'LEAVE' in client_data:
            leave(client_data,conn,addr)
        elif 'Keep_Alive' in client_data:
            keep_alive(client_data,conn,addr)
        peer_list.display()
        if not client_data: conn.close()
        #peer_listr_list.display()
		
		
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def ttlloop():
    global peer_list
    while True:
        peer_list.ttlupdate(3)
        time.sleep(3)
		
global_cookie=-1
host= get_ip_address('ens33')
port= 65423
peer_list=linkedlist()

def main():
    global host
    global port
    global peer_list
    s=socket.socket()  
    s.bind((host,port)) 
    s.listen(8)  
    ttlThread=Thread(target=ttlloop,args=())
    ttlThread.start()
	
    while True:
        try:
            conn, addr = s.accept()
            t=Thread(target=connection,args=(conn,addr))
            t.start()
        except socket.error:
            s.close()            
            break
if __name__=='__main__':
	main()