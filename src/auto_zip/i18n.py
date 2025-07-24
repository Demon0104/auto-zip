#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lang import LANGUAGES

class I18n:
    current_lang = "zh"
    _listeners = []

    LANGUAGE_NAMES = {
        "zh": "中文",
        "en": "English"
    }

    @classmethod
    def set_language(cls, lang: str):
        if lang in LANGUAGES:
            cls.current_lang = lang
            cls._notify_all()
        else:
            raise ValueError(f"Unsupported language: {lang}")

    @classmethod
    def get_available_languages(cls):
        return list(cls.LANGUAGE_NAMES.keys())

    @classmethod
    def get_language_display_name(cls, lang_code: str):
        return cls.LANGUAGE_NAMES.get(lang_code, lang_code)

    @classmethod
    def t(cls, key: str, **kwargs) -> str:
        return LANGUAGES[cls.current_lang].get(key, key).format(**kwargs)

    @classmethod
    def register_listener(cls, func):
        cls._listeners.append(func)

    @classmethod
    def _notify_all(cls):
        for func in cls._listeners:
            func()

