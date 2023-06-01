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



send_addr = 'ka@industriation.ru'


#send_addr = 'petraevvladimirmailru@mail.ru'
id = "3d33e0bfdf054c8690e95e47286a224c"
token = "y0_AgAAAABpdHKKAAmLJQAAAADh8wCrJJ0g0oOJQb6o2fRiGeKksfzUq6M"
secret = "b5b951dfcdd442079cb4d863d6532532"
host_server = "imap.yandex.ru"
login='testindustriation@yandex.ru'
password = '125478963Qq'

filepath_up = 'tovars-pemaks-update-price.csv'
filepath_nl = 'tovars-pemaks-null-price.csv'
filename_up = os.path.basename(filepath_up)
filename_nl = os.path.basename(filepath_nl)


def send_mes(message:str):
    msg = MIMEMultipart()
    msg['From'] = login
    msg['To'] = send_addr
    msg['Subject'] = Header(f"Обновление цен Пемакс {datetime.now()}",'utf-8')
    msg.attach(MIMEText(message))

    if os.path.isfile(filepath_nl):  # Если файл существует
        ctype, encoding = mimetypes.guess_type(filepath_nl)  # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:  # Если тип файла не определяется
            ctype = 'application/octet-stream'  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
        if maintype == 'text':  # Если текстовый файл
            with open(filepath_nl) as fp:  # Открываем файл для чтения
                file = MIMEText(fp.read(), _subtype=subtype)  # Используем тип MIMEText
                fp.close()  # После использования файл обязательно нужно закрыть
        else:  # Неизвестный тип файла
            with open(filepath_nl, 'rb') as fp:
                file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
                file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
                fp.close()
            encoders.encode_base64(file)
    file.add_header('Content-Disposition', 'attachment', filename=filename_nl)
    msg.attach(file)

    if os.path.isfile(filename_up):  # Если файл существует
        ctype, encoding = mimetypes.guess_type(filename_up)  # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:  # Если тип файла не определяется
            ctype = 'application/octet-stream'  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
        if maintype == 'text':  # Если текстовый файл
            with open(filename_up) as fp:  # Открываем файл для чтения
                file = MIMEText(fp.read(), _subtype=subtype)  # Используем тип MIMEText
                fp.close()  # После использования файл обязательно нужно закрыть
        else:  # Неизвестный тип файла
            with open(filename_up, 'rb') as fp:
                file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
                file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
                fp.close()
            encoders.encode_base64(file)
    file.add_header('Content-Disposition', 'attachment', filename=filename_up)
    msg.attach(file)

    mailserver = smtplib.SMTP('smtp.yandex.ru', 587)
    mailserver.ehlo(login)
    mailserver.starttls()
    mailserver.ehlo(login)
    mailserver.login(login, password)
    mailserver.sendmail(login, send_addr, msg.as_string())
    mailserver.quit()


def read_native_table():
    data = {}
    data['client_id'] = 'vvt31323'
    data['query'] = []
    data['query'].append({'select':'product_id, model, price, sku','where':'manufacturer_id = 2850'})
    zap_json = str(json.dumps(data))#, ensure_ascii=False)
    zap_json = zap_json.replace(']', '')
    zap_json = zap_json.replace('[', '')
    #print(zap_json)
    basic = HTTPBasicAuth('admin', '^*&GKJG*%*&5312')
    head = {'Content-type':'application/json', 'Content-Length':str(len(zap_json))}
    url = 'https://products.industriation.com/api.php?api=get_product&other_db=ind_db'
    x = requests.post(url, str(zap_json), auth=basic,headers=head)
    x = json.loads(str.encode(x.text, encoding='utf-8'))

    dop_data = {}
    for i in x['results']:
        dop_data[i['model']] = {}
        dop_data[i['model']]['product_id'] = i['product_id']
        dop_data[i['model']]['price'] = i['price']
        dop_data[i['model']]['sku'] = i['sku']

    rez_data = dop_data
    # rez_data = {}
    # rez_data['nums'] = {}
    # rez_data['strs'] = {}
    #
    # for i in dop_data:
    #     flag = False
    #     for j in i:
    #         if (not (j in ('-','.','/')) and ((ord('9') < ord(j)) or (ord(j) < ord('0')))):
    #             flag = True
    #             break
    #     if flag:
    #         rez_data['strs'][i] = dop_data[i]
    #     else:
    #         rez_data['nums'][i] = dop_data[i]

    # for i in rez_data:
    #     print(i,'====', rez_data[i],'\n')
    return rez_data



def post_read(old, data):
    f_null = open('tovars-pemaks-null-price.csv', 'w', encoding='utf-8')
    names_not_null = ['product_id', 'price', 'date']
    names_null = ['product_id', 'sku', 'date']
    wr_nulls = csv.DictWriter(f_null, delimiter=';', lineterminator="\r", fieldnames=names_null)

    wr_nulls.writeheader()
    wr_nulls.writerow({'date': str(datetime.now())})
    mass_null = []
    for i in old:
        flag = True
        for j in data['products']:
            if (old[i]['product_id'] == j['product_id']):
                flag = False
                break
        if(flag):
            wr_nulls.writerow({'product_id': old[i]['product_id'], 'sku': old[i]['sku']})
            mass_null.append(str(old[i]['product_id']))

    for s in mass_null:
        data['products'].append({"product_id":s, "benchmark_price": float(0.0000), "remote_store": 0,"remote_store_days": 0})
    f_null.close()
    # f_null = open('tovars-pneumax-null-price.csv', 'w', encoding='utf-8')
    # for s in mass_null:
    #     wr_nulls.writerow({'product_id': s, 'model': s})
    #     data['products'].append({"product_id":s, "price": float(0.0000), "remote_store": 0, "remote_store_days": 0})
    return len(mass_null), data
