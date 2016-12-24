#!/usr/bin/env python
# -*- coding: utf-8 -*-



from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys  
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time  
from selenium.webdriver.common.proxy import *

# from pymongo import *

import sys
reload(sys)
sys.setdefaultencoding('utf8')
# print sys.getfilesystemencoding()


# 'proxy': 'HWJB1R49VGL78Q3D:0C29FFF1CB8308C4@proxy.abuyun.com:9020'
myProxy= 'proxy.abuyun.com:9020'

def getChromeBrowser():
    option = webdriver.ChromeOptions()
    option.add_argument('--user-data-dir=C:\Users\LZ\AppData\Local\Google\Chrome\User Data\Default') #设置成用户自己的数据目录
    option.add_argument('--proxy-server=%s' % myProxy)
    browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=option)
    return browser

from base64 import b64encode        

def getFirefoxBrowser():
    # myProxy = "xx.xx.xx.xx:xxxx"
    # proxy = {
    #     "host": "proxy.com",
    #     "port": "1000",
    #     "user": "usr123",
    #     "pass": "pwd123"
    # }
    proxy = {'host': "proxy.abuyun.com", 'port': 9020, 'usr': "HWJB1R49VGL78Q3D", 'pwd': "0C29FFF1CB8308C4"}

    fp = webdriver.FirefoxProfile()

    fp.add_extension('closeproxy.xpi')
    fp.set_preference('network.proxy.type', 1)
    fp.set_preference('network.proxy.http', proxy['host'])
    fp.set_preference('network.proxy.http_port', int(proxy['port']))

    fp.set_preference('network.proxy.ssl', proxy['host'])
    fp.set_preference('network.proxy.ssl_port', int(proxy['port']))
    fp.set_preference('network.proxy.ftp', proxy['host'])
    fp.set_preference('network.proxy.ftp_port', int(proxy['port']))       
    fp.set_preference('network.proxy.no_proxies_on', 'localhost, 127.0.0.1')

# 禁止浏览器访问图片信息
    fp.set_preference('permissions.default.image', 2)
# permissions.default.image
    credentials = '{usr}:{pwd}'.format(**proxy)
    credentials = b64encode(credentials.encode('ascii')).decode('utf-8')
    fp.set_preference('extensions.closeproxyauth.authtoken', credentials)

    # driver = webdriver.Firefox(fp)
    browser = webdriver.Firefox(executable_path="geckodriver", firefox_profile=fp)
    return browser
    # proxy = Proxy({
    #     'proxyType': ProxyType.MANUAL,
    #     'httpProxy': myProxy,
    #     'ftpProxy': myProxy,
    #     'sslProxy': myProxy,
    #     'noProxy': '', # set this value as desired
    #     'socksUsername':  'HWJB1R49VGL78Q3D',
    #     'socksPassword':  '0C29FFF1CB8308C4',
    #     })
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference('network.http.phishy-userpass-length', 255)

    # browser = webdriver.Firefox(executable_path="geckodriver", proxy=proxy)
    # return browser

    # pass

# browser = getChromeBrowser()
browser = getFirefoxBrowser()


browser.get("https://www.baidu.com") # Load page
time.sleep(10)

# client = MongoClient()
# db = client['result']
# col = db['lagou']
encodeName = "gb18030"

CompanyNameSelector = ".company_main > h1 > a"
CompanyBasicInfoSelector = '#basic_container ul > li'
CompanyIntroSelector = ".company_intro_text"
CompanyIntroHasExpandSelector = ".company_intro_text .company_content"

CompanyNavsSelector = '#company_navs li'
ExpandOrFoldSelector = ".text_over"
Page404 = ".page404"
MaxWaitTime = 10

def getCompanyInfoUrl(cid):
    return "https://www.lagou.com/gongsi/" + str(cid) + ".html"

# 函数返回类型    
ResultOK = 0
ResultShouldWait = 1
ResultTerminate = 2

# 封装函数，等待函数执行确实执行完毕，或者超出了时间上限
# 如果返回true表示执行成功，false表示超出时间上限
# fun是一个函数，参数为空，
def waitFunctionFinish(fun, maxWaitTime = MaxWaitTime, sleepSeconds = 1):
    for i in xrange(maxWaitTime):
        resultType = fun()
        if resultType == ResultOK:
            return True
        elif resultType == ResultShouldWait:
            time.sleep(sleepSeconds)
        else:
            return False
    print "time excceed"
    return False

