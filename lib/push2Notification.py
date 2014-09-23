import xbmc
from lib.common import log, localise, showNotification

class Push2Notification():
    """
    Pushbullet push to Kodi Notification
    """

    def __init__(self, notificationTime=6000, notificationIcon=None, tempPath=None):
        self.notificationTime = notificationTime
        self.notificationIcon = notificationIcon
        self.tempPath = tempPath

        from os.path import join
        self.imgFilePath = join(self.tempPath, 'temp-notification-icon')

    def onMessage(self, message):
        from json import dumps
        log('New push received: ' + dumps(message))

        if message['type'] == 'mirror':
            if 'icon' in message:
                iconPath = self._base64Img2file(message['icon'])
                body = message['body'].replace("\n", " / ") if 'body' in message else ''

                showNotification(message["application_name"], body, self.notificationTime, iconPath)
        else:
            title = message['title'] if 'title' in message else ''
            body = message['body'].replace("\n", " / ") if 'body' in message else ''

            showNotification(title, body, self.notificationTime, self.notificationIcon)

    def onError(self, error):
        log(error, xbmc.LOGERROR)
        showNotification(localise(30101), error, self.notificationTime, self.notificationIcon)

    def onClose(self):
        log('Socket closed')

    def onOpen(self):
        log('Socket opened')

    def _base64Img2file(self, base64Img, imgFilePath=None):
        imgFilePath = self.imgFilePath if imgFilePath is None else imgFilePath

        import base64
        imgDecoded = base64.b64decode(base64Img)

        file = open(imgFilePath, "wb")
        file.write(imgDecoded)
        file.close()

        return imgFilePath

    def setNotificationTime(self, notificationTime):
        self.notificationTime = notificationTime
