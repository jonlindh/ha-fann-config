DOMAIN = "fann"

CONF_SERIAL = "serial"
CONF_KEY = "key"

PLATFORMS = [
    "switch",
    "sensor",
    "binary_sensor",
    "button",
]

BASE_URL = "https://fannconfig.se"

LOGIN_URL = f"{BASE_URL}/login.jsp"
DYNAMIC_URL = (
    f"{BASE_URL}/dynamic.jsp?dbid=null&ha=null&type=user&hash=null"
)
ZZZ_URL = f"{BASE_URL}/zzz.jsp"

MODEL_ECOTREAT = "EkoTreat"
MODEL_BIOBED = "Biobed"

STATE_ON = "on"
STATE_OFF = "off"
STATE_UNKNOWN = "unknown"
STATE_WAKING = "waking"
STATE_SLEEPING = "sleeping"