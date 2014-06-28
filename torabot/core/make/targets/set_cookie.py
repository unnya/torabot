import requests
import jsonpickle
from http.cookies import SimpleCookie
from .base import Base


class Target(Base):

    def __call__(self, request, set_cookie):
        assert isinstance(set_cookie, str) or isinstance(set_cookie, list), str(type(set_cookie))
        if not isinstance(request, dict):
            request = jsonpickle.decode(request)
        jar = request.get('cookies', requests.cookies.RequestsCookieJar())
        headers = request.get('headers', {})
        cookie = headers.get('Cookie')
        if cookie:
            jar.update(SimpleCookie(cookie))
            del headers['Cookie']
        cookies = [set_cookie] if isinstance(set_cookie, str) else set_cookie
        for cookie in cookies:
            jar.update(SimpleCookie(cookie))
        request['cookies'] = jar
        return jsonpickle.encode(request)