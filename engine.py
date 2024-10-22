#импорт библиотек
from flask import Flask, render_template, json, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_,inspect
from models import *
import qrcode
import datetime
from datetime import time,timedelta
import shutil
import os

#создание экземпляра класса Flask для работы скрипта в качестве веб сервера
app = Flask(__name__)

#указываем библиотеке SQLAlchemy путь до базы данных
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'

#создаем и устанавливаем в приложении секретный ключ для токенов и подписей
SECRET_KEY = 'x81k\xe5p\x9fBP\xea+b\xdfD\xd2\xbe3\xb6+\xf1\xc6@\xe6\xb7\xe8\xcc'
app.config['SECRET_KEY'] = SECRET_KEY
app.config.from_object(__name__)

#словарь, хранящий пути к иконкам на карте
icons_path = {
    'food': '../static/images/map-icons/food.png',
    'sleep': '../static/images/map-icons/sleep.png',
    'sight': '../static/images/map-icons/sight.png',
    'shopping': '../static/images/map-icons/shopping.png',
    'bank': '../static/images/map-icons/bank.png',
    'beauty': '../static/images/map-icons/beauty.png'
}

"""
    функция index, вызывающаяся при загрузке домашней страницы
    Функция по очереди обращается в базу данных и подгружает информацию о   достопримечательностях и их аттрибутах,
                                                                            гидах,
                                                                            страховках
    Затем структурирует их в словари для дальнейшей отправки на клиентскую часть приложения
"""
@app.route('/')
@app.route('/index')
def index():
    #создание массива с последующей подгрузкой данных в него в цикле
    results=[]

    for item in db_session.query(Sightseeings.id, Sightseeings.image, Sightseeings.name, Sightseeings.description, 
                                Sightseeings.price, Sightseeings.rating, Sightseeings.coord_x, 
                                Sightseeings.coord_y,Sightseeings.timeToSee,Sightseeings.schedule,
                                    Types.name,Categories.name).filter(and_(SightseeingsTypes.sightseeing_id==Sightseeings.id, 
                                                                            Types.id==SightseeingsTypes.type_id,
                                                                            SightseeingsCategories.sightseeing_id==Sightseeings.id,
                                                                            Categories.id==SightseeingsCategories.category_id)):

        results.append(item)

    guides=[]

    for items in db_session.query(Guides.id,Guides.name,
                                Guides.price, Types.name).filter(and_(
                                                        GuideTypes.guide_id==Guides.id,
                                                        Types.id==GuideTypes.type_id
                                                        )):
                                                    
        guides.append(items)
    
    insurance = []

    for item in db_session.query(Insurance.id,Insurance.name,Insurance.price):
        insurance.append(item)


    #структурирование полученных данных об объектах в словарь перебором
    resultsss= [
        {
            'id': row[0],
            'name':row[2],
            'x': row.coord_x, 
            'y': row.coord_y,
            'img': row.image,
            'desc':row.description,
            'price': row.price,
            'rating':row.rating,
            'tts': row.timeToSee,
            'schedule':row.schedule,
            'typee': row[10],
            'category': row[11]
        } 
        for row in results]

    #структурирование полученных данных о гидах в словарь перебором
    guidesss = [
        {
            'id': row[0],
            'name':row[1],
            'price':row[2],
            'typee':row[3],
        } 
    for row in guides]

    #структурирование полученных данных о страховках в словарь перебором
    insurancesss = [
        {
            'id': row[0],
            'name':row[1],
            'price':row[2]
        }
    for row in insurance]

    #закрываем соединение с базой данных
    db_session.close()

    #вызов шаблона страницы с отправкой полученных словарей на него                                                                         
    return render_template('index.html',
                            sights=json.dumps(resultsss),
                            guides = json.dumps(guidesss),
                            insur= json.dumps(insurancesss),
                            icons = json.dumps(icons_path))

#объявление пустых переменных для описания маршрута и краткого описания для qr-кода
text=''
qrtext = ''
#для qr-кода требуется укороченное описание, т.к. он может хранить в себе только 2953 символов из-за русской раскладки


