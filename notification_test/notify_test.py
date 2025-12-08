#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

def test_notify_module():
    """测试青龙面板内置notify模块"""
    print("=== 青龙面板notify模块测试 ===")
    print("测试时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 尝试导入notify模块
        from notify import send
        print("✓ 成功导入notify模块")
        
        # 发送测试通知
        title = "青龙面板通知测试"
        content = f"notify模块工作正常\n测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            send(title, content)
            print("✓ 测试通知发送成功")
            return True
        except Exception as e:
            print(f"✗ 测试通知发送失败: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ 无法导入notify模块: {e}")
        return False
    except Exception as e:
        print(f"✗ 测试过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    success = test_notify_module()
    if success:
        print("\n🎉 notify模块测试通过!")
    else:
        print("\n❌ notify模块测试失败!")
