#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

print("=== 通知模块调试脚本 ===")
print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())

# 检查是否存在sendNotify.py文件
possible_paths = [
    './sendNotify.py',
    '../sendNotify.py',
    '/ql/scripts/sendNotify.py',
    '/ql/data/scripts/sendNotify.py',
    '/ql/sendNotify.py'
]

print("\n检查sendNotify.py文件是否存在:")
for path in possible_paths:
    if os.path.exists(path):
        print(f"✓ 找到文件: {path}")
    else:
        print(f"✗ 未找到: {path}")

# 尝试导入通知模块
print("\n尝试导入通知模块:")

notify_success = False

# 方法1: 直接导入
try:
    print("1. 尝试: from sendNotify import send")
    from sendNotify import send
    print("✓ 成功导入")
    notify_success = True
    # 测试发送
    try:
        send("测试标题", "这是一条测试消息")
        print("✓ 测试消息发送成功")
    except Exception as e:
        print("✗ 测试消息发送失败:", str(e))
except Exception as e:
    print("✗ 导入失败:", str(e))

# 方法2: 导入模块
if not notify_success:
    try:
        print("2. 尝试: import sendNotify")
        import sendNotify
        send = sendNotify.send
        print("✓ 成功导入sendNotify模块")
        notify_success = True
        # 测试发送
        try:
            send("测试标题", "这是一条测试消息")
            print("✓ 测试消息发送成功")
        except Exception as e:
            print("✗ 测试消息发送失败:", str(e))
    except Exception as e:
        print("✗ 导入失败:", str(e))

# 方法3: 添加路径后导入
if not notify_success:
    try:
        print("3. 尝试添加路径后导入")
        additional_paths = ['/ql/scripts', '/ql/data/scripts', '/ql']
        for path in additional_paths:
            if path not in sys.path:
                sys.path.append(path)
        
        import sendNotify
        send = sendNotify.send
        print("✓ 成功导入sendNotify模块(添加路径后)")
        notify_success = True
        # 测试发送
        try:
            send("测试标题", "这是一条测试消息")
            print("✓ 测试消息发送成功")
        except Exception as e:
            print("✗ 测试消息发送失败:", str(e))
    except Exception as e:
        print("✗ 导入失败:", str(e))

# 方法4: 检查青龙面板环境
if not notify_success:
    print("\n检查是否在青龙面板环境中:")
    ql_indicators = ['/ql/', '/ql/scripts', '/ql/data']
    is_ql_env = any(indicator in os.getcwd() for indicator in ql_indicators) or \
                any('ql' in path.lower() for path in sys.path)
    
    if is_ql_env:
        print("✓ 检测到青龙面板环境")
    else:
        print("✗ 未检测到青龙面板环境")

print("\n=== 调试结束 ===")
