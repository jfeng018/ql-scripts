#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import time

# 青龙面板通知模块
def send_notification(title, content):
    """
    使用青龙面板内置通知机制
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

def safe_date(date_str):
    """日期安全处理函数"""
    if not date_str or date_str == "null" or date_str == "0000-00-00":
        return None
    return date_str

def calculate_days(start_date, end_date):
    """日期计算函数"""
    start_date = safe_date(start_date)
    end_date = safe_date(end_date)
    
    if not start_date or not end_date:
        return "N/A"
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days
    except Exception:
        return "N/A"

def countdown(target_date):
    """计算倒计时"""
    target_date = safe_date(target_date)
    if not target_date:
        return "N/A"
    
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.today()
        
        # 如果目标日期已过，则计算下一年的日期
        if today >= target:
            next_year = today.year + 1
            target = target.replace(year=next_year)
        
        return (target - today).days
    except Exception:
        return "N/A"

def calculate_child_age(child_birthday):
    """计算孩子年龄"""
    child_birthday = safe_date(child_birthday)
    if not child_birthday:
        return "N/A"
    
    try:
        birth = datetime.strptime(child_birthday, "%Y-%m-%d")
        today = datetime.today()
        
        if birth > today:
            return "N/A"
        
        seconds = (today - birth).total_seconds()
        years = int(seconds // 31536000)
        months = int((seconds % 31536000) // 2592000)
        days = int((seconds % 2592000) // 86400)
        
        return f"{years}岁{months}个月{days}天"
    except Exception:
        return "N/A"

def get_holiday_countdown(tianapi_key):
    """获取节假日倒计时"""
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        
        # 使用天行API获取节假日信息
        if tianapi_key:
            url = f"https://apis.tianapi.com/jiejiari/index?key={tianapi_key}&date={today}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    holiday_list = data.get("result", {}).get("list", [])
                    if holiday_list:
                        next_holiday = holiday_list[0]
                        name = next_holiday.get("name", "")
                        date = next_holiday.get("time", "")
                        
                        # 过滤非中国节日
                        if name and "国际" not in name and "世界" not in name:
                            holiday_date = datetime.strptime(date, "%Y-%m-%d")
                            today_date = datetime.strptime(today, "%Y-%m-%d")
                            days = (holiday_date - today_date).days
                            
                            return {
                                "name": name,
                                "date": date,
                                "days": days
                            }
    except Exception as e:
        print(f"获取节假日信息失败: {e}")
    
    # 备用方案：返回默认值
    return {
        "name": "近期没有节日",
        "date": "",
        "days": "N/A"
    }

def get_daily_quote():
    """获取每日一句"""
    try:
        response = requests.get("https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d", timeout=10)
        if response.status_code == 200:
            data = response.json()
            hitokoto = data.get("hitokoto", "")
            source = data.get("from", "")
            
            if hitokoto and hitokoto != "null":
                return {
                    "content": hitokoto,
                    "author": source if source and source != "null" else "未知"
                }
    except Exception as e:
        print(f"获取每日一句失败: {e}")
    
    return {
        "content": "生活就像海洋，只有意志坚强的人才能到达彼岸",
        "author": "马克思"
    }

def get_daily_poetry():
    """获取每日古诗词"""
    try:
        response = requests.get("https://v2.jinrishici.com/one.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                content = data.get("data", {}).get("content", "")
                origin = data.get("data", {}).get("origin", {})
                author = origin.get("author", "") if origin else ""
                title = origin.get("title", "") if origin else ""
                dynasty = origin.get("dynasty", "") if origin else ""
                
                if content and content != "null":
                    return {
                        "content": content,
                        "author": author if author and author != "null" else "未知",
                        "title": title if title and title != "null" else "无题",
                        "dynasty": dynasty if dynasty and dynasty != "null" else "未知"
                    }
    except Exception as e:
        print(f"获取古诗词失败: {e}")
    
    return {
        "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
        "author": "李白",
        "title": "静夜思",
        "dynasty": "唐"
    }

def get_cloud_comment(tianapi_key):
    """获取网易云热评"""
    try:
        if tianapi_key:
            url = f"https://apis.tianapi.com/hotreview/index?key={tianapi_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    result = data.get("result", {})
                    content = result.get("content", "")
                    song = result.get("song", "")
                    singer = result.get("singer", "")
                    
                    if content and song and content != "null" and song != "null":
                        return {
                            "content": content,
                            "song": song,
                            "singer": singer if singer and singer != "null" else ""
                        }
    except Exception as e:
        print(f"获取网易云热评失败: {e}")
    
    # 备用热评
    comments = [
        {"content": "十七岁吻的人额头没有粉底", "song": "十七岁"},
        {"content": "十年前你说生如夏花般绚烂，十年后你说平凡才是唯一的答案", "song": "生如夏花"},
        {"content": "后来我终于知道，它并不是我的花，我只是恰好途经了它的盛放", "song": "平凡之路"},
        {"content": "你那么孤独，却说一个人真好", "song": "If"},
        {"content": "小时候刮奖刮出‘谢’字还不扔，非要把‘谢谢惠顾’都刮得干干净净才舍得放手", "song": "情书"}
    ]
    
    import random
    return random.choice(comments)

def get_anniversaries():
    """计算纪念日信息"""
    # 从环境变量获取配置
    love_date = os.environ.get("FAMILY_LOVE_DATE", "2014-12-13")
    birthday_wife = os.environ.get("FAMILY_BIRTHDAY_WIFE", "1996-04-12")
    birthday_husband = os.environ.get("FAMILY_BIRTHDAY_HUSBAND", "1994-10-31")
    birthday_marry = os.environ.get("FAMILY_BIRTHDAY_MARRY", "2022-07-30")
    child_birthday = os.environ.get("FAMILY_CHILD_BIRTHDAY", "2024-02-28")
    
    today = datetime.today().strftime("%Y-%m-%d")
    year = datetime.today().year
    
    # 计算各项日期
    love_days = calculate_days(love_date, today)
    wife_days = countdown(f"{year}-{birthday_wife.split('-')[1]}-{birthday_wife.split('-')[2]}")
    husband_days = countdown(f"{year}-{birthday_husband.split('-')[1]}-{birthday_husband.split('-')[2]}")
    marry_days = countdown(f"{year}-{birthday_marry.split('-')[1]}-{birthday_marry.split('-')[2]}")
    child_days = countdown(f"{year}-{child_birthday.split('-')[1]}-{child_birthday.split('-')[2]}")
    child_age = calculate_child_age(child_birthday)
    
    return {
        "love_days": love_days,
        "wife_days": wife_days,
        "husband_days": husband_days,
        "marry_days": marry_days,
        "child_days": child_days,
        "child_age": child_age,
        "love_date": love_date,
        "birthday_wife": birthday_wife,
        "birthday_husband": birthday_husband,
        "birthday_marry": birthday_marry,
        "child_birthday": child_birthday
    }

def generate_message():
    """生成推送内容"""
    # 获取配置
    tianapi_key = os.environ.get("FAMILY_TIANAPI_KEY", "")
    
    # 获取各类信息
    anniversaries = get_anniversaries()
    quote = get_daily_quote()
    holiday = get_holiday_countdown(tianapi_key)
    poetry = get_daily_poetry()
    comment = get_cloud_comment(tianapi_key)
    
    today = datetime.today().strftime("%Y-%m-%d")
    
    # 构造消息内容
    message = f"📅 每日生活简报 ({today})\n\n"
    
    # 节日信息
    message += f"🎉 {holiday['name']}\n"
    if holiday['date']:
        message += f"📅 日期: {holiday['date']}\n"
    if holiday['days'] != "N/A":
        message += f"⏳ 倒计时: {holiday['days']}天\n"
    message += "\n"
    
    # 家庭纪念日
    message += "❤️ 家庭纪念日\n"
    message += "----------------\n"
    message += f"相恋天数: {anniversaries['love_days']}天\n"
    message += f"结婚纪念日倒计时: {anniversaries['marry_days']}天\n"
    message += f"老婆生日倒计时: {anniversaries['wife_days']}天\n"
    message += f"老公生日倒计时: {anniversaries['husband_days']}天\n"
    message += f"孩子年龄: {anniversaries['child_age']}\n"
    message += f"孩子生日倒计时: {anniversaries['child_days']}天\n"
    message += "\n"
    
    # 古诗词
    message += "🎋 每日古诗词\n"
    message += f"{poetry['content']}\n"
    message += f"—— {poetry['dynasty']}·{poetry['author']}《{poetry['title']}》\n"
    message += "\n"
    
    # 网易云热评
    message += "🎵 网易云热评\n"
    message += f"{comment['content']}\n"
    if comment.get('singer'):
        message += f"—— {comment['song']} · {comment['singer']}\n"
    else:
        message += f"—— {comment['song']}\n"
    message += "\n"
    
    # 每日一句
    message += "💬 每日一句:\n"
    message += f"{quote['content']}\n"
    message += f"—— {quote['author']}"
    
    return message

def main():
    """主函数"""
    print("=== 家庭纪念日提醒脚本 ===")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 生成消息内容
        message = generate_message()
        title = f"家庭温馨提醒 - {datetime.now().strftime('%Y-%m-%d')}"
        
        print("\n生成的推送内容:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        
        # 发送通知
        print("\n--- 通知发送 ---")
        if send_notification(title, message):
            print("🔔 通知已发送")
        else:
            print("📝 使用控制台输出")
            
    except Exception as e:
        print(f"❌ 脚本执行出错: {e}")
        send_notification("家庭纪念日脚本执行失败", f"错误信息: {e}")

if __name__ == "__main__":
    main()
