#!/usr/bin/env python3
"""
PHOENIX DEVICE ENGINEER
Takes best concept design per condition and produces full engineering specs.
Real enough for an engineer to build from.
"""
import json
from pathlib import Path
from datetime import datetime

SWARM   = Path("/data/data/com.termux/files/home/swarm-platform")
DEVICES = SWARM / "devices"
ENG_DIR = SWARM / "engineering"
ENG_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# ENGINEERING DATABASE
# Real components, real part numbers, real specs
# ═══════════════════════════════════════════════════════════════

ENGINEERING = {

"biofeedback_neural": {
    "mcu": {
        "part": "Nordic nRF52840",
        "description": "ARM Cortex-M4F 64MHz, BLE 5.0, 1MB Flash, 256KB RAM",
        "cost_usd": 4.20,
        "datasheet": "infocenter.nordicsemi.com/topic/struct_nrf52/struct/nrf52840.html"
    },
    "sensors": [
        {"part": "AD8232", "function": "Single-lead ECG / heart rate", "cost_usd": 2.80},
        {"part": "MAX30102", "function": "PPG pulse oximetry + SpO2", "cost_usd": 3.50},
        {"part": "GSR Grove Sensor", "function": "Galvanic skin response (stress)", "cost_usd": 1.90},
        {"part": "ICM-42688-P", "function": "6-axis IMU accelerometer+gyro", "cost_usd": 2.10},
    ],
    "output": {
        "part": "DRV2605L",
        "function": "Haptic feedback driver — vibrotactile response",
        "cost_usd": 1.40
    },
    "power": {
        "battery": "Li-Po 500mAh 3.7V",
        "charger": "MCP73831 single-cell charger",
        "regulator": "TPS62740 ultra-low-power buck",
        "estimated_life_hours": 168,
        "cost_usd": 3.20
    },
    "pcb": {
        "layers": 4,
        "size_mm": "28x18",
        "thickness_mm": 0.8,
        "process": "ENIG (Electroless Nickel Immersion Gold)",
        "estimated_cost_usd": 2.50
    },
    "enclosure": {
        "material": "Medical-grade silicone overmold + ABS shell",
        "ip_rating": "IP67",
        "size_mm": "45x30x8",
        "estimated_cost_usd": 4.00
    },
    "firmware": {
        "rtos": "Zephyr RTOS",
        "sampling_rate_hz": 250,
        "algorithm": "HRV analysis via time-domain RMSSD + frequency-domain LF/HF ratio. Skin conductance threshold detection. IMU gesture recognition via edge ML (TensorFlow Lite Micro).",
        "ml_model": "TensorFlow Lite Micro — stress/calm classifier, <50KB model size",
        "data_protocol": "BLE GATT custom profile, AES-128 encrypted, local storage only"
    },
    "signal_processing": {
        "ecg_filter": "Bandpass 0.5-40Hz, notch 50/60Hz",
        "ppg_filter": "Low-pass 10Hz, DC removal",
        "hrv_window": "5-minute rolling window, R-R interval detection via Pan-Tompkins algorithm",
        "stress_detection": "SVM classifier trained on HRV + GSR + accelerometer fusion"
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k) Premarket Notification",
        "predicate_devices": ["Garmin HRV Status", "Whoop Strap", "Polar H10"],
        "estimated_timeline_months": 12,
        "estimated_cost_usd": 50000
    }
},

