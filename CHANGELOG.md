# Hardware Changelog

All notable changes to the WingFC flight controller hardware will be documented in this file.

## [Rev B - v1.0.0] - 2026-09-25

### 🚀 Enhancements & Redesign
- **Rotated North-Facing USB-C Notch:** Re-oriented Seeed Studio XIAO nRF52840 Sense Plus (`U1`) 180° so the USB-C receptacle faces forward over a recessed edge notch, ensuring zero cable collision.
- **10 Actuator Channels:** Expanded servo breakout from 7 channels to 10 channels total (2 ESCs + 8 Servos) in a continuous 3x10 2.54mm rear header block.
- **Outward-Facing JST-SH Connectors:** Rotated horizontal 4-pin RC (`J_RC`) and 6-pin GPS (`J_GPS`) connectors 180° so cable latches face outward from the PCB edge.
- **Dedicated Barometer:** Integrated Infineon DPS310 high-precision barometric pressure sensor on the secondary I2C bus (`TWISPI1`).
- **Optimized Footprint:** Compact 34.0 mm × 40.0 mm outline with standard 25.5 × 25.5 mm M2 mounting pattern.

## [Rev A - v0.3.0] - Historical Baseline
- Initial Seeed Studio XIAO nRF52840 Sense carrier prototype with 7-channel PWM/DShot breakout and MP2315 BEC.
