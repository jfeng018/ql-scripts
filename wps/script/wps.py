#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import base64
import random
import string
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

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

class WPSEncryption:
    """WPS加密工具类"""

    @staticmethod
    def generate_aes_key(length: int = 32) -> str:
        """
        生成AES密钥: 随机字符 + 时间戳

        Args:
            length (int): 密钥长度，默认32位

        Returns:
            str: 生成的AES密钥
        """
        chars = string.ascii_lowercase + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(length - 10))
        timestamp_part = str(int(time.time()))
        return random_part + timestamp_part

    @staticmethod
    def aes_encrypt(plain_text: str, aes_key: str) -> str:
        """
        AES-CBC加密

        Args:
            plain_text (str): 明文文本
            aes_key (str): AES密钥

        Returns:
            str: Base64编码的加密数据
        """
        # 使用AES密钥的前16位作为IV
        iv = aes_key[:16].encode('utf-8')
        key = aes_key.encode('utf-8')

        # 创建AES加密器
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # PKCS7填充
        padded_data = pad(plain_text.encode('utf-8'), AES.block_size)

        # 加密
        encrypted_data = cipher.encrypt(padded_data)

        # 返回Base64编码的结果
        return base64.b64encode(encrypted_data).decode('utf-8')

    @staticmethod
    def rsa_encrypt(plain_text: str, public_key_pem: str) -> str:
        """
        RSA加密

        Args:
            plain_text (str): 明文文本
            public_key_pem (str): PEM格式的RSA公钥

        Returns:
            str: Base64编码的加密数据
        """
        # 加载公钥
        public_key = RSA.import_key(public_key_pem)

        # 创建RSA加密器
        cipher = PKCS1_v1_5.new(public_key)

        # 加密
        encrypted_data = cipher.encrypt(plain_text.encode('utf-8'))

        # 返回Base64编码的结果
        return base64.b64encode(encrypted_data).decode('utf-8')

class WPSApiClient:
    """WPS API客户端"""
    
    def __init__(self, cookies, user_agent=None):
        self.cookies = {'wps_sid': cookies}
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        
        # 设置User-Agent
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # 基础请求头
        self.base_headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://vip.wps.cn/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json'
        }
        
        # API端点
        self.encrypt_key_url = 'https://vip.wps.cn/sign/v1/rpc/getEncryptKey'
        self.sign_in_url = 'https://vip.wps.cn/sign/v1/signin'
        self.user_info_url = 'https://vip.wps.cn/userinfo'
        self.sign_info_url = 'https://vip.wps.cn/sign/v1/get'
        
        # 加密工具
        self.encryption = WPSEncryption()
    
    def get_encrypt_key(self):
        """
        获取RSA公钥

        Returns:
            Dict: 结果字典
                {
                    'success': bool,      # 是否成功
                    'public_key': str,    # Base64编码的公钥
                    'error': str          # 错误信息
                }
        """
        try:
            headers = self.base_headers.copy()
            response = self.session.get(self.encrypt_key_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'ok':
                    public_key = data.get('data', {}).get('public_key')
                    if public_key:
                        return {
                            'success': True,
                            'public_key': public_key
                        }
                    else:
                        return {
                            'success': False,
                            'error': '公钥为空'
                        }
                else:
                    return {
                        'success': False,
                        'error': data.get('msg', '获取公钥失败')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_crypto_data(self, public_key_base64, user_id, platform=2):
        """
        生成加密数据和token

        Args:
            public_key_base64 (str): Base64编码的RSA公钥
            user_id (str): 用户ID
            platform (int): 平台标识，默认2

        Returns:
            Dict: 包含加密数据的字典
        """
        # 解码公钥
        public_key_pem = base64.b64decode(public_key_base64).decode('utf-8')

        # 生成AES密钥
        aes_key = self.encryption.generate_aes_key(32)

        # 准备明文数据
        plain_data = json.dumps({
            "user_id": user_id,
            "platform": platform
        }, separators=(',', ':'))

        # AES加密数据 (这是extra)
        encrypt_data = self.encryption.aes_encrypt(plain_data, aes_key)

        # RSA加密AES密钥 (这是请求头中的token)
        token = self.encryption.rsa_encrypt(aes_key, public_key_pem)

        return {
            "extra": encrypt_data,
            "token": token,
            "aesKey": aes_key
        }
    
    def get_user_info(self):
        """获取用户信息"""
        try:
            headers = self.base_headers.copy()
            response = self.session.get(self.user_info_url, headers=headers, timeout=10)
            return response.json()
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def sign_in(self, user_id):
        """执行签到"""
        try:
            # 1. 获取RSA公钥
            key_result = self.get_encrypt_key()
            if not key_result['success']:
                return {'result': 'error', 'msg': f"获取公钥失败: {key_result['error']}"}

            public_key_base64 = key_result['public_key']

            # 2. 生成加密数据和token
            crypto_result = self.generate_crypto_data(public_key_base64, user_id)

            # 3. 构造请求头 (使用生成的token)
            headers = self.base_headers.copy()
            headers['token'] = crypto_result['token']

            # 4. 构造请求数据
            data = {
                "encrypt": True,
                "extra": crypto_result['extra'],
                "pay_origin": "pc_ucs_rwzx_sign"
            }

            # 5. 发送签到请求
            response = self.session.post(self.sign_in_url, headers=headers, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"签到失败: {e}")
            return {'result': 'error', 'msg': str(e)}
    
    def get_sign_info(self):
        """获取签到信息"""
        try:
            headers = self.base_headers.copy()
            params = {'platform': '2'}
            response = self.session.get(self.sign_info_url, headers=headers, params=params, timeout=10)
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
        client = WPSApiClient(cookies, user_agent)
        
        # 获取用户信息
        user_info_data = client.get_user_info()
        if user_info_data and user_info_data.get('result') == 'ok':
            user_name = user_info_data.get('data', {}).get('nickname', '未知用户')
            user_info = f"{user_name}"
        else:
            user_info = "获取失败"
        
        print(f"- **用户信息**: {user_info}")
        
        # 执行签到
        sign_result = client.sign_in(user_id)
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