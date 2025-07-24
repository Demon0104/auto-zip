#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from platform import system

IS_WINDOWS = system().lower().startswith("win")
ZIP_SUFFIX = ".zip"
TXT_SUFFIX = ".txt"
CURRENT_DATE = datetime.now().strftime("%Y%m%d")
APP_TITLE = "自动压缩txt文件"