"electromagnetic": {
    "mcu": {
        "part": "STM32L476RG",
        "description": "ARM Cortex-M4 80MHz, ultra-low power, 1MB Flash",
        "cost_usd": 3.80,
        "datasheet": "st.com/resource/en/datasheet/stm32l476rg.pdf"
    },
    "drive_circuit": [
        {"part": "DRV8835", "function": "Dual H-bridge motor/coil driver", "cost_usd": 1.20},
        {"part": "INA219", "function": "Current sense for coil monitoring", "cost_usd": 0.90},
        {"part": "Custom air-core coil", "function": "PEMF generation 1-100Hz", "cost_usd": 3.50},
    ],
    "sensors": [
        {"part": "MLX90393", "function": "3-axis magnetometer for field verification", "cost_usd": 2.20},
        {"part": "LM35", "function": "Temperature monitor — safety cutoff", "cost_usd": 0.80},
    ],
    "power": {
        "battery": "Li-Po 800mAh 3.7V",
        "charger": "TP4056 with protection",
        "regulator": "XC6220 LDO 3.3V",
        "estimated_life_hours": 48,
        "cost_usd": 4.50
    },
    "pcb": {
        "layers": 2,
        "size_mm": "40x25",
        "thickness_mm": 1.0,
        "process": "HASL lead-free",
        "estimated_cost_usd": 1.80
    },
    "enclosure": {
        "material": "ABS medical grade",
        "ip_rating": "IP54",
        "size_mm": "80x50x15",
        "estimated_cost_usd": 5.00
    },
    "firmware": {
        "rtos": "FreeRTOS",
        "frequency_range_hz": "1-100Hz programmable",
        "waveform": "Sinusoidal, square, sawtooth — programmable",
        "intensity_mt": "0.1-2.0 mT field strength at skin surface",
        "safety": "Auto-shutoff at 40C skin temp. Max 20min session. 4hr lockout.",
        "algorithm": "PEMF protocol library: bone healing (75Hz), pain (10Hz), sleep (delta 0.5-4Hz), inflammation (50Hz)"
    },
    "signal_processing": {
        "field_verification": "Magnetometer feedback loop confirms field strength within 5%",
        "thermal_monitor": "PID temperature controller limits coil current if skin temp exceeds 38C",
        "session_timer": "Hardware watchdog enforces session limits"
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Orthofix Physio-Stim", "EarthPulse PEMF", "Bioelectronics ActiPatch"],
        "estimated_timeline_months": 18,
        "estimated_cost_usd": 75000
    }
},

"photobiomodulation": {
    "mcu": {
        "part": "STM32G031",
        "description": "ARM Cortex-M0+ 64MHz, low cost, sufficient for LED drive control",
        "cost_usd": 1.20,
        "datasheet": "st.com/en/microcontrollers-microprocessors/stm32g031.html"
    },
    "light_source": [
        {"part": "660nm Red LED array (Epistar)", "function": "Superficial tissue penetration 1-3mm", "cost_usd": 2.80},
        {"part": "850nm NIR LED array (Epistar)", "function": "Deep tissue penetration 5-10mm", "cost_usd": 3.20},
        {"part": "IRLML6402 MOSFET", "function": "PWM LED current control", "cost_usd": 0.30},
    ],
    "sensors": [
        {"part": "TSL2591", "function": "Ambient light sensor — dark adaptation check", "cost_usd": 1.50},
        {"part": "LM35", "function": "LED junction temperature monitor", "cost_usd": 0.80},
    ],
    "power": {
        "battery": "Li-Po 600mAh 3.7V",
        "charger": "MCP73831",
        "regulator": "AP2112K 3.3V LDO",
        "estimated_life_hours": 30,
        "cost_usd": 3.50
    },
    "pcb": {
        "layers": 2,
        "size_mm": "50x30",
        "thickness_mm": 1.0,
        "process": "HASL",
        "estimated_cost_usd": 1.50
    },
    "enclosure": {
        "material": "Opaque ABS — light-sealed",
        "ip_rating": "IP44",
        "size_mm": "60x40x12",
        "estimated_cost_usd": 3.50
    },
    "firmware": {
        "rtos": "Bare metal",
        "pwm_frequency_hz": 10000,
        "duty_cycle_range": "1-100% programmable",
        "irradiance_mw_cm2": "10-200 mW/cm² at skin surface",
        "protocols": {
            "wound_healing": "660nm 50mW/cm² 10min 2x/day",
            "depression": "810nm 250mW/cm² 20min/day transcranial",
            "sleep": "660nm 10mW/cm² 30min before bed",
            "pain": "660nm+850nm combined 100mW/cm² 15min"
        },
        "safety": "Max 20min session. Eye protection warning on startup. Temp cutoff 45C."
    },
    "signal_processing": {
        "dose_calculation": "Joules/cm² = Power(W/cm²) × Time(s). Target 4-60 J/cm² depending on condition.",
        "feedback": "Photodiode monitors output power, adjusts PWM to maintain calibrated dose"
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Joovv Solo", "PlatinumLED BioMax", "Tendlite Red Light"],
        "estimated_timeline_months": 12,
        "estimated_cost_usd": 40000
    }
},

