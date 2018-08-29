import logging
import db
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name        = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default     = default

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super(StringField, self).__init__(name, ddl, primary_key, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='bigint'):
        super(IntegerField, self).__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='boorealean'):
        super(BooleanField, self).__init__(name, ddl, primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='real'):
        super(FloatField, self).__init__(name, ddl, primary_key, default)

class TextField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='text'):
        super(TextField, self).__init__(name, ddl, primary_key, default)

class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName  = attrs.get('__table__', None) or name
        mapping    = dict()      
        fields     = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                mapping[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field %s'
                                            % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary has not found')
        for k in mapping.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'   ] = mapping
        attrs['__table__'      ] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'     ] = fields
        attrs['__select__'] = 'select %s, %s from %s' % (
                               primaryKey, 
                               ','.join(escaped_fields), 
                               tableName)
        attrs['__insert__'] = 'insert into %s (%s, %s) values(%s)' % (
                              tableName, 
                              ','.join(escaped_fields), primaryKey,  
                              ','.join('?'*(len(escaped_fields)+1))
                              )                    
        attrs['__update__'] = 'update %s set %s where %s=?' % (
                              tableName, 
                              ','.join(map(lambda f: '%s=?' % (mapping.get(f).name or \
                                f), fields)),
                              primaryKey)
        attrs['__delete__'] = 'delete from %s where %s=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('Model obj has no attr %s' % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self ,key):
        return getattr(self, key, None)
    
    def getValueOrDefault(self, key):
        value = self.getValue(key)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if (callable(field.default)) else field.default
                logging.debug('using default value for %s:%s' % (key ,str(value)))
                setattr(self, key , value)
            
        return value
        
    @classmethod
    async def find(cls, pk):
        'find obj by primary key'
        rs = await db.select('%s where %s=?' % (cls.__select__, cls.__primary_key__),
                             [pk], 1)
        if rs is None or len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        'find all objs and return list<obj>'
        sql = [cls.__select__]
        if args is None:
            args = []
        if where:
            sql.append('where')
            sql.append(where)
        order_by = kw.get('order_by', None)
        if order_by:
            sql.append('order by')
            sql.append(order_by)
        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                args.append('limit')
                args.append((limit[0], limit[1]))
            else:
                raise AttributeError('limit len error')
        
        rs = await db.select('select * from %s' % (cls.__table__), [])
        if len(rs) == 0:
            return None
        return [cls(**r) for r in rs]

    async def save(self):
        'save obj in database'
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await db.execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record : affect rows %s' % (rows))

    async def update(self):
        'update values of obj in database'
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await db.execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update record : affect rows %s' % (rows))

    @classmethod
    async def remove(cls, pk):
        'delete obj in database'
        # args.append(self.getValueOrDefault(self.__primary_key__))
        logging.warn('prepare remove %d' % (pk))
        rows = await db.execute(cls.__delete__, [pk])
        if rows != 1:
            logging.warn('failed to delete record : affect rows %d' % (pk))
