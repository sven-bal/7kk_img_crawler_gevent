# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 00:09:09 2017

@author: bal
"""

import requests
from bs4 import BeautifulSoup as bs
import os
import re
import time
import gevent
import random
import configparser
import gevent.monkey
import sys
from gevent.pool import Pool
#gevent.monkey.patch_socket
gevent.monkey.patch_all()



#f1：回话对象，接收url。
class session:
    def __init__(self):
        self.failed_l=[]
        self.session = requests.Session()
        self.config = configparser.ConfigParser()
        self.config.read('cfg.txt')
        self.proxies_list = []
        self.cookie=dict(Hm_lvt_9e68697c4389c6fbd87784c533e967db='1489071189,1489162734,1489230703,1489232265',
                    PHPSESSID='nmd9ng2lrc6k68d4vsigdoubk6',
                    Hm_lpvt_9e68697c4389c6fbd87784c533e967db=str(int(time.time())))
    def f0(self,url,proxy=None,num_c=5):
        IP = self.config.items('proxy')
        u=self.config.items('UA')
        UA=random.choice(u[0][1].split('|'))        
        head = {'User-Agent':UA,}

        if proxy == None:
            try:
#                print('使用默认配置')
                time.sleep(0.2)
                return self.session.get(url,headers=head,timeout=5,cookies=self.cookie,proxies=None)
            except:
                if num_c > 0:
                    time.sleep(2)
                    print('重试%s'%url)
                    return self.f0(url,num_c-1)
                else:
                    time.sleep(2)
                    ip=random.choice(IP[0][1].split('|'))
                    pr={'http':str(ip)}
                    print('开始使用代理%s'%url)
                    return self.f0(url,proxy=pr)
        else:
            try:
                ip=random.choice(IP[0][1].split('|'))
                pr={'http':str(ip)}
                print('使用代理%s'%url)
                return self.session.get(url,headers=head,timeout=10,cookies=self.cookie,proxies=pr)
            except:
                if num_c >0:
                    ip=random.choice(IP[0][1].split('|'))
                    pr={'http':str(ip)}
                    print('更换代理%s'%url)
                    time.sleep(2)
                    return self.f0(url,pr,num_c-1)
                else:
                    print('%s cant connect'% url)
                    self.failed_l.append(url)
                    


                                        
meinv_url = 'http://www.7kk.com/meinv/all/new----'
renwu_url='http://www.7kk.com/renwu/nvmingxing/new----'
base_person_url = 'http://www.7kk.com/album/photos/'
start_url = 'http://www.7kk.com'
p = Pool(100)

def f1(url):
    src=session().f0(url) 
    soup = bs(src.content,'html.parser')
#    print('>>>>>>',src.status_code,url)
    if soup:
        
        return soup
    else:
        print('soup is error')
        pass
    

#f2：创建文件夹
def f2(title):
    if title in os.listdir():
        print('%s is existed'% title)
        pass
    else:
        os.mkdir(title)
        print('make %s done'% title)
        
        
#f3：open main url and select the person's url,
def f3(main_url):
    d={}
    soup=f1(main_url)
    detail = soup.find('ul',attrs={'class':'beautyUl clear'})
    img_list = detail.find_all('a',attrs={'class':'lblName'},href=True)
    for i in img_list:
        title = i.getText()
        f2(title)
        person_url = start_url+i.get('href')
        d[title]=person_url
        p.spawn(f4,d)
        d={}

        
#f4:open person's url and select the sub page
def f4(f3):
    for k,v in f3.items():
        title = k
        person_url = v
        ID = person_url.split('.')[-2].split('/')[-1]
        soup = f1(person_url)
        detail = soup.find('div',attrs={'id':'bottompage'})
        next_page_src = detail.find('a',attrs={'class':'last'})
        if next_page_src:
            next_page = int(next_page_src.getText())
        else:
            next_page = 1
        for i in range(1,next_page+1):
            p.spawn(f5,title,ID,i)
            
            
#open all sub page and select the max_img url
def f5(title,ID,sub_page_num):
    sub_page_url = base_person_url+ID+'-'+str(sub_page_num)+'.html'
    soup = f1(sub_page_url)
    if soup:
        detail = soup.find('div',{'id':'container'}).find_all('img',{'class':'lazy-img',})
        for i in detail:
            s=i.attrs['data-original']
            max_url=re.sub(r'(.+)/(\d+)_(\d+)','http://pic.7kk.com/upload',s)
#            print(max_url)
            p.spawn(f7,title,max_url)

            
#download
def f7(title,max_url):
    person_dir = os.getcwd()+'\\'+title+'\\'
    file_name = max_url.split('.')[-2].split('/')[-1]+'.jpg'
    soup = session().f0(max_url)
#    print(soup.status_code)
    if soup.status_code ==200:
        with open(person_dir+file_name,'wb') as f:
            f.write(soup.content)
            time.sleep(0.05)
#            print('write img %s done'%file_name)
    else:
        print('cant get src %s'% max_url)
        pass
    

def main():
    with open('log.txt','a+') as f:
        start = time.time()
        sys.stdout = f
        sys.stderr = f
        for i in range(14,15):#start page num and the end     
            url=meinv_url+str(i)
            p.spawn(f3,url)
            p.join()
        end = time.time()
        print('@@@@@@@@@@@@@@@@@@@',(end-start))


if __name__ == '__main__':
    main()



    
    
