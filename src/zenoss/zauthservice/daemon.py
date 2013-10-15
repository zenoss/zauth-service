import Globals
import json
import copy
import eventlet
from contextlib import contextmanager
from eventlet import tpool
import time
from eventlet import wsgi
from eventlet.pools import Pool
from zope.component import getUtility
from transaction._manager import TransactionManager
from Products.ZenUtils.CmdBase import CmdBase
from Products.Zuul.interfaces import IAuthorizationTool
from Products.ZenUtils.ZodbFactory import IZodbFactoryLookup
from Products.ZenUtils.ZenDaemon import ZenDaemon
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.WSGIPublisher import WSGIResponse



class DBConnectionContainer(object):
    """
    All access to the database and transactions should be through this object,
    guaranteeing that the dbs and transaction manager don't get confused.
    """
    def __init__(self, zodb, sessiondb, tm):
        self._tm = tm

        self._zodb = zodb.open(transaction_manager=tm)
        zodb_app = self._zodb.root()['Application']
        self._dmd = zodb_app.zport.dmd
        self._browser_id_manager = zodb_app.browser_id_manager

        self._sessiondb = sessiondb.open(transaction_manager=tm)
        session_app = self._sessiondb.root()['Application']
        self._session_data = session_app.temp_folder.session_data

    def dmd(self):
        return self._dmd

    def session_data(self):
        return self._session_data

    def browser_id_manager(self):
        return self._browser_id_manager

    def sync(self):
        self._zodb.sync()
        self._sessiondb.sync()

    def commit(self):
        self._tm.commit()

    def abort(self):
        self._tm.abort()

    def __del__(self):
        self.abort()
        self._zodb.close()
        self._sessiondb.close()



class ZAuthServer(CmdBase):

    _dbs = {}
    _pool = None

    def _create(self):
        _tm = TransactionManager()
        return DBConnectionContainer(self._dbs['zodb'], 
                self._dbs['zodb_session'],_tm)

    def _setup_dbs(self):
        for db in 'zodb', 'zodb_session':
            options = copy.deepcopy(self.options.__dict__)
            options['zodb_db'] = db
            connectionFactory = getUtility(IZodbFactoryLookup).get()
            self._dbs[db], _ = connectionFactory.getConnection(**options)
        self._pool = Pool(create=self._create, max_size=20)

    @property
    @contextmanager
    def db(self):
        """
        Use this context manager exclusively for database access. It manages
        checking DBConnectionContainers out from the pool, wrapping them in
        a tpool Proxy, and cleaning up transactions afterward.
        """
        with self._pool.item() as conns:
            proxied = tpool.Proxy(conns)
            yield proxied
            proxied.abort()

    def run(self, host, port):
        self._setup_dbs()
        wsgi.server(eventlet.listen((host, port)), self.route)

    def _unauthorized(self, msg, start_response):
        start_response('401 Unauthorized', [('Content-Type', 'text/html')])
        return msg

    def _challenge(self, start_response):
        body = 'Please authenticate'
        headers = [
            ('content-type', 'text/plain'),
            ('content-length', str(len(body))),
            ('WWW-Authenticate', 'Basic realm="%s"' % "ZAuthRealm")]
        start_response('401 Unauthorized', headers)
        return [body]

    def handleLogin(self, env, start_response):
        basic = env.get('HTTP_AUTHORIZATION', None)
        if basic is None:
            return self._challenge(start_response)
        response = WSGIResponse()
        request = HTTPRequest(env['wsgi.input'], env, response)
        with self.db as db:
            authorization = IAuthorizationTool(db.dmd())
            credentials = authorization.extractCredentials(request)

        login = credentials.get('login', None)
        password = credentials.get('password', None)
        # no credentials to test authentication
        if login is None or password is None:
            return self._unauthorized("Missing Authentication Credentials", start_response)

        # test authentication
        if not authorization.authenticateCredentials(login, password):
            return self._unauthorized( "Failed Authentication", start_response)

        # create the session data
        with self.db as db:
            db.browser_id_manager().REQUEST = request
            tokenId = db.browser_id_manager().getBrowserId(create=1)
        expires = time.time() + 60 * 20
        token = dict(id=tokenId, expires=expires)
        with self.db as db:
            db.session_data()[tokenId] = token
            start_response('200 OK', [('Content-Type', 'text/html')])
            db.commit()
        return json.dumps(token)

    def handleValidate(self, env, start_response):
        print "Validate"
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ""

    def route(self, env, start_response):
        path = env['PATH_INFO']
        if path == '/authorization/login':
            result =  self.handleLogin(env, start_response)
            return result
        elif path == '/authorization/validate':
            return self.handleValidate(env, start_response)
        elif path =='/':
            return self.index(env, start_response)
        else:
            start_response('404 OK', [('Content-Type', 'text/html')])
            return ""

    def index(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return """
        <html>
            <head>
                <title>ZAuthService</title>
            </head>
            <body>
                <h1>Menu</h1>
                <ul>
                    <li><a href="/authorization/login">Login</a></li>
                    <li><a href="/authorization/validate">Validate</a></li>
                </ul>
            </body>
        </html>
        """

    def buildOptions(self):
        CmdBase.buildOptions(self)
        connectionFactory = getUtility(IZodbFactoryLookup).get()
        connectionFactory.buildOptions(self.parser)


def main():
    server = ZAuthServer()
    try:
        server.run('0.0.0.0', 8998)
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        pass
