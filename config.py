import os.path
app_path = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(app_path, 'icons')

ICON_ACTIVE = os.path.join(icon_path, 'active.png')
ICON_INACTIVE = os.path.join(icon_path, 'inactive.png')
ENCRYPTED_CONFIG_PATH = os.path.join(app_path, 'config.json.gpg')
CHECK_INTERVAL = 150