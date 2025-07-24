#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional
from zipfile import ZipFile, ZIP_DEFLATED

from config import IS_WINDOWS, ZIP_SUFFIX

if IS_WINDOWS:
    from winreg import OpenKey, HKEY_CURRENT_USER, QueryValueEx


class PathUtil:
    @staticmethod
    def get_desktop_path() -> Optional[Path]:
        """获取桌面路径，兼容 Windows 和其他系统"""
        if IS_WINDOWS:
            try:
                with OpenKey(
                        HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
                ) as key:
                    desktop = Path(QueryValueEx(key, "Desktop")[0])
                    if desktop.exists():
                        return desktop
            except (FileNotFoundError, OSError):
                pass

        fallback = Path.home() / "Desktop"
        return fallback if fallback.exists() else None

    @staticmethod
    def ensure_dir(path: Path) -> None:
        """确保目录存在"""
        path.mkdir(parents=True, exist_ok=True)


class ZipUtil:
    @staticmethod
    def zip_one(file_path: Path, zip_path: Path) -> None:
        """
        压缩单个文件到指定 zip 文件中。
        :param file_path: 要压缩的文件路径
        :param zip_path: 输出 zip 文件路径
        """
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
                zipf.write(file_path, arcname=file_path.name)
        except Exception:
            raise

    @staticmethod
    def zip_many_into_one(file_paths: List[Path], final_zip_path: Path) -> None:
        """
        将多个文件压缩成一个最终 zip 文件，每个文件先打包成独立 zip 再打进最终包。
        :param file_paths: 要压缩的文件列表
        :param final_zip_path: 最终输出 zip 文件路径
        """
        if not file_paths:
            raise ValueError("未提供任何文件进行压缩")

        try:
            with TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                temp_zips = []

                for idx, f in enumerate(file_paths):
                    if not f.exists() or not f.is_file():
                        continue

                    # 确保不重名
                    zip_name = f"{f.stem}_{idx}{ZIP_SUFFIX}"
                    z = tmp_path / zip_name
                    ZipUtil.zip_one(f, z)
                    temp_zips.append(z)

                with ZipFile(final_zip_path, "w", ZIP_DEFLATED) as zipf:
                    for z in temp_zips:
                        zipf.write(z, arcname=z.name)

        except Exception:
            raise
