#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import hashlib
import random

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

def calculate_sign(appid, member_id, timestamp=None):
    """
    计算请求签名
    
    Args:
        appid: 小程序appid
        member_id: 会员ID
        timestamp: 时间戳，不传则自动生成
    
    Returns:
        dict: 包含sign和相关参数的字典
    """
    if timestamp is None:
        timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
    
    trans_id = appid + timestamp
    secret = "damogic8888"
    random_str = str(random.randint(100000, 999999))
    
    # 拼接签名字符串
    sign_str = f"{secret}{member_id}{random_str}{timestamp}{trans_id}"
    
    # MD5加密
    md5_hash = hashlib.md5()
    md5_hash.update(sign_str.encode('utf-8'))
    sign = md5_hash.hexdigest().upper()
    
    return {
        'sign': sign,
        'random': random_str,
        'appid': appid,
        'transId': trans_id,
        'timestamp': timestamp
    }

class ErkeClient:
    """鸿星尔克API客户端"""
    
    def __init__(self, member_id, enterprise_id, unionid, openid, wx_openid, appid="wxa1f1fa3785a42271", user_agent=None):
        self.member_id = member_id
        self.enterprise_id = enterprise_id
        self.unionid = unionid
        self.openid = openid
        self.wx_openid = wx_openid
        self.appid = appid
        self.session = requests.Session()
        
        # 设置请求头
        self.user_agent = user_agent or 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.15(0x17000f20) NetType/WIFI Language/zh_CN'
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Referer': 'https://erp-mp.erke.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json'
        })
    
    def get_headers(self, enterprise_id="-1"):
        """获取请求头"""
        return {
            'Host': 'wxx.erke.com',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent': self.user_agent,
            'Referer': 'https://servicewechat.com/wxa1f1fa3785a42271/339/page-frame.html',
            'enterpriseId': enterprise_id
        }
    
    def get_points_info(self):
        """获取积分信息"""
        try:
            # 计算签名
            sign_data = calculate_sign(self.appid, self.member_id)
            
            # 构建请求数据
            data = {
                'memberId': self.member_id,
                'cliqueId': '-1',
                'cliqueMemberId': '-1',
                'useClique': '0',
                'enterpriseId': self.enterprise_id,
                'unionid': self.unionid,
                'openid': self.openid,
                'wxOpenid': self.wx_openid,
                'random': sign_data['random'],
                'appid': sign_data['appid'],
                'transId': sign_data['transId'],
                'sign': sign_data['sign'],
                'timestamp': sign_data['timestamp'],
                'gicWxaVersion': '3.9.56',
                'launchOptions': '{"path":"pages/authorize/authorize","query":{},"scene":1101,"referrerInfo":{},"apiCategory":"default"}'
            }
            
            # 获取请求头
            headers = self.get_headers(self.enterprise_id)
            
            # 发送请求
            url = 'https://wxx.erke.com/gic-wx-app-member/member/getMemberInfoByWxApp'
            response = self.session.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('rsp_code') == '0000':
                    data = result.get('data', {})
                    point = data.get('point', 0) if data else 0
                    return True, f"当前积分: {point}"
                else:
                    return False, f"获取积分信息失败: {result.get('rsp_msg', '未知错误')}"
            else:
                return False, f"获取积分信息请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"获取积分信息失败: {e}")
            return False, f"获取积分信息异常: {str(e)}"
    
    def sign_in(self):
        """执行签到"""
        try:
            # 计算签名
            sign_data = calculate_sign(self.appid, self.member_id)
            
            # 构建签到数据
            data = {
                'source': 'wxapp',
                'memberId': self.member_id,
                'cliqueId': '-1',
                'cliqueMemberId': '-1',
                'useClique': 0,
                'enterpriseId': self.enterprise_id,
                'unionid': self.unionid,
                'openid': self.openid,
                'wxOpenid': self.wx_openid,
                'sign': sign_data['sign'],
                'random': sign_data['random'],
                'appid': sign_data['appid'],
                'transId': sign_data['transId'],
                'timestamp': sign_data['timestamp'],
                'gicWxaVersion': '3.9.56',
                'launchOptions': '{"path":"pages/authorize/authorize","query":{},"scene":1101,"referrerInfo":{},"apiCategory":"default"}'
            }
            
            # 获取请求头
            headers = self.get_headers(self.enterprise_id)
            headers['Content-Type'] = 'application/json;charset=UTF-8'
            
            # 发送签到请求
            url = 'https://wxx.erke.com/gic-wx-app-member/sign/member_sign.json'
            response = self.session.post(url, headers=headers, json=data, timeout=10)
            
            # 检查响应内容判断签到结果
            if response.status_code == 200:
                result = response.json()
                rsp_code = result.get('rsp_code', '')
                rsp_msg = result.get('rsp_msg', '')
                
                # 处理各种成功情况
                success_codes = ['0000', '1001', '0', '200']
                if rsp_code in success_codes or '成功' in rsp_msg or '已签到' in rsp_msg:
                    # 尝试提取积分信息
                    data = result.get('data', {})
                    point = data.get('point', 0) if data else 0
                    return True, f"签到成功，获得{point}积分"
                else:
                    return False, f"签到失败: {rsp_msg}"
            else:
                return False, f"签到请求失败，状态码: {response.status_code}"
                
        except Exception as e:
            print(f"签到失败: {e}")
            return False, f"签到异常: {str(e)}"

