#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os

def test_notify_module():
    """测试青龙面板内置notify模块 - 增强版"""
    print("=== 青龙面板notify模块增强测试 ===")
    print("测试时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 检查环境变量
    print("\n[环境变量检查]")
    notify_env_vars = [
        'PUSH_KEY',         # Server酱
        'TG_BOT_TOKEN',     # Telegram
        'TG_USER_ID',       # Telegram用户ID
        'QYWX_KEY',         # 企业微信机器人
        'BARK_PUSH',        # Bark
        'PUSH_PLUS_TOKEN',  # PushPlus
    ]
    
    found_vars = []
    for var in notify_env_vars:
        if os.environ.get(var):
            found_vars.append(var)
            print(f"✓ 找到通知变量: {var}")
    
    if not found_vars:
        print("⚠ 未找到任何通知变量，通知可能只会输出到控制台")
    else:
        print(f"共找到 {len(found_vars)} 个通知变量")
    
    # 测试多种导入方式
    print("\n[模块导入测试]")
    import_methods = [
        ("from notify import send", lambda: __import__('notify', fromlist=['send']).send),
        ("import notify", lambda: __import__('notify')),
        ("import ql.notify", lambda: __import__('ql', fromlist=['notify'])),
    ]
    
    successful_method = None
    for method_name, method_func in import_methods:
        try:
            module = method_func()
            print(f"✓ {method_name} - 成功")
            successful_method = (method_name, module)
        except ImportError as e:
            print(f"✗ {method_name} - 失败: {e}")
        except Exception as e:
            print(f"✗ {method_name} - 错误: {e}")
    
    if not successful_method:
        print("❌ 所有导入方式都失败")
        return False
    
    # 发送测试通知
    print("\n[通知发送测试]")
    try:
        title = "青龙面板通知测试"
        content = f"""青龙面板通知模块测试报告
测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
环境变量: {', '.join(found_vars) if found_vars else '无'}
导入方式: {successful_method[0]}
状态: 测试成功

此通知用于验证青龙面板的通知功能是否正常工作。"""
        
        # 根据导入方式调用相应的发送函数
        if "from notify import send" in successful_method[0]:
            from notify import send
            send(title, content)
        elif "import notify" in successful_method[0]:
            import notify
            notify.send(title, content)
        elif "import ql.notify" in successful_method[0]:
            import ql.notify
            ql.notify.send(title, content)
            
        print("✓ 测试通知发送成功")
        return True
        
    except Exception as e:
        print(f"✗ 测试通知发送失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试...")
    success = test_notify_module()
    
    if success:
        print("\n🎉 测试通过!")
        print("青龙面板通知模块工作正常，可以接收通知")
    else:
        print("\n❌ 测试失败!")
        print("请检查青龙面板的通知配置")

if __name__ == "__main__":
    main()
