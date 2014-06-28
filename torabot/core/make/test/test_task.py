import os
import feedparser
from nose.tools import assert_equal, assert_greater
from ..task import Task
from ..envs.dict_with_fs import Env as DictWithFsEnv
from .... import make


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def read(name):
    with open(os.path.join(CURRENT_PATH, name), 'rb') as f:
        return f.read().decode('utf-8')


def test_toy_task():
    task = Task.from_string(read('task.json'))
    assert_equal(task(), 0)


def test_bgm_task():
    app = make()
    with app.app_context():
        task = Task.from_string(
            read('bgm.json'),
            make_env=lambda d: DictWithFsEnv(d, CURRENT_PATH)
        )
        result = task()
        feed = feedparser.parse(result)
        assert not feed.bozo
        assert_greater(len(feed.entries), 0)