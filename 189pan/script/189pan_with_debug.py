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

print("=== 天翼云盘签到脚本调试信息 ===")
print("脚本启动时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path[:3], "...")  # 只显示前3个避免太长

# 青龙面板通知模块
notify_enabled = False
send = None

print("\n[调试] 开始尝试导入通知模块...")

# 尝试多种方式导入通知模块
try:
    print("[调试] 尝试: from sendNotify import send")
    from sendNotify import send
    notify_enabled = True
    print("[调试] ✓ 成功导入 sendNotify.send")
except Exception as e:
    print("[调试] ✗ from sendNotify import send 失败:", str(e))
    try:
        print("[调试] 尝试: import sendNotify")
        import sendNotify
        send = sendNotify.send
        notify_enabled = True
        print("[调试] ✓ 成功导入 sendNotify")
    except Exception as e:
        print("[调试] ✗ import sendNotify 失败:", str(e))
        try:
            # 青龙面板2.0版本的通知模块
            print("[调试] 尝试添加青龙面板路径...")
            additional_paths = ['/ql/scripts', '/ql/data/scripts', '/ql']
            for path in additional_paths:
                if path not in sys.path:
                    sys.path.append(path)
            print("[调试] 新增路径后尝试导入...")
            import sendNotify
            send = sendNotify.send
            notify_enabled = True
            print("[调试] ✓ 成功导入 sendNotify (添加路径后)")
        except Exception as e:
            print("[调试] ✗ import sendNotify (添加路径后) 失败:", str(e))
            def send(title, content):
                print(f"[通知] {title}\n{content}")
            notify_enabled = False
            print("[调试] ⚠ 使用备用打印功能")

print("[调试] 通知模块最终状态:")
print("[调试] - notify_enabled:", notify_enabled)
if notify_enabled:
    print("[调试] - send 函数: 已加载")
else:
    print("[调试] - send 函数: 未加载，使用模拟函数")

print("=" * 40)

# ... rest of the original script ...
