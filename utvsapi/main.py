from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from sqlalchemy.engine.url import URL

try:
    from eve_docs import eve_docs
    from flask.ext.bootstrap import Bootstrap
except ImportError:
    Bootstrap = None

from utvsapi.tables import domain, Base, on_fetched_item, on_fetched_resource
from utvsapi.auth import BearerAuth


url = URL('mysql', query={'read_default_file': './mysql.cnf'})

SETTINGS = {
    'DEBUG': True,
    'SQLALCHEMY_DATABASE_URI': url,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'DOMAIN': domain
}

app = Eve(auth=BearerAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)
app.on_fetched_item += on_fetched_item
app.on_fetched_resource += on_fetched_resource

if Bootstrap:
    Bootstrap(app)
    app.register_blueprint(eve_docs, url_prefix='/docs')

db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base

if __name__ == '__main__':
    app.run(debug=True)
