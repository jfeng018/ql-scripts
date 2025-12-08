import time
import re
import json
import base64
import hashlib
import rsa
import requests
import os
import sys
from datetime import datetime

print("=== 调试信息 ===")
print("Python路径:", sys.executable)
print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)
print("==================")

# 青龙面板通知模块
notify_enabled = False
send = None

print("开始尝试导入通知模块...")

# 尝试多种方式导入通知模块
try:
    print("尝试: from sendNotify import send")
    from sendNotify import send
    notify_enabled = True
    print("✓ 成功导入 sendNotify.send")
except Exception as e:
    print("✗ from sendNotify import send 失败:", str(e))
    try:
        print("尝试: import sendNotify")
        import sendNotify
        send = sendNotify.send
        notify_enabled = True
        print("✓ 成功导入 sendNotify")
    except Exception as e:
        print("✗ import sendNotify 失败:", str(e))
        try:
            # 青龙面板2.0版本的通知模块
            print("尝试添加青龙面板路径...")
            sys.path.append('/ql/scripts')
            sys.path.append('/ql/data/scripts')
            print("新Python路径:", sys.path)
            print("尝试: import sendNotify (添加路径后)")
            import sendNotify
            send = sendNotify.send
            notify_enabled = True
            print("✓ 成功导入 sendNotify (添加路径后)")
        except Exception as e:
            print("✗ import sendNotify (添加路径后) 失败:", str(e))
            def send(title, content):
                print(f"[通知] {title}\n{content}")
            notify_enabled = False
            print("⚠ 使用备用打印功能")

print("通知模块状态:")
print("- notify_enabled:", notify_enabled)
print("- send 函数:", send)
print("==================")

# ... rest of the script ...
