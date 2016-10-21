import os
import re
import sys

os.environ['FLASK_APP'] = "app.py"
os.environ['FLASK_DEBUG'] = '1'

from flask.cli import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
