from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from sqlalchemy.engine.url import URL

from utvsapi.tables import domain, Base
from utvsapi.auth import BearerAuth


url = URL('mysql', query={'read_default_file': './mysql.cnf'})

SETTINGS = {
    'DEBUG': True,
    'SQLALCHEMY_DATABASE_URI': url,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'DOMAIN': domain
}

app = Eve(auth=BearerAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base

if __name__ == '__main__':
    app.run(debug=True)
