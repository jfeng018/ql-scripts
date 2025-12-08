#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime

def main():
    print("=== 青龙面板通知模块测试 ===")
    print("当前工作目录:", os.getcwd())
    print("Python路径:", sys.executable)
    print("脚本运行时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # 检查sendNotify文件
    sendnotify_paths = [
        "./sendNotify.py",
        "../sendNotify.py",
        "/ql/scripts/sendNotify.py",
        "/ql/data/scripts/sendNotify.py"
    ]

    print("\n[检查] sendNotify.py文件是否存在:")
    found_sendnotify = False
    for path in sendnotify_paths:
        if os.path.exists(path):
            print(f"✓ 找到sendNotify文件: {path}")
            found_sendnotify = True
        else:
            print(f"✗ 未找到: {path}")

    # 尝试导入
    print("\n[测试] 尝试导入通知模块:")
    notify_success = False
    
    # 方法1: 直接导入send函数
    try:
        print("1. 尝试: from sendNotify import send")
        from sendNotify import send
        notify_success = True
        print("✓ 成功导入sendNotify.send")
        
        # 发送测试消息
        try:
            send("青龙面板通知测试", "这是一条测试消息\n测试时间: {}\n通知模块导入方式: from sendNotify import send".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            print("✓ 测试消息发送成功")
        except Exception as e:
            print("✗ 测试消息发送失败:", str(e))
            
    except ImportError as e:
        print("✗ 导入sendNotify.send失败:", str(e))
        
        # 方法2: 导入模块
        try:
            print("2. 尝试: import sendNotify")
            import sendNotify
            notify_success = True
            print("✓ 成功导入sendNotify模块")
            
            # 发送测试消息
            try:
                sendNotify.send("青龙面板通知测试", "这是一条测试消息\n测试时间: {}\n通知模块导入方式: import sendNotify".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                print("✓ 测试消息发送成功")
            except Exception as e:
                print("✗ 测试消息发送失败:", str(e))
                
        except ImportError as e:
            print("✗ 导入sendNotify模块失败:", str(e))
            
            # 方法3: 添加路径后导入
            try:
                print("3. 尝试添加路径后导入")
                additional_paths = ["/ql/scripts", "/ql/data/scripts"]
                for path in additional_paths:
                    if path not in sys.path:
                        sys.path.append(path)
                
                import sendNotify
                notify_success = True
                print("✓ 成功导入sendNotify模块(添加路径后)")
                
                # 发送测试消息
                try:
                    sendNotify.send("青龙面板通知测试", "这是一条测试消息\n测试时间: {}\n通知模块导入方式: import sendNotify (添加路径后)".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    print("✓ 测试消息发送成功")
                except Exception as e:
                    print("✗ 测试消息发送失败:", str(e))
                    
            except ImportError as e:
                print("✗ 导入sendNotify模块(添加路径后)失败:", str(e))
                
                # 最后的备用方案
                print("⚠ 使用备用通知函数")
                def mock_send(title, content):
                    print(f"[模拟通知] 标题: {title}")
                    print(f"[模拟通知] 内容: {content}")
                
                try:
                    mock_send("青龙面板通知测试", "这是一条测试消息\n测试时间: {}\n通知模块状态: 使用模拟函数".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    print("✓ 模拟通知显示成功")
                except Exception as e:
                    print("✗ 模拟通知显示失败:", str(e))

    print("\n=== 测试结束 ===")

if __name__ == "__main__":
    main()
