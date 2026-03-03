#!/usr/bin/env python3
"""
Batch process all devices to generate engineering specs
"""
import json
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

DEVICES_DIR = Path('devices')
ENG_DIR = Path('engineering')
REGISTRY = DEVICES_DIR / 'device_registry.json'

def generate_spec(device):
    """Generate engineering spec for a single device"""
    device_id = device.get('id', 'unknown')
    pain = device.get('pain', device.get('pain_addressed', 'unknown'))
    
    # Create condition-specific command
    cmd = f"python3 device_engineer.py --device-id {device_id} --condition {pain}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        return f"✅ {device_id}: {pain}"
    else:
        return f"❌ {device_id}: {result.stderr[:50]}"

print("🔥 BATCH ENGINEERING — 6,265 DEVICES")
print("="*60)

registry = json.loads(REGISTRY.read_text())
print(f"📊 Processing {len(registry)} devices...")

# Process in parallel (10 at a time)
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(generate_spec, registry[:50]))  # Start with 50

for result in results:
    print(result)

print("\n✅ BATCH COMPLETE — Check engineering/ directory")
