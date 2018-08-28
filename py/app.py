import logging; logging.basicConfig(level=logging.INFO)
import asyncio
import os
import json
import time
from datetime import datetime
from aiohttp import web


def index(request):
    return web.Response(body=b'<html><h1>Awesome</h1></html>', content_type='text/html')


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9999)
    logging.info('server started at http://192.168.8.60:9999')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
