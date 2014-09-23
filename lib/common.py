import xbmc
import xbmcaddon

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__addonname__    = __addon__.getAddonInfo('name')
__addonauthor__  = __addon__.getAddonInfo('author')
__addonpath__    = __addon__.getAddonInfo('path').decode('utf-8')
__addonprofile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
__addonicon__    = __addon__.getAddonInfo('icon')


def localise(id):
    string = __addon__.getLocalizedString(id).encode('utf-8', 'ignore')
    return string


def log(txt, level=xbmc.LOGDEBUG):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonname__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=level)


def getMainSetting(name):
    import json

    result = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "' + name + '"}, "id": 1 }')
    return json.loads(result)['result']['value']


def showNotification(title, message, timeout=2000, icon=__addonicon__):
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % (
        title.encode('utf-8', 'ignore'), message.encode('utf-8', 'ignore'), timeout, icon))


class serviceMonitor(xbmc.Monitor):
    def __init__(self, onSettingsChangedAction=None):
        xbmc.Monitor.__init__(self)

        self.onSettingsChangedAction = onSettingsChangedAction

    def onSettingsChanged(self):
        if self.onSettingsChangedAction:
            self.onSettingsChangedAction()

    def setOnSettingsChangedAction(self, action):
        self.onSettingsChangedAction = action


# import time
# from threading import Thread, Event
#
# class IntervalTimer(Thread):
#     def __init__(self, worker_func, interval, worker_func_args):
#         Thread.__init__(self)
#         self._interval = interval
#         self._worker_func = worker_func
#         self._worker_func_args = worker_func_args
#         self._stop_event = Event()
#
#     def run(self):
#         while not self._stop_event.is_set():
#             self._worker_func(self, *self._worker_func_args)
#             time.sleep(self._interval)
#
#     def stop(self):
#         if self.isAlive() is True:
#             # set event to signal thread to terminate
#             self._stop_event.set()