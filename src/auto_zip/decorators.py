#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps
from tkinter import messagebox
from loguru import logger
from traceback import format_exc


def catch_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("函数 {} 出错:\n{}", func.__name__, format_exc())
            messagebox.showerror("程序异常", str(e))

    return wrapper
