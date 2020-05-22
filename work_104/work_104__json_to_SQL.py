
import pandas as pd
import re, time, requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import jieba
import os
from pandas.io.json import json_normalize


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

#----------------------自動翻頁-取湯結束--------------------

#創建存json資料夾
if os.path.exists('job104_json'):
    pass
else:
    os.mkdir('job104_json')
    
#------------------------迴圈將所有json存到資料夾-----------------------------------    
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
        json_data = json.loads(json_str)['data']
        filename = './job104_json/{}.json'.format(code)
        with open(filename, 'w', encoding = 'utf8') as f:
            json.dump(json_data,f) 
            # json.dump()用於將dict型別的資料轉成str，並寫入到json檔案中。#
        print('processing item: {}: write to {}'.format(i, filename))
        
        i += 1
    
    except:
        print("Fail and Try Again!")
        
        

#---------------定義資料處理函數-------------------


def json2pd(path):
    file_list=os.listdir(path)
    jobinfo_list=[]

    for each_file in file_list:
        cpath=source_file_path+'/'+each_file

        with open(cpath, 'r') as f:
            _jobinfo= json.loads(f.read())
        jobinfo_list.append(_jobinfo)  
        #將json做成2層資料結構
    return json_normalize(jobinfo_list, max_level=2)



def role_filter(rolelist):
    if isinstance(rolelist, list):
        rolelist_filter=[]
        for _role_dict in rolelist:
            rolelist_filter.append(_role_dict['description']) #選取字典description的值
        return rolelist_filter
    else:
        return rolelist

'''
isinstance(object, classinfo) 函数来判断一个对象是否是一个已知的类型，类似 type()。
object -- 实例对象。
classinfo -- 可以是直接或间接类名、基本类型或者由它们组成的元组。
'''

def skill_filter(skillDesc):
    jieba_list=jieba.cut(skillDesc, cut_all=False)
    skill_Dict={}
    for _skill in jobskill_def:
        skill_Dict[_skill] = 0
    
    for _word in jieba_list:
        _word = re.sub("[\!\%\[\]\,\。,\.]", "", _word)
        #_word = re.sub(u'[^0-9a-zA-Z\u4e00-\u9fa5.，,。？“”]+',"", _word)
        #print(_word)
        if _word.upper() in jobskill_def:
            skill_Dict[_word.upper()]=1 #不需要加1
    
    _job_skill_list=[]
    
    for k, v in skill_Dict.items():
         _job_skill_list.append(v)
        
    return _job_skill_list

#-----------------將JSON轉成pd.dataframe------------------------

source_file_path='./job104_json'
df=json2pd(source_file_path) #套用json2pd函數
jobskill_def=[]

with open('./jobskill.txt', 'r', encoding='utf-8') as file:
    for _skill in file.readlines():
        _skill = _skill.strip()
        jobskill_def.append(_skill.upper())

df['condition.other']=df['condition.other'].apply(skill_filter)
df[jobskill_def] = df['condition.other'].apply(pd.Series) # Series是一个一维的数据结构
df['condition.acceptRole.role']= df['condition.acceptRole.role'].apply(role_filter)


#df colunm selection
Index_header=['header.jobName', 'header.appearDate','header.custName', 'header.custUrl',
              'condition.acceptRole.role', 'condition.workExp', 'condition.edu',
              'condition.major', 'condition.language','condition.other',
              'jobDetail.salary', 'jobDetail.salaryMin', 'jobDetail.salaryMax',
              'jobDetail.addressRegion','jobDetail.needEmp',
              'contact.hrName', 'contact.email','contact.phone']

Index_header.extend(jobskill_def) #將jobskill_def附加在Index_header之後

df[Index_header].to_csv('./jbinfo_tmp.csv', index=0, encoding='utf-8-sig')
print("CSV output success!!")

df[Index_header].head()
work_104_df =df[Index_header]
len(work_104_df.columns)


#---------------輸入MySQL-------------
from sqlalchemy import create_engine

df = pd.read_csv("./jbinfo_tmp.csv", sep=',') 

def df_to_mysql(tableName, dataFrame, db):

    sqlEngine = create_engine('mysql+pymysql://root:Ttpp9819@127.0.0.1/{}'.format(db), pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    
    try:
        frame = dataFrame.to_sql(tableName, dbConnection ,if_exists='append',index=False);
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print("Table %s created successfully." % tableName);
    finally:
        dbConnection.close()
        
df_to_mysql('test104', df, 'crawler_104')

#--------------將整筆df直接匯入--------------------------------
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:Ttpp9819@localhost:3306/crawler_104')

work_104_df.to_sql('crawler_104', engine, index= False)

#----------------------------------------
df = pd.read_csv("./jbinfo_tmp.csv", sep=',') 
# 將新建的DataFrame儲存為MySQL中的數據表，不儲存index列 
df.to_sql('jbinfo_tmp', engine, index= False) 
print("Write to MySQL successfully!")


#-----------------------------------

#创建表头
sql = "CREATE TABLE work_104 \
    (code  VARCHAR(32),\
     charge  VARCHAR(100),\
     level VARCHAR(100),\
     name VARCHAR(100),\
     remark VARCHAR(100),\
         prov VARCHAR(100));"

def prem(db):
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print("Database version : %s " % data)  # 结果表明已经连接成功
    cursor.execute("DROP TABLE IF EXISTS jsondb")  
    sql = """create table jsondb(
    name varchar(100) not null, 
    releasetime varchar(255) not null,
    actor varchar(255) not null,
    score varchar(255) not null)"""
    cursor.execute(sql)  


'''
cursor.fetchone()：将只取最上面的第一条结果，返回单个元组如('id','name')，然后多次循环使用cursor.fetchone()，依次取得下一条结果，直到为空。

cursor.fetchall() :将返回所有结果，返回二维元组，如(('id','name'),('id','name')),
'''


