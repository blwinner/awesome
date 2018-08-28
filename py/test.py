import db
import orm
import asyncio

class User(orm.Model):
    __table__ = 'user'
    id = orm.IntegerField('id', primary_key=True)
    name = orm.StringField('name')
loop = asyncio.get_event_loop()
async def init():
    await db.create_db_pool(loop, **{'user':'root', 'password':'root', 'db':'org'})
loop.run_until_complete(init())
async def save_data():
    u = User(id=123, name='bl')
    await u.save()
loop.run_until_complete(save_data())
loop.run_forever()