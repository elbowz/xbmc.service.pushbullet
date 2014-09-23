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

from lib.common import localise, log, showNotification, serviceMonitor

class Service:
    def __init__(self):
        log('Service version %s starting' % __addonversion__)

        self.pushbullet = None
        self.stg_pbAccessToken = None

        # notification time for service error
        self.serviceNotifcationTime = 6000

        # convert push to Kodi notification
        from lib.push2Notification import Push2Notification
        self.push2Notification = Push2Notification(notificationIcon=__addonicon__, tempPath=__addonprofile__)

        # catch addon settings change
        self.serviceMonitor = serviceMonitor(onSettingsChangedAction=self._checkSettingChanged)

        self._getSettings()
        self.run()

        while not xbmc.abortRequested:
            xbmc.sleep(1000)

        log('Closing socket (waiting...)')

        self.pushbullet.close()

        log('Closed')

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

            # setup pushbullet (iden, mirroring, filter)
            self._setupPushbullet()

            # start listening websocket
            self.pushbullet.realTimeEventStream(on_open=self.push2Notification.onOpen,
                                                on_message=self.push2Notification.onMessage,
                                                on_error=self.push2Notification.onError,
                                                on_close=self.push2Notification.onClose)

            log('Started successful')

        except Exception as ex:
            log(ex.args[0], xbmc.LOGERROR)
            showNotification(localise(30101), ex.args[0], self.serviceNotifcationTime)

    def _setupPushbullet(self):
        log('Setup Pushbullet Client')

        self.pushbullet.setIden(self.stg_pbClientIden)
        self.pushbullet.setFilterDeny({'application_name': self.stg_pbFilterDeny.split()})
        self.pushbullet.setFilterAllow({'application_name': self.stg_pbFilterAllow.split()})
        self.pushbullet.setMirrorMode(self.stg_pbMirroring)

        self.push2Notification.setNotificationTime(self.stg_notificationTime*1000)

    def _checkSettingChanged(self):
        """
        Run the correct "procedure" following which settings are changed
        """
        # if access_token is changed => restart service
        if self.stg_pbAccessToken != __addon__.getSetting('pb_access_token'):
            log('Access token is changed')

            self._getSettings()
            self.run()

        # if one of the listed settings are changed and access token is set => setup Pushbullet
        elif self.stg_pbAccessToken and \
                (self.stg_pbMirroring != (__addon__.getSetting('pb_mirroring') == 'true')
                 or self.stg_pbFilterDeny != __addon__.getSetting('pb_filter_deny')
                 or self.stg_pbFilterAllow != __addon__.getSetting('pb_filter_allow')
                 or self.stg_notificationTime != int(__addon__.getSetting('notification_time'))):
            log('Setting is changed by user')

            self._getSettings()
            self._setupPushbullet()

    def _getSettings(self):
        log('Reading settings')

        self.stg_pbAccessToken      = __addon__.getSetting('pb_access_token')
        self.stg_notificationTime   = int(__addon__.getSetting('notification_time'))
        self.stg_pbMirroring        = __addon__.getSetting('pb_mirroring') == 'true'
        self.stg_pbFilterDeny       = __addon__.getSetting('pb_filter_deny')
        self.stg_pbFilterAllow      = __addon__.getSetting('pb_filter_allow')

        # read only settings
        self.stg_pbClientIden       = __addon__.getSetting('pb_client_iden')
        self.stg_pbClientNickname   = __addon__.getSetting('pb_client_nickname')
        self.stg_pbClientModel      = __addon__.getSetting('pb_client_model')

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


if __name__ == "__main__":
    Service()


