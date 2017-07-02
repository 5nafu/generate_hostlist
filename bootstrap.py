#!/usr/bin/env python

import sys
from os.path import join

SOURCEPATH = join("src", "main", "python")
SCRIPTPATH = join("src", "main", "scripts", "generate_hostlist.py")

sys.path.insert(0, SOURCEPATH)
exec(open(SCRIPTPATH, 'r').read())
