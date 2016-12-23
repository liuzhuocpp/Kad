#coding=utf-8



from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys  
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time  
from selenium.webdriver.common.proxy import *

# 'proxy': 'HWJB1R49VGL78Q3D:0C29FFF1CB8308C4@proxy.abuyun.com:9020'
myProxy= 'proxy.abuyun.com:9020'



option = webdriver.ChromeOptions()
option.add_argument('--user-data-dir=C:\Users\LZ\AppData\Local\Google\Chrome\User Data\Default') #设置成用户自己的数据目录
option.add_argument('--proxy-server=%s' % myProxy)


browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=option)

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
