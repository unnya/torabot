'''
model used to sync tora and local database
'''


from .model import Art, Change, Query, Result
from .spider import list_all
from sqlalchemy.sql import exists, and_
from . import state
from . import what
from logbook import Logger


log = Logger(__name__)


def dict_to_art(d):
    kargs = {}
    if 'ptime' in d:
        kargs['ptime'] = d['ptime']
    art = Art(
        title=d['title'],
        author=d['author'],
        comp=d['comp'],
        state=state.RESERVE if d['reserve'] else state.OTHER,
        **kargs
    )
    art.uri = d['uri']
    return art


def isnew(art, session):
    return not bool(session.query(exists().where(
        Art.toraid == art.toraid
    )).scalar())


def isreserve(art, session):
    return art.reserve and not bool(session.query(exists().where(and_(
        Art.toraid == art.toraid,
        Art.state == state.RESERVE
    ))).scalar())


def ischanged(art, session):
    return bool(session.query(exists().where(and_(
        Art.toraid == art.toraid,
        Art.timestamp == art.timestamp
    ))).scalar())


def add_art(art, session):
    session.add(art)


def has_art(art, session):
    return bool(session.query(exists().where(Art.toraid == art.toraid)).scalar())


def put_art(art, session):
    if has_art(art, session):
        art.id = session.query(Art).filter_by(toraid=art.toraid).one().id
        return session.merge(art)
    session.add(art)
    return art


def add_reserve_change(art, session):
    session.add(Change(art=art, what=what.RESERVE))


def add_new_change(art, session):
    session.add(Change(art=art, what=what.NEW))


def checkstate(art, session):
    return (
        isreserve(art, session),
        isnew(art, session),
        ischanged(art, session),
    )


def has_query(session, **kargs):
    if 'query' in kargs:
        query = kargs['query']
    elif 'text' in kargs:
        query = Query(text=kargs['text'])
    else:
        assert False, 'must provide query or text'
    return bool(session.query(exists().where(Query.text == query.text)).scalar())


def clear_query(query, session):
    query.result.clear()


def reset_query(query, session):
    if has_query(query=query, session=session):
        clear_query(query, session)
        return
    session.add(query)


def add_result(query, art, rank, session):
    query.result.append(Result(query=query, art=art, rank=rank))


def sync(query, session):
    log.debug('sync start: {}', query)
    query = Query(text=query)
    reset_query(query, session)
    arts = []
    for rank, art in enumerate(map(dict_to_art, list_all(query.text))):
        isreserve, isnew, ischanged = checkstate(art, session)
        if isreserve:
            add_reserve_change(art, session)
        if isnew:
            add_new_change(art, session)
            add_art(art, session)
        elif ischanged:
            art = put_art(art, session)
        else:
            log.debug('{} unchange', art.toraid)
            break
        add_result(query, art, rank, session)
        arts.append(art)
    log.debug('sync done, got {} arts', len(arts))
    return arts
