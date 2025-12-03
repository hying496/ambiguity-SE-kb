"""
指标赋值工具 - 简化版
根据数据或标准快速赋值
"""
import json
import argparse
from typing import Dict, Any, Optional

class MetricsAssigner:
    """指标赋值器"""
    
    @staticmethod
    def assign_confidence_weight(
        source_type: str,
        correct_count: Optional[int] = None,
        total_count: Optional[int] = None
    ) -> float:
        """
        赋值confidence_weight
        
        Args:
            source_type: 来源类型 (classic_theory/expert_consensus/empirical/experimental)
            correct_count: 正确应用次数（如果有验证数据）
            total_count: 总应用次数（如果有验证数据）
        """
        # 有验证数据时，使用实际正确率
        if correct_count is not None and total_count is not None and total_count > 0:
            accuracy = correct_count / total_count
            return round(accuracy, 2)
        
        # 无验证数据时，基于来源类型
        source_ranges = {
            "classic_theory": (0.85, 0.95),      # 经典理论/原则
            "expert_consensus": (0.75, 0.85),    # 专家共识
            "empirical": (0.65, 0.75),           # 经验总结
            "experimental": (0.50, 0.65)          # 实验性/假设
        }
        
        if source_type in source_ranges:
            min_val, max_val = source_ranges[source_type]
            # 返回中值
            return round((min_val + max_val) / 2, 2)
        
        # 默认值
        return 0.70
    
    @staticmethod
    def assign_usage_frequency(
        priority: int,
        scenario_count: int,
        usage_count: Optional[int] = None,
        total_usage: Optional[int] = None
    ) -> float:
        """
        赋值usage_frequency
        
        Args:
            priority: 优先级（1最高）
            scenario_count: 适用场景数量
            usage_count: 使用次数（如果有统计）
            total_usage: 同类知识总使用次数（如果有统计）
        """
        # 有使用统计时，使用实际频率
        if usage_count is not None and total_usage is not None and total_usage > 0:
            frequency = usage_count / total_usage
            return round(frequency, 2)
        
        # 无统计时，基于优先级和场景数量
        if priority == 1:  # 高优先级
            if scenario_count >= 3:
                return 0.85
            else:
                return 0.75
        elif priority == 2:  # 中优先级
            if scenario_count >= 3:
                return 0.65
            else:
                return 0.55
        else:  # 低优先级
            return 0.40
    
    @staticmethod
    def assign_term_frequency(
        term_freq_level: str,
        occurrence_count: Optional[int] = None,
        total_words: Optional[int] = None
    ) -> float:
        """
        赋值frequency（术语频率）
        
        Args:
            term_freq_level: 频率级别 (very_high/high/medium/low)
            occurrence_count: 出现次数（如果有语料库统计）
            total_words: 总词数（如果有语料库统计）
        """
        # 有语料库统计时，使用实际频率
        if occurrence_count is not None and total_words is not None and total_words > 0:
            # 归一化到0-1范围（假设每1000词出现1次为0.5）
            freq_per_1k = (occurrence_count / total_words) * 1000
            # 简单归一化：每1000词出现10次为1.0
            normalized = min(freq_per_1k / 10, 1.0)
            return round(normalized, 2)
        
        # 无统计时，基于经验判断
        level_ranges = {
            "very_high": 0.95,  # 极高频
            "high": 0.80,       # 高频
            "medium": 0.60,     # 中频
            "low": 0.40         # 低频
        }
        
        return level_ranges.get(term_freq_level, 0.60)

def interactive_assign():
    """交互式赋值工具"""
    assigner = MetricsAssigner()
    
    print("=" * 60)
    print("指标赋值工具（简化版）")
    print("=" * 60)
    print()
    
    print("请选择要赋值的指标:")
    print("1. confidence_weight（置信度权重）")
    print("2. usage_frequency（使用频率）")
    print("3. frequency（术语频率）")
    
    choice = input("\n请输入选项 (1-3): ").strip()
    
    if choice == "1":
        print("\n赋值confidence_weight:")
        print("来源类型: classic_theory/expert_consensus/empirical/experimental")
        source = input("来源类型: ").strip()
        
        has_data = input("是否有验证数据？(y/n): ").strip().lower()
        if has_data == "y":
            correct = int(input("正确应用次数: ").strip())
            total = int(input("总应用次数: ").strip())
            result = assigner.assign_confidence_weight(source, correct, total)
            print(f"\n计算结果（基于验证数据）: confidence_weight = {result}")
        else:
            result = assigner.assign_confidence_weight(source)
            print(f"\n赋值结果（基于来源类型）: confidence_weight = {result}")
    
    elif choice == "2":
        print("\n赋值usage_frequency:")
        priority = int(input("优先级 (1最高): ").strip())
        scenario_count = int(input("适用场景数量: ").strip())
        
        has_data = input("是否有使用统计？(y/n): ").strip().lower()
        if has_data == "y":
            usage = int(input("使用次数: ").strip())
            total = int(input("同类知识总使用次数: ").strip())
            result = assigner.assign_usage_frequency(priority, scenario_count, usage, total)
            print(f"\n计算结果（基于使用统计）: usage_frequency = {result}")
        else:
            result = assigner.assign_usage_frequency(priority, scenario_count)
            print(f"\n赋值结果（基于优先级和场景）: usage_frequency = {result}")
    
    elif choice == "3":
        print("\n赋值frequency:")
        print("频率级别: very_high/high/medium/low")
        level = input("频率级别: ").strip()
        
        has_data = input("是否有语料库统计？(y/n): ").strip().lower()
        if has_data == "y":
            occurrence = int(input("出现次数: ").strip())
            total = int(input("总词数: ").strip())
            result = assigner.assign_term_frequency(level, occurrence, total)
            print(f"\n计算结果（基于语料库统计）: frequency = {result}")
        else:
            result = assigner.assign_term_frequency(level)
            print(f"\n赋值结果（基于经验判断）: frequency = {result}")
    
    else:
        print("无效选项")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指标赋值工具（简化版）")
    parser.add_argument("--mode", choices=["interactive"], default="interactive",
                       help="运行模式")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_assign()

