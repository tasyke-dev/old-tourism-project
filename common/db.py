#!/usr/bin/python2.6
# -*- coding: UTF-8 -*-
import os
import datetime
import calendar
import  time
import shutil
import urllib
import json
import yaml
import pickle
import tempfile
from itertools import groupby

from sqlalchemy.orm.attributes import InstrumentedAttribute, ScalarAttributeImpl
from sqlalchemy import Column, Integer, SMALLINT, Float, String, DateTime, Date, UnicodeText, Boolean, Unicode, ForeignKey, or_, not_, extract
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql import func, case

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

class TblMixIn(object):
    _as_dict_fields_ = []
    _from_dict_fields_ = []
    def __init__(self, **fields):
        for name, value in fields.iteritems():
            if hasattr(self, name):
                setattr(self, name, value)

        now = datetime.datetime.now()
        for field_date in ('creation_date', 'last_modified'):
            setattr(self, field_date, now)
##            if hasattr(self, field_date) and field_date not in fields:
##                setattr(self, field_date, now)



    def from_dict(self, *args, exclude=None, dict_obj=None):
        exclude = exclude or []
        dict_obj = dict_obj or {}
        keys = args or (list(self._sa_class_manager.keys())+self._from_dict_fields_)
        for k in keys:
            if k not in exclude and k in dict_obj:
               setattr(self, k, dict_obj[k])

    def as_dict(self, *args, exclude=None, **kwargs):
        exclude = exclude or []
        keys = args or (list(self._sa_class_manager.keys())+self._as_dict_fields_)
        result = dict((k, getattr(self, k)) for k in keys if k not in exclude)
        result.update(kwargs)
        popKeys = []
        for k,v in result.items():
            if type(v) in (datetime.datetime,datetime.date): result[k] = v.isoformat()
            elif type(v) == InstrumentedList: popKeys.append(k)
        list(map(result.pop, popKeys))
        return result

    def get_file(self, request_files, file_attr_name, path2save):
        def get_tmp_name():
            fd, fpath = tempfile.mkstemp()
            os.close(fd)
            os.remove(fpath)
            return os.path.basename(fpath)
        tmp_file = ""
        new_file = ""

        if file_attr_name in request_files and request_files[file_attr_name].filename != '':
            w_path = path2save
            if not os.path.isdir(w_path): os.makedirs(w_path)
            w_path = os.path.join(w_path, "{}")
            old_file = getattr(self, file_attr_name)
            if old_file and old_file.startswith("/"): old_file = old_file[1:]
            _file = request_files[file_attr_name]
            _filename = secure_filename(
                             os.path.basename(_file.filename)
                        )
            ext = os.path.splitext(_filename)[-1]
            tmp_file = w_path.format(get_tmp_name() + ext)
            new_file = w_path.format(_filename)
            _file.save(tmp_file)

            setattr(self, file_attr_name, "/"+tmp_file.replace("\\","/"))

##        if new_file:
##           #Означает что передавалась новая картинка и старую надо удалить
##           if os.path.isfile(old_file):
##              os.remove(old_file)
##           #os.rename(tmp_file, new_file)


    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)


    @classmethod
    def get_by_fields_query(cls, **kwargs):
        return cls.query.filter(*( getattr(cls, f_name) == value for f_name, value in kwargs.items() ))

    @classmethod
    def get_by_fields(cls, first=True, **kwargs):
        query = cls.get_by_fields_query(**kwargs)
        return query.first() if first else query

    @classmethod
    def dump_in_json(cls, attrs):
        cls_name = cls.__name__
        obj2dict_f = lambda o: dict((name, getattr(o, name)) for name in attrs)
        for o in cls.query.all():
            yield yaml.dump((cls_name, obj2dict_f(o)))




class UserCommon(TblMixIn):
    __tablename__ = 'users'
    id     = Column(Integer, primary_key=True)
    login  = Column(Unicode(255))
    fio  = Column(Unicode(255))
    password  = Column(Unicode(255))
    isAdmin   = Column(Boolean)
    blocked   = Column(Boolean)

    MESSAGE_INVALID_LOGIN       = { 'message': 'Неверный логин или пароль', 'message_e': 'Invalid credentials', 'authenticated': False }
    MESSAGE_INVALID_CREDENTIALS = { 'message': 'Invalid token. Registeration and / or authentication required', 'authenticated': False }
    MESSAGE_EXPIRED_TOKEN       = { 'message': 'Expired token. Reauthentication required.', 'authenticated': False }
    MESSAGE_BLOCKED             = { 'message': 'Account have been blocked.', 'authenticated': False }
    MESSAGE_USER_NOT_FOUND      = { 'message': 'User not found.', 'authenticated': False }
    MESSAGE_NEED_ADMIN          = { 'message': 'Need admin rights.', 'authenticated': False }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(self.password, method='sha256')

    def to_dict(self):
        return dict(id=self.id, login=self.login)

    def update_password(self, new, old=None):
        if old and not check_password_hash(self.password, old):
            return False
        self.password = generate_password_hash(new, method='sha256')
        return True




    def as_dict(self, *args, **kw):
        dct = super().as_dict(*args, **kw)
        dct["password"] = ""
        return dct



    @classmethod
    def authenticate(cls, **kwargs):
        login = kwargs.get('login')
        password = kwargs.get('password')

        if not login or not password:
            return None

        user = cls.query.filter_by(login=login).first()
        if not user or not check_password_hash(user.password, password):
            #raise Exception("User {} no correct password {}".format(user,password) )
            return None

        return user

class SettingsCommon(TblMixIn):
    __tablename__ = 'settings_json'
    name = Column(Unicode(255), primary_key=True)
    json_data = Column(UnicodeText)
    changed = Column(DateTime)
    _json = None

    @property
    def value(self):
        if self._json==None and self.json_data:
           self._json = yaml.load(self.json_data, Loader=yaml.Loader)
        return self._json

    @property
    def scalar(self):
        return self.value and self.value.get("value")

    @value.setter
    def value(self, v):
        self._json = v

    @classmethod
    def get(cls, name):
        return cls.get_by_fields(first=True,name=name) or cls(name=name)

    def update(self):
        self.changed = datetime.datetime.now()
        if self._json!=None: self.json_data = yaml.dump(self._json)
        self.query.session.add(self)
        self.query.session.commit()


    @classmethod
    def update_by_name(cls, name, value):
        obj = cls.get(name)
        obj.value = value
        obj.update()

class PersistentType(object):
      settings_class = None
      @property
      def settings_name(self):
          return self.__class__.__name__[:-4]

      def save(self):
          self.settings_class.update_by_name(self.settings_name, dict(self))

      def load(self, clearIt=True):
          if clearIt:dict.clear(self)
          s_obj = self.settings_class.get(self.settings_name)
          if type(s_obj.value) != dict and s_obj.value!=None: raise
          if s_obj.value!=None:
             dict.update(self, s_obj.value)



      @classmethod
      def wrap(cls, name,method):
          def f(self, *args, **kwargs):
              res = method(self, *args, **kwargs)
              self.save()
              return res
          setattr(cls, name, f)

      @classmethod
      def genPersistentClass(cls, classname, src_cls, methods):
          new_class = type(classname, (src_cls, cls),{})
          for m in methods:
             new_class.wrap(m, getattr(src_cls, m))
          return new_class

      @classmethod
      def genPersistentInstance(cls, classname, settings_class):
          new_class = type(classname+"_cls", (cls, ), dict(settings_class=settings_class))
          return new_class()

PersistentDict = PersistentType.genPersistentClass("PersistentType", dict, ["pop", "__setitem__", "clear", "update"])
