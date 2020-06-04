#!/usr/bin/env python3
import sys
import re

data = sys.stdin.read()
if not data.endswith("\n"):
    data += "\n"