"""
    Функция обработки POST-запроса клиентской части
    На вход мы получаем данные от клиента о выбранном маршруте, страховке и гиде.
    Т.к. из списка маршрута мы получаем точки в виде [название точки, координата Х, координата Y],
    обращаемся в базу данных для подгрузки информации о них по координатам, т.к. они уникальны
    Затем составляется описание маршрута и считается стоимость тура в зависимости от выбранных объектов
    А также, создается краткая версия описания для создания QR-кода
    Из-за того, что библиотека qrcode создает изображение в корневой папке проекта,
    Используется библиотека для переноса изображения shutil, потому что страницы, отображаемые flask, работают только с изображениями в папке Static

"""
#декоратор для обработки post-запроса
@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    #создаем массив, в который затем будем помещать информацию по объектам из базы данных
    data=[]

    #обращаемся к глобальным переменным описания маршрута и описанием для qr-кода, чтобы в последующем отправить их в get-запросе
    global text
    global qrtext

    #обнуляем эти переменные
    text=''
    qrtext = ''

    #проверяем какой тип запроса пришел
    if request.method == 'POST':
        #получаем данные от клиента о выбранном маршруте, страховке и гиде
        jsdata=request.get_json()
        #обходим список с точками из выбранного маршрута
        for point in jsdata['points']:
            #ищем совпадения в БД
            for item in db_session.query(Sightseeings.id, Sightseeings.image, Sightseeings.name, Sightseeings.description, 
                                Sightseeings.price, Sightseeings.rating, Sightseeings.coord_x, 
                                Sightseeings.coord_y,Sightseeings.timeToSee,Sightseeings.schedule,
                                    Types.name,Categories.name).filter(and_(Sightseeings.coord_x==float(point[1]),
                                                                            Sightseeings.coord_y==float(point[2]),
                                                                            SightseeingsTypes.sightseeing_id==Sightseeings.id, 
                                                                            Types.id==SightseeingsTypes.type_id,
                                                                            SightseeingsCategories.sightseeing_id==Sightseeings.id,
                                                                            Categories.id==SightseeingsCategories.category_id)):
                #добавляем точки в наш массив
                data.append(item)
        #закрываем соединение с БД
        db_session.close()
        #создаем переменную стоимости, времени, с учетом посещения объекта
        price=0
        time = datetime.timedelta(hours=7,minutes=0)
        
        #создаем переменные завтрака, обеда, ужина и ночевки, чтобы не повторялось в описании
        lunch = False
        breakfast=False
        dinner=False
        sleep=False


        #обходим элементы массива объектов
        for it in data:
            #добавляем в описание текст, т.к. по умолчанию, тур начинается в 7 утра
            if time>=datetime.timedelta(hours=7,minutes=0) and time<datetime.timedelta(hours=12,minutes=0) and breakfast==False:
                breakfast=True
                sleep=False
                text+= "Время завтрака. Выберите заведение по вкусу!\n\n"
            #добавляем название в описание маршрута и текст для qr-кода
            text+=f"{data.index(it)+1} точка  \nНазвание: {it[2]}"
            qrtext+=f"Название: {it[2]}\n"
            #добавляем в описание рейтинг, координаты, время на посещение и расписание работы
            text+= f"\nРейтинг: {it[5]} \nКоординаты: {it[6]} {it[7]} \nВремя, требующееся на посещение: {it[8]} \nЧасы работы: {it[9]} \n"

            #проверяем тип объекта
            if it[11]=='Еда' or it[11]=='Ночлег' or it[11]=='Развлечения':
                #добавляем в описание стоимость посещения
                text+= f"Стоимость: {it[4]}р.\n"
                qrtext+=f"Стоимость: {it[4]}р.\n\n"
                #добавляем в описание тип объекта
                text+=f"Тип: {it[10]} \n"
                #прибавляем стоимость посещения к общей стоимости тура
                price+=it[4]

            #добавляем в описание категорию объекта
            text+=f"Категория: {it[11]}\n\n\n"
            
            #устанавливаем формат входного времени из БД
            format = "%H:%M"
            #переводим элемент времени из строкового типа в тип time
            timeToSee=datetime.datetime.strptime(it[8],format).time()
            #затем переводим его в формат timedelta для калькуляций
            timeToSee=datetime.timedelta(hours=timeToSee.hour,minutes=timeToSee.minute)
            #рассчитываем время после посещения объекта
            time=time+ timeToSee

            #в зависимости от получившегося результата, добавлем в описание сообщение о необходимости пообедать, поужинать или переночевать
            if time>=datetime.timedelta(hours=12,minutes=0) and time<datetime.timedelta(hours=18,minutes=0) and lunch==False:
                text+="\nВремя обеда. Выберите заведение по вкусу!\n\n"
                lunch=True
            elif time>=datetime.timedelta(hours=18,minutes=0)  and time<datetime.timedelta(hours=22,minutes=0) and dinner==False:
                text+="\nВремя ужина. Выберите заведение по вкусу!\n\n"
                dinner=True
            elif time>=datetime.timedelta(hours=22,minutes=0) and sleep==False:
                breakfast,dinner,lunch=False
                time = datetime.timedelta(hours=7,minutes=0)
                sleep=True
                text+="\nВремя выбрать место для ночлега!\n\n"

        #проверяем наличие страховки
        if jsdata['insurance']==None:
            #если ее нет, то добавляем в описание "без страховки"
            qrtext+='Без страховки\n'
            text+='Без страховки\n'
        else:
            #если есть, то рассчитываем стоимость страховки как определенный процент от стоимости тура
            insur=price/100 * float(jsdata['insurance'].get('price'))
            #добавляем в описание организацию-страхователя и стоимость страховки
            text+=f'Страховка от компании: {jsdata["insurance"].get("name")}    \nСтоимость страховки: {insur}\n'
            qrtext+=f'Страховка от компании: {jsdata["insurance"].get("name")}    \nСтоимость страховки: {insur}\n'
            #прибавляем к итоговой стоимости стоимость страховки
            price+=insur

        #проверяем налчие гида
        if jsdata['guides']!=None:
            #добавляем имя гида и стоимость его услуг в описание
            text+=f'Гид: {jsdata["guides"].get("name")}    \nСтоимость услуг гида: {jsdata["guides"].get("price")}\n'
            qrtext+=f'Гид: {jsdata["guides"].get("name")}    \nСтоимость услуг гида: {jsdata["guides"].get("price")}\n'
            #прибавляем к итоговой стоимости стоимость услуг гида
            price+=jsdata["guides"].get("price")

        #добавляем в описание итоговую стоимость тура
        text+=f'Общая стоимость тура: {price}р.\n\n'
        qrtext+=f'Общая стоимость тура: {price}р.\n\n'

        #задаем параметры qr-кода
        qr = qrcode.QRCode(
            version=2,      # use upper level version
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            )
        #добавляем текст в qr-код
        qr.add_data(qrtext)
        #создаем qr-код
        qr.make(fit=True)

        #задаем цвета qr-кода
        qrcodeImg= qr.make_image(fill_color='black',back_color='white')
        #сохраняем qr-код в виде изображения
        qrcodeImg.save('qrcode.png')

        #если qr-код уже существует в папке static, то удаляем его
        try:
            os.remove('static/qrcode.png')
        except:
            pass
        
        #переносим изображение в папку static
        shutil.move('qrcode.png','static')

        #удаляем дубликат изображения в корневой папке
        try:
            os.remove('qrcode.png')
        except:
            pass

    #возвращаем 'ok' так так для работы маршрутиризации flask нужно что либо возвращать из функции
    return 'ok'


"""
    Функция обработки GET-запроса от клиента
    Функция возвращает клиенту описание маршрута и путь до изображения с qr-кодом
"""
#декоратор обработки get-запросов
@app.route('/test', methods = ['GET'])
def get_request():
    #проверка типа запроса
    if request.method == 'GET':
        #добавляем в переменную словарь с путем до изображения qr-кода и описание маршрута, приводим его в формату json-файла (нужно для корректной обработки JavaScript функциями)
        data=jsonify({'qrcode':'../static/qrcode.png','text':text})
        #отправляем информацию клиенту
        return data

#запуск серверного приложения на локальной машине
if __name__=="__main__":
    app.run(host='0.0.0.0')