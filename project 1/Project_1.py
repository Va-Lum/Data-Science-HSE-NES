#!/usr/bin/env python
# coding: utf-8

# Здесь все загружаемые модули, словари и функции которые понадобятся для работы с программой. Запустите их сразу

# In[1]:


import numpy as np
import pandas as pd
from IPython.core.display import HTML
import requests
from bs4 import BeautifulSoup
import sys
get_ipython().system('"{sys.executable}" -m pip install selenium')
get_ipython().system('"{sys.executable}" -m pip install plotly_express')
import plotly 
import plotly_express as px
from selenium.webdriver import Chrome
from time import sleep
from selenium.webdriver.common import keys
from selenium.common.exceptions import NoSuchElementException
from IPython.display import clear_output, display
from datetime import datetime, date, time
from ipywidgets import Button


# In[2]:


format_str = '%d/%m/%Y' 

month_conv = {' янв. ': '/01/',
              ' фев. ': '/02/',
              ' мар. ': '/03/',
              ' апр. ': '/04/',
              ' мая. ': '/05/',
              ' июн. ': '/06/',
              ' июл. ': '/07/',
              ' авг. ': '/08/',
              ' сен. ': '/09/',
              ' окт. ': '/10/',
              ' ноя. ': '/11/',
              ' дек. ': '/12/'}


# In[3]:


def sortby_Name(df):
    return(df.sort_values("Game Name"))

def sortby_Rating(df):
    df['temp_column'] = [0 if rt =='' else int(rt[:-1]) for rt in df["Rating"]]
    df = df.sort_values("temp_column", ascending=False)
    df = df.drop("temp_column", axis = 1)
    return(df)

def sortby_Num_Rating(df):
    df['temp_column'] = [0 if nrt =='' else int(nrt.replace(",", "")) for nrt in df["Number of Ratings"]]
    df = df.sort_values("temp_column", ascending=False)
    df = df.drop("temp_column", axis=1)
    return(df)

def sortby_Price(df):
    df['temp_column'] = [-1 if pr =='' else 0 if (pr =='Бесплатно' or pr =='Демо') else float(pr.replace("pуб.", "").replace(",", ".")) for pr in df["Ordinary Price"]]
    df = df.sort_values("temp_column", ascending=False)
    df = df.drop("temp_column", axis=1)
    return(df)

def sortby_Price_Now(df):
    df['temp_column'] = [-1 if pr =='' else 0 if (pr =='Бесплатно' or pr =='Демо') else float(pr.replace("pуб.", "").replace(",", ".")) for pr in df["Price Now"]]
    df = df.sort_values("temp_column", ascending=False)
    df = df.drop("temp_column", axis=1)
    return(df)

def standart_sort(df):
    return(df.sort_index())

def sortby_Date(df):
    df['temp_column'] = [ date(1,1,1) if dt =='' else dt for dt in df["Release Date"]]
    dtt = []
    for dt in df['temp_column']:
        if dt !=date(1,1,1):
            for key in month_conv.keys():
                dt = dt.replace(key, month_conv[key])
            dtt.append(datetime.strptime(dt, format_str).date())
        else:
            dtt.append(dt)
    df['temp_column'] = dtt
    df = df.sort_values("temp_column", ascending=False)
    df = df.drop("temp_column", axis=1)
    return(df)


# Сама программа, для её работы понадобится файл Labels.txt, который будет в архиве и будет необходимо припосать путь к нему в первой строке программы.
# В вводах меток и сортироки можно писать что угодно программа просто не пустит неправильные значения, но в других вводах пожалуйста пишите в нужном формате.
# Так же необходим хром драйвер и к нему тоже нужно будет прописать путь в 23 строке.

# Так как у разных людей разная скорость интернета страницы могут грузиться дольше чем считывается информация, поэтому настройте параметры команды sleep под себя (К примеру если в таблички повторяются игры, то его следует увеличить). Так же не советую писать по одной метке или all, это ну очень много игр, а значит программа будет работать долго.

# Достаточно неплохой вариант для запуска программы по меткам: 'Инди, Шахматы'. Там 2 страницы, 40 игр.

# In[8]:


# ........................................................................................................................................................................................................................................
f = open(r'C:\Users\vadim\Desktop\Labels.txt', 'r')
Labels = f.read().split("\n")
print("Введите все метки через запятую и пробел, если не знаете как пишутся метки напишите 'метки'\nЕсли хотите вывести все игры, то пишите All. ")
Labs = input().split(", ")
if Labs == ["Тодд Говард"]:
    print("Купи Скайрим!")
