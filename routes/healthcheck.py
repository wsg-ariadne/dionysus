from flask import Blueprint


bp_healthcheck = Blueprint('healthcheck', __name__)


@bp_healthcheck.route('/healthcheck', methods=['GET'])
def healthcheck():
    return 'OK'
