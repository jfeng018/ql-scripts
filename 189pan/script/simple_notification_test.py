#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_notification():
    """测试通知功能"""
    print("开始测试通知功能...")
    
    # 尝试导入通知模块
    notify_enabled = False
    send_func = None
    
    try:
        # 青龙面板标准导入方式
        from sendNotify import send
        notify_enabled = True
        send_func = send
        print("✓ 成功从 sendNotify 导入 send 函数")
    except ImportError as e:
        print("✗ 从 sendNotify 导入 send 函数失败:", str(e))
        try:
            # 备用导入方式
            import sendNotify
            notify_enabled = True
            send_func = sendNotify.send
            print("✓ 成功导入 sendNotify 模块")
        except ImportError as e:
            print("✗ 导入 sendNotify 模块失败:", str(e))
            print("⚠ 使用模拟通知函数")
            def mock_send(title, content):
                print(f"[模拟通知] 标题: {title}")
                print(f"[模拟通知] 内容: {content}")
            send_func = mock_send
    
    # 测试发送通知
    if send_func:
        try:
            print("尝试发送测试通知...")
            send_func("天翼云盘签到测试", "这是一条测试通知消息\n测试时间: {}".format(__import__('datetime').datetime.now()))
            print("✓ 通知发送完成")
        except Exception as e:
            print("✗ 通知发送失败:", str(e))
            print("[通知内容预览]")
            print("标题: 天翼云盘签到测试")
            print("内容: 这是一条测试通知消息")
    else:
        print("✗ 无法获取通知函数")

if __name__ == "__main__":
    test_notification()