"rf_sensing": {
    "mcu": {
        "part": "ESP32-S3",
        "description": "Xtensa LX7 240MHz, WiFi+BLE, 8MB PSRAM for ML inference",
        "cost_usd": 3.50,
        "datasheet": "espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf"
    },
    "rf_module": [
        {"part": "BGT60TR13C (Infineon)", "function": "60GHz FMCW radar — micro-motion detection", "cost_usd": 8.50},
        {"part": "HMC5883L", "function": "Magnetometer for orientation", "cost_usd": 1.20},
    ],
    "power": {
        "battery": "Li-Po 2000mAh 3.7V (mains powered option)",
        "charger": "TP4056",
        "regulator": "AMS1117-3.3",
        "estimated_life_hours": 72,
        "cost_usd": 6.00
    },
    "pcb": {
        "layers": 4,
        "size_mm": "55x45",
        "thickness_mm": 0.8,
        "process": "ENIG — RF requires tight impedance control",
        "estimated_cost_usd": 4.50
    },
    "enclosure": {
        "material": "ABS with RF-transparent window",
        "ip_rating": "IP44",
        "size_mm": "80x60x20",
        "estimated_cost_usd": 6.00
    },
    "firmware": {
        "rtos": "FreeRTOS + TensorFlow Lite Micro",
        "radar_config": "FMCW 58-63.5GHz, range 0.2-5m, velocity ±3m/s",
        "sampling_rate_hz": 25,
        "algorithm": "Range-Doppler processing. Fall detection via sudden velocity spike + absence of periodic breathing motion post-event. Gait analysis via cadence extraction.",
        "ml_model": "CNN trained on radar signatures of normal gait vs fall events. <200KB model.",
        "alert": "BLE to phone + optional 4G via SIM800L module"
    },
    "signal_processing": {
        "fmcw_processing": "FFT on I/Q samples → range profile → Doppler processing → micro-Doppler spectrogram",
        "fall_detection": "Threshold: velocity > 1.5m/s + horizontal displacement + cessation of periodic motion for >5s",
        "breathing_monitor": "0.1-0.5Hz chest movement extraction from static radar return"
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Google Nest Hub radar sleep", "Vayyar Care fall detection"],
        "estimated_timeline_months": 15,
        "estimated_cost_usd": 60000
    }
},

"electrochemical": {
    "mcu": {
        "part": "STM32L031",
        "description": "Ultra-low power Cortex-M0+ — ideal for always-on sensing",
        "cost_usd": 1.80,
        "datasheet": "st.com/en/microcontrollers-microprocessors/stm32l031.html"
    },
    "sensing": [
        {"part": "LMP91000", "function": "Potentiostat AFE for electrochemical sensors", "cost_usd": 2.40},
        {"part": "Custom enzyme electrode", "function": "Glucose oxidase or target-specific", "cost_usd": 1.50},
        {"part": "DS18B20", "function": "Temperature compensation for sensor drift", "cost_usd": 0.90},
        {"part": "ADS1115", "function": "16-bit ADC for precision measurement", "cost_usd": 1.80},
    ],
    "connectivity": [
        {"part": "SHTC3", "function": "Humidity sensor — environmental compensation", "cost_usd": 1.20},
        {"part": "nRF52810", "function": "BLE 5.0 for data transmission", "cost_usd": 2.80},
    ],
    "power": {
        "battery": "CR2032 coin cell (passive) or Li-Po 200mAh (active)",
        "estimated_life_hours": 720,
        "cost_usd": 1.50
    },
    "pcb": {
        "layers": 2,
        "size_mm": "20x15",
        "thickness_mm": 0.6,
        "process": "HASL",
        "estimated_cost_usd": 1.20
    },
    "enclosure": {
        "material": "Medical-grade polycarbonate",
        "ip_rating": "IP68",
        "size_mm": "30x20x8",
        "estimated_cost_usd": 2.50
    },
    "firmware": {
        "rtos": "Bare metal ultra-low power",
        "sampling_interval": "Every 5 minutes active, sleep between",
        "calibration": "2-point factory calibration + 1-point user calibration",
        "algorithm": "Amperometric current → glucose via Michaelis-Menten kinetics. Temperature-corrected. Drift compensation via baseline subtraction.",
        "accuracy_target": "±10% vs lab reference (FDA CGM standard)"
    },
    "signal_processing": {
        "noise_reduction": "16-sample averaging, outlier rejection",
        "drift_correction": "Exponential moving average baseline subtraction",
        "alert_thresholds": "Configurable high/low alerts via companion app"
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k) / De Novo if novel analyte",
        "predicate_devices": ["Abbott FreeStyle Libre", "Dexcom G7"],
        "estimated_timeline_months": 24,
        "estimated_cost_usd": 150000
    }
},

