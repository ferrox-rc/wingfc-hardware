# WingFC Hardware Carrier Board

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![KiCad Version](https://img.shields.io/badge/KiCad-8.0%20%2F%209.0%20%2F%2010.0-blue.svg)](https://kicad.org)
[![Form Factor](https://img.shields.io/badge/Mounting-25.5x25.5mm%20M2-brightgreen.svg)]()
[![Firmware](https://img.shields.io/badge/Firmware-ferrox--rc%2Fwingfc--rs-orange.svg)](https://github.com/ferrox-rc/wingfc-rs)

Official hardware carrier board design, schematics, PCB layout, and mechanical CAD for the **WingFC** open-source flight controller ecosystem.

Engineered specifically for sub-250g FPV flying wings, acrobatic wings, and compact autonomous UAVs, this carrier board hosts the **Seeed Studio XIAO nRF52840 Sense Plus** and breaks out all actuation channels, serial links, and power regulation onto an ultra-compact footprint.

---

## 3D Board Visualizations

| Isometric 3D View | Top View | Bottom View |
| :---: | :---: | :---: |
| ![WingFC Iso](docs/images/WingFC_3D_iso.png) | ![WingFC Top](docs/images/WingFC_3D_top.png) | ![WingFC Bottom](docs/images/WingFC_3D_bottom.png) |

---

## Key Hardware Features

- **Standard 25.5 × 25.5 mm Whoop Mounting Pattern:** Fits standard micro-quad and fixed-wing carrier bays with 4× M2 mounting holes (`H1`–`H4`).
- **Ultra-Compact Profile:** Only **32.0 mm wide × 33.2 mm long**, minimizing mass and fuselage cavity requirements.
- **Edge-Mounted North-Facing USB-C Port:**
  - MCU rotated so the USB-C receptacle faces forward into free air.
  - Dedicated $10.0\,\text{mm} \times 0.8\,\text{mm}$ recessed access notch ensures standard USB-C cables plug in flush without mechanical collision.
- **10 Actuator Channels (2 ESCs + 8 Servos):**
  - **6 Primary Channels (`ESC1`, `ESC2`, `S1`..`S4`):** Standard 2.54 mm pitch vertical pin headers (Signal / +5V / GND) nestled directly between lower mounting screws `H3` and `H4`.
  - **4 Auxiliary Channels (`S5`..`S8`):** Compact 1.27 mm pitch horizontal pin headers located in the East bay for advanced airframe functions (flaps, pan/tilt gimbals, landing gear, payload drop).
- **Outward-Facing JST-SH Quick-Connect Sockets:**
  - **RC Receiver (`J_RC`):** 4-pin horizontal JST-SH on the West flank (5V, GND, UARTE0 TX/RX for CRSF/ELRS/iBus).
  - **GPS & Navigation (`J_GPS`):** 6-pin horizontal JST-SH on the East flank (5V, GND, UARTE1 TX/RX for NMEA GPS, TWISPI1 SDA/SCL for external compass).
- **High-Efficiency 5V / 2A Synchronous BEC:**
  - Monolithic Power Systems **MP2315** high-efficiency step-down buck regulator on the bottom layer.
  - Supports 2S to 4S LiPo input voltages (up to 24V).
  - High-current Bourns SRN4018 3.3µH shielded power inductor.
- **Comprehensive Power & Brownout Protection:**
  - **VBAT TVS (`D3`):** Littelfuse SMAJ24A (400W) TVS diode across battery input pads.
  - **+5V TVS (`D4`):** Littelfuse SMAJ5.0A (400W) TVS diode across the servo rail.
  - **Servo Surge Buffer (`C_BULK`):** 100µF 1206 low-ESR ceramic capacitor absorbs motor/servo inductive spikes.
  - **MCU Brownout Hold-Up (`C8` + `D1`):** Diodes Inc B0520W Schottky diode and 22µF 0805 capacitor buffer the MCU 5V rail (`+5V_MCU`) against aerodynamic stall current spikes.
  - **ESC BEC Isolation (`JP1`, `JP2`):** Solder jumpers to disconnect +5V from ESC1 and ESC2 pins, preventing back-feeding into the onboard regulator.
- **Integrated High-Precision Barometer:**
  - Onboard Infineon **DPS310** 24-bit barometric pressure sensor on the secondary I2C bus (`TWISPI1`).
  - Enables sub-meter altitude hold and autonomous vertical Kalman filtering.
- **Antenna Keepout Zone:**
  - Complete copper-free zone across all 4 layers under the South antenna portion of the XIAO module.
- **Breakout & Testability:**
  - SWD test pads (`TP1`..`TP5`): SWCLK, SWDIO, RST, GND, 3V3.
  - Spare GPIO breakout pads (`TP6`..`TP8`): D17, D18, D19.
  - 11:1 precision resistor divider (100kΩ / 10kΩ + 100nF filtering) connected to SAADC `AIN7` (`D16` / `P0.31`) for LiPo pack telemetry.

---

## Pinout & Electrical Allocation

| Header / Pin | Label | nRF52840 Pin | Peripheral | Function |
| :--- | :--- | :--- | :--- | :--- |
| **ESC 1** | `ESC1` | `P0.02` (`D0`) | `PWM0` Ch 0 | Motor 1 (DShot / PWM) |
| **ESC 2** | `ESC2` | `P0.03` (`D1`) | `PWM0` Ch 1 | Motor 2 / Differential Thrust |
| **Servo 1** | `S1` | `P0.04` (`D2`) | `PWM1` Ch 0 | Elevon Left / Aileron |
| **Servo 2** | `S2` | `P0.05` (`D3`) | `PWM1` Ch 1 | Elevon Right / Elevator |
| **Servo 3** | `S3` | `P0.28` (`D4`) | `PWM1` Ch 2 | Rudder / V-Tail |
| **Servo 4** | `S4` | `P0.29` (`D5`) | `PWM1` Ch 3 | Flap Left / Aux |
| **Servo 5** | `S5` | `P0.17` (`D11`)| `PWM2` Ch 0 | Aux / Pan Servo |
| **Servo 6** | `S6` | `P0.18` (`D12`)| `PWM2` Ch 1 | Flap Right / Tilt Servo |
| **Servo 7** | `S7` | `P0.19` (`D13`)| `PWM2` Ch 2 | Aux / Gear Retract |
| **Servo 8** | `S8` | `P0.20` (`D14`)| `PWM2` Ch 3 | Payload Drop / Aux |
| **RC Connector** | `J_RC` | `P1.11` / `P1.12` | `UARTE0` | CRSF / ELRS @ 420k or iBus @ 115.2k |
| **GPS Serial** | `J_GPS` | `P0.09` / `P0.10` | `UARTE1` | NMEA GPS @ 115.2k |
| **External I2C**| `J_GPS` | `P0.15` / `P0.16` | `TWISPI1` | QMC5883L Compass / Ext. Sensors |
| **Battery ADC** | `VBAT_SENSE`| `P0.31` (`D16`)| `SAADC` AIN7 | 11:1 LiPo Voltage Sensing |

---

## KiCad Project Structure

The KiCad project is located in [`kicad/`](kicad/):
- `WingFC.kicad_pro`: KiCad project management file.
- `WingFC.kicad_sch`: Master schematic (includes onboard power supply, filtering, and breakout nets).
- `WingFC.kicad_pcb`: 4-layer PCB layout with dedicated power planes and signal routing.
- `build_pcb.py`: Automated layout generator and validation script.
- `footprints/`: Self-contained project footprint libraries.

---

## Compatible Firmware

This carrier board is fully supported by the **WingFC-rs** bare-metal Rust flight controller firmware:
👉 **[ferrox-rc/wingfc-rs](https://github.com/ferrox-rc/wingfc-rs)**

---

## License

Hardware design files, schematics, PCB layouts, and documentation are licensed under the [MIT License](LICENSE).
