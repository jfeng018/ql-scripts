#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import random
import logging

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
    
    def __init__(self, token, device_id, site_id="310110", user_agent=None):
        self.base_url = "https://app.ypmedia.cn"
        self.session = requests.Session()
        self.token = token
        self.device_id = device_id
        self.site_id = site_id
        self.logger = logging.getLogger(__name__)
        
        # 设置请求头
        self.user_agent = user_agent or "okhttp/4.10.0"
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "log-header": "I am the log request header.",
            "deviceid": self.device_id,
            "siteid": self.site_id,
            "token": self.token,
            "content-type": "application/json; charset=UTF-8"
        })
    
    def _make_request(self, method, endpoint, data=None):
        """发送API请求的通用方法"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return None
    
    def get_user_info(self):
        """获取用户信息"""
        try:
            index_data = self._make_request("GET", f"/media-basic-port/api/app/index/index?siteId={self.site_id}")
            if not index_data or index_data.get("code") != 0:
                return None
            
            return index_data.get("data", {}).get("userInfo", {})
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {e}")
            return None
    
    def sign_in(self):
        """执行签到"""
        try:
            # 获取用户信息
            user_info = self.get_user_info()
            if not user_info:
                return False, "获取用户信息失败"
            
            # 检查是否已签到
            if user_info.get("signInStatus") == 1:
                return True, "今日已签到"
            
            # 执行签到
            sign_data = {
                "siteId": self.site_id
            }
            sign_result = self._make_request("POST", "/media-basic-port/api/app/user/sign/in", sign_data)
            
            if sign_result and sign_result.get("code") == 0:
                # 签到成功，获取签到积分
                sign_info = sign_result.get("data", {})
                integral = sign_info.get("integral", 0)
                return True, f"签到成功，获得{integral}积分"
            else:
                return False, f"签到失败: {sign_result.get('msg', '未知错误') if sign_result else '请求失败'}"
                
        except Exception as e:
            self.logger.error(f"签到失败: {e}")
            return False, f"签到异常: {str(e)}"
    
    def get_points_info(self):
        """获取积分信息"""
        try:
            user_info = self.get_user_info()
            if not user_info:
                return False, "获取用户信息失败"
            
            total_score = user_info.get("totalScore", 0)
            today_point = user_info.get("todayPoint", 0)
            
            return True, f"总积分: {total_score}, 今日获得: {today_point}分"
                
        except Exception as e:
            self.logger.error(f"获取积分信息失败: {e}")
            return False, f"获取积分信息异常: {str(e)}"
    
    def get_task_list(self):
        """获取任务列表"""
        try:
            # 获取任务中心信息
            task_data = self._make_request("GET", f"/media-basic-port/api/app/task/center?siteId={self.site_id}")
            if not task_data or task_data.get("code") != 0:
                return False, f"获取任务列表失败: {task_data.get('msg', '未知错误') if task_data else '请求失败'}"
            
            task_info = task_data.get("data", {})
            task_list = task_info.get("taskList", [])
            
            # 过滤出未完成的日常任务
            incomplete_tasks = []
            for task in task_list:
                if task.get("frequencyType") == "DAILY" and task.get("status") == 0:
                    incomplete_tasks.append(task)
            
            return True, incomplete_tasks
                
        except Exception as e:
            self.logger.error(f"获取任务列表失败: {e}")
            return False, f"获取任务列表异常: {str(e)}"
    
    def complete_read_task(self, order_by="release_desc", request_type="1"):
        """完成阅读任务"""
        try:
            task_data = {
                "orderBy": order_by,
                "requestType": request_type,
                "siteId": self.site_id
            }
            
            result = self._make_request("POST", "/media-basic-port/api/app/points/read/add", task_data)
            
            if result and result.get("code") == 0:
                return True, "阅读任务完成"
            else:
                return False, f"阅读任务完成失败: {result.get('msg', '未知错误') if result else '请求失败'}"
                
        except Exception as e:
            self.logger.error(f"完成阅读任务失败: {e}")
            return False, f"完成阅读任务异常: {str(e)}"
    
    def complete_video_task(self, order_by="release_desc", request_type="1"):
        """完成视频任务"""
        try:
            task_data = {
                "orderBy": order_by,
                "requestType": request_type,
                "siteId": self.site_id
            }
            
            result = self._make_request("POST", "/media-basic-port/api/app/points/video/add", task_data)
            
            if result and result.get("code") == 0:
                return True, "视频任务完成"
            else:
                return False, f"视频任务完成失败: {result.get('msg', '未知错误') if result else '请求失败'}"
                
        except Exception as e:
            self.logger.error(f"完成视频任务失败: {e}")
            return False, f"完成视频任务异常: {str(e)}"
    
    def complete_share_task(self, order_by="release_desc", request_type="1"):
        """完成分享任务"""
        try:
            task_data = {
                "orderBy": order_by,
                "requestType": request_type,
                "siteId": self.site_id
            }
            
            result = self._make_request("POST", "/media-basic-port/api/app/points/share/add", task_data)
            
            if result and result.get("code") == 0:
                return True, "分享任务完成"
            else:
                return False, f"分享任务完成失败: {result.get('msg', '未知错误') if result else '请求失败'}"
                
        except Exception as e:
            self.logger.error(f"完成分享任务失败: {e}")
            return False, f"完成分享任务异常: {str(e)}"

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    shyp_accounts_env = os.environ.get("SHYP_ACCOUNTS")
    
    if not shyp_accounts_env:
        print("错误：环境变量SHYP_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：SHYP_ACCOUNTS=[{\"token\": \"your_token\", \"device_id\": \"your_device_id\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(shyp_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：SHYP_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：SHYP_ACCOUNTS=[{\"token\": \"your_token\", \"device_id\": \"your_device_id\"}]")
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
        device_id = account.get('device_id')
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i}")
        
        if not token or not device_id:
            result = {
                'sign_result': '失败',
                'points_info': '配置错误',
                'task_result': '缺少token或device_id'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **积分信息**: 配置错误")
            print(f"- **任务信息**: 缺少token或device_id")
            continue
        
        # 创建API客户端
        client = SHYPClient(token, device_id, user_agent=user_agent)
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        # 获取积分信息
        points_success, points_msg = client.get_points_info()
        print(f"- **积分信息**: {points_msg}")
        
        # 获取任务列表并执行任务
        task_success, task_list = client.get_task_list()
        task_msg = f"获取到{len(task_list)}个未完成任务" if task_success else "获取任务列表失败"
        print(f"- **任务信息**: {task_msg}")
        
        # 处理任务
        completed_tasks = []
        if task_success and task_list:
            for task in task_list:
                task_name = task.get("title", "未知任务")
                task_type = task.get("taskType", "")
                
                print(f"  - 尝试完成任务: {task_name} ({task_type})")
                
                # 根据任务类型完成任务
                if task_type == "read":
                    task_result, task_msg = client.complete_read_task()
                elif task_type == "video":
                    task_result, task_msg = client.complete_video_task()
                elif task_type == "share":
                    task_result, task_msg = client.complete_share_task()
                else:
                    task_result, task_msg = False, f"不支持的任务类型: {task_type}"
                
                if task_result:
                    completed_tasks.append(task_name)
                    print(f"    ✓ 任务完成: {task_msg}")
                else:
                    print(f"    ✗ 任务失败: {task_msg}")
                
                # 添加随机延迟避免请求过快
                time.sleep(random.uniform(1, 3))
        
        result = {
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'points_info': points_msg,
            'task_result': task_msg,
            'completed_tasks': completed_tasks
        }
        all_results.append(result)
        
        # 添加延迟避免请求过快
        if i < len(accounts):
            time.sleep(random.uniform(2, 5))
        
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