"mechanical_haptic": {
    "mcu": {
        "part": "Nordic nRF52832",
        "description": "Cortex-M4F 64MHz, BLE 5.0 — proven wearable platform",
        "cost_usd": 3.20,
        "datasheet": "infocenter.nordicsemi.com/topic/struct_nrf52/struct/nrf52832.html"
    },
    "actuators": [
        {"part": "DRV2605L", "function": "Haptic driver — ERM/LRA control", "cost_usd": 1.40},
        {"part": "Precision Microdrives 310-101", "function": "LRA vibration motor 175Hz resonance", "cost_usd": 3.50},
        {"part": "ICM-42688-P", "function": "IMU — motion tracking + tremor measurement", "cost_usd": 2.10},
    ],
    "sensors": [
        {"part": "FSR 402", "function": "Force sensing resistor — contact detection", "cost_usd": 1.80},
        {"part": "MAX30102", "function": "PPG — confirm device worn", "cost_usd": 3.50},
    ],
    "power": {
        "battery": "Li-Po 400mAh 3.7V",
        "charger": "MCP73831",
        "regulator": "TPS62740",
        "estimated_life_hours": 72,
        "cost_usd": 3.00
    },
    "pcb": {
        "layers": 4,
        "size_mm": "25x20",
        "thickness_mm": 0.8,
        "process": "ENIG",
        "estimated_cost_usd": 2.20
    },
    "enclosure": {
        "material": "TPU flexible overmold + hard ABS core",
        "ip_rating": "IP67",
        "size_mm": "40x35x10",
        "estimated_cost_usd": 5.50
    },
    "firmware": {
        "rtos": "Zephyr RTOS",
        "tremor_detection": "Accelerometer FFT → peak frequency 4-12Hz = pathological tremor",
        "compensation": "Counter-phase vibration at detected tremor frequency via LRA",
        "algorithm": "Adaptive notch filter at tremor frequency. Phase-locked loop tracks tremor drift. Vibrotactile stimulation at 100-300Hz competes with tremor pathway via proprioceptive interference.",
        "calibration": "Auto-calibrates to individual tremor signature in first 60 seconds"
    },
    "signal_processing": {
        "tremor_analysis": "FFT 256-point on 1-second window. Peak detection 3-12Hz band. Amplitude threshold >0.5g = treatment trigger.",
        "compensation_waveform": "Sinusoidal counter-vibration, phase-inverted to tremor signal",
        "efficacy_monitor": "Continuous tremor amplitude tracking. Session log stored locally."
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Cala Health kIQ tremor therapy", "GyroGlove"],
        "estimated_timeline_months": 18,
        "estimated_cost_usd": 80000
    }
},

"acoustic_ultrasound": {
    "mcu": {
        "part": "STM32H743",
        "description": "Cortex-M7 480MHz — needed for real-time ultrasound processing",
        "cost_usd": 8.50,
        "datasheet": "st.com/en/microcontrollers-microprocessors/stm32h743.html"
    },
    "transducer": [
        {"part": "Piezo transducer 1MHz (custom)", "function": "Ultrasound emission + receive", "cost_usd": 12.00},
        {"part": "TC6320 (Texas Instruments)", "function": "Ultrasound AFE — TX/RX switch + TGC", "cost_usd": 6.50},
        {"part": "DAC80501", "function": "16-bit DAC for waveform generation", "cost_usd": 2.80},
    ],
    "power": {
        "battery": "Li-Po 1500mAh 3.7V + boost to 12V for TX",
        "charger": "BQ25895 USB-C fast charge",
        "boost": "TPS61230A 12V boost converter",
        "estimated_life_hours": 8,
        "cost_usd": 8.00
    },
    "pcb": {
        "layers": 6,
        "size_mm": "70x50",
        "thickness_mm": 1.0,
        "process": "ENIG — high frequency requires controlled impedance",
        "estimated_cost_usd": 8.00
    },
    "enclosure": {
        "material": "Medical-grade ABS + acoustic coupling window",
        "ip_rating": "IP54",
        "size_mm": "120x70x30",
        "estimated_cost_usd": 12.00
    },
    "firmware": {
        "rtos": "FreeRTOS",
        "frequency_mhz": "1-3MHz programmable",
        "modes": {
            "therapeutic": "1MHz CW or pulsed, 0.5-2.0 W/cm² SATA",
            "diagnostic": "3MHz pulse-echo, A-mode imaging",
            "phonophoresis": "Drug delivery enhancement 1MHz pulsed"
        },
        "safety": "BNR verification at startup. Thermal index monitoring. Max 10min continuous.",
        "algorithm": "Pulse-echo time-of-flight for distance measurement. Doppler shift for flow detection."
    },
    "signal_processing": {
        "tx_waveform": "DDS sine generation, 8-cycle bursts at PRF 1-10kHz",
        "rx_processing": "TGC amplification, bandpass filter, envelope detection, log compression",
        "imaging": "A-mode: time-domain waveform. No beamforming needed for point-of-care."
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Butterfly iQ+", "Clarius L15 HD3", "Sonosite SII"],
        "estimated_timeline_months": 24,
        "estimated_cost_usd": 200000
    }
},

