#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import time
import sys

def main():
    # 公司CSV文件目录
    company_dir = os.path.join('output', 'company')
    
    # 检查目录是否存在
    if not os.path.exists(company_dir):
        print(f"错误: 目录 '{company_dir}' 不存在")
        return
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(company_dir, '*.csv'))
    
    if not csv_files:
        print(f"未在 '{company_dir}' 目录中找到CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件需要处理")
    
    # 处理每个CSV文件
    for i, csv_file in enumerate(csv_files):
        csv_name = os.path.basename(csv_file)
        print(f"\n[{i+1}/{len(csv_files)}] 正在处理: {csv_name}")
        
        # 构建命令
        command = f'python extract_contact_info.py --csv "{csv_file}" --url-column Domain --headless --merge-results'
        print(f"执行命令: {command}")
        
        # 执行命令
        start_time = time.time()
        exit_code = os.system(command)
        end_time = time.time()
        
        # 检查命令执行结果
        if exit_code == 0:
            print(f"✓ 成功处理 {csv_name}, 耗时: {end_time - start_time:.2f}秒")
        else:
            print(f"✗ 处理 {csv_name} 失败，退出码: {exit_code}")
        
        # 在处理下一个文件前等待一会儿
        if i < len(csv_files) - 1:
            print("等待5秒后处理下一个文件...")
            time.sleep(5)
    
    print(f"\n完成处理所有 {len(csv_files)} 个CSV文件")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
        sys.exit(1)
    except Exception as e:
        print(f"出现错误: {e}")
        sys.exit(1) 