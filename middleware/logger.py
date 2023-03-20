from pprint import pprint


# https://stackoverflow.com/a/25467602
class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, env, resp):
        error_log = env['wsgi.errors']
        pprint(('REQUEST', env), stream=error_log)

        def log_response(status, headers, *args):
            pprint(('RESPONSE', status, headers), stream=error_log)
            return resp(status, headers, *args)

        return self._app(env, log_response)
