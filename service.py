# import rpdb2
# rpdb2.start_embedded_debugger('pw')

import xbmc

import lib.common

__addon__        = lib.common.__addon__
__addonid__      = lib.common.__addonid__
__addonversion__ = lib.common.__addonversion__
__addonname__    = lib.common.__addonname__
__addonauthor__  = lib.common.__addonauthor__
__addonpath__    = lib.common.__addonpath__
__addonprofile__ = lib.common.__addonprofile__
__addonicon__    = lib.common.__addonicon__

from lib.common import *

class Service:
    def __init__(self):
        log('Service version %s starting' % __addonversion__)

        self.pushbullet = None
        self.serviceMonitor = None
        self.push2Notification = None
        self.stg_pbAccessToken = None

        # notification time for service error
        self.serviceNotifcationTime = 6000

        # xbmc icon (used as ephemerals icon)
        import os
        xbmcImgPath = os.path.join(__addonpath__, 'resources/media/xbmc.jpg')

        import base64
        with open(xbmcImgPath, "rb") as imgFile:
            self.xbmcImgEncoded = base64.b64encode(imgFile.read())

        # catch add-on settings change
        self.serviceMonitor = serviceMonitor(onSettingsChangedAction=self._checkSettingChanged)

        # convert push to Kodi notification
        from lib.push2Notification import Push2Notification
        self.push2Notification = Push2Notification(notificationIcon=__addonicon__, tempPath=__addonprofile__)

        self._getSettings()
        self.run()

        while not xbmc.abortRequested:
            xbmc.sleep(1000)

        log('Closing socket (waiting...)')

        self.pushbullet.close()

        log('Service closed')

    def run(self):
        """
        Run or restart service.
        """

        if self.pushbullet:
            log('Restarting')

            self.pushbullet.close()
            del self.pushbullet

        try:
            if not self.stg_pbAccessToken:
                raise Exception(localise(30100))

            from lib.pushbullet import Pushbullet

            # init pushbullet
            self.pushbullet = Pushbullet(access_token=self.stg_pbAccessToken)

            # create device if it's the first run
            if not self.stg_pbClientIden:
                self._createDevice()

            # get device info (also if edited by user on Pushbullet panel)
            self._getDevice()

            # setup service and pushbullet (iden, mirroring, filter)
            self._setupService()

            # start listening websocket
            self.pushbullet.realTimeEventStream(on_open=self.push2Notification.onOpen,
                                                on_message=self.push2Notification.onMessage,
                                                on_error=self.push2Notification.onError,
                                                on_close=self.push2Notification.onClose)

            log('Started successful')

        except Exception as ex:
            log(ex.args[0], xbmc.LOGERROR)
            showNotification(localise(30101), ex.args[0], self.serviceNotifcationTime)

    def _setupService(self):
        log('Setup Service and Pushbullet Client')

        # setup pushbullet
        self.pushbullet.setDeviceIden(self.stg_pbClientIden)
        self.pushbullet.setFilterDeny({'application_name': self.stg_pbFilterDeny.split()})
        self.pushbullet.setFilterAllow({'application_name': self.stg_pbFilterAllow.split()})
        self.pushbullet.setMirrorMode(self.stg_pbMirroring)

        # setup service
        self.push2Notification.setNotificationTime(self.stg_notificationTime*1000)

        # outbound mirroring
        if self.stg_pbMirroringOut:
            # trigger for Kodi Notification
            self.serviceMonitor.setOnNotificationAction(self._onKodiNotification)
        else:
            self.serviceMonitor.setOnNotificationAction(None)

    def _checkSettingChanged(self):
        """
        Run the correct "procedure" following which settings are changed
        """

        # if access_token is changed => restart service
        if self.stg_pbAccessToken != __addon__.getSetting('pb_access_token'):
            log('Access token is changed')

            self._getSettings()
            self.run()

        # if one of the listed settings are changed and access token is set => read setting setup service
        elif self.stg_pbAccessToken and self._isSettingChanged():
            log('Setting is changed by user')

            self._getSettings()
            self._setupService()

    def _isSettingChanged(self):
        if self.stg_notificationTime != int(__addon__.getSetting('notification_time')): return True
        elif self.stg_pbMirroring != (__addon__.getSetting('pb_mirroring') == 'true'): return True
        elif self.stg_pbFilterDeny != __addon__.getSetting('pb_filter_deny'): return True
        elif self.stg_pbFilterAllow != __addon__.getSetting('pb_filter_allow'): return True
        elif self.stg_pbMirroringOut != (__addon__.getSetting('pb_mirroring_out') == 'true'): return True
        elif self.stg_pbMirroringOutMediaNfo != (__addon__.getSetting('pb_mirroring_out_media_nfo') == 'true'): return True

        return False

    def _getSettings(self):
        log('Reading settings')

        self.stg_pbAccessToken          = __addon__.getSetting('pb_access_token')
        self.stg_notificationTime       = int(__addon__.getSetting('notification_time'))

        self.stg_pbMirroring            = __addon__.getSetting('pb_mirroring') == 'true'
        self.stg_pbFilterDeny           = __addon__.getSetting('pb_filter_deny')
        self.stg_pbFilterAllow          = __addon__.getSetting('pb_filter_allow')

        self.stg_pbMirroringOut         = __addon__.getSetting('pb_mirroring_out') == 'true'
        self.stg_pbMirroringOutMediaNfo = __addon__.getSetting('pb_mirroring_out_media_nfo') == 'true'

        # read only settings
        self.stg_pbClientIden           = __addon__.getSetting('pb_client_iden')
        self.stg_pbClientNickname       = __addon__.getSetting('pb_client_nickname')
        self.stg_pbClientModel          = __addon__.getSetting('pb_client_model')

    def _createDevice(self):
        log('No iden found. Maybe the first time %s start' % __addonname__)

        from lib.common import getMainSetting
        deviceName = getMainSetting('services.devicename')

        import platform
        manufacturer = platform.system()

        response = self.pushbullet.createDevice({'nickname': deviceName, 'type': 'stream', 'model': 'Kodi', 'manufacturer': manufacturer})

        log('New device (%s) created with iden: %s' % (response['nickname'], response['iden']))

        __addon__.setSetting(id='pb_client_iden', value=response['iden'])

        # update iden var setting (just created)
        self.stg_pbClientIden = __addon__.getSetting('pb_client_iden')

    def _getDevice(self):
        device = self.pushbullet.getDevice(self.stg_pbClientIden)

        if device:
            # set setting
            __addon__.setSetting(id='pb_client_nickname', value=device['nickname'])
            __addon__.setSetting(id='pb_client_model', value=device['model'])

            # update vars setting
            self.stg_pbClientNickname = __addon__.getSetting('pb_client_nickname')
            self.stg_pbClientModel  = __addon__.getSetting('pb_client_model')

            log('Device %s (%s) found e loaded' % (self.stg_pbClientNickname, self.stg_pbClientModel))
        else:
            raise Exception('No device found with iden: ' + self.stg_pbClientIden)

    # TODO: create a notification2Push class
    import sys
    import random
    notificationId = random.randint(-sys.maxint-1, sys.maxint)

    def _onKodiNotification(self, sender, method, data):


        import json
        data = json.loads(data)

        if sender == 'xbmc':
            if method == 'Player.OnPlay' and self.stg_pbMirroringOutMediaNfo:
                log('onKodiNotification: %s %s %s' % (sender, method, data))

                playerId = data['player']['playerid']

                if data['item']['type'] == 'movie':
                    result = executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title","year","tagline","thumbnail","file"], "playerid": ' + str(playerId) + ' }, "id": "1"}')

                    if 'title' in result['item']:
                        title = '%s (%s)' % (result['item']['title'], result['item']['year'])
                        body = result['item']['tagline']
                    else:
                        title = result['item']['file']
                        body = None

                    if 'thumbnail' in result['item']:
                        posterFile = result['item']['thumbnail']
                        icon = fileTobase64(posterFile, imgFormat='JPEG', imgSize=(80, 80))
                    else:
                        icon = self.xbmcImgEncoded

                    ephemeralMsg = {'title': title, 'body': body, 'notification_id': self.notificationId, 'icon': icon}

                elif data['item']['type'] == 'song':
                    result = executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title","album","artist","thumbnail","file"], "playerid": ' + str(playerId) + ' }, "id": "1"}')

                    if 'title' in result['item']:
                        title = result['item']['title']
                        body = '%s / %s' % (result['item']['album'], ', '.join(result['item']['artist']))
                    else:
                        title = result['item']['file']
                        body = None

                    if 'thumbnail' in result['item']:
                        posterFile = result['item']['thumbnail']
                        icon = fileTobase64(posterFile, imgFormat='JPEG', imgSize=(80, 80))
                    else:
                        icon = self.xbmcImgEncoded

                    ephemeralMsg = {'title': title, 'body': body, 'notification_id': self.notificationId, 'icon': icon}

                if len(self.pushbullet.sendEphemeral(ephemeralMsg)) == 0:
                    log('Ephemeral push sended: %s - %s' % (ephemeralMsg['title'], ephemeralMsg['body']))
                else:
                    log('Ephemeral push NOT send: %s - %s' % (ephemeralMsg['title'], ephemeralMsg['body']), xbmc.LOGERROR)

if __name__ == "__main__":
    Service()