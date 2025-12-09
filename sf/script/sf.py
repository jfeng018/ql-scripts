#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime
import time
import hashlib
import execjs
import random
import logging
from typing import Dict, Any, List

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

class SFExpressClient:
    """顺丰速运API客户端"""
    
    def __init__(self, cookies, user_id, user_agent=None, channel=None, device_id=None):
        self.cookies = cookies
        self.user_id = user_id
        self.channel = channel or 'weixin'
        self.device_id = device_id or 'device_id'
        self.session = requests.Session()
        
        # JavaScript文件路径
        self.js_file_path = os.path.join(os.path.dirname(__file__), 'code.js')
        self.base_url = "https://mcs-mimp-web.sf-express.com"
        
        # 设置Cookies
        cookie_dict = {}
        for item in cookies.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        self.session.cookies.update(cookie_dict)
        
        # 设置User-Agent和其他请求头
        self.user_agent = user_agent or (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/18.5 Mobile/15E148 Safari/604.1'
        )
        
        self.default_headers = {
            "User-Agent": self.user_agent,
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "timestamp": "",
            "signature": "",
            "channel": self.channel,
            "syscode": "MCS-MIMP-CORE",
            "sw8": "",
            "platform": "SFAPP",
            "sec-gpc": "1",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://mcs-mimp-web.sf-express.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mcs-mimp-web.sf-express.com/superWelfare?citycode=&cityname=&tab=0",
            "cookie": self.cookies,
            "priority": "u=1, i"
        }
        
        # 初始化JavaScript环境
        self._init_js()
    
    def _init_js(self):
        """初始化JavaScript环境"""
        try:
            # 创建默认的JavaScript代码（如果没有code.js文件）
            default_js_code = '''
            window = global;
            navigator = {}
            navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            location = {
                "ancestorOrigins": {},
                "href": "https://y.qq.com/n/ryqq/toplist/4",
                "origin": "https://y.qq.com",
                "protocol": "https:",
                "host": "y.qq.com",
                "hostname": "y.qq.com",
                "port": "",
                "pathname": "/n/ryqq/toplist/4",
                "search": "",
                "hash": ""
            }
            proxy_array = ['window', 'document', 'location', 'navigator', 'history','screen' ]
            
            N = /[\uD800-\uDBFF][\uDC00-\uDFFFF]|[^\x00-\x7F]/g;
            const B = (t) => Buffer.from(t, "utf8").toString("base64");
            
            V = (t, e=!1) => e ? (t => t.replace(/=/g, "").replace(/[+\/]/g, (t => "+" == t ? "-" : "_")))(B(t)) : B(t);
            
            var M = {
                        randomUUID: "undefined" != typeof crypto && crypto.randomUUID && crypto.randomUUID.bind(crypto)
                    };
            
            function O(t, e, r) {
                        if (M.randomUUID && !e && !t)
                            return M.randomUUID();
                        const n = (t = t || {}).random || (t.rng || C)();
                        if (n[6] = 15 & n[6] | 64,
                        n[8] = 63 & n[8] | 128,
                        e) {
                            r = r || 0;
                            for (let t = 0; t < 16; ++t)
                                e[r + t] = n[t];
                            return e
                        }
                        return function(t, e=0) {
                            return (T[t[e + 0]] + T[t[e + 1]] + T[t[e + 2]] + T[t[e + 3]] + "-" + T[t[e + 4]] + T[t[e + 5]] + "-" + T[t[e + 6]] + T[t[e + 7]] + "-" + T[t[e + 8]] + T[t[e + 9]] + "-" + T[t[e + 10]] + T[t[e + 11]] + T[t[e + 12]] + T[t[e + 13]] + T[t[e + 14]] + T[t[e + 15]]).toLowerCase()
                        }(n)
                    }
            
            function ft(t, e) {
                var r = O()
                  , n = String(V(r))
                  , i = String(V(O()))
                  , o = String(V(t))
                  , a = String(V("web"))
                  , s = String(V((null === location || void 0 === location ? void 0 : location.pathname) || ""))
                  , c = String(V(e));
                return {
                    code: "".concat(1, "-").concat(n, "-").concat(i, "-").concat(0, "-").concat(o, "-").concat(a, "-").concat(s, "-").concat(c),
                    traceId: r
                }
            }
            var key = "fb40817085be4e398e0b6f4b08177746"
            function get_sw8(url_path) {
                return ft(key, url_path)
            }
            '''
            
            # 如果code.js文件不存在，则创建默认文件
            if not os.path.exists(self.js_file_path):
                with open(self.js_file_path, 'w', encoding='utf-8') as f:
                    f.write(default_js_code)
            
            with open(self.js_file_path, 'r', encoding='utf-8') as f:
                js_code = f.read()
            self.js_context = execjs.compile(js_code)
        except Exception as e:
            logger.error(f"初始化JavaScript环境失败: {e}")
            self.js_context = None
    
    def get_sw8(self, url_path):
        """调用JavaScript中的get_sw8函数"""
        if self.js_context is None:
            raise RuntimeError("JavaScript context not initialized")
        
        try:
            result = self.js_context.call('get_sw8', url_path)
            return result
        except Exception as e:
            logger.error(f"调用get_sw8函数时出错: {e}")
            return None
    
    def generate_signature(self, timestamp: str, sys_code: str = None) -> str:
        """生成签名"""
        sign_str = f"wwesldfs29aniversaryvdld29&timestamp={timestamp}&sysCode={sys_code}"
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def automatic_sign_fetch_package(self, come_from: str = "vioin", channel_from: str = "SFAPP") -> Dict[str, Any]:
        """
        自动签到获取礼包接口
        """
        url_path = "/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage"
        url = f"{self.base_url}{url_path}"
        
        timestamp = str(int(time.time() * 1000))
        
        data = {
            "comeFrom": come_from,
            "channelFrom": channel_from
        }
        
        headers = self.default_headers.copy()
        sys_code = 'MCS-MIMP-CORE'
        headers.update({
            'timestamp': timestamp,
            'signature': self.generate_signature(timestamp, sys_code),
            'sw8': self.get_sw8(url_path).get('code') if self.get_sw8(url_path) else '',
            'deviceid': self.device_id,
            'accept-language': 'zh-CN,zh-Hans;q=0.9',
            'priority': 'u=3, i',
            'referer': f'https://mcs-mimp-web.sf-express.com/superWelfare?mobile=176****2621&userId={self.user_id}&path=/superWelfare&supportShare=YES&from=appIndex&tab=1'
        })
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "自动签到获取礼包请求失败"
            }
    
    def sign_in(self):
        """执行签到"""
        try:
            result = self.automatic_sign_fetch_package()
            
            if result.get("success"):
                obj = result.get("obj", {})
                has_finish_sign = obj.get("hasFinishSign", 0)
                count_day = obj.get("countDay", 0)
                package_list = obj.get("integralTaskSignPackageVOList", [])
                
                if has_finish_sign == 1:
                    msg = f"今日已完成签到，连续签到 {count_day} 天"
                else:
                    msg = f"签到成功！连续签到 {count_day} 天"
                
                # 记录获得的礼包
                if package_list:
                    msg += "，获得签到礼包: "
                    for package in package_list:
                        package_name = package.get("commodityName", "未知礼包")
                        invalid_date = package.get("invalidDate", "")
                        msg += f"[{package_name} (有效期至: {invalid_date})] "
                else:
                    msg += "，未获得签到礼包"
                
                return True, msg
            else:
                error_msg = result.get("errorMessage", "未知错误")
                return False, f"签到失败: {error_msg}"
                
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
    
    def query_point_task_and_sign(self, channel_type: str = "1", device_id: str = None) -> Dict[str, Any]:
        """
        查询积分任务和签到信息
        """
        url_path = "/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES"
        url = f"{self.base_url}{url_path}"
        
        timestamp = str(int(time.time() * 1000))
        
        data = {
            "channelType": channel_type,
            "deviceId": device_id or self.device_id
        }
        
        headers = self.default_headers.copy()
        sys_code = 'MCS-MIMP-CORE'
        headers.update({
            'timestamp': timestamp,
            'signature': self.generate_signature(timestamp, sys_code),
            'sw8': self.get_sw8(url_path).get('code') if self.get_sw8(url_path) else ''
        })
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "请求失败"
            }
    
    def finish_task(self, task_code: str) -> Dict[str, Any]:
        """
        完成任务接口
        """
        url_path = "/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask"
        url = f"{self.base_url}{url_path}"
        
        timestamp = str(int(time.time() * 1000))
        
        data = {
            "taskCode": task_code
        }
        
        headers = self.default_headers.copy()
        sys_code = 'MCS-MIMP-CORE'
        headers.update({
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'timestamp': timestamp,
            'signature': self.generate_signature(timestamp, sys_code),
            'sw8': self.get_sw8(url_path).get('code') if self.get_sw8(url_path) else '',
            'referer': 'https://mcs-mimp-web.sf-express.com/home?from=qqjrwzx515&WC_AC_ID=111&WC_REPORT=111'
        })
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "完成任务请求失败"
            }
    
    def fetch_tasks_reward(self, channel_type: str = "1", device_id: str = None) -> Dict[str, Any]:
        """
        获取任务奖励接口
        """
        url_path = "/mcs-mimp/commonNoLoginPost/~memberNonactivity~integralTaskStrategyService~fetchTasksReward"
        url = f"{self.base_url}{url_path}"
        
        timestamp = str(int(time.time() * 1000))
        
        data = {
            "channelType": channel_type,
            "deviceId": device_id or self.device_id
        }
        
        headers = self.default_headers.copy()
        sys_code = 'MCS-MIMP-CORE'
        headers.update({
            'User-Agent': self.user_agent,
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'timestamp': timestamp,
            'signature': self.generate_signature(timestamp, sys_code),
            'sw8': self.get_sw8(url_path).get('code') if self.get_sw8(url_path) else '',
            'referer': 'https://mcs-mimp-web.sf-express.com/superWelfare?citycode=&cityname=&tab=0',
        })
        
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": "获取任务奖励请求失败"
            }
    
    def get_task_list(self):
        """获取任务列表"""
        try:
            result = self.query_point_task_and_sign()
            task_list = result.get("obj", {}).get("taskTitleLevels", [])
            logger.info(f"获取到 {len(task_list)} 个任务")
            return True, task_list
        except Exception as e:
            print(f"获取任务列表失败: {e}")
            return False, []
    
    def process_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个任务
        """
        task_title = task.get('title', '未知任务')
        task_status = task.get("status")
        task_code = task.get('taskCode')
        
        if not task_code:
            logger.warning(f"任务 {task_title} 缺少任务代码，跳过")
            return {'title': task_title, 'success': False, 'points': 0}
        
        try:
            finish_result = self.finish_task(task_code)
            if finish_result and finish_result.get('success'):
                logger.info(f"任务 {task_title} 完成成功")
                
                # 获取任务奖励
                reward_result = self.fetch_tasks_reward()
                logger.info(f"任务奖励获取结果: {reward_result}")
                
                # 提取获得的积分
                points = 0
                if reward_result and reward_result.get('success'):
                    obj_list = reward_result.get('obj', [])
                    if isinstance(obj_list, list):
                        for item in obj_list:
                            points += item.get('point', 0)
                
                return {'title': task_title, 'success': True, 'points': points}
            else:
                logger.warning(f"任务 {task_title} 完成失败或无返回结果")
                return {'title': task_title, 'success': False, 'points': 0}
        except Exception as e:
            logger.error(f"执行任务 {task_title} 时发生错误: {e}")
            return {'title': task_title, 'success': False, 'points': 0}

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
        
        # 获取任务列表并执行任务
        task_success, task_list = client.get_task_list()
        task_msg = f"获取到{len(task_list)}个任务" if task_success else "获取任务列表失败"
        print(f"- **任务信息**: {task_msg}")
        
        # 处理任务
        completed_tasks = 0
        total_points = 0
        if task_success and task_list:
            for i, task in enumerate(task_list, 1):
                logger.info(f"开始处理第 {i}/{len(task_list)} 个任务")
                
                if task.get("taskPeriod") != "D":
                    logger.info(f"任务 {task.get('title', '未知任务')} 非日常任务，跳过")
                    continue
                
                # 如果任务已完成，跳过
                if task.get("status") == 3:
                    logger.info(f"任务 {task.get('title', '未知任务')} 已完成，跳过")
                    continue
                
                # 添加延时
                time.sleep(random.uniform(10, 15))
                
                task_result = client.process_single_task(task)
                if task_result.get('success'):
                    completed_tasks += 1
                    total_points += task_result.get('points', 0)
        
        task_result_msg = f"完成{completed_tasks}个任务，获得{total_points}积分"
        print(f"- **任务完成**: {task_result_msg}")
        
        result = {
            'user_id': user_id,
            'sign_result': f"{'成功' if sign_success else '失败'} - {sign_msg}",
            'points_info': points_msg,
            'task_result': task_result_msg
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