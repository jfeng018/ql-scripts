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

class SHYPClient:
    """上海杨浦API客户端"""
    
    def __init__(self, token, user_agent=None):
        self.token = token
        self.session = requests.Session()
        
        # 设置请求头
        self.user_agent = user_agent or 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.15(0x17000f20) NetType/WIFI Language/zh_CN'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Referer': 'https://yp-sh-citymanage.zhengdingtrip.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
    
    def sign_in(self):
        """执行签到"""
        try:
            # 构造签到URL
            sign_url = 'https://yp-sh-citymanage.zhengdingtrip.com/api/v1/user/signIn'
            
            # 发送签到请求
            response = self.session.post(sign_url, timeout=10)
            
            # 检查响应内容判断签到结果
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    return True, f"签到成功，获得{data.get('integral', 0)}积分"
                elif result.get('code') == 400 and '已签到' in result.get('msg', ''):
                    return True, "今日已签到"
                else:
                    return False, f"签到失败: {result.get('msg', '未知错误')}"
            else:
                return False, f"签到请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"签到失败: {e}")
            return False, f"签到异常: {str(e)}"
    
    def get_points_info(self):
        """获取积分信息"""
        try:
            # 获取用户信息URL
            user_url = 'https://yp-sh-citymanage.zhengdingtrip.com/api/v1/user/info'
            
            # 发送请求
            response = self.session.get(user_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    return True, f"当前积分: {data.get('integral', 0)}"
                else:
                    return False, f"获取积分信息失败: {result.get('msg', '未知错误')}"
            else:
                return False, f"获取积分信息请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"获取积分信息失败: {e}")
            return False, f"获取积分信息异常: {str(e)}"
    
    def get_task_list(self):
        """获取任务列表"""
        try:
            # 获取任务列表URL
            task_url = 'https://yp-sh-citymanage.zhengdingtrip.com/api/v1/task/list'
            
            # 发送请求
            response = self.session.get(task_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', [])
                    return True, f"获取到{len(data)}个任务"
                else:
                    return False, f"获取任务列表失败: {result.get('msg', '未知错误')}"
            else:
                return False, f"获取任务列表请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"获取任务列表失败: {e}")
            return False, f"获取任务列表异常: {str(e)}"

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    shyp_accounts_env = os.environ.get("SHYP_ACCOUNTS")
    
    if not shyp_accounts_env:
        print("错误：环境变量SHYP_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：SHYP_ACCOUNTS=[{\"token\": \"your_token\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(shyp_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：SHYP_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：SHYP_ACCOUNTS=[{\"token\": \"your_token\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"上海杨浦签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i}:\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  积分信息: {result.get('points_info', '未知')}\n"
        content += f"  任务信息: {result.get('task_result', '未知')}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== 上海杨浦签到脚本 ===")
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
        token = account.get('token')
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i}")
        
        if not token:
            result = {
                'sign_result': '失败',
                'points_info': '配置错误',
                'task_result': '缺少token'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **积分信息**: 配置错误")
            print(f"- **任务信息**: 缺少token")
            continue
        
        # 创建API客户端
        client = SHYPClient(token, user_agent)
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        # 获取积分信息
        points_success, points_msg = client.get_points_info()
        print(f"- **积分信息**: {points_msg}")
        
        # 获取任务列表
        task_success, task_msg = client.get_task_list()
        print(f"- **任务信息**: {task_msg}")
        
        result = {
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'points_info': points_msg,
            'task_result': task_msg
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
        notification_title = f"上海杨浦签到 - {end_time.strftime('%Y-%m-%d')}"
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