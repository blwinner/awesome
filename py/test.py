import db
import orm
import asyncio
from random import randint
from models import User, Blog, Comment

def test():
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
        for i in range(10):
            u = User(id=i, name='bl'+str(i))
            await u.save()
    loop.run_until_complete(save_data())

    lu = list()
    async def findAll():
        global lu
        lu = await User.findAll()
        print(lu)
    loop.run_until_complete(findAll())
    async def updateAll():
        for i in range(len(lu)):
            lu[i].name = lu[i].name + ' love tutu'
            await lu[i].update()
    # loop.run_until_complete(updateAll())
    # loop.run_until_complete(findAll())
    async def removeOne():
        await User.remove(randint(0, 10))
    loop.run_until_complete(removeOne())
    loop.run_until_complete(findAll())
    loop.run_forever()

async def test2():
    await db.create_db_pool(user='root', password='root', db='awesome')
    u = User(name='test', email='294336945@qq.com', passwd='test', image='about:blank')
    await u.save()

await test2()