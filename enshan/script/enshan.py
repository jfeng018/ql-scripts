#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import re

# 青龙面板官方通知方式 - 最简实现
def send_notification(title, content):
    """
    使用青龙面板官方推荐的通知方式
    完全按照青龙面板的标准实现
    """
    try:
        # 青龙面板标准通知导入方式
        import notify
        notify.send(title, content)
        print("✅ 通知发送成功")
        return True
    except Exception as e:
        print(f"❌ 通知发送失败: {e}")
        # 备用方案：打印到控制台
        print(f"\n[通知] {title}\n{content}")
        return False

class EnshanClient:
    """恩山论坛API客户端"""
    
    def __init__(self, cookies, formhash, user_agent=None):
        self.cookies = cookies
        self.formhash = formhash
        self.session = requests.Session()
        
        # 设置Cookies
        cookie_dict = {}
        for item in cookies.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        self.session.cookies.update(cookie_dict)
        
        # 设置User-Agent和其他请求头
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Referer': 'https://www.right.com.cn/forum/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
    
    def sign_in(self):
        """执行签到"""
        try:
            # 构造签到URL
            sign_url = f'https://www.right.com.cn/forum/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'
            
            # 构造签到数据
            data = {
                'formhash': self.formhash,
                'submit': '1',
                'qiandao': '1'
            }
            
            # 发送签到请求
            response = self.session.post(sign_url, data=data, timeout=10)
            
            # 检查响应内容判断签到结果
            if '签到成功' in response.text or '恭喜你签到成功' in response.text:
                return True, "签到成功"
            elif '您今日已经签到' in response.text:
                return True, "今日已签到"
            else:
                # 尝试提取错误信息
                match = re.search(r'<div class="alert_error">(.*?)</div>', response.text)
                if match:
                    error_msg = match.group(1).strip()
                    return False, f"签到失败: {error_msg}"
                else:
                    return False, "签到失败，未知原因"
                    
        except Exception as e:
            print(f"签到失败: {e}")
            return False, f"签到异常: {str(e)}"
    
    def get_sign_info(self):
        """获取签到信息"""
        try:
            # 访问论坛首页获取用户信息
            home_url = 'https://www.right.com.cn/forum/'
            response = self.session.get(home_url, timeout=10)
            
            # 尝试提取用户信息
            # 查找用户名
            username_match = re.search(r'<strong><a href="home\.php\?mod=space.*?>(.*?)</a>', response.text)
            username = username_match.group(1) if username_match else "未知用户"
            
            # 查找签到信息
            sign_info_match = re.search(r'您已经连续签到 <b>(\d+)</b> 天', response.text)
            sign_days = sign_info_match.group(1) if sign_info_match else "未知"
            
            return True, f"用户: {username}, 连续签到: {sign_days}天"
            
        except Exception as e:
            print(f"获取签到信息失败: {e}")
            return False, f"获取签到信息异常: {str(e)}"

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    enshan_accounts_env = os.environ.get("ENSHAN_ACCOUNTS")
    
    if not enshan_accounts_env:
        print("错误：环境变量ENSHAN_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：ENSHAN_ACCOUNTS=[{\"cookies\": \"your_cookies\", \"formhash\": \"your_formhash\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(enshan_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：ENSHAN_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：ENSHAN_ACCOUNTS=[{\"cookies\": \"your_cookies\", \"formhash\": \"your_formhash\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"恩山论坛签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i}:\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  签到信息: {result.get('sign_info', '未知')}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== 恩山论坛签到脚本 ===")
    print("启动时间:", start_time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # 加载账户信息
    accounts = load_accounts()
    print(f"## 执行概览")
    print(f"- **启动时间**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- **账户数量**: {len(accounts)} 个")
    print()
    
    # 存储所有账户的执行结果
    all_results = []
    
    # 处理每个账户
    for i, account in enumerate(accounts, 1):
        cookies = account.get('cookies')
        formhash = account.get('formhash')
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i}")
        
        if not cookies or not formhash:
            result = {
                'sign_result': '失败',
                'sign_info': '配置错误'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **签到信息**: 配置错误")
            continue
        
        # 创建API客户端
        client = EnshanClient(cookies, formhash, user_agent)
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        # 获取签到信息
        info_success, info_msg = client.get_sign_info()
        print(f"- **签到信息**: {info_msg}")
        
        result = {
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'sign_info': info_msg
        }
        all_results.append(result)
        
        # 添加延迟避免请求过快
        if i < len(accounts):
            time.sleep(2)
        
        print()
    
    # 记录结束时间并计算运行时间
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("---")
    print("## 执行统计")
    print(f"- **结束时间**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- **运行时长**: {duration:.2f} 秒")
    print()
    print("✅ **所有账户处理完成！**")
    
    # 发送通知
    try:
        notification_title = f"恩山论坛签到 - {end_time.strftime('%Y-%m-%d')}"
        notification_content = format_notification_content(all_results, duration)
        
        # 使用青龙面板官方通知
        print("\n--- 通知发送 ---")
        if send_notification(notification_title, notification_content):
            print("🔔 通知已发送")
        else:
            print("📝 通知内容预览:")
            print(notification_content)
    except Exception as e:
        print(f"\n❌ 发送通知失败: {e}")

if __name__ == "__main__":
    main()