while True:
    if set(Labs).issubset(Labels) or Labs ==['All']:
        break
    elif ((Labs == ['метки']) or (Labs==["'метки'"])):
        print("метки в Steam: ")
        print(Labels)
        print("Введите метки игры:")
        Labs = input().split(", ")
    else:
        print("вводите только метки указанные в списке 'метки'")
        Labs = input().split(", ")
f.close() 

# часть принимающая общий список меток и частный от человека.


driver = Chrome(executable_path="C://Users/vadim/Desktop/chromedriver.exe")
driver.get("https://store.steampowered.com/search/?")
Sett = driver.find_element_by_css_selector(".dropdown")
Sett.click()
Sett = driver.find_element_by_css_selector(".item~ .item+ .item")
Sett.click()                                                     #эти четыре строки добавляют в список 600 игр изключённых из-за фильтра стима.
if Labs !=['All']:
    form  = driver.find_elements_by_css_selector("#TagSuggest")[0]
    for Lab in Labs:
        form.send_keys(Lab)
        cell = driver.find_element_by_xpath("//div[@data-loc='" + Lab + "']")
        cell.click()
        form.clear()
sleep(10)

# часть оставляющая в списке только игры с нужными метками

Pics = []
Names = []
Dates = []
Rates = []
Rates_N = []
Prices = []
Prices_Now = [] #еее, скидки!

for i in range(2400):
    
    Pics_on_Page = driver.find_elements_by_css_selector("#search_result_container img")
    for Pic in Pics_on_Page:
        Pics.append('<img src="'+ Pic.get_attribute('src') + '" width="60" >')
    
    Names_on_page = driver.find_elements_by_css_selector(".title")
    Names.extend([name.text for name in Names_on_page])
    
    Dates_on_page = driver.find_elements_by_class_name("search_released")
    Dates.extend([date.text for date in Dates_on_page])
    
    Rates_on_page = driver.find_elements_by_class_name("search_reviewscore")
    for R in Rates_on_page:
        try:
            R = R.find_element_by_class_name("search_review_summary").get_attribute("data-tooltip-html")
            R_N = R[R.find("из")+3:R.find("об")]
            R = R[R.find("<")+4:R.find("%")+1]
        except NoSuchElementException:
            R = ''
            R_N=''
        Rates.append(R)
        Rates_N.append(R_N)
    
    Prices_on_page  =  driver.find_elements_by_class_name("search_price")
    for Price in Prices_on_page:
        Price = Price.text
        if Price.count('pуб') != 2:
            Prices.append(Price)
            Prices_Now.append(Price)
        else:
            Prices.append(Price.split("\n")[0])
            Prices_Now.append(Price.split("\n")[1])
    
    try:
        arrow = driver.find_element_by_css_selector("a+ .pagebtn")
        arrow.click()
        sleep(10)
    except Exception as e:
        break
        
driver.quit()
        
clear_output()
        
d = {"Icon":Pics, "Game Name":Names, "Release Date": Dates, "Rating": Rates,"Number of Ratings":Rates_N, "Ordinary Price": Prices, "Price Now":Prices_Now}
df = pd.DataFrame(d)

if len(df.index) == 0:
    sys.exit("Игр с таким набором меток нет")

display(HTML(df.style.set_properties(**{'index-align': 'left', 'text-align': 'left'}).render()))

# а теперь сортировки

func_dic = {"Game Name": sortby_Name, "Release Date": sortby_Date, "Rating": sortby_Rating, "Number of Ratings": sortby_Num_Rating, "Ordinary Price":sortby_Price, "Price Now": sortby_Price_Now, "Standart": standart_sort}

print("по какой характеристике сортируем? Если не хотите сортировать напишите стоп.")
sleep(1)
Sor = input()

while Sor != "стоп":
    sleep(2)
    if Sor == "вводите нормально":
        print("vvedite normalno")
    elif (Sor in func_dic) or (Sor == "стоп"):
        df = func_dic[Sor](df)
        clear_output()
        display(HTML(df.style.set_properties(**{'index-align': 'left', 'text-align': 'left'}).render()))
        print("Можете отсортировать ещё раз, если хотите вернуться к стандартной сортировке напишите 'Standart', Если хотети прекратить напишите 'стоп'")
    else:
        print("вводите нормально")
    Sor = input()
    
    
