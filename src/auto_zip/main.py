#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from platform import system
from atexit import register
from enum import Enum
from os import startfile
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from threading import Thread, current_thread, main_thread
from tkinter import StringVar, messagebox
from ttkbootstrap import Window, Label, Frame, Button, Entry, Progressbar
from ttkbootstrap.constants import *
from traceback import format_exc
from typing import List, Optional

from config import APP_TITLE, TXT_SUFFIX, CURRENT_DATE, ZIP_SUFFIX
from log_config import logger
from decorators import catch_exceptions
from utils import PathUtil, ZipUtil
from i18n import I18n


class CompressMode(Enum):
    INDIVIDUAL = "individual"
    COMBINED = "combined"


class CompressApp:
    def __init__(self):
        logger.info("Initializing GUI...")
        self.window = Window(themename="flatly")
        self.window.title(APP_TITLE)
        self._center_window()

        self.input_path = StringVar(value=I18n.t("init_input_text"))
        self.file_suffix = StringVar(value=TXT_SUFFIX)
        self.desktop = PathUtil.get_desktop_path()

        self.tmp_dir: Optional[TemporaryDirectory] = None
        self.workspace: Optional[Path] = None
        self.temp_cleaned = True

        self.progressbar = None
        register(self._cleanup_temp_dir)

        self._build_ui()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.mainloop()

    def _center_window(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width, height = int(screen_width * 0.4), int(screen_height * 0.42)
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        logger.info("Window centered with size {}x{}", width, height)

    def _build_ui(self):
        logger.info("Building UI components...")
        container = Frame(self.window, padding=20)
        container.pack(fill="both", expand=True)

        label_opts = {'sticky': E, 'padx': (0, 15), 'pady': 10}

        self.language_label = Label(container, text=I18n.t("language"), font=("微软雅黑", 11))
        self.language_label.grid(row=0, column=0, **label_opts)

        self.lang_var = StringVar(value=I18n.current_lang)
        lang_frame = Frame(container)
        lang_frame.grid(row=0, column=1, columnspan=2, sticky=W)
        self.lang_buttons = {}
        for idx, code in enumerate(I18n.get_available_languages()):
            btn = Button(lang_frame, text=I18n.get_language_display_name(code), width=10,
                         command=lambda c=code: self._on_language_select(c))
            btn.grid(row=0, column=idx, padx=5)
            self.lang_buttons[code] = btn

        self.file_type_label = Label(container, text=I18n.t("file_type"), font=("微软雅黑", 11))
        self.file_type_label.grid(row=1, column=0, **label_opts)
        self.file_type_entry = Entry(container, textvariable=self.file_suffix, width=14)
        self.file_type_entry.grid(row=1, column=1, sticky=W, pady=10)

        self.input_folder_label = Label(container, text=I18n.t("input_folder"), font=("微软雅黑", 11))
        self.input_folder_label.grid(row=2, column=0, **label_opts)
        self.show_path_label = Label(container, textvariable=self.input_path)
        self.show_path_label.grid(row=2, column=1, sticky=W, pady=10)
        self.choose_button = Button(container, text=I18n.t("choose"), command=self._choose_folder)
        self.choose_button.grid(row=2, column=2, padx=5)

        self.btn_individual = Button(container, text=I18n.t("compress_individual"),
                                     command=lambda: self._start_compress(CompressMode.INDIVIDUAL))
        self.btn_individual.grid(row=3, column=0, columnspan=3, sticky=EW, pady=(20, 10))

        self.btn_combined = Button(container, text=I18n.t("compress_combined"),
                                   command=lambda: self._start_compress(CompressMode.COMBINED))
        self.btn_combined.grid(row=4, column=0, columnspan=3, sticky=EW, pady=10)

        self.progressbar = Progressbar(container, mode='determinate', maximum=100)
        self.progressbar.grid(row=5, column=0, columnspan=3, sticky=EW, pady=10)

        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, minsize=120)

        I18n.register_listener(self._refresh_ui_texts)
        self._refresh_ui_texts()

    def _on_language_select(self, lang_code: str):
        logger.info("Language switched to: {}", lang_code)
        I18n.set_language(lang_code)
        self.lang_var.set(lang_code)
        self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        for code, btn in self.lang_buttons.items():
            btn.config(bootstyle=PRIMARY if code == I18n.current_lang else SECONDARY)
        self.language_label.config(text=I18n.t("language"))
        self.file_type_label.config(text=I18n.t("file_type"))
        self.input_folder_label.config(text=I18n.t("input_folder"))
        if not self.input_path:
            self.input_path = StringVar(value=I18n.t("init_input_text"))
            self.show_path_label.config(textvariable=self.input_path)
        self.choose_button.config(text=I18n.t("choose"))
        self.btn_individual.config(text=I18n.t("compress_individual"))
        self.btn_combined.config(text=I18n.t("compress_combined"))

    def _choose_folder(self):
        from tkinter.filedialog import askdirectory
        folder = askdirectory(title="Choose Folder")
        if folder:
            folder_path = str(Path(folder).resolve())
            logger.info("User selected folder: {}", folder_path)
            self.input_path.set(folder_path)

    def _get_matched_files(self, dir_path: Path) -> List[Path]:
        suffix = self.file_suffix.get().strip().lower()
        if not suffix.startswith("."):
            suffix = "." + suffix
        matched = [f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() == suffix]
        logger.info("Matched files with suffix '{}': {}", suffix, matched)
        return matched

    def _prepare_workspace(self) -> List[Path]:
        input_dir = Path(self.input_path.get().strip())
        logger.info("Preparing workspace with input dir: {}", input_dir)

        if not input_dir.is_dir():
            raise ValueError(I18n.t("invalid_input_dir"))

        files = self._get_matched_files(input_dir)
        if not files:
            raise ValueError(I18n.t("no_files_found", suffix=self.file_suffix.get()))

        self._cleanup_temp_dir()
        self.tmp_dir = TemporaryDirectory()
        self.workspace = Path(self.tmp_dir.name)
        self.temp_cleaned = False
        logger.info("Temporary workspace created at: {}", self.workspace)
        return files

    def _start_compress(self, mode: CompressMode):
        logger.info("Starting compression in mode: {}", mode.value)
        Thread(target=self._compress_task, args=(mode,), daemon=True).start()

    def _compress_task(self, mode: CompressMode):
        try:
            self.compress(mode)
        except Exception:
            logger.error("Compression thread error: {}", format_exc())
            self.window.after(0, lambda: self._show_message(I18n.t("error_title"), I18n.t("unknown_error"), "error"))

    @catch_exceptions
    def compress(self, mode: CompressMode):
        files = self._prepare_workspace()
        total = len(files)

        if mode == CompressMode.INDIVIDUAL:
            for idx, f in enumerate(files, 1):
                zip_path = self.workspace / f"{f.stem}{ZIP_SUFFIX}"
                logger.info("Compressing file: {} → {}", f, zip_path)
                ZipUtil.zip_one(f, zip_path)
                self.window.after(0, lambda v=idx * 100 // total: self.progressbar.configure(value=v))
        else:
            zip_path = self.workspace / f"{CURRENT_DATE}{ZIP_SUFFIX}"
            logger.info("Compressing {} files into one archive: {}", len(files), zip_path)
            ZipUtil.zip_many_into_one(files, zip_path)
            self.window.after(0, lambda: self.progressbar.configure(value=100))

        self.window.after(0, lambda: self._notify_success(files))

    def _notify_success(self, files: List[Path]):
        logger.info("Compression completed successfully. Files: {}", files)
        msg = f"{I18n.t('success')}\n" + "\n".join(str(f) for f in files)
        msg += f"\n{I18n.t('output_dir', path=self.workspace)}"
        self._show_message(I18n.t("done"), msg, "info")
        self._open_folder(self.workspace)

    def _show_message(self, title: str, message: str, kind: str):
        def _msg():
            getattr(messagebox, f"show{kind}")(title, message)

        if kind == "info":
            logger.info(message)
        elif kind == "warning":
            logger.warning(message)
        elif kind == "error":
            logger.error(message)

        if current_thread() is main_thread():
            _msg()
        else:
            self.window.after(0, _msg)

    def _open_folder(self, folder: Path):
        try:
            logger.info("Opening folder: {}", folder)
            if system() == "Windows":
                startfile(folder)
            elif system() == "Darwin":
                run(["open", folder], check=False)
            else:
                run(["xdg-open", folder], check=False)
        except Exception as e:
            logger.warning(I18n.t("cannot_open", err=e))

    def _cleanup_temp_dir(self):
        if self.tmp_dir and not self.temp_cleaned:
            logger.info("Cleaning up temporary directory: {}", self.tmp_dir.name)
            self.tmp_dir.cleanup()
            self.temp_cleaned = True

    def _on_close(self):
        logger.info("Application closing.")
        self._cleanup_temp_dir()
        self.window.destroy()


if __name__ == '__main__':
    try:
        CompressApp()
    except Exception:
        logger.error("Unhandled exception in program: {}", format_exc())
        messagebox.showerror(I18n.t("app_error"), I18n.t("app_error_exit"))
