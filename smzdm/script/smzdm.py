#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import re
import hashlib

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

# 公共变量：用于 sign 计算的固定 key
SECRET_KEY = "zok5JtAq3$QixaA%mncn*jGWlEpSL3E1"

def calculate_sign_from_params(params):
    """
    从字典参数生成 sign 签名

    Args:
        params: 包含请求参数的字典

    Returns:
        计算出的 MD5 签名（大写）
    """
    # 1. 获取所有 key 并按字母顺序排序
    sorted_keys = sorted(params.keys())

    # 2. 构建 key=value 对，并用 & 连接（跳过空值）
    param_list = []
    for key in sorted_keys:
        value = params[key]
        # 跳过空值（None、空字符串、空列表等）
        if value is not None and value != "" and value != []:
            # 转换为字符串并去除空格和换行符
            value_str = re.sub(r'[^\S\r\n]+', '', str(value))
            # 再次检查处理后的值是否为空
            if value_str:
                param_list.append(f"{key}={value_str}")

    # 3. 用 & 连接所有参数
    query_string = "&".join(param_list)

    # 4. 在最后拼接固定的 key
    query_string += f"&key={SECRET_KEY}"

    # 5. 计算 MD5
    md5_hash = hashlib.md5(query_string.encode('utf-8')).hexdigest()

    # 6. 返回大写的 MD5
    return md5_hash.upper()

class SMZDMClient:
    """什么值得买API客户端"""
    
    def __init__(self, cookie, user_agent=None):
        self.cookie = cookie
        self.session = requests.Session()
        
        # 设置Cookies
        cookie_dict = {}
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        self.session.cookies.update(cookie_dict)
        
        # 设置User-Agent和其他请求头
        self.user_agent = user_agent or 'smzdm 11.1.35 rv:167 (iPhone 6s; iOS 15.8.3; zh_CN)/iphone_smzdmapp/11.1.35'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Referer': 'https://m.smzdm.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
    
    def sign_in(self):
        """执行签到"""
        try:
            # 构造签到URL
            sign_url = 'https://user-api.smzdm.com/checkin'
            
            # 构建请求参数
            current_time = int(time.time() * 1000)
            params = {
                'basic_v': '0',
                'f': 'iphone',
                'time': str(current_time),
                'v': '11.1.35',
                'weixin': '1',
                'zhuanzai_ab': 'b'
            }
            
            # 计算签名
            sign = calculate_sign_from_params(params)
            params['sign'] = sign
            
            # 设置特殊请求头
            headers = self.session.headers.copy()
            headers.update({
                'request_key': str(int(time.time() * 1000000000))[:18],
                'Content-Encoding': 'gzip',
                'Accept-Language': 'zh-Hans-CN;q=1'
            })
            
            # 发送签到请求
            response = self.session.post(sign_url, data=params, headers=headers, timeout=10)
            
            # 检查响应内容判断签到结果
            if response.status_code == 200:
                result = response.json()
                if result.get('error_code') == 0:
                    data = result.get('data', {})
                    # 提取签到信息
                    cpadd = data.get('cpadd', 0)  # 本次新增积分
                    daily_num = data.get('daily_num', 0)  # 连续签到天数
                    cpoints = data.get('cpoints', 0)  # 当前积分
                    
                    return True, f"签到成功，获得{cpadd}积分，连续签到{daily_num}天，当前积分{cpoints}"
                elif result.get('error_code') == 1 and '已经签到' in result.get('error_msg', ''):
                    return True, "今日已签到"
                else:
                    return False, f"签到失败: {result.get('error_msg', '未知错误')}"
            else:
                return False, f"签到请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"签到失败: {e}")
            return False, f"签到异常: {str(e)}"
    
    def get_points_info(self):
        """获取积分信息"""
        try:
            # 获取用户信息URL
            user_url = 'https://user-api.smzdm.com/user_info'
            
            # 发送请求
            response = self.session.get(user_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error_code') == 0:
                    data = result.get('data', {})
                    point = data.get('point', 0)
                    exp = data.get('exp', 0)
                    gold = data.get('gold', 0)
                    return True, f"当前积分: {point}, 经验值: {exp}, 金币: {gold}"
                else:
                    return False, f"获取积分信息失败: {result.get('error_msg', '未知错误')}"
            else:
                return False, f"获取积分信息请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"获取积分信息失败: {e}")
            return False, f"获取积分信息异常: {str(e)}"
    
    def get_task_list(self):
        """获取任务列表"""
        try:
            # 获取任务列表URL
            task_url = 'https://user-api.smzdm.com/task/list'
            
            # 构建请求参数
            current_time = int(time.time() * 1000)
            params = {
                'basic_v': '0',
                'f': 'iphone',
                'time': str(current_time),
                'v': '11.1.35',
                'weixin': '1',
                'zhuanzai_ab': 'b'
            }
            
            # 计算签名
            sign = calculate_sign_from_params(params)
            params['sign'] = sign
            
            # 设置特殊请求头
            headers = self.session.headers.copy()
            headers.update({
                'request_key': str(int(time.time() * 1000000000))[:18],
                'Content-Encoding': 'gzip',
                'Accept-Language': 'zh-Hans-CN;q=1'
            })
            
            # 发送请求
            response = self.session.get(task_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error_code') == 0:
                    data = result.get('data', {})
                    return True, data
                else:
                    return False, f"获取任务列表失败: {result.get('error_msg', '未知错误')}"
            else:
                return False, f"获取任务列表请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"获取任务列表失败: {e}")
            return False, f"获取任务列表异常: {str(e)}"
    
    def complete_task(self, task_id, task_type):
        """完成任务"""
        try:
            # 根据任务类型选择不同的API
            if task_type == 'normal':
                task_url = 'https://user-api.smzdm.com/task/achieve'
            else:
                task_url = 'https://user-api.smzdm.com/task/achieve'
            
            # 构建请求参数
            current_time = int(time.time() * 1000)
            params = {
                'basic_v': '0',
                'f': 'iphone',
                'task_id': task_id,
                'time': str(current_time),
                'v': '11.1.35',
                'weixin': '1',
                'zhuanzai_ab': 'b'
            }
            
            # 计算签名
            sign = calculate_sign_from_params(params)
            params['sign'] = sign
            
            # 设置特殊请求头
            headers = self.session.headers.copy()
            headers.update({
                'request_key': str(int(time.time() * 1000000000))[:18],
                'Content-Encoding': 'gzip',
                'Accept-Language': 'zh-Hans-CN;q=1'
            })
            
            # 发送请求
            response = self.session.post(task_url, data=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error_code') == 0:
                    return True, "任务完成"
                else:
                    return False, f"任务完成失败: {result.get('error_msg', '未知错误')}"
            else:
                return False, f"任务完成请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"任务完成失败: {e}")
            return False, f"任务完成异常: {str(e)}"

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    smzdm_accounts_env = os.environ.get("SMZDM_ACCOUNTS")
    
    if not smzdm_accounts_env:
        print("错误：环境变量SMZDM_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：SMZDM_ACCOUNTS=[{\"cookie\": \"your_cookie\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(smzdm_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：SMZDM_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：SMZDM_ACCOUNTS=[{\"cookie\": \"your_cookie\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"什么值得买签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i}:\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  积分信息: {result.get('points_info', '未知')}\n"
        if 'completed_tasks' in result:
            content += f"  完成任务: {', '.join(result['completed_tasks'])}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== 什么值得买签到脚本 ===")
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
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i}")
        
        if not cookie:
            result = {
                'sign_result': '失败',
                'points_info': '配置错误'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **积分信息**: 配置错误")
            continue
        
        # 创建API客户端
        client = SMZDMClient(cookie, user_agent)
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        # 获取积分信息
        points_success, points_msg = client.get_points_info()
        print(f"- **积分信息**: {points_msg}")
        
        # 获取任务列表并执行任务
        task_success, task_data = client.get_task_list()
        completed_tasks = []
        if task_success and task_data:
            task_list = task_data.get('task_list', [])
            print(f"- **任务信息**: 获取到{len(task_list)}个任务")
            
            # 处理未完成的任务
            for task in task_list:
                task_id = task.get('task_id')
                task_name = task.get('task_name', '未知任务')
                task_status = task.get('task_status')
                
                # 如果任务未完成，尝试完成任务
                if task_status != '3':  # 3表示已完成
                    print(f"  - 尝试完成任务: {task_name}")
                    task_result, task_msg = client.complete_task(task_id, 'normal')
                    if task_result:
                        completed_tasks.append(task_name)
                        print(f"    ✓ 任务完成: {task_msg}")
                    else:
                        print(f"    ✗ 任务失败: {task_msg}")
                    
                    # 添加延迟避免请求过快
                    time.sleep(2)
        else:
            print(f"- **任务信息**: 获取任务列表失败")
        
        result = {
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'points_info': points_msg,
            'completed_tasks': completed_tasks
        }
        all_results.append(result)
        
        # 添加延迟避免请求过快
        if i < len(accounts):
            time.sleep(5)
        
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
        notification_title = f"什么值得买签到 - {end_time.strftime('%Y-%m-%d')}"
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