import aiomysql
import logging


logging.basicConfig(level=logging.INFO)


async def create_db_pool(loop, **kw):
    logging.info('create database connect pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', '127.0.0.1'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['database'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


async def select(sql, args, size=None):
    # logging(sql, args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info("rows return : %d", len(rs))
        return rs


async def execute(sql, args):
#    logging(sql, args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor()
        try:
            await cur.execute(sql.replace('?', '%s'), args)
            affect = cur.rowcount
            return affect
        except aiomysql.DatabaseError as e:
            print(e)
        finally:
            await cur.close()
        