#!/usr/bin/env python3
"""
Generate engineering specs for EVERY device, not just the best per condition
"""
import json
import subprocess
import time
from pathlib import Path

DEVICES_DIR = Path('devices')
ENG_DIR = Path('engineering')
REGISTRY = DEVICES_DIR / 'device_registry.json'

print("🔥 ENGINEERING ALL 6,265 DEVICES")
print("="*60)

# Load registry
registry = json.loads(REGISTRY.read_text())
total = len(registry)
print(f"📊 Total devices: {total}")

# Track progress
completed = 0
skipped = 0

for i, device in enumerate(registry):
    device_id = device.get('id', 'unknown')
    pain = device.get('pain', device.get('pain_addressed', 'unknown'))
    name = device.get('name', 'unknown')
    
    print(f"\n[{i+1}/{total}] Processing {name} ({pain})...")
    
    # Check if spec already exists
    spec_file = ENG_DIR / f"{pain}_{device_id}_engineering.json"
    if spec_file.exists():
        print(f"  ⏭️  Spec already exists, skipping")
        skipped += 1
        continue
    
    # Generate spec for this specific device
    cmd = f"python3 device_engineer.py --device-id {device_id} --condition {pain}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        completed += 1
        print(f"  ✅ Generated spec for {device_id}")
    else:
        print(f"  ❌ Failed: {result.stderr[:100]}")
    
    # Progress report every 100 devices
    if (i+1) % 100 == 0:
        print(f"\n📊 PROGRESS: {i+1}/{total} devices processed")
        print(f"  ✅ New specs: {completed}")
        print(f"  ⏭️  Already existed: {skipped}")
    
    time.sleep(0.5)  # Rate limiting

print(f"\n✅ COMPLETE!")
print(f"  Total devices: {total}")
print(f"  New specs generated: {completed}")
print(f"  Skipped (already existed): {skipped}")
print(f"  Final coverage: {(completed+skipped)/total*100:.1f}%")