"thermal": {
    "mcu": {
        "part": "STM32G031",
        "description": "Cortex-M0+ — sufficient for thermal control PID loop",
        "cost_usd": 1.20
    },
    "thermal_elements": [
        {"part": "Peltier TEC1-12706", "function": "Thermoelectric cooler/heater", "cost_usd": 3.50},
        {"part": "DRV8871", "function": "H-bridge motor driver for TEC control", "cost_usd": 1.80},
        {"part": "NTC 10K thermistor", "function": "Skin temperature sensing x4", "cost_usd": 0.40},
        {"part": "MLX90614", "function": "IR contactless temp verification", "cost_usd": 4.50},
    ],
    "power": {
        "battery": "Li-Po 2000mAh 3.7V (TEC is power hungry)",
        "charger": "BQ25895",
        "estimated_life_hours": 4,
        "cost_usd": 7.00
    },
    "pcb": {"layers": 2, "size_mm": "50x40", "estimated_cost_usd": 2.00},
    "enclosure": {
        "material": "Aluminum heatsink + silicone contact surface",
        "ip_rating": "IP44",
        "size_mm": "80x60x20",
        "estimated_cost_usd": 8.00
    },
    "firmware": {
        "algorithm": "PID thermal control loop. Setpoint ±0.5°C accuracy. Ramp rate 1°C/min.",
        "safety": "Hardware cutoff at 42°C skin surface. Redundant thermistors.",
        "protocols": {
            "heat_therapy": "38-40°C, 20min session",
            "cold_therapy": "10-15°C, 10min session",
            "contrast": "Alternating hot/cold 2min cycles x5"
        }
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Breg Polar Care", "Game Ready GRPro"],
        "estimated_timeline_months": 12,
        "estimated_cost_usd": 35000
    }
},

"magnetic_resonance": {
    "mcu": {
        "part": "STM32F103",
        "description": "Cortex-M3 72MHz — proven in PEMF devices",
        "cost_usd": 1.50
    },
    "coil_driver": [
        {"part": "IRF540N MOSFET", "function": "High current coil switching", "cost_usd": 0.60},
        {"part": "Custom Helmholtz coil", "function": "Uniform magnetic field generation", "cost_usd": 5.00},
        {"part": "ACS712", "function": "Current monitoring for coil", "cost_usd": 1.20},
    ],
    "power": {
        "battery": "Li-Po 1000mAh 3.7V",
        "estimated_life_hours": 24,
        "cost_usd": 4.50
    },
    "pcb": {"layers": 2, "size_mm": "45x35", "estimated_cost_usd": 1.80},
    "enclosure": {
        "material": "ABS — non-ferromagnetic required",
        "ip_rating": "IP44",
        "size_mm": "90x70x25",
        "estimated_cost_usd": 5.00
    },
    "firmware": {
        "frequency_range_hz": "1-100Hz programmable",
        "pulse_width_us": "100-1000",
        "field_strength_mt": "0.1-2.0",
        "protocols": {
            "bone_healing": "75Hz, 200μs, 1.5mT, 30min/day",
            "pain": "10Hz, 400μs, 0.5mT, 20min BID",
            "depression": "1Hz, 500μs, 1.0mT, 40min/day"
        }
    },
    "fda_pathway": {
        "device_class": "Class II",
        "submission_type": "510(k)",
        "predicate_devices": ["Neuralieve", "eNeura SpringTMS"],
        "estimated_timeline_months": 18,
        "estimated_cost_usd": 85000
    }
}
}

