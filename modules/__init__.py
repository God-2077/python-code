# -*- coding: utf-8 -*-

# 包级别的常量/变量
__version__ = "1.0.0"
__author__ = "kissablecho"
__doc__ = """
模块初始化文件
用于导入模块中的所有公共接口
"""

# 用于导入模块中的所有公共接口
from ._async import _async
from ._Logger import Logger

__all__ = [
    "_async",
    "Logger"
]

