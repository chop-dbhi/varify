import os
from settings import *

os.system('phantomjs --webdriver={0} 2>&1 > {1} &'.format(PHANTOMJS_PORT,LOG_FILE))
