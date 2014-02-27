NAME = 'Retroshare'
TYPE = 'plugin'
ICON = 'gen-screen'
PLATFORMS = ['any']
DESCRIPTION = 'Retroshare: secure communications with friends'
LONG_DESCRIPTION = ("RetroShare is a Open Source cross-platform, Friend-2-Friend and"
					" secure decentralised communication platform."
					"It lets you to securely chat and share files with your friends, family and coworkers,"
					" using a web-of-trust to authenticate peers and OpenSSL to encrypt all communication. "
					" RetroShare provides filesharing, chat, messages, forums and channels.")
VERSION = '0'
AUTHOR = 'electron'
HOMEPAGE = ''
APP_AUTHOR = "Retroshare Team"
APP_HOMEPAGE = "http://retroshare.org"


CATEGORIES = [
    {
        "primary": "Communication",
        "secondary": ["Chat", "Instant Messaging (IM)", "Filesharing", "Downloads", "Forums", "Channels", "Social Network"]
    }
]


MODULES = ['main', "retroshare_mmi"]

PLATFORMS = ["any"]

DEPENDENCIES = {}
'''
DEPENDENCIES = {
    "any": [
        {
            "type": "app",
            "name": "retroshare-nogui",
            "package": "retroshare-nogui",
            "binary": "retroshare-nogui"
        }
    ]
}
'''

GENERATION = 1