#уберём игры которые не укладываются в диапазон цен/оценок

print("введите диапазон цен в формате 'от N до M'(N,M >= 0). Можно опустить одну часть или оставить пустой ввод для всех игр")
PrRange = input()
PrRange = PrRange.split(" ")
if 'от' in PrRange:
    PrRangeL = int(PrRange[1])
    if 'до' in PrRange:
        PrRangeR = int(PrRange[3])
    else:
        PrRangeR = 1000000 #здесь стоило бы использовать sys.maxsize, но так как в стиме точно нет ничего дороже миллиона, то пусть будет так
else:
    PrRangeL = -2
    if 'до' in PrRange:
        PrRangeR = int(PrRange[1])
    else:
        PrRangeR = 1000000
        
df['temp_column'] = [-1 if pr =='' else 0 if (pr =='Бесплатно' or pr =='Демо') else float(pr.replace("pуб.", "").replace(",", ".")) for pr in df["Ordinary Price"]]
df = df[np.logical_and(df['temp_column']>PrRangeL, df['temp_column']<=PrRangeR)]
df = df.drop(['temp_column'], axis = 1)

print("введите диапазон оценок в формате 'от N до M'(0<=N,M<=100). Можно опустить одну часть или оставить пустой ввод для всех игр")
RtRange = input()
RtRange = RtRange.split(" ")
if 'от' in RtRange:
    RtRangeL = int(RtRange[1])
    if 'до' in RtRange:
        RtRangeR = int(RtRange[3])
    else:
        RtRangeR = 101 
else:
    RtRangeL = -2
    if 'до' in RtRange:
        RtRangeR = int(RtRange[1])
    else:
        RtRangeR = 101
        
df['temp_column'] = [-1 if rt =='' else int(rt[:-1]) for rt in df["Rating"]]
df = df[np.logical_and(df['temp_column']>RtRangeL, df['temp_column']<=RtRangeR)]
df = df.drop(['temp_column'], axis = 1)
clear_output()
display(HTML(df.style.set_properties(**{'index-align': 'left', 'text-align': 'left'}).render()))

#и снова сортировка 

print("Отсортируем новые значения")
print("по какой характеристике сортируем? Если не хотите сортировать напишите стоп.")
sleep(1)
Sor = input()

while Sor != "стоп":
    sleep(2)
    if Sor == "вводите нормально":
        print("vvedite normalno")
    elif (Sor in func_dic) or (Sor == "стоп"):
        df = func_dic[Sor](df)
        clear_output()
        display(HTML(df.style.set_properties(**{'index-align': 'left', 'text-align': 'left'}).render()))
        print("Можете отсортировать ещё раз, если хотите вернуться к стандартной сортировке напишите 'Standart', Если хотети прекратить напишите 'стоп'")
    else:
        print("вводите нормально")
    Sor = input()

#время покупок 

print('раз уж мы оставили только самые-самые игры, не пора ли выбрать те из них которые мы хотим купить?')
print('пишите названия игр через запятую')

pd.options.mode.chained_assignment = None
Basket = input()
if Basket =='':
    print("ну чтож пустая корзина, она на то и пустая. 0 Рублей.")
else:
    Basket = Basket.split(', ')
    df_Basket = df[df["Game Name"].isin(Basket)]
    df_Basket["Ordinary Price"] = df_Basket["Ordinary Price"].replace('pуб.','', regex=True).replace(',','.', regex=True).replace('Бесплатно',0, regex=True).replace('Демо',0, regex=True).replace('',0, regex=True)
    df_Basket["Price Now"] = df_Basket["Price Now"].replace('pуб.','', regex=True).replace(',','.', regex=True).replace('Бесплатно',0, regex=True).replace('Демо',0, regex=True).replace('',0, regex=True)
    df_Basket["Price Now"] = df_Basket["Price Now"].astype(float)
    df_Basket["Ordinary Price"] = df_Basket["Ordinary Price"].astype(float)
    Total = df_Basket.sum()["Ordinary Price"]
    Total_Now = df_Basket.sum()["Price Now"]
    print("Сейчас Общая сумма состовляет ", Total)
    print("Без скидок бы это стоило ",Total_Now)
    if Total == 0:
        Sale = 0
    else: 
        Sale = (1 - Total_Now/Total)*100
    print("А значит мы сэкономили ",Total-Total_Now,"рублей или ",Sale, "процентов"  )

