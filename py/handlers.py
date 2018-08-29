# -*- coding: utf-8 -*-

from webframe import get, post
from models import User
' url handlers '

@get('/test')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }