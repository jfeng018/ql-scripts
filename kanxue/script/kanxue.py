#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import re
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

class KanxueClient:
    """看雪论坛API客户端"""
    
    def __init__(self, cookie, csrf_token, user_agent=None):
        self.cookie = cookie
        self.csrf_token = csrf_token
        self.session = requests.Session()
        
        # 设置Cookies
        cookie_dict = {}
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        self.session.cookies.update(cookie_dict)
        
        # 设置User-Agent和其他请求头
        self.user_agent = user_agent or (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/141.0.0.0 Safari/537.36'
        )
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-ch-ua-platform': '"macOS"',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'Sec-GPC': '1',
            'Accept-Language': 'zh-CN,zh;q=0.6',
            'Origin': 'https://bbs.kanxue.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://bbs.kanxue.com/',
            'Cookie': self.cookie
        })
    
    def get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        """
        return {
            'User-Agent': self.user_agent,
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-ch-ua-platform': '"macOS"',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'Sec-GPC': '1',
            'Accept-Language': 'zh-CN,zh;q=0.6',
            'Origin': 'https://bbs.kanxue.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://bbs.kanxue.com/',
            'Cookie': self.cookie
        }
    
    def sign_in(self):
        """执行签到"""
        logger.info("开始执行看雪论坛签到...")
        headers = self.get_headers()
        sign_url = 'https://bbs.kanxue.com/user-signin.htm'
        data = {
            'csrf_token': self.csrf_token
        }
        
        try:
            response = requests.post(
                sign_url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 尝试解析JSON响应
            try:
                result = response.json()
                logger.info(f"看雪论坛签到结果: {result}")
                
                if 'code' in result:
                    if result.get('code') == '0':
                        message = result.get('message', '')
                        return True, f"签到成功 - {message}"
                    else:
                        message = result.get('message', '签到完成')
                        if '已经签到' in message or '已签到' in message:
                            return True, f"今日已签到 - {message}"
                        else:
                            return False, f"签到失败 - {message}"
                else:
                    # 如果没有code字段，检查message字段
                    message = result.get('message', '')
                    if '签到成功' in message or 'success' in message.lower():
                        return True, f"签到成功 - {message}"
                    elif '已经签到' in message or '已签到' in message:
                        return True, f"今日已签到 - {message}"
                    else:
                        return False, f"签到失败 - {message}"
                        
            except json.JSONDecodeError:
                # 如果不是JSON响应，检查文本内容
                response_text = response.text
                if '签到成功' in response_text:
                    return True, "签到成功"
                elif '已经签到' in response_text or '已签到' in response_text:
                    return True, "今日已签到"
                else:
                    return False, f"签到失败，响应内容: {response_text[:100]}"
                    
        except requests.RequestException as e:
            error_msg = f"签到失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"签到异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_user_info(self):
        """获取用户信息"""
        try:
            # 访问论坛首页获取用户信息
            home_url = 'https://bbs.kanxue.com/'
            response = self.session.get(home_url, timeout=30)
            
            # 检查响应状态
            response.raise_for_status()
            
            # 尝试提取用户信息
            # 查找用户名
            username_match = re.search(r'<a href="home\.php\?mod=space.*?username=(.*?)">', response.text)
            if not username_match:
                username_match = re.search(r'<strong><a href="home\.php\?mod=space.*?>(.*?)</a>', response.text)
            username = username_match.group(1) if username_match else "未知用户"
            
            # 查找签到信息
            sign_info_match = re.search(r'您已经连续签到 <b>(\d+)</b> 天', response.text)
            sign_days = sign_info_match.group(1) if sign_info_match else "未知"
            
            return True, f"用户: {username}, 连续签到: {sign_days}天"
            
        except requests.RequestException as e:
            error_msg = f"获取用户信息失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"获取用户信息异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    kanxue_accounts_env = os.environ.get("KANXUE_ACCOUNTS")
    
    if not kanxue_accounts_env:
        print("错误：环境变量KANXUE_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：KANXUE_ACCOUNTS=[{\"cookie\": \"your_cookie\", \"csrf_token\": \"your_csrf_token\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(kanxue_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：KANXUE_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：KANXUE_ACCOUNTS=[{\"cookie\": \"your_cookie\", \"csrf_token\": \"your_csrf_token\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"看雪论坛签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i}:\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  用户信息: {result.get('user_info', '未知')}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== 看雪论坛签到脚本 ===")
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
        cookie = account.get('cookie')
        csrf_token = account.get('csrf_token')
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i}")
        
        if not cookie or not csrf_token:
            result = {
                'sign_result': '失败',
                'user_info': '配置错误'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **用户信息**: 配置错误")
            continue
        
        # 创建API客户端
        client = KanxueClient(cookie, csrf_token, user_agent)
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        # 获取用户信息
        info_success, info_msg = client.get_user_info()
        print(f"- **用户信息**: {info_msg}")
        
        result = {
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'user_info': info_msg
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
        notification_title = f"看雪论坛签到 - {end_time.strftime('%Y-%m-%d')}"
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