sleep(5)

# насортировались? теперь пойдут графики.

clear_output()

df_new = df[["Rating", "Ordinary Price", "Game Name", "Number of Ratings"]]
df_new = (df_new[df_new['Rating']!=''])
df_new = (df_new[df_new['Ordinary Price']!=''])
df_new['Number of Ratings'] = [0 if nrt =='' else int(nrt.replace(",", "")) for nrt in df_new["Number of Ratings"]]
df_new["Ordinary Price"] = ['' if pr =='' else 0 if pr =='Бесплатно' else float(pr.replace("pуб.", "").replace(",", ".")) for pr in df_new["Ordinary Price"]]
df_new['Rating'] = ['' if rt =='' else int(rt[:-1]) for rt in df_new["Rating"]]

i = 0
Sc = []

print("А теперь графики")
print("графики исключают игры без цены, оценки или количества оценок")
print("тут придётся подождать, графики грузятся долго")

Sc.append(px.bar(df_new.sort_values(["Ordinary Price"], ascending=False), x="Game Name", y="Ordinary Price", title = plotly.graph_objs.layout.Title(text = "график распределения цен на игры", x = 0.5) ))

Sc.append(px.scatter(df_new, x="Ordinary Price", y="Rating", trendline="lowess", hover_name="Game Name", title = plotly.graph_objs.layout.Title(text = "график зависимости цены на игру и её оценки", x = 0.5) ))

Sc.append(px.scatter(df_new, x="Ordinary Price", y="Number of Ratings", trendline="lowess", hover_name="Game Name", title = plotly.graph_objs.layout.Title(text = "график зависимости цены на игру и её количества оценок", x = 0.5) ))

Sc.append(px.scatter(df_new, x="Number of Ratings", y="Rating", trendline="lowess", hover_name="Game Name" , title = plotly.graph_objs.layout.Title(text = "график зависимости количества оценок на игру и её оценки", x = 0.5)))

Sc.append("А где график? A нет графика"
          "¯\uFF3C_(ツ)_/¯")

button = Button(description="следующий график")
display(button)

def on_button_clicked(b):
    global i
    clear_output()
    if i <len(Sc):
        display(Sc[i])
        if i <len(Sс)-1:
            display(button)
    i = i+1

button.on_click(on_button_clicked)



# In[ ]:





# вторая чать проекта основанная на API

# Программа может работать долго так как обрабатывается большой массим данных

# Так как для ботов нельзя получить больше 500 значений, то некоторые года будут отображать именно это значение

# In[ ]:


enterpoint = "https://en.wikipedia.org/w/api.php"
params = {"action": "query", 
          "list": "categorymembers",
          "cmtitle":"Category:Video_games_by_year", 
          "cmlimit": 100,
          "format": "json"}
r = requests.get(enterpoint, params=params)
titles = [item['title'] for item in r.json()['query']["categorymembers"]]
titles = titles[3:-3]
years = [int(t[9:13]) for t in titles]
G = []
for title in titles:
    params = {"action": "query", 
          "list": "categorymembers",
          "cmtitle":title, 
          "cmlimit":999,
          "format": "json"}
    r = requests.get(enterpoint, params=params)
    G.append([item['title'] for item in r.json()['query']["categorymembers"]])
Games_by_year = dict(zip(years, G))
for i in range(1947, 2018):
    if not (i in Games_by_year.keys()):
        Games_by_year[i] = ['Нет Игр']
Num_of = {}
for key in Games_by_year.keys():
    if Games_by_year[key] == ['Нет Игр']:
        Num_of[key] = 0
    else:
        Num_of[key] = len(Games_by_year[key])
        
print('вводите год и будет выведено сколько игр вышло в этом году и их названия. Чтобы остановиться напишите 0')    

year = int(input('Введите год: '))

while year != 0:
    clear_output()
    if Num_of[year] < 500:
        print('в', year, 'вышло игр:', Num_of[year], '. А именно:')
        for game in Games_by_year[year]:
            print(game)
    else:
        print('в', year, 'вышло более 500 игр, в том числе:')
        for game in Games_by_year[year]:
            print(game)      
    year = int(input('Введите следующий год: '))
    


# Ссылка на саму категорию: https://en.wikipedia.org/wiki/Category:Video_games_by_year

# In[ ]:
