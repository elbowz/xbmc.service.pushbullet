Kodi/XBMC Pushbullet Notification Client
===================================

### Info
A Pushbullet client that receive pushes and/or mirroring other devices.

### Tips
For set the Pushbullet *access token* as well as in the addon settings, you can directly edit the file:
*userdata/addon_data/service.pushbullet/settings.xml*

### Settings
* **Notifications Appname Filters**: *Deny* & *Allow* directives are the filters applied on application name (viewed on title in the Kodi notification). The filters are case insensitive regex, separated by space. 

es. (view only *gmail* and *whatsapp* notification)
```
Deny: .* 
Allow: gmail whatsapp
```
or (view all apps except *yatse*)
```
Deny: yatse  
Allow:
```

### Features (TODOS)
- [X] Creation of a real (pushbullet) device. Now, you can push (send) notifications only to Kodi
- [X] App icon appear in kodi notification
- [X] Notification duration is customizable
- [X] Enable/Disable new beta sync (mirroring) Pushbullet mode
- [X] Allow and Deny directives let you allow and deny to view notification by app name
- [ ] Push audio/video link to playback on Kodi
- [ ] Push image to view on Kodi
- [ ] Pushpull **send** push to other devices (which one?)

### www
* [Official Topic](http://forum.xbmc.org/showthread.php?tid=204567)
* [Kodi Official Page (soon)](http://addons.xbmc.org/show/service.pushbullet/)

### Latest release
Manual install service addon: [Download ZIP](https://github.com/elbowz/xbmc.service.pushbullet/archive/master.zip)

### Support
* If you would like contribute to the projects, feel free to do: fork, pull-request, issues, etc...
* Instead if you would like offer me a coffee or beer: [Donate with PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=muttley%2ebd%40gmail%2ecom&lc=IT&item_name=XBMC%20Pushbullet%20%28muttley%29&item_number=Pushbullet&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted)

### Thanks
To sordfish for the first addon release!

This add-on uses the following Python modules:  
*httplib2, six, websocket-client, backports.ssl_match_hostname*