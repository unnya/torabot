import abc
from .spy import spy


class InstanceField(object):

    def __get__(self, obj, cls):
        if cls is None:
            cls = type(obj)
        from ..core.mod import mod
        return mod(cls.name)


class Core(object, metaclass=abc.ABCMeta):
    '''mod without frontend'''

    instance = InstanceField()

    def __init__(self, conf={}):
        self.conf = conf

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractmethod
    def changes(self, old, new):
        pass

    def spy(self, query, timeout, options={}):
        return spy(
            self.name,
            query,
            timeout=timeout,
            slaves=self.conf.get('TORABOT_SPY_SLAVES', 1),
            options=options,
        )

    def expired(self, query):
        from datetime import datetime, timedelta
        return query.mtime + timedelta(seconds=self.life(query)) < datetime.utcnow()

    def life(self, query):
        from nose.tools import assert_equal
        t = self.conf.get('TORABOT_QUERY_EXPIRE', 0)
        assert_equal(int(t), t)
        return int(t)

    def sync_on_expire(self, query):
        return True


class Frontend(Core):
    '''mod with frontend'''

    has_advanced_search = False
    has_normal_search = True
    normal_search_prompt = ''
    description = ''
    allow_empty_query = False
    frontend_need_init = False
    frontend_options = {}
    completion_options = {}
    public = True

    def display_name(self):
        return self.name

    @abc.abstractmethod
    def format_notice_status(self, view, notice):
        pass

    @abc.abstractmethod
    def format_notice_body(self, view, notice):
        pass

    def notice_attachments(self, view, notice):
        return []

    def format_query_text(self, view, text):
        return text

    @abc.abstractmethod
    def format_query_result(self, view, query):
        pass

    @abc.abstractmethod
    def format_advanced_search(self, view, **kargs):
        pass

    def format_help_page(self):
        return ''

    def get(self, arg):
        return {}

    @property
    def carousel(self):
        pass

    def guess_name(self, query):
        pass


# for back compatibility
Mod = Frontend