def load_best_devices():
    """Find the highest-scoring device for each condition"""
    registry_file = DEVICES / "device_registry.json"
    if not registry_file.exists():
        return {}
    
    registry = json.loads(registry_file.read_text())
    best = {}
    for entry in registry:
        pain = entry.get("pain", entry.get("pain_addressed"))
        if not pain:
            continue
        score = entry.get("total_score", 0)
        if pain not in best or score > best[pain]["score"]:
            best[pain] = {
                "name": entry["name"],
                "score": score,
                "physics": entry["physics"],
                "generation": entry["generation"],
                "id": entry["id"]
            }
    return best

def generate_engineering_specs(condition, device, physics):
    """Generate full engineering specs for a device"""
    if physics not in ENGINEERING:
        return None
    
    eng = ENGINEERING[physics]
    spec = {
        "device_name": device["name"],
        "condition": condition,
        "score": device["score"],
        "generation": device["generation"],
        "generated_at": datetime.now().isoformat(),
        "physics_principle": physics,
        "engineering": eng,
        "firmware_notes": eng["firmware"],
        "fda_pathway": eng["fda_pathway"],
        "estimated_bom_cost_usd": sum([
            eng["mcu"]["cost_usd"],
            sum(s["cost_usd"] for s in eng.get("sensors", [])),
            sum(d["cost_usd"] for d in eng.get("drive_circuit", []) if isinstance(eng.get("drive_circuit"), list)),
            eng.get("output", {}).get("cost_usd", 0),
            eng["power"]["cost_usd"],
            eng["pcb"]["estimated_cost_usd"],
            eng["enclosure"]["estimated_cost_usd"]
        ]),
        "assembly_notes": [
            "IPC-A-610 Class 2 assembly",
            "Conformal coating required for moisture resistance",
            "RF testing required for wireless modules",
            "Calibration required before final assembly",
            "Hermetic seal verification for IP67 devices"
        ],
        "testing_requirements": [
            "Electrical safety test (IEC 60601-1)",
            "EMC/EMI testing (IEC 60601-1-2)",
            "Biocompatibility (ISO 10993-5, -10) for skin contact",
            "Environmental testing (temperature, humidity, shock)",
            "Clinical validation required for FDA submission"
        ]
    }
    return spec

def main():
    print("\n" + "=" * 70)
    print("🔧 PHOENIX DEVICE ENGINEER — PRODUCTION SPECS")
    print("=" * 70)
    
    best = load_best_devices()
    print(f"\nFound best designs for {len(best)} conditions\n")
    
    specs = {}
    for condition, device in best.items():
        print(f"Generating specs for {condition} ({device['physics']})...")
        spec = generate_engineering_specs(condition, device, device["physics"])
        if spec:
            specs[condition] = spec
            
            # Save individual spec
            out_file = ENG_DIR / f"{condition}_engineering.json"
            out_file.write_text(json.dumps(spec, indent=2))
            print(f"  ✅ Saved to {out_file}")
    
    # Save master registry
    registry = {
        "generated": datetime.now().isoformat(),
        "conditions": len(specs),
        "specs": specs
    }
    master = ENG_DIR / "engineering_registry.json"
    master.write_text(json.dumps(registry, indent=2))
    
    print(f"\n{'='*70}")
    print(f"✅ ENGINEERING SPECS COMPLETE")
    print(f"   {len(specs)} devices spec'd")
    print(f"   Saved to: {ENG_DIR}")
    print(f"   Master:   {master}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

# ── BATCH MODE ADDITION ──────────────────────────────
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--device-id', help='Specific device ID to process')
    parser.add_argument('--condition', help='Condition to process')
    parser.add_argument('--batch', action='store_true', help='Process all devices')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of devices')
    
    args = parser.parse_args()
    
    if args.batch:
        # Load registry
        with open('devices/device_registry.json') as f:
            registry = json.load(f)
        
        devices = registry
        if args.limit > 0:
            devices = devices[:args.limit]
        
        print(f"📊 Processing {len(devices)} devices...")
        for device in devices:
            device_id = device.get('id')
            condition = device.get('pain', device.get('pain_addressed'))
            print(f"  Processing {condition}...")
            # Call main with device_id and condition
            sys.argv = ['device_engineer.py', '--device-id', device_id, '--condition', condition]
            main()
    else:
        main()
