#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time

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

class WPSApiClient:
    """WPS API客户端"""
    
    def __init__(self, user_id, cookies, user_agent=None):
        self.user_id = user_id
        self.cookies = cookies
        self.session = requests.Session()
        self.session.cookies.update({
            'wps_sid': cookies
        })
        
        # 设置User-Agent
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Referer': 'https://vip.wps.cn/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
    
    def get_user_info(self):
        """获取用户信息"""
        try:
            url = f'https://vip.wps.cn/userinfo?platform=2&uid={self.user_id}'
            response = self.session.get(url, timeout=10)
            return response.json()
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def sign_in(self):
        """执行签到"""
        try:
            url = 'https://vip.wps.cn/sign/v1'
            data = {
                'platform': '2'
            }
            response = self.session.post(url, data=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"签到失败: {e}")
            return {'result': 'error', 'msg': str(e)}
    
    def get_sign_info(self):
        """获取签到信息"""
        try:
            url = 'https://vip.wps.cn/sign/v1/get'
            params = {
                'platform': '2'
            }
            response = self.session.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"获取签到信息失败: {e}")
            return None

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    wps_accounts_env = os.environ.get("WPS_ACCOUNTS")
    
    if not wps_accounts_env:
        print("错误：环境变量WPS_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：WPS_ACCOUNTS=[{\"user_id\": \"12345\", \"cookies\": \"your_cookies\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(wps_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：WPS_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：WPS_ACCOUNTS=[{\"user_id\": \"12345\", \"cookies\": \"your_cookies\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"WPS签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i} ({result.get('user_id', 'Unknown')}):\n"
        content += f"  用户信息: {result.get('user_info', '获取失败')}\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  签到详情: {result.get('sign_detail', '无')}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== WPS签到脚本 ===")
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
        user_id = account.get('user_id')
        cookies = account.get('cookies')
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i} ({user_id})")
        
        if not user_id or not cookies:
            result = {
                'user_id': user_id or '未知',
                'user_info': '配置错误',
                'sign_result': '失败',
                'sign_detail': '缺少user_id或cookies'
            }
            all_results.append(result)
            print(f"- **用户信息**: 配置错误")
            print(f"- **签到结果**: 失败")
            print(f"- **签到详情**: 缺少user_id或cookies")
            continue
        
        # 创建API客户端
        client = WPSApiClient(user_id, cookies, user_agent)
        
        # 获取用户信息
        user_info_data = client.get_user_info()
        if user_info_data and user_info_data.get('result') == 'ok':
            user_name = user_info_data.get('data', {}).get('nickname', '未知用户')
            user_info = f"{user_name}"
        else:
            user_info = "获取失败"
        
        print(f"- **用户信息**: {user_info}")
        
        # 执行签到
        sign_result = client.sign_in()
        if sign_result.get('result') == 'ok':
            sign_status = "成功"
            sign_detail = sign_result.get('data', {}).get('msg', '签到成功')
        else:
            sign_status = "失败"
            sign_detail = sign_result.get('msg', '签到失败')
        
        print(f"- **签到结果**: {sign_status}")
        print(f"- **签到详情**: {sign_detail}")
        
        # 获取签到信息
        sign_info = client.get_sign_info()
        if sign_info and sign_info.get('result') == 'ok':
            total_sign_days = sign_info.get('data', {}).get('total_sign_days', 0)
            print(f"- **累计签到**: {total_sign_days}天")
        
        result = {
            'user_id': user_id,
            'user_info': user_info,
            'sign_result': sign_status,
            'sign_detail': sign_detail
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
        notification_title = f"WPS签到 - {end_time.strftime('%Y-%m-%d')}"
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