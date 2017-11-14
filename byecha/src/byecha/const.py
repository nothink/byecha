
# Chatwork.com URL definitions
BASE_URL = 'https://www.chatwork.com'
LOGIN_URL = BASE_URL + '/login.php'
GATEWAY_URL = BASE_URL + '/gateway.php'

AVATAR_BASE_URL = 'https://appdata.chatwork.com/avatar/'
ICON_BASE_URL = 'https://appdata.chatwork.com/icon/'

# connection interval and max length settings
MAX_CHAT_SIZE = 40
MAX_RETRY_CNT = 5
INTERVAL_ORDER = 1.0
LONG_INTERVAL_ORDER = 30.0 * 60

# dump path and filename settings
ACCOUNT_CONFIG_FILE = 'conf.json'
MYID_FILE = 'myid.txt'
TEMPLATE_PATH = './templates'
