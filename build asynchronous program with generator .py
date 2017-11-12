# -*- coding:utf-8 -*-
"""
Author:icedrunkard@github

python yield 实现异步编程

"""
import socket
from selectors import DefaultSelector,EVENT_WRITE,EVENT_READ
selector = DefaultSelector()
stopped =False
urls_todo=['/']#,'/1','/2','/3'


class Crawler():
    def __init__(self,url):
        self.url = url
        self.response=b''
    def fetch(self):
        sock=socket.socket()
        #sock.setblocking(False)
        try:
            sock.connect(('baidu.com',80))
        except BlockingIOError:
            pass
        f=Future()#第2个Future
        print('in crawler',f)
        def connected():
            """
            会执行callback list中的step方法,其中执行无更改的参数不会变：得到第三个Future，在其中添加step

            """
            f.set_result(None)  
        """
        selector能监听/记录函数内存位置，调用connected

        """
        selector.register(sock.fileno(),EVENT_WRITE,connected)
        
        """
        yield 能记录生成器每一步执行截止的位置

        """
        m=yield f#触发connected后，send data


        selector.unregister(sock.fileno())
        get='GET {} HTTP/1.0\r\nHost: baidu.com\r\n\r\n'.format(self.url)
        sock.send(get.encode('ascii'))
        global stopped
        while True:
            f=Future()#第三个Future
            print('in while',f)
            def readable():
                r=sock.recv(4096)#chunk
                f.set_result(r)#会强制改变yield f的返回值


            selector.register(sock.fileno(),EVENT_READ,readable)#等待调用readable
            chunk=yield f#触发readable之后进行循环结束
            selector.unregister(sock.fileno())
            if chunk:

                self.response+=chunk
            else:
                urls_todo.remove(self.url)
                if not urls_todo:
                    stopped =True
                break
            


  

class Task():
    def __init__(self,i,func):
        self.i=i
        self.func=func
        f=Future()#第一个Future
        print('intask',f)
        f.set_result(None)
        self.step(f)

    def step(self,f):
        print('step母的类:',self,'self.func',self.func,'self.i',self.i)
        try:
            n=self.func.send(f.result)#得到第二个Future
        except StopIteration:
            return
        print(self.i,'in Task',self.step,'\n')
        n.add(self.step)#第二个Future中有step方法



class Future():
    def __init__(self):
        self.result=None
        self.callback=[]
    def add(self,func):
        self.callback.append(func)
    def set_result(self,result):
        self.result=result
        for func in self.callback:
            print('future',func,'\n')
            func(self)


def loop():
    while not stopped:
        events=selector.select()
        print('events',events,'\n')
        for key,mask in events:
            #Selectorkey：namedtuple
            print('key and mask',key,mask,'\n')
            callback=key.data
            print('callback',callback,'\n')

            callback()

if __name__ == '__main__':
    for i in range(len(urls_todo)):
        crawler=Crawler(urls_todo[i])
        Task(i,crawler.fetch())
    loop()
             
            



        
