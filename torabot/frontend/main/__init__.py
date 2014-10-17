from flask import Blueprint


bp = Blueprint(
    'main',
    __name__,
    static_folder='static',
    template_folder='templates',
    static_url_path='/main/static'
)


from . import main, thumbnail
assert main
assert thumbnail


def make(app):
    app.register_blueprint(bp)
