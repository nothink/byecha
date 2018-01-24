
# Chatwork.com URL definitions
BASE_URL = 'https://www.chatwork.com'
LOGIN_URL = BASE_URL + '/login.php'
GATEWAY_URL = BASE_URL + '/gateway.php'

AVATAR_BASE_URL = 'https://appdata.chatwork.com/avatar/'
ICON_BASE_URL = 'https://appdata.chatwork.com/icon/'

API_ENDPOINT_URL = 'https://api.chatwork.com/v2'
TOKEN_PUBLUSHER_URL = 'https://www.chatwork.com/service/packages/chatwork/subpackages/api/token.php'

# connection interval and max length settings
MAX_CHAT_SIZE = 40
MAX_RETRY_CNT = 5
INTERVAL_ORDER = 1.0
LONG_INTERVAL_ORDER = 30.0 * 60

# dump path and filename settings
ACCOUNT_CONFIG_FILE = 'conf.json'
MYID_FILE = 'myid.txt'
STATIC_BASE = '/static'
TEMPLATE_PATH = 'templates'
IMAGE_PATH = 'images'
AVATAR_PATH = 'images/avatar'
ICON_PATH = 'images/icon'
DEFAULT_AVATAR = 'ico_default.png'
FILE_PATH = 'file'
THUMB_PATH = 'thumb'

# dictionary of system message (dtext)
DTEXT_DICT = {
    'file_uploaded': 'ファイルをアップロードしました。',
    'chatroom_chat_edited': '',
    'chatroom_member_is': '',
    'chatroom_added': '',
    'chatroom_contact_added': 'コンタクトを追加しました。',
    'chatroom_description_is': '概要を「',
    'chatroom_changed': '」に変更しました。',
    'chatroom_leaved': '',
    'chatroom_priv_changed': '',
    'chatroom_icon_updated': '',
    'chatroom_groupchat_created': '',
    'chatroom_chatname_is': '',
    'chatroom_set': '',
    'chatroom_over_groupchatnum': '',
    'chatroom_deleted': '',
    'chatroom_mychat_created': 'マイチャットを作成しました。',
    'task_added': 'タスクを追加しました。',
    'task_done': 'タスクを完了しました。',
    'task_edited': 'タスクを編集しました。',
    'task_reverted': '',
    'live_start': '',
}
