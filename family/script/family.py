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

def get_anniversaries():
    """计算纪念日信息"""
    # 从环境变量获取配置（新方案：使用单个变量包含所有日期）
    family_dates = os.environ.get("FAMILY_DATES", "")
    
    # 默认值（使用假数据）
    default_dates = "2020-01-01|1990-05-15|1988-12-03|2021-10-01|2023-03-20"
    
    # 如果没有配置，则使用默认值
    if not family_dates:
        family_dates = default_dates
    
    # 解析日期
    dates = family_dates.split("|")
    if len(dates) != 5:
        # 如果格式不正确，使用默认值
        dates = default_dates.split("|")
    
    love_date = dates[0]  # 恋爱日期
    birthday_wife = dates[1]  # 妻子生日
    birthday_husband = dates[2]  # 丈夫生日
    birthday_marry = dates[3]  # 结婚纪念日
    child_birthday = dates[4]  # 孩子生日
    
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
    # 获取各类信息
    anniversaries = get_anniversaries()
    
    today = datetime.today().strftime("%Y-%m-%d")
    
    # 构造消息内容
    message = f"📅 家庭温馨提醒 ({today})\n\n"
    
    # 家庭纪念日
    message += "❤️ 家庭纪念日\n"
    message += "----------------\n"
    message += f"相恋天数: {anniversaries['love_days']}天\n"
    message += f"结婚纪念日倒计时: {anniversaries['marry_days']}天\n"
    message += f"老婆生日倒计时: {anniversaries['wife_days']}天\n"
    message += f"老公生日倒计时: {anniversaries['husband_days']}天\n"
    message += f"孩子年龄: {anniversaries['child_age']}\n"
    message += f"孩子生日倒计时: {anniversaries['child_days']}天\n"
    
    return message

def main():
    """主函数"""
    print("=== 家庭纪念日提醒脚本（合并变量版） ===")
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
