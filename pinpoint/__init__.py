from flask import Flask, url_for
from flask.ext.bootstrap import Bootstrap

application = Flask(__name__)
application.config.from_object('config')

from pinpoint import views
bootstrap = Bootstrap(application)


