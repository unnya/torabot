from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import (
    sessionmaker,
    relationship,
)
from sqlalchemy import (
    Column,
    Integer,
    String,
    Index,
    ForeignKey,
    DateTime,
)
from .tora import order_uri_from_toraid, toraid_from_order_uri
from . import state
from .time import utcnow
from contextlib import contextmanager


Base = declarative_base()
Session = sessionmaker()


@contextmanager
def makesession(commit=False, **kargs):
    session = Session(**kargs)
    try:
        yield session
        if commit:
            session.commit()
    except:
        session.rollback()
        raise


class Art(Base):

    __tablename__ = 'art'

    OTHER = 0
    RESERVE = 1

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    comp = Column(String)
    toraid = Column(String(12), unique=True, index=True)
    state = Column(Integer, index=True)
    ptime = Column(DateTime)
    atime = Column(DateTime, default=utcnow)
    hash = Column(String(32))

    @declared_attr
    def __table_args__(cls):
        return (Index('%s_idx_toraid_state' % cls.__tablename__, 'toraid', 'state'),)

    @property
    def uri(self):
        return order_uri_from_toraid(self.toraid)

    @uri.setter
    def uri(self, value):
        self.toraid = toraid_from_order_uri(value)

    @property
    def reserve(self):
        return self.state == state.RESERVE


class Change(Base):

    __tablename__ = 'change'

    NEW = 1
    RESERVE = 2

    id = Column(Integer, primary_key=True)
    art_id = Column(Integer, ForeignKey(Art.id), index=True)
    what = Column(Integer)
    ctime = Column(DateTime, default=utcnow, index=True)

    art = relationship(Art)

    @property
    def text(self):
        from . import render
        return render.make_change_text(self)


class Query(Base):

    __tablename__ = 'query'

    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True, index=True)
    ctime = Column(DateTime, default=utcnow, index=True)
    version = Column(Integer, default=0)
    total = Column(Integer)

    #result = relationship('Result', order_by='Result.rank')

    #@property
    #def arts(self):
        #return [qa.art for qa in self.result]


class Result(Base):

    __tablename__ = 'result'

    query_id = Column(Integer, ForeignKey(Query.id), primary_key=True, index=True)
    art_id = Column(Integer, ForeignKey(Art.id), primary_key=True)
    rank = Column(Integer, index=True)
    hash = Column(String(32))
    version = Column(Integer, index=True, default=0)

    query = relationship(Query)
    art = relationship(Art)


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    openid = Column(String, unique=True, index=True)


class Subscription(Base):

    __tablename__ = 'subscription'

    query_id = Column(Integer, ForeignKey(Query.id), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, index=True)
    ctime = Column(DateTime, default=utcnow)
    version = Column(Integer, index=True, default=0)

    query = relationship(Query)


class Notice(Base):

    __tablename__ = 'notice'

    PENDING = 0
    EATEN = 1

    id = Column(Integer, primary_key=True)
    text = Column(String)
    user_id = Column(Integer, ForeignKey(User.id), index=True)
    ctime = Column(DateTime, default=utcnow)
    mtime = Column(DateTime, default=utcnow)
    state = Column(Integer, default=PENDING)

    user = relationship(User, backref='notices')

    @declared_attr
    def __table_args__(cls):
        return (Index(
            '%s_idx_ctime_mtime_state' % cls.__tablename__,
            'ctime',
            'mtime',
            'state',
        ),)

    @property
    def state_string(self):
        from . import render
        return render.make_notice_state_string(self)

    @property
    def text_web(self):
        from . import render
        return render.make_notice_text_web(self)
