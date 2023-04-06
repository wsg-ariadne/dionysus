from typing import TYPE_CHECKING
from .classify import bp_classify
from .healthcheck import bp_healthcheck
from .report import bp_report

if TYPE_CHECKING:
    from flask import Flask


def install_routes(app: 'Flask'):
    url_prefix = app.config['API_URL_PREFIX']
    
    app.register_blueprint(bp_classify, url_prefix=url_prefix + '/classify')
    app.register_blueprint(bp_healthcheck, url_prefix=url_prefix)
    app.register_blueprint(bp_report, url_prefix=url_prefix + '/reports')
