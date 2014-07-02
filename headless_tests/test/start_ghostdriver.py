import os
from settings import *  # noqa

PHANTOMJS_PORT = os.environ['PHANTOMJS_PORT'] or None
LOG_FILE = os.environ['LOG_FILE'] or None

if not PHANTOMJS_PORT and not LOG_FILE:
    print "Please set the environment variables PHANTOMJS_PORT and LOG_FILE"
else:
    os.system('phantomjs --webdriver={0} 2>&1 > {1} &'.format(PHANTOMJS_PORT,
                                                              LOG_FILE))
