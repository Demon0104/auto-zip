#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from loguru import logger
from utils import PathUtil

desktop = PathUtil.get_desktop_path()
log_path = desktop / "auto_zip.log"

logger.add(log_path, encoding="utf-8", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

__all__ = ["logger"]
