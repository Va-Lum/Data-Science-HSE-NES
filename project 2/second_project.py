#!/usr/bin/env python
# coding: utf-8

# Первым делом скачаем обе таблицы

# In[136]:


import sys
from natasha import DatesExtractor
import re
from numpy import prod


# In[8]:


get_ipython().system('"{sys.executable}" -m pip install google-cloud-bigquery')


# In[9]:


from google.cloud import bigquery


# В клиент вставьте свой ключ аккаунта Google Cloud Platform.

# In[10]:


client = bigquery.Client.from_service_account_json("Путь к вашему ключу")


# Первым делом мы сформируем запрос на русском языке. В этом запросе укажите время создания интересующего вас обекта(пожалуйста не пишите век, natasha их не распознаёт). Вернётся весь массив с точной датой (он выбирает основываясь на границах времени, но выдаёт более точный отрезок) и некоторую другую информацию. Я использовал 1956 год. В нём не так много данных

# In[45]:


input_information = input()
extractor = DatesExtractor()
Date_request = extractor(input_information)
Date_to_found = Date_request[0].fact.as_json["year"]


# In[66]:


df_of_objects  = client.query("""
SELECT object_name, title, culture, object_date, country, link_resource FROM  `bigquery-public-data.the_met.objects` 
WHERE object_begin_date <= {DATE} AND object_end_date >= {DATE} AND object_date IS NOT NULL
""".format(DATE=Date_to_found, )).to_dataframe() # из лекции можно вспомнить, что такой метод не очень надёжный, но так как Date_to_found точно будет числом, использовать его вполне безопасно.
df_of_objects = df_of_objects.style.set_properties( **{'width': '200px'})


# In[67]:


df_of_objects


# Теперь давайте найдём дополнително все фотографии этих объектов хранящиеся в базе данных.
# Некоторые ссылки выдают оштбку 404. Это из-за того, что база данных немного устарела.

# In[80]:


df_of_images  = client.query("""
SELECT object_name, BQTMobj.title, culture, object_date, country, link_resource, original_image_url FROM  `bigquery-public-data.the_met.objects` as BQTMobj
LEFT JOIN `bigquery-public-data.the_met.images` as BQTMimg ON BQTMobj.object_id = BQTMimg.object_id
WHERE object_begin_date <= {DATE} AND object_end_date >= {DATE} AND object_date IS NOT NULL
ORDER BY BQTMobj.object_id
""".format(DATE=Date_to_found, )).to_dataframe()
df_of_images = df_of_images.style.set_properties( **{'width': '200px'})
df_of_images


# Теперь мне хотелось бы найти самое позднее, самое ранные и среднее время надодок для каждой из культур.

# In[ ]:


client.query("""
SELECT culture, MIN(object_begin_date) AS Earliest, AVG((object_begin_date+object_end_date)/2) AS Average, MAX(object_end_date) AS Latest FROM `bigquery-public-data.the_met.objects`
GROUP BY culture
""").to_dataframe()


# Найдём культуры экспонаты для которой принадлежат только нашей эре и отдельно только до н.э.

# In[83]:


client.query("""
SELECT culture, MIN(object_begin_date) AS Earliest, AVG((object_begin_date+object_end_date)/2) AS Average, MAX(object_end_date) AS Latest FROM `bigquery-public-data.the_met.objects`
GROUP BY culture
HAVING MIN(object_begin_date)>0
""").to_dataframe()


# In[84]:


client.query("""
SELECT culture, MIN(object_begin_date) AS Earliest, AVG((object_begin_date+object_end_date)/2) AS Average, MAX(object_end_date) AS Latest FROM `bigquery-public-data.the_met.objects`
GROUP BY culture
HAVING MAX(object_end_date)<0
""").to_dataframe()


# Теперь воспользуемся регулярными выражениями и попробуем найти все экспонаты у которых отображены все 3 размера в сантиметрах, а затем нйдём самые большой и маленький из этих объектов.

# In[115]:


df = client.query("""
SELECT dimensions FROM `bigquery-public-data.the_met.objects`
WHERE dimensions IS NOT NULL
""").to_dataframe()


# In[131]:


list_of_dims = df["dimensions"]
list_of_3dim = []
for dim in list_of_dims:
    dim =  re.findall("(?:\d+(?:\.\d*)?|\.\d+) × (?:\d+(?:\.\d*)?|\.\d+) × (?:\d+(?:\.\d*)?|\.\d+)", dim)
    if len(dim)>0 :
        list_of_3dim.extend(dim)


# In[145]:


list_of_volumes = []
for dim3 in list_of_3dim:
    d = dim3.split(' × ')
    d = [float(i) for i in d]
    list_of_volumes.append(prod(d))
print(" max - ",  max(list_of_volumes), "cm^3\n","min - ",  
min(list_of_volumes), "cm^3")

