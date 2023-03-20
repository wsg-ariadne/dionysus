from typing import TYPE_CHECKING
from .healthcheck import bp_healthcheck

if TYPE_CHECKING:
    from flask import Flask


def install_routes(app: 'Flask'):
    url_prefix = app.config['API_URL_PREFIX']
    
    app.register_blueprint(bp_healthcheck, url_prefix=url_prefix)
