import os
import re
import sys
from flask.cli import main

os.environ['FLASK_APP'] = "app.py"
os.environ['FLASK_DEBUG'] = '1'


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
