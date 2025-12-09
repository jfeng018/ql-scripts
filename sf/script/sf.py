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

class SFExpressClient:
    """顺丰速运API客户端"""
    
    def __init__(self, cookies, user_id, user_agent=None, channel=None, device_id=None):
        self.cookies = cookies
        self.user_id = user_id
        self.channel = channel or 'weixin'
        self.device_id = device_id or 'device_id'
        self.session = requests.Session()
        
        # 设置Cookies
        cookie_dict = {}
        for item in cookies.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        self.session.cookies.update(cookie_dict)
        
        # 设置User-Agent和其他请求头
        self.user_agent = user_agent or 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.15(0x17000f20) NetType/WIFI Language/zh_CN'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Referer': 'https://m.csair.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'channel': self.channel,
            'device-id': self.device_id,
            'user-agent': self.user_agent
        })
    
    def sign_in(self):
        """执行签到"""
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect?source=JFZX&bizType=88&appId=16892&serviceCode=JFZX&redirect_url=%2Fmcs-mimp%2Fweb%2FexchangeCenter%2Findex%3Fbusiness%3Dintegral%26scene%3DpointExchange%26pageType%3Dapp'
            response = self.session.get(url, timeout=10)
            
            # 获取签到相关信息
            sign_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
            data = {
                "comeFrom": "vioin",
                "channelFrom": "WEIXIN"
            }
            
            sign_response = self.session.post(sign_url, json=data, timeout=10)
            result = sign_response.json()
            
            if result.get('success') and result.get('obj'):
                obj = result.get('obj')
                if obj.get('hasFinishSign') == 1:
                    return True, f"今日已签到，获得{obj.get('count', 0)}积分"
                else:
                    return True, f"签到成功，获得{obj.get('count', 0)}积分"
            else:
                return False, result.get('errorMessage', '签到失败')
                
        except Exception as e:
            print(f"签到失败: {e}")
            return False, f"签到异常: {str(e)}"
    
    def get_points_info(self):
        """获取积分信息"""
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/member/points/balance'
            response = self.session.get(url, timeout=10)
            result = response.json()
            
            if result.get('success'):
                obj = result.get('obj', {})
                return True, f"当前积分: {obj.get('availablePoints', 0)}"
            else:
                return False, "获取积分信息失败"
        except Exception as e:
            print(f"获取积分信息失败: {e}")
            return False, f"获取积分信息异常: {str(e)}"
    
    def get_task_list(self):
        """获取任务列表"""
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
            data = {
                "channelType": "1",
                "deviceId": self.device_id,
                "pageType": "APP"
            }
            
            response = self.session.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('success'):
                task_list = result.get('obj', [])
                return True, task_list
            else:
                return False, []
        except Exception as e:
            print(f"获取任务列表失败: {e}")
            return False, []

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    sf_accounts_env = os.environ.get("SF_ACCOUNTS")
    
    if not sf_accounts_env:
        print("错误：环境变量SF_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：SF_ACCOUNTS=[{\"cookies\": \"your_cookies\", \"user_id\": \"your_user_id\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(sf_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：SF_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：SF_ACCOUNTS=[{\"cookies\": \"your_cookies\", \"user_id\": \"your_user_id\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"顺丰速运签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i} ({result.get('user_id', 'Unknown')}):\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  积分信息: {result.get('points_info', '未知')}\n"
        content += f"  任务完成: {result.get('task_result', '未知')}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== 顺丰速运签到脚本 ===")
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
        user_id = account.get('user_id')
        user_agent = account.get('user_agent')
        channel = account.get('channel')
        device_id = account.get('device_id')
        
        print(f"## 账户{i} ({user_id})")
        
        if not cookies or not user_id:
            result = {
                'user_id': user_id or '未知',
                'sign_result': '失败',
                'points_info': '配置错误',
                'task_result': '缺少cookies或user_id'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **积分信息**: 配置错误")
            print(f"- **任务完成**: 缺少cookies或user_id")
            continue
        
        # 创建API客户端
        client = SFExpressClient(cookies, user_id, user_agent, channel, device_id)
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        # 获取积分信息
        points_success, points_msg = client.get_points_info()
        print(f"- **积分信息**: {points_msg}")
        
        # 获取任务列表
        task_success, task_list = client.get_task_list()
        task_msg = f"获取到{len(task_list)}个任务" if task_success else "获取任务列表失败"
        print(f"- **任务完成**: {task_msg}")
        
        result = {
            'user_id': user_id,
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
        notification_title = f"顺丰速运签到 - {end_time.strftime('%Y-%m-%d')}"
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