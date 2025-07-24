# AutoZip GUI 压缩工具

## 项目简介

AutoZip GUI 是基于 Python Tkinter 开发的桌面图形界面应用，支持按文件类型批量压缩文件，提供两种压缩模式：

- **每个文件单独压缩**：对目标文件夹内匹配后缀的文件分别生成独立压缩包
- **打包为一个压缩包**：将所有匹配文件统一打包成一个压缩包

程序简单易用，支持跨平台（Windows/macOS/Linux）打开输出文件夹，并且集成了日志记录和异常捕获。

---

## 依赖环境

- Python 3.7+
- Tkinter（Python 标准库自带）
- 依赖第三方库见 `requirements.txt`（如果有）


---

## 快速开始

1. 克隆或下载本项目代码
2. 在命令行中进入项目目录，确保Python环境满足要求
3. 运行程序：
   ```bash
   python main.py

## 生成 EXE 文件

在项目根目录中执行以下命令，命令执行完后在dist文件夹下找到生成的exe文件执行即可

   ```bash
   pip install pyinstaller
   pip install -r requirements.txt
   pyinstaller .\auto_zip.spec --noconfirm
  
