
import pandas as pd
import re, time, requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json

# 加入使用者資訊(如使用什麼瀏覽器、作業系統...等資訊)模擬真實瀏覽網頁的情況
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

# 查詢的關鍵字
my_params = {'ro':'1', # 限定全職的工作，如果不限定則輸入0
             'keyword':'大數據', # 想要查詢的關鍵字
             'area':'6001001000', # 限定在台北的工作
             'isnew':'30', # 只要最近一個月有更新的過的職缺
             'mode':'l'} # 清單的瀏覽模式

url = requests.get('https://www.104.com.tw/jobs/search/?' , my_params, headers = headers).url
driver = webdriver.Chrome()
driver.get(url)


# 網頁的設計方式是滑動到下方時，會自動加載新資料，在這裡透過程式送出Java語法幫我們執行「滑到下方」的動作
for i in range(20): 
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(0.6)
    
# 自動加載只會加載15次，超過之後必須要點選「手動載入」的按鈕才會繼續載入新資料（可能是防止爬蟲）
k = 1
while k != 0:
    try:
        # 手動載入新資料之後會出現新的more page，舊的就無法再使用，所以要使用最後一個物件
        driver.find_elements_by_class_name("js-more-page",)[-1].click() 
        # 如果真的找不到，也可以直接找中文!
        # driver.find_element_by_xpath("//*[contains(text(),'手動載入')]").click()
        print('Click 手動載入，' + '載入第' + str(15 + k) + '頁')
        k = k+1
        time.sleep(1) # 時間設定太短的話，來不及載入新資料就會跳錯誤
    except:
        k = 0
        print('No more Job')


soup = BeautifulSoup(driver.page_source, 'lxml')
List = soup.findAll('a',{'class':'js-job-link'})
print('共有 ' + str(len(List)) + ' 筆資料')



columns = ['公司','職缺','工作內容','福利制度','薪水']
data = []

i = 0
while i < len(List):
    print('正在處理第' + str(i) + '筆，共 ' + str(len(List)) + ' 筆資料')
    content = List[i]
    header2 =  {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                "Referer" :"" 
    }
    
    # 這裡用Try的原因是，有時候爬太快會遭到系統阻擋導致失敗。因此透過這個方式，當我們遇到錯誤時，會重新再爬一次資料！
    try:
        code = content['href'].split('job/')[1].split('?')[0]
        header2["Referer"] = 'https://www.104.com.tw/job/' + code + '?jobsource=jolist_c_relevance'          
        url = 'https://www.104.com.tw/job/ajax/content/' + code
        resp = requests.get(url,headers = header2)
        
        json_str = resp.text
        json_data = json.loads(json_str)
        #json_data = json_data['data']
        
        
        each_data = []
        
        each_data.append(json_data['data']['header']['custName'])
        each_data.append(json_data['data']['header']['jobName'])
        each_data.append(json_data['data']['jobDetail']['jobDescription'])
        each_data.append(json_data['data']['welfare']['welfare'])
        each_data.append(json_data['data']['jobDetail']['salary'])
        
    
        
        data.append(each_data)
        
        each_data = []
        
        print("Success and Crawl Next 目前正在爬第" + str(i) + "個職缺資訊")
        time.sleep(0.5) # 執行完休息0.5秒，避免造成對方主機負擔
        i += 1
    except:
        print("Fail and Try Again!")

df = pd.DataFrame(data = data, columns = columns)

df.to_csv('./104_work.csv', index = 0, encoding = 'utf-8-sig')
