#!/usr/bin/env python3
"""A/B test validator: check experiment configs, traffic splits, and metric collection."""

import json
import sys
from pathlib import Path

def validate() -> int:
    experiments = Path("experiments.json")
    if not experiments.exists():
        print("ℹ️  No experiments.json found.")
        return 0
    
    data = json.loads(experiments.read_text())
    
    print(f"# A/B Test Validation\n")
    
    total_split = 0
    for exp_name, config in data.items():
        variants = config.get("variants", {})
        split_sum = sum(v.get("traffic_percent", 0) for v in variants.values())
        total_split += split_sum
        
        print(f"{exp_name}:")
        print(f"  Variants: {len(variants)}")
        print(f"  Split:    {split_sum}%")
        
        if split_sum != 100:
            print(f"  ❌ Split doesn't sum to 100%")
        
        # Check metric collection
        metrics = config.get("metrics", [])
        if not metrics:
            print(f"  ⚠️  No success metric defined")
        else:
            print(f"  Metrics:  {', '.join(metrics)}")
    
    print(f"\n{'✅' if all(sum(v.get('traffic_percent', 0) for v in e.get('variants', {}).values()) == 100 for e in data.values()) else '❌'} Experiments validated.")
    return 0

if __name__ == "__main__":
    sys.exit(validate())
