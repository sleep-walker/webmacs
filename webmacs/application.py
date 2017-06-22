import os

from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineScript
from PyQt5.QtWidgets import QApplication

from .websocket import WebSocketClientWrapper
from .keyboardhandler import KEY_EATER

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


class Application(QApplication):
    INSTANCE = None

    def __init__(self, args):
        QApplication.__init__(self, args)
        self.__class__.INSTANCE = self

        with open(os.path.join(THIS_DIR, "app_style.css")) as f:
            self.setStyleSheet(f.read())
        self._setup_websocket()
        self._setup_default_profile(self.sock_client.port)

        from .global_comands import register_global_commands
        register_global_commands()

        self.installEventFilter(KEY_EATER)

        from . import default_webjumps  # noqa

    def _setup_websocket(self):
        """
        An internal websocket is used to communicate between web page content
        (using javascript) and the python code.
        """
        self.sock_client = WebSocketClientWrapper()

    def _setup_default_profile(self, port):
        default_profile = QWebEngineProfile.defaultProfile()

        def inject_js(src):
            script = QWebEngineScript()
            script.setInjectionPoint(QWebEngineScript.DocumentCreation)
            script.setSourceCode(src)
            script.setWorldId(QWebEngineScript.ApplicationWorld)
            default_profile.scripts().insert(script)

        for script in ("qwebchannel.js", "setup.js"):
            with open(os.path.join(THIS_DIR, script)) as f:
                src = f.read()
            if script == "setup.js":
                src = ("var webmacsBaseUrl = 'ws://localhost:%d';\n%s"
                       % (port, src))
            inject_js(src)