def load_accounts():
    """加载账户信息 - 适配青龙面板环境变量"""
    # 从环境变量获取配置
    erke_accounts_env = os.environ.get("ERKE_ACCOUNTS")
    
    if not erke_accounts_env:
        print("错误：环境变量ERKE_ACCOUNTS未设置")
        print("请在青龙面板中配置环境变量，格式：ERKE_ACCOUNTS=[{\"member_id\": \"your_member_id\", \"enterprise_id\": \"your_enterprise_id\", \"unionid\": \"your_unionid\", \"openid\": \"your_openid\", \"wx_openid\": \"your_wx_openid\"}]")
        sys.exit(1)
    
    try:
        accounts = json.loads(erke_accounts_env)
        return accounts
    except json.JSONDecodeError:
        print("错误：ERKE_ACCOUNTS环境变量格式不正确，应为JSON格式")
        print("示例：ERKE_ACCOUNTS=[{\"member_id\": \"your_member_id\", \"enterprise_id\": \"your_enterprise_id\", \"unionid\": \"your_unionid\", \"openid\": \"your_openid\", \"wx_openid\": \"your_wx_openid\"}]")
        sys.exit(1)

def format_notification_content(accounts_results, duration):
    """格式化通知内容"""
    content = f"鸿星尔克签到任务完成\n"
    content += f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"运行时长: {duration:.2f}秒\n"
    content += f"账户数量: {len(accounts_results)}个\n"
    content += "=" * 30 + "\n"
    
    for i, result in enumerate(accounts_results, 1):
        content += f"账户{i}:\n"
        content += f"  签到结果: {result.get('sign_result', '未知')}\n"
        content += f"  积分信息: {result.get('points_info', '未知')}\n"
        content += "\n"
    
    content += "=" * 30 + "\n"
    content += "✅ 任务执行完成!"
    return content

def main():
    """主程序"""
    # 记录开始时间
    start_time = datetime.now()
    
    print("=== 鸿星尔克签到脚本 ===")
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
        member_id = account.get('member_id')
        enterprise_id = account.get('enterprise_id')
        unionid = account.get('unionid')
        openid = account.get('openid')
        wx_openid = account.get('wx_openid')
        user_agent = account.get('user_agent')
        
        print(f"## 账户{i}")
        
        if not member_id or not enterprise_id or not unionid or not openid or not wx_openid:
            result = {
                'sign_result': '失败',
                'points_info': '配置错误'
            }
            all_results.append(result)
            print(f"- **签到结果**: 失败")
            print(f"- **积分信息**: 配置错误")
            continue
        
        # 创建API客户端
        client = ErkeClient(member_id, enterprise_id, unionid, openid, wx_openid, user_agent)
        
        # 获取积分信息
        points_success, points_msg = client.get_points_info()
        print(f"- **积分信息**: {points_msg}")
        
        # 执行签到
        sign_success, sign_msg = client.sign_in()
        print(f"- **签到结果**: {'成功' if sign_success else '失败'} - {sign_msg}")
        
        result = {
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'points_info': points_msg
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
        notification_title = f"鸿星尔克签到 - {end_time.strftime('%Y-%m-%d')}"
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