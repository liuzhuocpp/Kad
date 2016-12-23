#coding=utf-8
# import httplib
# import urllib2

# import urllib


# # html = urllib2.urlopen("http://202.118.67.200:8888")

# # html = html.decode('utf-8')
# # print html



# headers = {
# # "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
# # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

# # "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
# # "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
# # "Accept-Encoding":"gzip, deflate, br",
# # "Cache-Control": "no-cache",
# # "Connection":"keep-alive",
# # "Upgrade-Insecure-Requests":"1",

# # "Cache-Control":"max-age=0",
# # "Cookie":"JSESSIONID=4AD4A5CD0E629A4E4965A7E670F6646D; _ga=GA1.2.2109852302.1482388080; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1482388080; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1482388207; user_trace_token=20161222142832-a66b9ba8d3c949c59437581d26c307c3; LGRID=20161222143039-281247d6-c810-11e6-8097-5254005c3644; LGUID=20161222142832-dc35ebfb-c80f-11e6-8097-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_company",


# "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# "Accept-Encoding":"gzip, deflate, sdch, br",
# "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,vi;q=0.2",
# "Cache-Control":"no-cache",
# "Connection":"keep-alive",
# # "Cookie":"user_trace_token=20161222155012-4491faed-c81b-11e6-8097-5254005c3644; LGUID=20161222155012-4491fded-c81b-11e6-8097-5254005c3644; JSESSIONID=D6FE85882FAE279A9CCA37DA93A56BA8; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_company; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1482392979,1482408133; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1482408178; _ga=GA1.2.2098364144.1482392979; LGSID=20161222200246-8d187ec6-c83e-11e6-80a0-5254005c3644; LGRID=20161222200331-a7fa3ced-c83e-11e6-80a0-5254005c3644",
# "Host":"www.lagou.com",
# "Pragma":"no-cache",
# "Referer":"https://www.lagou.com/gongsi/",
# "Upgrade-Insecure-Requests":"1",
# "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",


# }
# #params = {'companyId':'5706'} 
# params = {}
# data = urllib.urlencode(params)        
# host = 'www.lagou.com'
# url = '/gongsi/5998.html'


# conn = httplib.HTTPConnection(host)
# # conn = httplib.HTTPSConnection(host)
# conn.request('GET', url, data, headers)
# httpres = conn.getresponse()  
# print httpres.status  
# print httpres.reason  
# res =  httpres.read()

# import sys
# print sys.getfilesystemencoding()

# print len(res)
# print type(res)
# # print res
# print res.decode('UTF-8').encode("mbcs")
# # print res.encode("mbcs")


# conn.close()

from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys  
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time  
from selenium.webdriver.common.proxy import *

# 'proxy': 'HWJB1R49VGL78Q3D:0C29FFF1CB8308C4@proxy.abuyun.com:9020'
# proxy= 'HWJB1R49VGL78Q3D:0C29FFF1CB8308C4@proxy.abuyun.com:9020'
myProxy= 'proxy.abuyun.com:9020'


# DesiredCapabilities capabilities = DesiredCapabilities.chrome();
# capabilities.setCapability("chrome.switches", Arrays.asList("--proxy-server=http://user:password@proxy.com:8080"));
# WebDriver driver = new ChromeDriver(capabilities);




option = webdriver.ChromeOptions()
option.add_argument('--user-data-dir=C:\Users\LZ\AppData\Local\Google\Chrome\User Data\Default') #设置成用户自己的数据目录
# option.setproxy(chromeProxy)
option.add_argument('--proxy-server=%s' % myProxy)

# desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
# desired_capabilities['proxy'] = chromeProxy
browser = webdriver.Chrome(chrome_options=option)
# browser = webdriver.Firefox() # Get local session of firefox  
#browser = webdriver.Chrome() # Get local session of firefox  

browser.get("https://www.baidu.com") # Load page  
time.sleep(10)
browser.get("https://www.lagou.com/gongsi/j34551.html") # Load page  


soup = BeautifulSoup(browser.page_source, "html.parser")

while 1:
    for ele in soup.select(".con_list_item .item_title_date a"):
        print (ele.text).encode('gb18030')

    tag = soup.select(".next")[0]
    if len(tag['class']) == 2: # contain u'next', u'disable'
        break;

    print '-----------------'
    browser.find_element_by_class_name("next").click()
    time.sleep(1)
    soup = BeautifulSoup(browser.page_source, "html.parser")

#print(soup.prettify()).encode('gb18030')

# assert "Yahoo!" in browser.title  

# print browser.page_source.decode('UTF-8').encode("mbcs")


# elem = browser.find_element_by_name("p") # Find the query box  
# elem.send_keys("seleniumhq" + Keys.RETURN)  
# time.sleep(0.2) # Let the page load, will be added to the API  
# try:  
#     browser.find_element_by_xpath("//a[contains(@href,'http://seleniumhq.org')]")  
# except NoSuchElementException:  
#     assert 0, "can't find seleniumhq"  
#browser.close()  
