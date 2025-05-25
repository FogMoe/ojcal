#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
100% Orange Juice (100oj) 游戏中的 DEF/EVD 胜率计算器
当被攻击时，计算选择 DEF 或 EVD 的存活概率
"""

import random
import sys
import argparse
from typing import Tuple, List
from itertools import product


def calculate_def_damage(attack_power: int, def_value: int, dice_rolls: List[int]) -> int:
    """
    计算使用DEF时受到的伤害
    
    Args:
        attack_power: 对手的攻击点数
        def_value: 角色的DEF点数
        dice_rolls: 骰子点数列表
    
    Returns:
        受到的伤害值 (最低为1)
    """
    total_dice = sum(dice_rolls)
    damage = attack_power - def_value - total_dice
    return max(1, damage)


def calculate_evd_damage(attack_power: int, evd_value: int, dice_rolls: List[int]) -> int:
    """
    计算使用EVD时受到的伤害
    
    Args:
        attack_power: 对手的攻击点数
        evd_value: 角色的EVD点数
        dice_rolls: 骰子点数列表
    
    Returns:
        受到的伤害值 (成功闪避则为0，否则为完整攻击力)
    """
    total_dice = sum(dice_rolls)
    if evd_value + total_dice > attack_power:
        return 0  # 成功闪避
    else:
        return attack_power  # 受到完整伤害


def generate_dice_combinations(dice_config: List[int]) -> List[Tuple[int, ...]]:
    """
    生成所有可能的骰子组合
    
    Args:
        dice_config: 骰子配置，例如 [6, 6] 表示两个6面骰子
    
    Returns:
        所有可能的骰子点数组合
    """
    dice_ranges = [range(1, faces + 1) for faces in dice_config]
    return list(product(*dice_ranges))


def calculate_survival_probability(current_hp: int, attack_power: int, 
                                 def_value: int, evd_value: int, 
                                 use_def: bool, dice_config: List[int] = [6]) -> float:
    """
    计算选择DEF或EVD的存活概率
    
    Args:
        current_hp: 当前HP
        attack_power: 对手攻击点数
        def_value: 角色DEF点数
        evd_value: 角色EVD点数
        use_def: True表示使用DEF，False表示使用EVD
        dice_config: 骰子配置，默认为[6]表示一个6面骰子
    
    Returns:
        存活概率 (0.0 到 1.0)
    """
    survival_count = 0
    dice_combinations = generate_dice_combinations(dice_config)
    total_outcomes = len(dice_combinations)
    
    for dice_combo in dice_combinations:
        dice_rolls = list(dice_combo)
        if use_def:
            damage = calculate_def_damage(attack_power, def_value, dice_rolls)
        else:
            damage = calculate_evd_damage(attack_power, evd_value, dice_rolls)
        
        if current_hp > damage:
            survival_count += 1
    
    return survival_count / total_outcomes


def analyze_best_choice(current_hp: int, attack_power: int, 
                       def_value: int, evd_value: int, 
                       dice_config: List[int] = [6]) -> Tuple[str, float, float]:
    """
    分析应该选择DEF还是EVD
    
    Args:
        current_hp: 当前HP
        attack_power: 对手攻击点数
        def_value: 角色DEF点数
        evd_value: 角色EVD点数
        dice_config: 骰子配置，默认为[6]表示一个6面骰子
    
    Returns:
        (推荐选择, DEF胜率, EVD胜率)
    """
    def_probability = calculate_survival_probability(
        current_hp, attack_power, def_value, evd_value, use_def=True, dice_config=dice_config)
    evd_probability = calculate_survival_probability(
        current_hp, attack_power, def_value, evd_value, use_def=False, dice_config=dice_config)
    
    if def_probability > evd_probability:
        recommendation = "DEF"
    elif evd_probability > def_probability:
        recommendation = "EVD"
    else:
        recommendation = "DEF/EVD (相同胜率)"
    
    return recommendation, def_probability, evd_probability


def show_detailed_analysis(current_hp: int, attack_power: int, 
                          def_value: int, evd_value: int, dice_config: List[int] = [6]):
    """
    显示详细的伤害分析
    """
    print(f"\n=== 详细分析 ===")
    print(f"当前HP: {current_hp}, 对手攻击: {attack_power}, DEF: {def_value}, EVD: {evd_value}")
    print(f"骰子配置: {dice_config}")
    
    dice_combinations = generate_dice_combinations(dice_config)
    
    print(f"\nDEF选择 - 各骰子组合的伤害:")
    for dice_combo in dice_combinations:
        dice_rolls = list(dice_combo)
        damage = calculate_def_damage(attack_power, def_value, dice_rolls)
        survive = "存活" if current_hp > damage else "死亡"
        dice_str = "+".join(map(str, dice_rolls)) if len(dice_rolls) > 1 else str(dice_rolls[0])
        print(f"  骰子{dice_str}: 伤害{damage} -> {survive}")
    
    print(f"\nEVD选择 - 各骰子组合的伤害:")
    for dice_combo in dice_combinations:
        dice_rolls = list(dice_combo)
        damage = calculate_evd_damage(attack_power, evd_value, dice_rolls)
        if damage == 0:
            result = "闪避成功"
        else:
            result = f"伤害{damage} -> {'存活' if current_hp > damage else '死亡'}"
        evd_total = evd_value + sum(dice_rolls)
        dice_str = "+".join(map(str, dice_rolls)) if len(dice_rolls) > 1 else str(dice_rolls[0])
        print(f"  骰子{dice_str} (EVD+骰子={evd_total}): {result}")


def parse_dice_config(dice_str: str) -> List[int]:
    """
    解析骰子配置字符串
    
    Args:
        dice_str: 骰子配置字符串，例如 "6" 或 "6,6" 或 "4,6,8"
    
    Returns:
        骰子配置列表
    """
    if not dice_str.strip():
        return [6]  # 默认一个6面骰子
    
    try:
        dice_config = [int(x.strip()) for x in dice_str.split(',')]
        # 验证骰子面数
        for faces in dice_config:
            if faces < 1:
                raise ValueError("骰子面数必须大于0")
        return dice_config
    except ValueError as e:
        print(f"错误: 无效的骰子配置 '{dice_str}' - {e}")
        return [6]


def parse_quick_input(args_str: str) -> Tuple[int, int, int, int, List[int]]:
    """
    解析快捷输入字符串
    
    Args:
        args_str: 快捷输入字符串，格式: "hp,attack,def,evd[,dice]" 或 "hp attack def evd [dice]"
        例如: "3,5,2,1" 或 "3 5 2 1" 或 "3,5,2,1,6,6" 或 "3 5 2 1 6 6"
    
    Returns:
        (current_hp, attack_power, def_value, evd_value, dice_config)
    """
    # 支持逗号或空格分割参数
    if ',' in args_str:
        parts = [x.strip() for x in args_str.split(',')]
    else:
        parts = [x.strip() for x in args_str.split() if x.strip()]
    
    if len(parts) < 4:
        raise ValueError("需要至少4个参数: HP,攻击,DEF,EVD")
    
    current_hp = int(parts[0])
    attack_power = int(parts[1])
    def_value = int(parts[2])
    evd_value = int(parts[3])
    
    # 解析骰子配置
    if len(parts) > 4:
        dice_config = [int(x) for x in parts[4:]]
    else:
        dice_config = [6]  # 默认一个6面骰子
    
    return current_hp, attack_power, def_value, evd_value, dice_config


def main():
    """
    主程序
    """
    # 处理命令行参数
    parser = argparse.ArgumentParser(description='100oj DEF/EVD 胜率计算器')
    parser.add_argument('-q', '--quick', type=str, 
                       help='快捷输入: hp,attack,def,evd[,dice1,dice2,...] 例如: "3,5,2,1" 或 "3,5,2,1,6,6"')
    args = parser.parse_args()
      # 如果有快捷输入参数，直接计算并退出
    if args.quick:
        try:
            current_hp, attack_power, def_value, evd_value, dice_config = parse_quick_input(args.quick)
            recommendation, def_prob, evd_prob = analyze_best_choice(
                current_hp, attack_power, def_value, evd_value, dice_config)
            
            print(f"输入: HP={current_hp}, 攻击={attack_power}, DEF={def_value}, EVD={evd_value}, 骰子={dice_config}")
            print(f"DEF胜率: {def_prob:.1%} | EVD胜率: {evd_prob:.1%} | 推荐: {recommendation}")
            
            if def_prob != evd_prob:
                advantage = abs(def_prob - evd_prob)
                print(f"胜率优势: {advantage:.1%}")
            return
        except Exception as e:
            print(f"快捷输入错误: {e}")
            return
    print("=" * 50)
    print("100% Orange Juice DEF/EVD 胜率计算器")
    print("=" * 50)
    print("GitHub项目地址: https://github.com/FogMoe/ojcal")
    print("=" * 50)
    print("提示: 骰子配置格式例如 '6' (一个6面骰) 或 '6,6' (两个6面骰) 或 '4,6' (一个4面骰+一个6面骰)")
    print("快捷模式: python main.py -q \"hp,攻击,def,evd[,骰子1,骰子2...]\" 或 \"hp 攻击 def evd [骰子1 骰子2]\"")
    print("输入 'exit' 可退出程序")
    
    # 开始时选择输入模式和是否显示详细分析
    print("\n=== 初始设置 ===")
    print("1. 逐项输入 (详细)")
    print("2. 一行输入 (快速): hp,攻击,def,evd[,骰子配置] 或 hp 攻击 def evd [骰子配置]")
    input_mode = input("选择输入模式 (1/2): ").strip()
    use_quick_input = (input_mode == "2")
    
    show_detail_input = input("是否总是显示详细分析？(y/n): ").lower().strip()
    always_show_detail = show_detail_input in ['y', 'yes', '是']
    
    while True:
        try:
            print(f"\n{'='*20} 新的计算 {'='*20}")
            
            if use_quick_input:
                # 快速输入模式
                quick_input = input("输入 hp,攻击,def,evd[,骰子配置] (逗号或空格分割，输入exit退出): ").strip()
                if quick_input.lower() == 'exit':
                    break
                if not quick_input:
                    continue
                current_hp, attack_power, def_value, evd_value, dice_config = parse_quick_input(quick_input)
            else:
                # 详细输入模式
                print("请输入以下数值:")
                hp_input = input("当前HP (输入exit退出): ").strip()
                if hp_input.lower() == 'exit':
                    break
                current_hp = int(hp_input)
                
                attack_input = input("对手攻击点数: ").strip()
                if attack_input.lower() == 'exit':
                    break
                attack_power = int(attack_input)
                
                def_input = input("角色DEF点数: ").strip()
                if def_input.lower() == 'exit':
                    break
                def_value = int(def_input)
                
                evd_input = input("角色EVD点数: ").strip()
                if evd_input.lower() == 'exit':
                    break
                evd_value = int(evd_input)
                
                dice_input = input("骰子配置 (例如 '6' 或 '6,6', 留空默认6): ").strip()
                if dice_input.lower() == 'exit':
                    break
                dice_config = parse_dice_config(dice_input)
            
            if current_hp <= 0:
                print("错误: HP必须大于0")
                continue
            if attack_power <= 0:
                print("错误: 攻击点数必须大于0")
                continue
            
            # 计算最佳选择
            recommendation, def_prob, evd_prob = analyze_best_choice(
                current_hp, attack_power, def_value, evd_value, dice_config)
            
            # 显示结果
            print(f"\n=== 计算结果 ===")
            total_outcomes = len(generate_dice_combinations(dice_config))
            print(f"DEF胜率: {def_prob:.1%} ({def_prob*total_outcomes:.0f}/{total_outcomes})")
            print(f"EVD胜率: {evd_prob:.1%} ({evd_prob*total_outcomes:.0f}/{total_outcomes})")
            print(f"推荐选择: {recommendation}")
            
            if def_prob != evd_prob:
                advantage = abs(def_prob - evd_prob)
                print(f"胜率优势: {advantage:.1%}")
            
            # 根据初始设置决定是否显示详细分析
            if always_show_detail:
                show_detailed_analysis(current_hp, attack_power, def_value, evd_value, dice_config)
                
        except ValueError as e:
            print(f"错误: {e}")
        except KeyboardInterrupt:
            print("\n\n程序已退出")
            break
    
    print("感谢使用100oj胜率计算器！")


if __name__ == "__main__":
    main()