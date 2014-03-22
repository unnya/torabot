import json
from nose.tools import assert_equal
from stevedore.extension import ExtensionManager
from flask import (
    request,
    current_app,
    render_template,
    session as flask_session
)
from logbook import Logger
from ..core.query import query
from ..ut.bunch import Bunch
from ..db import (
    watch as _watch,
    unwatch as _unwatch,
    watching as _watching,
    get_user_bi_id,
    set_email,
    get_notice_count_bi_user_id,
    get_pending_notice_count_bi_user_id,
)
from ..core.notice import (
    get_notices_bi_user_id,
    get_pending_notices_bi_user_id,
)
from ..core.watch import get_watches_bi_user_id
from . import auth, bp
from ..ut.connection import appccontext
from ..core.mod import mod
from .momentjs import momentjs


log = Logger(__name__)


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/watch', methods=['GET'])
@auth.require_session
def watching(user_id):
    with appccontext() as conn:
        return render_template(
            'watching.html',
            user=get_user_bi_id(conn, user_id),
            watches=get_watches_bi_user_id(conn, user_id)
        )


@bp.route('/notice/all', methods=['GET'], defaults=dict(page=0))
@bp.route('/notice/all/<int:page>', methods=['GET'])
@auth.require_session
def all_notices(page, user_id):
    room = current_app.config['TORABOT_NOTICE_ROOM']
    with appccontext() as conn:
        return render_template(
            'notices.html',
            tab='all',
            view=all_notices.__name__,
            page=page,
            room=room,
            total=get_notice_count_bi_user_id(conn, user_id),
            notices=get_notices_bi_user_id(conn, user_id, page=page, room=room)
        )


@bp.route('/notice/pending', methods=['GET'], defaults=dict(page=0))
@bp.route('/notice/pending/<int:page>', methods=['GET'])
@auth.require_session
def pending_notices(page, user_id):
    room = current_app.config['TORABOT_NOTICE_ROOM']
    with appccontext() as conn:
        return render_template(
            'notices.html',
            tab='pending',
            view=pending_notices.__name__,
            page=page,
            room=room,
            total=get_pending_notice_count_bi_user_id(conn, user_id),
            notices=get_pending_notices_bi_user_id(conn, user_id, page=page, room=room)
        )


@bp.route('/notice/config', methods=['GET', 'POST'])
@auth.require_session
def notice_conf(user_id):
    if request.method == 'GET':
        with appccontext() as conn:
            return render_template(
                'noticeconf.html',
                user=get_user_bi_id(conn, user_id)
            )

    assert_equal(request.method, 'POST')
    try:
        with appccontext(commit=True) as conn:
            set_email(
                conn,
                id=user_id,
                email=request.values['email'],
            )
        return render_template(
            'message.html',
            ok=True,
            message='更新成功'
        )
    except:
        log.exception(
            'user {} change email to {} failed',
            user_id,
            request.values['email']
        )
        return render_template(
            'message.html',
            ok=True,
            message='更新失败'
        )


@bp.route('/search/advanced', methods=['GET'])
def advanced_search():
    sq = get_standard_query()
    return render_template(
        'advanced_search.html',
        query_kind=sq.kind,
        query_text=sq.text,
        content=mod(sq.kind).format_advanced_search('web', sq.text)
    )


def try_get_json_query_text():
    d = dict((key, request.args[key]) for key in request.args)
    if 'torabot_query_text' in d:
        del d['torabot_query_text']
    del d['torabot_query_kind']
    if d:
        return json.dumps(d, sort_keys=True)
    return ''


def try_sort_json_query_text(text):
    try:
        d = json.loads(text)
    except:
        return text
    return json.dumps(d, sort_keys=True)


def get_standard_query():
    text = request.args.get('torabot_query_text', '').strip()
    kind = request.args.get('torabot_query_kind')
    if not text:
        text = try_get_json_query_text()
    else:
        text = try_sort_json_query_text(text)
    if text == 'json':
        kind = json.loads(text)['kind']
    return Bunch(
        kind=kind,
        text=text
    )


@bp.route('/search', methods=['GET'])
def search():
    sq = get_standard_query()
    with appccontext(commit=True) as conn:
        q = query(
            conn=conn,
            kind=sq.kind,
            text=sq.text,
            timeout=current_app.config['TORABOT_SPY_TIMEOUT'],
        )
        options = dict(
            query=q,
            content=mod(q.kind).format_query_result('web', q)
        )
        if 'userid' in flask_session:
            options['watching'] = _watching(
                conn,
                user_id=int(flask_session['userid']),
                query_id=q.id,
            )
    return render_template('list.html', **options)


@bp.route('/watch/add', methods=['POST'])
def watch():
    try:
        with appccontext(commit=True) as conn:
            _watch(
                conn,
                user_id=request.values['user_id'],
                query_id=request.values['query_id'],
            )
        return render_template(
            'message.html',
            ok=True,
            message='订阅成功'
        )
    except:
        log.exception('watch failed')
        return render_template(
            'message.html',
            ok=False,
            message='订阅失败'
        )


@bp.route('/watch/del', methods=['POST'])
def unwatch():
    try:
        with appccontext(commit=True) as conn:
            _unwatch(
                conn,
                user_id=request.values['user_id'],
                query_id=request.values['query_id'],
            )
            return render_template(
                'message.html',
                ok=True,
                message='退订成功'
            )
    except:
        log.exception('unwatch failed')
        return render_template(
            'message.html',
            ok=False,
            message='退订失败'
        )


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.context_processor
def inject_locals():
    log.info('mods: {}', len([e.obj for e in ExtensionManager(
        'torabot.mods',
        invoke_on_load=True,
        invoke_args=(current_app.config,)
    )]))
    return dict(
        min=min,
        max=max,
        len=len,
        str=str,
        isinstance=isinstance,
        momentjs=momentjs,
        mods=[e.obj for e in ExtensionManager(
            'torabot.mods',
            invoke_on_load=True,
            invoke_args=(current_app.config,)
        )]
    )