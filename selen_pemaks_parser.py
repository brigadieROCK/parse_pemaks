from selenium.webdriver.common.by import By
from selenium import webdriver
from parsertools import *
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import time
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings('ignore')
client = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_argument("--headless")
client = webdriver.Chrome(chrome_options=options)


native_mass = read_native_table()#['PVSA-010-100', 'PS1-R-S2-12', 'PS1-FR-S3-34-A']
count_good, count_bad = 0,0

data = {}
data['client_id'] = 'vvt31323'
data['products'] = []

for mod in native_mass:
    finded_flag = True
    client.get(f'https://www.pemaks.ru/catalog/?q={mod}&sНайти')
    try:
        find_page = client.find_element(by=By.CLASS_NAME, value="dark_link").text#.get_attribute('href')
        # print(find_page)
        # print('=======================')
        # if(find_page.lower().find('найдено')!= -1):
        tovars = client.find_elements(by=By.CLASS_NAME, value="item_block")
        for i in range(len(tovars)):
            finded = tovars[i].find_element(by=By.CLASS_NAME, value="article_block").get_attribute('data-value')
            if(finded.lower().replace('артикул: ','').replace('-', '').replace(' ','') == mod.lower().replace('-', '').replace(' ', '')):

                price = tovars[i].find_element(by=By.CLASS_NAME, value="price").get_attribute('data-value')
                # rez_pars = rez_pars.split('./шт')
                # price = float(rez_pars[0].replace(u'\xa0', '').replace(' ', '').replace('руб', ''))
                aval = tovars[i].find_element(by=By.CLASS_NAME, value="value").text
                if(aval.replace(u'\n', '').lower() != 'нет в наличии'):
                    aval = aval[aval.find('(')+1:aval.find(')')]
                    # print('НАШЕЛ ОСТАТКИ ===>', aval)
                else:
                    aval = 0
                # print(mod, finded, float(float(price)/1.2), aval, sep=' ===> ')
                # print(mod, ' = ', finded, ' result===> ',price, ' ===> ', rez_pars[1].replace(u'\n', ''))
                count_good += 1
                finded_flag = False
                try:
                    data['products'].append({"product_id": native_mass[mod]['product_id'], "benchmark_price": float(float(price)/1.2),"remote_store": int(aval), "remote_store_days": 5})
                except:
                    print('Ошибка записи в JSON ---> ', native_mass[mod]['product_id'], price, aval, sep=' ')
            # else:
            #     print('не соответствует', mod, finded, sep=' ===> ')
        if(finded_flag):
            count_bad += 1

    #url_tovar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "myDynamicElement"))

        # print(url_tovar)
        # if (url_tovar != None):
        #     client.get(url_tovar)
        #     artic = client.find_element(by=By.CLASS_NAME, value='top_info').text
        #     #print(artic.replace('Артикул: ',''))
        #     if (artic.lower().replace('артикул: ','').replace('-', '').replace(' ','') == mod.lower().replace('-', '').replace(' ', '')):
        #         rez_pars = client.find_element(by=By.CLASS_NAME, value="prices_block").text
        #         rez_pars = rez_pars.split('./шт')
        #         price = float(rez_pars[0].replace(u'\xa0', '').replace(' ', '').replace('руб', ''))
        #         if(rez_pars[1].replace(u'\n', '').lower() != 'нет в наличии'):
        #             aval = rez_pars[1].replace(u'\n', '').lower()
        #             print('НАШЕЛ ОСТАТКИ ===>', aval)
        #         else:
        #             aval = 0
        #         print(mod, ' = ', artic, ' result===> ',price, ' ===> ', rez_pars[1].replace(u'\n', ''))
        #         count_good += 1
        #         try:
        #             data['products'].append({"product_id": native_mass[mod]['product_id'], "benchmark_price": float(price),"remote_store": int(aval), "remote_store_days": 5})
        #         except:
        #             print('Ошибка записи в JSON ---> ', native_mass[mod]['product_id'], price, aval, sep=' ')
    except:
        # print('error bluat')
        continue
        # url_tovar = client.find_element(by=By.CLASS_NAME, value="middle").text
        # print(mod, ' ===> ',url_tovar)




nulls, data = post_read(native_mass, data)

f = open('tovars-pemaks-update-price.csv', 'w', encoding='utf-8')
names = ['product_id', 'benchmark_price','remote_store', 'date']
wr = csv.DictWriter(f, delimiter = ';',lineterminator="\r", fieldnames=names)
wr.writeheader()
wr.writerow({'date':str(datetime.now())})
for i in data['products']:
    wr.writerow({'product_id':i['product_id'], 'benchmark_price':i['benchmark_price'], 'remote_store':i['remote_store']})
f.close()

basic = HTTPBasicAuth('login', 'pasword')
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
    send_mes('Количество обновленных товаров : ' + str(count_good) + '\nКоличество товаров без цены : ' + str(nulls) + '\nЧасть товаров не была обновленна по неизвестным причинам')
else:
    send_mes('Количество обновленных товаров : ' + str(count_good) + '\nКоличество товаров без цены : ' + str(nulls))
# print(count_good)
# soner = json.dumps(data, indent=4)
# file = open("selen-soner.json", "w")
# # file.write(f'Update: {updt_price}\n Null-price :{null_count}')
# file.write(soner)
# file.close()