def getCompanyInfo(cid, browser):
    print '\n\n'
    print cid, "-"*100
    time.sleep(4)
    url = getCompanyInfoUrl(cid)
    try:
        browser.get(url)
    except Exception, e:    
        print "WebDriverException occurs !!"
        return 

    
    soup = None
    def checkPageLoadFinish():
        soup = BeautifulSoup(browser.page_source, "html.parser")
        if len(soup.select(Page404)) > 0:
            print "compage: ", cid, "does not exsit: page404 fuound"
            return ResultTerminate

        if len(soup.select(".incomplete_tips")) > 0:
            print u'这个公司的主页还在建设中...'
            return ResultTerminate
        # 这个公司的主页还在建设中

        if len(soup.select(CompanyNameSelector)) == 0:
            print "CompanyNameSelector has not yet present"
        elif len(soup.select(CompanyBasicInfoSelector)) == 0:
            print "CompanyBasicInfoSelector has not yet present"
        elif len(soup.select(CompanyIntroSelector)) == 0:
            print "CompanyIntroSelector has not yet present"        
        else:
            return ResultOK
        return ResultShouldWait

    if waitFunctionFinish(checkPageLoadFinish):
        pass
    else:
        return 


    content = ""
    soup = BeautifulSoup(browser.page_source, "html.parser")
    if len(soup.select(ExpandOrFoldSelector)) == 0:
        content = soup.select(CompanyIntroSelector)[0].text
    else :

        try:
            browser.find_element_by_class_name("text_over").click()
            def checkExpandChickFinish():
                soup = BeautifulSoup(browser.page_source, "html.parser")
                if soup.select(ExpandOrFoldSelector)[0].text == u'收起':
                    return ResultOK
                else:
                    return ResultShouldWait
            if waitFunctionFinish(checkExpandChickFinish):
                soup = BeautifulSoup(browser.page_source, "html.parser")
                content = soup.select(CompanyIntroHasExpandSelector)[0].text
            else:
                print 'Expand is no good !!!'
                return 
        except Exception, e:
            print u"It has \'text_over\', but maybe it hides"
            content = soup.select(CompanyIntroHasExpandSelector)[0].text


    total = int(filter(unicode.isdigit, soup.select(CompanyNavsSelector)[1].text))

    name = soup.select(CompanyNameSelector)[0].text.strip()
    info = soup.select(CompanyBasicInfoSelector)
    tag = info[0].find('span').text.encode(encodeName, "ignore")
    process = info[1].find('span').text.encode(encodeName, "ignore")
    content = content.encode(encodeName, "ignore")

    # obj = {
    #     "cid": cid,
    #     "url": url.decode(encodeName).encode("utf-8"),
    #     "name": name.decode(encodeName).encode("utf-8"),
    #     "content": cont.decode(encodeName).encode("utf-8"),
    #     "tag": tag.decode(encodeName).encode("utf-8"),
    #     "process": process.decode(encodeName).encode("utf-8"),
    #     "salary": [],
    #     "total": total
    # }
    print "compange cid:", cid
    print "compange name:", name
    print "compange content:", content
    print "compange tag:", tag
    print "compange process:", process
    print "compange total:", total
        # col.insert(obj)
        # getPosition(cid, browser)


def getPosition(cid, browser):
    print cid
    pageNo = 1
    time.sleep(4)
    url = "https://www.lagou.com/gongsi/j" + str(cid) + ".html"
    browser.get(url)

    # while 1:


    soup = BeautifulSoup(browser.page_source, "html.parser")
    # if col.find_one({'cid': cid})['total'] <= 10:
    #     for ele in soup.select(".con_list_item > .item_detail > .item_salary"):
    #         col.update({"cid": cid}, {"$push": {"salary": (ele.text).encode(encodeName, "ignore")}})
    #     return

    while 1:
        for ele in soup.select(".con_list_item > .item_detail > .item_salary"):
            pass
            # col.update({"cid": cid}, {"$push": {"salary": (ele.text).encode(encodeName, "ignore")}})

        tag = soup.select(".next")[0]
        if len(tag['class']) == 2: # contain u'next', u'disable'
            break;

        browser.find_element_by_class_name("next").click()
        time.sleep(4)
        pageNo += 1
        while 1:
            soup = BeautifulSoup(browser.page_source, "html.parser")

            newPage = soup.select('.pages > .current')[0].text.encode(encodeName, "ignore")
            newPage = int(newPage)
            print "New page number:", newPage, "; real page:", pageNo
            if newPage and pageNo == newPage:
                break
            else:
                time.sleep(1)

        #soup = BeautifulSoup(browser.page_source, "html.parser")

for cid in range(22790, 22890):
    getCompanyInfo(cid, browser)
# getPosition(cid, browser)