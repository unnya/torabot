import base64
from asyncio import coroutine
from .base import Base


class Env(Base):

    def __init__(self, d):
        super(Env, self).__init__()
        self.d = d

    @coroutine
    def read(self, name):
        for f in self.d:
            if f['name'] == name:
                return base64.b64decode(f.content)
        raise Exception('no file named %s' % name)
