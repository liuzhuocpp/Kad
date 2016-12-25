#!/usr/bin/env python
# -*- coding: utf-8 -*-



from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys  
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time  
from selenium.webdriver.common.proxy import *

import sys
reload(sys)
sys.setdefaultencoding('utf8')
# print sys.getfilesystemencoding()



def getChromeBrowser():
    myProxy= 'proxy.abuyun.com:9020'
    option = webdriver.ChromeOptions()
    option.add_argument('--user-data-dir=C:\Users\LZ\AppData\Local\Google\Chrome\User Data\Default') #设置成用户自己的数据目录
    option.add_argument('--proxy-server=%s' % myProxy)
    browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=option)
    return browser

from base64 import b64encode        

def getFirefoxBrowser():
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
    credentials = '{usr}:{pwd}'.format(**proxy)
    credentials = b64encode(credentials.encode('ascii')).decode('utf-8')
    fp.set_preference('extensions.closeproxyauth.authtoken', credentials)
    browser = webdriver.Firefox(executable_path="geckodriver", firefox_profile=fp)
    # browser = webdriver.Firefox(executable_path="geckodriver")
    return browser

# browser = getChromeBrowser()
browser = getFirefoxBrowser()

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
# fun的返回值类型：
ResultOK = 0 # 表示函数执行成功立即返回
ResultShouldWait = 1 # 表示函数执行未成功，但未发现严重错误，应继续sleep and wait
ResultTerminate = 2 # 表示函数执行未成功，并且发现严重错误，应立即停止

# waitFunctionFinish的返回值类型：
WaitOK = 0 # 表示等待的fun函数已经执行成功并且返回了ResultOK
WaitTimeExceed = 1 # 表示等待的fun函数已经执行一直未成功，并且超出了等待时间长度
WaitTerminate = 2 # 表示等待的fun函数未成功，并且fun函数返回了ResultTerminate
HtmlParser = "html.parser"

# 封装函数，等待函数执行确实执行完毕，或者超出了时间上限
# 如果返回true表示执行成功，false表示超出时间上限
# fun是一个函数，参数为空，
def waitFunctionFinish(fun, maxWaitTime = MaxWaitTime, sleepSeconds = 1):
    for i in xrange(maxWaitTime):
        resultType = fun()
        if resultType == ResultOK:
            return WaitOK
        elif resultType == ResultShouldWait:
            time.sleep(sleepSeconds)
        else:
            return WaitTerminate
    print "time excceed"
    return WaitTimeExceed

def getCompanyInfo(cid, browser):    
    print '\n\n', cid, "-"*100
    # time.sleep(4)
    url = getCompanyInfoUrl(cid)
    soup = None
    def checkPageLoadFinish():
        soup = BeautifulSoup(browser.page_source, HtmlParser)
        if len(soup.select(Page404)) > 0:
            print "company: ", cid, "does not exsit: page404 fuound"
            return ResultTerminate

        if len(soup.select(".incomplete_tips")) > 0:
            print u'这个公司的主页还在建设中...'
            return ResultTerminate
        if len(soup.select(CompanyNameSelector)) == 0:
            print "CompanyNameSelector has not yet present"
        elif len(soup.select(CompanyBasicInfoSelector)) == 0:
            print "CompanyBasicInfoSelector has not yet present"
        elif len(soup.select(CompanyIntroSelector)) == 0:
            print "CompanyIntroSelector has not yet present"        
        else:
            return ResultOK
        return ResultShouldWait

    def loadPage():
        try:
            browser.get(url)
            waitType = waitFunctionFinish(checkPageLoadFinish)
            if waitType == WaitOK:
                return ResultOK
            elif waitType == WaitTerminate:
                return ResultTerminate
            elif waitType == WaitTimeExceed:
                return  ResultShouldWait
            else:
                print "Error occurs in loadPage, waitType is unknown"
        except Exception, e:    
            print "WebDriverException occurs, and reload"
            return ResultShouldWait

    if waitFunctionFinish(loadPage) != WaitOK:
        return

    content = ""

    # 获取 公司简介内容content：
    soup = BeautifulSoup(browser.page_source, HtmlParser)

    if len(soup.select(ExpandOrFoldSelector)) == 0:
        content = soup.select(CompanyIntroSelector)[0].text
        print "No expand button"
    elif soup.select(ExpandOrFoldSelector)[0].attrs.has_key("style") and\
         soup.select(ExpandOrFoldSelector)[0].attrs["style"].find("none") != -1:
        content = soup.select(CompanyIntroHasExpandSelector)[0].text
        print "Expand button must be hided "
        
    else :
        try:
            browser.find_element_by_class_name("text_over").click()
            def checkExpandClickFinish():
                soup = BeautifulSoup(browser.page_source, HtmlParser)
                if soup.select(ExpandOrFoldSelector)[0].text == u'收起':
                    return ResultOK
                else:
                    print u"Not found expand button"
                    return ResultShouldWait
            if waitFunctionFinish(checkExpandClickFinish, 3) == WaitOK:
                soup = BeautifulSoup(browser.page_source, HtmlParser)
                content = soup.select(CompanyIntroHasExpandSelector)[0].text
            else:
                print 'Expand button is not good'
                content = soup.select(CompanyIntroHasExpandSelector)[0].text 
                # return 
        except Exception, e:
            print u"It has \'text_over\', but maybe it hides"
            content = soup.select(CompanyIntroHasExpandSelector)[0].text


    total = int(filter(unicode.isdigit, soup.select(CompanyNavsSelector)[1].text))
    name = soup.select(CompanyNameSelector)[0].text.strip()
    info = soup.select(CompanyBasicInfoSelector)
    tag = info[0].find('span').text.encode(encodeName, "ignore")
    process = info[1].find('span').text.encode(encodeName, "ignore")
    content = content.encode(encodeName, "ignore")

    print "compange cid:", cid
    print "compange name:", name
    print "compange content:", content
    print "compange tag:", tag
    print "compange process:", process
    print "compange total:", total


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

for cid in range(22809, 52809 + 1):

    getCompanyInfo(cid, browser)
    # time.sleep(3)
# getPosition(cid, browser)