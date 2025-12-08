#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime

def diagnose_ql_environment():
    print("=== 青龙面板环境诊断 ===")
    print("诊断时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 1. 检查青龙面板标识
    print("\n[1] 青龙面板环境检查:")
    ql_indicators = [
        '/ql/',
        '/ql/scripts',
        '/ql/data',
        'qinglong'
    ]
    
    is_ql_env = False
    for indicator in ql_indicators:
        if indicator in os.getcwd() or indicator in sys.executable:
            is_ql_env = True
            print(f"✓ 检测到青龙面板标识: {indicator}")
    
    if not is_ql_env:
        print("⚠ 未明确检测到青龙面板环境")
    
    # 2. 检查目录结构
    print("\n[2] 目录结构检查:")
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 检查上级目录
    parent_dirs = []
    temp_dir = current_dir
    for i in range(5):  # 检查最多5层上级目录
        temp_dir = os.path.dirname(temp_dir)
        if temp_dir:
            parent_dirs.append(temp_dir)
            if any(ql_indicator in temp_dir for ql_indicator in ['/ql', 'qinglong']):
                print(f"✓ 在上级目录发现青龙面板标识: {temp_dir}")
    
    # 3. 检查常见青龙面板文件
    print("\n[3] 青龙面板文件检查:")
    common_ql_files = [
        '/ql/data/config/auth.json',
        '/ql/data/config/env.sh',
        '/ql/scripts/docker_entrypoint.sh',
        'package.json'  # 青龙面板根目录通常有package.json
    ]
    
    for file_path in common_ql_files:
        if os.path.exists(file_path):
            print(f"✓ 找到青龙面板文件: {file_path}")
        else:
            # 检查相对路径
            if os.path.exists(os.path.join(current_dir, file_path)):
                print(f"✓ 找到青龙面板文件: {file_path}")
    
    # 4. 检查环境变量
    print("\n[4] 青龙面板环境变量检查:")
    ql_env_vars = [
        'QL_DIR',
        'QL_BRANCH',
        'QL_REPO',
        'CONTAINER_APPPATH'
    ]
    
    for env_var in ql_env_vars:
        value = os.environ.get(env_var)
        if value:
            print(f"✓ 环境变量 {env_var}: {value}")
    
    # 5. 检查Python路径中的青龙面板特征
    print("\n[5] Python路径检查:")
    for i, path in enumerate(sys.path[:10]):  # 只检查前10个路径
        if any(ql_indicator in path for ql_indicator in ['/ql', 'qinglong']):
            print(f"✓ Python路径中的青龙面板特征: {path}")
    
    # 6. 检查可能的通知模块
    print("\n[6] 通知模块检查:")
    notification_modules = [
        'sendNotify',
        'notify',
        'ql',
        'notification'
    ]
    
    for module in notification_modules:
        try:
            __import__(module)
            print(f"✓ 找到通知模块: {module}")
        except ImportError:
            print(f"✗ 未找到模块: {module}")
    
    # 7. 检查配置文件
    print("\n[7] 配置文件检查:")
    config_patterns = [
        '*config*',
        '*env*',
        '*.json',
        '*.sh'
    ]
    
    try:
        import glob
        current_files = os.listdir('.')
        config_files = [f for f in current_files if any(pattern.replace('*', '') in f.lower() for pattern in config_patterns)]
        if config_files:
            print("当前目录配置文件:", config_files[:5])  # 只显示前5个
    except Exception as e:
        print(f"检查配置文件时出错: {e}")
    
    print("\n=== 诊断结束 ===")

if __name__ == "__main__":
    diagnose_ql_environment()
