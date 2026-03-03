#!/usr/bin/env python3
"""
Generate engineering specs for every device in the registry
"""
import json
import subprocess
import time
from pathlib import Path

DEVICES_DIR = Path('devices')
ENG_DIR = Path('engineering')
REGISTRY = DEVICES_DIR / 'device_registry.json'

print("🔥 GENERATING ENGINEERING SPECS FOR ALL DEVICES")
print("="*60)

# Load registry
if not REGISTRY.exists():
    print("❌ No device registry found")
    exit(1)

registry = json.loads(REGISTRY.read_text())
total = len(registry)
print(f"📊 Total devices in registry: {total}")

# Group by condition/pain type
conditions = {}
for device in registry:
    pain = device.get('pain', device.get('pain_addressed', 'unknown'))
    if pain not in conditions:
        conditions[pain] = []
    conditions[pain].append(device)

print(f"\n📊 Found {len(conditions)} unique conditions")
for condition, devices in list(conditions.items())[:10]:
    print(f"  {condition}: {len(devices)} devices")

# Generate specs for best device in each condition
print("\n🔧 Generating engineering specs for best devices...")

specs_generated = 0
for condition, devices in conditions.items():
    # Find highest scoring device for this condition
    best = max(devices, key=lambda d: d.get('total_score', 0))
    
    print(f"\n📋 Processing {condition}...")
    print(f"  Best device: {best.get('name', 'unknown')} (score: {best.get('total_score', 0)})")
    
    # Run device_engineer.py for this condition
    cmd = f"python3 device_engineer.py --condition {condition}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        specs_generated += 1
        print(f"  ✅ Generated specs for {condition}")
    else:
        print(f"  ❌ Failed: {result.stderr[:100]}")
    
    time.sleep(1)

print(f"\n✅ GENERATED {specs_generated} ENGINEERING SPECS")
print(f"📁 Check engineering/ directory for JSON files")
