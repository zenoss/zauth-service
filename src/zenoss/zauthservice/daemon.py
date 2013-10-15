import Globals
import json
import copy
import eventlet
import transaction
import time
from eventlet import wsgi
from zope.component import getUtility
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from Products.Zuul.interfaces import IAuthorizationTool
from Products.ZenUtils.ZodbFactory import IZodbFactoryLookup
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.WSGIPublisher import WSGIResponse


class ZAuthServer(ZenScriptBase):

    def run(self, host, port):
        self.connect()
        self._connectSession()
        wsgi.server(eventlet.listen((host, port)), self.route)

    def _connectSession(self):
        options = copy.deepcopy(self.options.__dict__)
        options['zodb_db'] = 'zodb_session'
        connectionFactory = getUtility(IZodbFactoryLookup).get()
        self.session_db, self.session_storage = connectionFactory.getConnection(**options)
        self.session_connection = self.session_db.open()
        root = self.session_connection.root()
        self.session_data = root['Application'].temp_folder.session_data
        self.browser_id_manager = self.dmd.unrestrictedTraverse('/').browser_id_manager

    def syncdb(self):
        super(ZAuthServer, self).syncdb()
        self.session_connection.sync()

    def shutdown(self):
        self.closedb()
        # close the session 
        self.session_connection.close()
        self.session_data = None
        self.session_db = None
        self.session_storage = None

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
        authorization = IAuthorizationTool( self.dmd)
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
        self.browser_id_manager.REQUEST = request
        tokenId = self.browser_id_manager.getBrowserId(create=1)
        expires = time.time() + 60 * 20
        token = dict(id=tokenId, expires=expires)
        transaction.abort()
        self.session_data[tokenId] = token
        start_response('200 OK', [('Content-Type', 'text/html')])
        transaction.commit()
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


def main():
    server = ZAuthServer()
    try:
        server.run('0.0.0.0', 8998)
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
            server.shutdown()
