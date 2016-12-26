#!/usr/bin/env python
# -*- coding: utf-8 -*-



from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys  
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time  
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base64 import b64encode        
import sys

reload(sys)
sys.setdefaultencoding('utf8')
# print sys.getfilesystemencoding()

# 常量：
encodeName = "gb18030"
CompanyNameSelector = ".company_main > h1 > a"
CompanyBasicInfoSelector = '#basic_container ul > li'
CompanyIntroSelector = ".company_intro_text"
CompanyIntroHasExpandSelector = ".company_intro_text .company_content"
CompanyNavsSelector = '#company_navs li'
ExpandOrFoldSelector = ".text_over"
Page404 = ".page404"
MaxWaitTime = 10


class OrEC:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    # callBackIndex 是一个列表只有一个元素，存储下标
    def __init__(self, callBackIndex, *args):
        self.callBackIndex = callBackIndex
        self.ecs = args
    def __call__(self, driver):
        for i in xrange(len(self.ecs)):
            fn = self.ecs[i]
            ans = None
            try:
                ans = fn(driver)
            except:
                pass
            if ans:
                self.callBackIndex[0] = i
                return ans
        return None

class AndEC:
    """ Use with WebDriverWait to combine expected_conditions
        in an AND.
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        resTuple = ()
        for fn in self.ecs:
            ans = None
            try:
                ans = fn(driver)
            except:
                ans = None
            if bool(ans) == False:                
                return ()
            resTuple += (ans,)
        return resTuple


def getChromeBrowser():
    myProxy= 'proxy.abuyun.com:9020'
    option = webdriver.ChromeOptions()
    option.add_argument('--user-data-dir=C:\Users\LZ\AppData\Local\Google\Chrome\User Data\Default') #设置成用户自己的数据目录
    option.add_argument('--proxy-server=%s' % myProxy)
    browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=option)
    return browser


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

    browser.set_page_load_timeout(0)
    return browser




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

Without_establishing_a_connection = "without establishing a connection"
This_browserForTab_is_undefined = "this.browserForTab is undefined"
Failed_to_decode_response_from_marionette = "Failed to decode response from marionette"

browser = None # 全局浏览器

def restartBrowser():
    global browser
    try:
        browser.quit()
    except Exception, e:                    
        print "when browser quit, some exception occurs:", e, "| just pass it"
    browser = getFirefoxBrowser()
    print "restart a new firefox browser"

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



def _getCompanyInfo(cid):
    global browser
    print '\n\n', cid, "-"*100
    answer = {
        "cid":-1, 
        "name":"", 
        "content":"", 
        "tag":"", 
        "process":"", 
        "total":"", 
    }

    url = getCompanyInfoUrl(cid)    
    soup = None
    def ensureLoadPage():
        global browser
        try:
            browser.get(url)
            print u"browser.get end-----"
        except Exception, e:
            print "WebDriverException occurs, and reload: ", e
            if str(e).find(Without_establishing_a_connection) != -1 or\
               str(e).find(This_browserForTab_is_undefined) != -1 or \
               str(e).find(Failed_to_decode_response_from_marionette) != -1: # need 重启firefox
                restartBrowser()
                return ResultShouldWait
            
            # return ResultShouldWait
        hasRealDataEC = AndEC(EC.presence_of_element_located((By.CSS_SELECTOR, CompanyNameSelector)),\
                            EC.presence_of_element_located((By.CSS_SELECTOR, CompanyBasicInfoSelector)),\
                            EC.presence_of_element_located((By.CSS_SELECTOR, CompanyIntroSelector)))
        page404EC = EC.presence_of_element_located((By.CSS_SELECTOR, Page404))
        pageStillConstruction = EC.presence_of_element_located((By.CSS_SELECTOR, ".incomplete_tips"))

        ansIndex = [-1]
        allEC = OrEC(ansIndex, hasRealDataEC, page404EC, pageStillConstruction)        
        try:
            element = WebDriverWait(browser, 10).until(allEC)
        except Exception, e:   
            print "Error in wait page element load finish: ", e
            return ResultShouldWait

        ansIndex = ansIndex[0]
        if ansIndex == 0:
            return ResultOK
        elif ansIndex == 1:
            print "page404"
            return ResultTerminate
        elif ansIndex == 2:
            print u"company page still construction"
            return ResultTerminate
        else:
            print u"Error ansIndex:", ansIndex
            return ResultTerminate

    waitLoadPageFinishType = waitFunctionFinish(ensureLoadPage)
    if waitLoadPageFinishType == WaitTerminate:
        return answer
    if waitLoadPageFinishType == WaitTimeExceed:
        print u'wait page load time exceed'
        return answer
    content = ""

    # 获取 公司简介内容content：
    soup = BeautifulSoup(browser.page_source, HtmlParser)

    if len(soup.select(ExpandOrFoldSelector)) == 0:
        content = soup.select(CompanyIntroSelector)[0].text
        print "no expand button"
    elif soup.select(ExpandOrFoldSelector)[0].attrs.has_key("style") and\
         soup.select(ExpandOrFoldSelector)[0].attrs["style"].find("none") != -1:
        content = soup.select(CompanyIntroHasExpandSelector)[0].text
        print "expand button must be hided "
        
    else :
        def checkExpandClickFinish():
            global browser
            soup = BeautifulSoup(browser.page_source, HtmlParser)
            if soup.select(ExpandOrFoldSelector)[0].text == u'收起':
                return ResultOK
            else:
                print u"not found expand button"
                return ResultShouldWait

        def ensureClickFinish():
            global browser
            try:
                browser.find_element_by_css_selector(ExpandOrFoldSelector).click()
            except Exception, e:
                print "ensureClickFinish exception occurs: ", e
                return ResultShouldWait

            waitType = waitFunctionFinish(checkExpandClickFinish, maxWaitTime = 2, sleepSeconds = 0.2 )
            if waitType == WaitOK:
                return ResultOK
            elif waitType == WaitTimeExceed:
                return ResultShouldWait
            else:
                print u"unknown waitType in ensureChickFinish"
                return ResultTerminate

        waitType = waitFunctionFinish(ensureClickFinish, 30)
        soup = BeautifulSoup(browser.page_source, HtmlParser)                
        if waitType == WaitOK:
            content = soup.select(CompanyIntroHasExpandSelector)[0].text
        else:
            print u'expand the company intro info not successful'
            content = soup.select(CompanyIntroSelector)[0].text



    content = content.encode(encodeName, "ignore")
    total = int(filter(unicode.isdigit, soup.select(CompanyNavsSelector)[1].text))
    name = soup.select(CompanyNameSelector)[0].text.strip()
    info = soup.select(CompanyBasicInfoSelector)
    tag = info[0].find('span').text.encode(encodeName, "ignore")
    process = info[1].find('span').text.encode(encodeName, "ignore")
    


    print "company cid:", cid
    print "company name:", name
    print "company content:", content
    print "company tag:", tag
    print "company process:", process
    print "company total:", total

    answer = {
        "cid":cid, 
        "name":name, 
        "content":content, 
        "tag":tag, 
        "process":process, 
        "total":total, 
    }
    return answer


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


def getCompanyInfo(cid):

    global browser
    if browser == None:
        browser = getFirefoxBrowser()
    
    answer = {
        "cid":-1, 
        "name":"", 
        "content":"", 
        "tag":"", 
        "process":"", 
        "total":"", 
    }
    try:        
        answer = _getCompanyInfo(cid)
    except Exception, e: # 当有任何Exception时候，直接pass
        print "Exception in getCompanyInfo", e

    answer["url"] = getCompanyInfoUrl(cid)
    answer["salary"] = []
    time.sleep(2)
    return answer



if __name__ == '__main__':

    for cid in range(22824, 52824 + 1):
        # answer = getCompanyInfo(cid)
        answer = getCompanyInfo(cid)
        print "answer:" + "-"*50
        print "answer cid:", answer['cid']
        print "answer name:", answer['name']
        print "answer content:", answer['content']
        print "answer tag:", answer['tag']
        print "answer process:", answer['process']
        print "answer total:", answer['total']
        print "answer url:", answer['url']
        print "answer salary:", answer['salary']


    # try:        
    #     getCompanyInfo(cid, browser)
    # except Exception, e: # 当有任何Exception时候，直接pass
    #     print "Exception in getCompanyInfo", e
    # time.sleep(2)
# getPosition(cid, browser)