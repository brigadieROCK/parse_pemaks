import time

from parsertools import *
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import csv
import mimetypes                                          # Импорт класса для обработки неизвестных MIME-типов, базирующихся на расширении файла
from email import encoders                                # Импортируем энкодер
from email.mime.base import MIMEBase                      # Общий тип
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
#url = 'https://pneumax.ru/catalog/drosseli/t3006m5p_drocsel_pnevmaticheskiy_bez_obratnogo_klapana_iz_tekhnopolimera/'
import warnings
#ft = time.time()
native_mass = read_native_table()#['PMYA-16-025']
count = 0

data = {}
data['client_id'] = 'vvt31323'
data['products'] = []

for mod in  native_mass:
    try:
        one_page = requests.get(f'https://www.pemaks.ru/catalog/?q={mod}&sНайти')

        one_soup = BeautifulSoup(one_page.text, 'html.parser')

        item_soped = one_soup.find('div', class_ = 'item-title')
        if (item_soped != None):
            index = str(item_soped).find('href')+6
            ref = 'https://www.pemaks.ru' + str(item_soped)[index:str(item_soped).find( '">',index)]

            item_page = requests.get(ref)
            page_soup = BeautifulSoup(item_page.text, 'html.parser')
            # print(mod, ' ===> ', page_soup.find('span', class_='value', itemprop='value').text)
            if(page_soup.find('span', class_ = 'value', itemprop = 'value').text.lower().replace('-','') == mod.lower().replace('-','')):
                price_soup = page_soup.find('span', class_ = 'price_value')
                aval_souped = page_soup.find('div', class_='item-stock')
                if(price_soup != None):
                    price = float(price_soup.text.replace(u'\xa0', ''))
                    if (aval_souped.text.lower() == 'нет в наличии'):
                        # print(0)
                        aval = 0
                    else:
                        # print(page_souped.text)
                        aval = aval_souped.text[aval_souped.text.find('(')+1:aval_souped.text.find(')')]
                        # print(int(aval))
                    data['products'].append({"product_id": native_mass[mod]['product_id'], "benchmark_price": float(price), "remote_store": aval,"remote_store_days": 5})
                # print(count, ' ===> ', float(mas_soup.text.replace(u'\xa0', '')))
        count += 1
        if count == 1000:
            break
    except:
        print(page_soup)
        print('------------------------------')
        print(mod,"\n\n\n\n\n")


updt_price = len(data['products'])
null_count, data = post_read(native_mass, data)

basic = HTTPBasicAuth('admin', '^*&GKJG*%*&5312')
url = 'https://products.industriation.com/api.php?api=update_product&other_db=ind_db'

bad_flag = False

for i in range(0,len(data['products']),100):
    dop_massiv = data['products'][i:i+100]
    new_data = {}
    new_data['client_id'] = 'vvt31323'
    new_data['products'] = []
    new_data['products'].append(dop_massiv)
    new_rez = json.dumps(new_data)
    head = {'Content-type': 'application/json', 'Content-Length': str(len(new_rez))}
    new = requests.post(url, str(new_rez).replace('"products": [', '"products": ').replace(']]', ']'), auth=basic, headers=head)
    #f.write(new_rez)
    if(new.status_code == 200):
        time.sleep(0.5)
    else:
        bad_flag = True

if(bad_flag):
    send_mes('Количество обновленных товаров : ' + str(updt_price) + '\nКоличество товаров без цены : ' + str(null_count) + '\nЧасть товаров не была обновленна по неизвестным причинам')
else:
    send_mes('Количество обновленных товаров : ' + str(updt_price) + '\nКоличество товаров без цены : ' + str(null_count))

soner = json.dumps(data, indent=4)
file = open("soner.json", "w")
file.write(f'Update: {updt_price}\n Null-price :{null_count}')
file.write(soner)
file.close()



#
# print(time.time() - ft)

