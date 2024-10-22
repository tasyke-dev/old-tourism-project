#загрузка библиотеки sqlalchemy и модуля db для создания классов таблиц
from common.db import TblMixIn

from sqlalchemy import create_engine,Column, Integer, String, ForeignKey,Float,DateTime,UnicodeText, select

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.orm import column_property, sessionmaker,scoped_session

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import text


#создание подключения к базе данных
engine= create_engine('sqlite:///data/data.db',convert_unicode=True)
#создание сессии для работы с базой данных
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
#создание переменной родительского класса таблиц из sqlaclhemy                                         
Base = declarative_base()
#создание очереди запросов для последующего создания таблиц
Base.query = db_session.query_property()

#функция для миграции базы данных (создания таблиц)
def create_db():
    Base.metadata.create_all(engine)


#класс таблицы объектов, наследующий аттрибуты из родительских классов "Base", "TblMixIn"
class Sightseeings(Base,TblMixIn):
    #установка названия таблицы
    __tablename__ = 'sightseeings'
    #создание столбцов в таблице для id, названия, описания, пути до изображения, стоимости посещения, рейтинга, координат,времени на посещение, расписания 
    #(где primary key - первичный ключ таблицы, autoncrement - автоинкремент при добавлении новой записи, nullable=false - запрет на нулевое значение в столбце)
    id =                Column(Integer,primary_key=True, autoincrement=True)
    name =              Column(String(50),nullable=False)
    description =       Column(String(300),nullable=False)
    image =             Column(String(100),nullable=False)
    price =             Column(Float,nullable=False)
    rating=             Column(Float,default=0.00)
    coord_x =           Column(Float,nullable=False)
    coord_y =           Column(Float,nullable=False)
    timeToSee =         Column(String(5))
    schedule =          Column(String(15))
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.id}, {self.name}, {self.description}, {self.image}, {self.price}, {self.rating},{self.coord_x}, {self.coord_y}, {self.timeToSee},{self.schedule}'


#класс таблицы гидов, наследующий аттрибуты из родительских классов "Base", "TblMixIn"
class Guides(Base,TblMixIn):
    #установка названия таблицы
    __tablename__ = 'guides'
    #создание столбцов в таблице для id, имени гида, стоимости услуг гида
    id =                Column(Integer,primary_key=True, autoincrement=True)
    name =              Column(String(50),nullable=False)
    price =             Column(Float,nullable=False)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.id}, {self.name}, {self.price}, {self.route}, {self.type})'

#класс таблицы отношения таблиц объектов и типов
class SightseeingsTypes(Base,TblMixIn):
     #установка названия таблицы
    __tablename__ = 'sightseeings_types'
    #создание столбцов в таблице для id объекта и id типа
    #(foreign key = ключ, который совпадает с id из таблицы, к которой он относится, например таблицей объектов
    # on delete cascade - удаление отношения между таблицами, если один из элементов (тип или объект), был удален)
    sightseeing_id =    Column(Integer,ForeignKey("sightseeings.id",ondelete='CASCADE'),nullable=False,index=True, primary_key=True)
    type_id =           Column(Integer,ForeignKey('types.id',ondelete='CASCADE'),nullable=False,index=True, primary_key=True)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.sightseeing_id}, {self.type_id}'

#класс таблицы отношения таблиц объектов и категорий
class SightseeingsCategories(Base,TblMixIn):
     #установка названия таблицы
    __tablename__ = 'sightseeings_categories'
    #создание столбцов в таблице для id объекта и id категории
    #(foreign key = ключ, который совпадает с id из таблицы, к которой он относится, например таблицей объектов
    # on delete cascade - удаление отношения между таблицами, если один из элементов (категория или объект), был удален)
    sightseeing_id =    Column(Integer,ForeignKey("sightseeings.id",ondelete='CASCADE'),nullable=False,index=True, primary_key=True)
    category_id =       Column(Integer,ForeignKey('categories.id',ondelete='CASCADE'),nullable=False,index=True, primary_key=True)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.sightseeing_id}, {self.category_id}'

#класс таблицы отношения таблиц гидов и типов
class GuideTypes(Base,TblMixIn):
     #установка названия таблицы
    __tablename__ = 'guide_types'
    #создание столбцов в таблице для id типа и id гида
    #(foreign key = ключ, который совпадает с id из таблицы, к которой он относится, например таблицей типов
    # on delete cascade - удаление отношения между таблицами, если один из элементов (тип или гид), был удален)
    type_id =           Column(Integer,ForeignKey("types.id",ondelete='CASCADE'),nullable=False,index=True, primary_key=True)
    guide_id =          Column(Integer,ForeignKey('guides.id',ondelete='CASCADE'),nullable=False,index=True, primary_key=True)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.type_id}, {self.guide_id}'


#класс вспомогательной таблицы типов объектов, наследующий аттрибуты из родительских классов "Base", "TblMixIn"
class Types(Base,TblMixIn):
    #установка названия таблицы
    __tablename__ = 'types'
    #создание столбцов в таблице для id, названия типа
    id =                Column(Integer,primary_key=True, autoincrement=True)
    name =              Column(String(50),nullable=False)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.id}, {self.name}'

#класс вспомогательной таблицы категорий, наследующий аттрибуты из родительских классов "Base", "TblMixIn"
class Categories(Base,TblMixIn):
    #установка названия таблицы
    __tablename__ = 'categories'
    #создание столбцов в таблице для id, названия категории
    id =                Column(Integer,primary_key=True, autoincrement=True)
    name =              Column(String(50),nullable=False)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.id}, {self.name}'

#класс таблицы страховок, наследующий аттрибуты из родительских классов "Base", "TblMixIn"
class Insurance(Base,TblMixIn):
    #установка названия таблицы
    __tablename__ = 'insurance'
    #создание столбцов в таблице для id, названия организации, стоимости услуг
    id =                Column(Integer,primary_key=True, autoincrement=True)
    name =              Column(String(50),nullable=False)
    price =             Column(Integer,nullable = False)
    #функция отображения для объектов класса, где по очереди выводятся все столбцы
    def __repr__(self):
        return f'{self.id}, {self.name}, {self.price}'