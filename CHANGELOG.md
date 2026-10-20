# Hardware Changelog

All notable changes to the WingFC flight controller hardware will be documented in this file.

## [Rev C - v1.1.0] - 2026-10-20

### 🚀 Enhancements & Redesign
- **Ultra-Compact Footprint:** Reduced board dimensions from 34.0 × 40.0 mm down to **32.0 × 33.2 mm**, centered directly on the standard 25.5 × 25.5 mm M2 whoop mounting pattern.
- **Actuator Architecture (10 Channels):**
  - **6 Primary Channels (`ESC1`, `ESC2`, `S1`..`S4`):** Standard 2.54 mm pitch 1x03 vertical pin headers nestled directly between mounting screws `H3` and `H4`, with corrected 3-hole pin alignment and 1.9 mm edge margin.
  - **4 Auxiliary Channels (`S5`..`S8`):** Compact 1.27 mm pitch horizontal pin headers located in the East bay for advanced airframe functions (flaps, pan/tilt gimbals, landing gear, payload drop).
- **Enhanced Power & Transient Protection:**
  - Added `D3` (SMAJ24A TVS diode) directly across `J_BAT` battery input solder pads.
  - Added `D4` (SMAJ5.0A TVS diode) across the +5V servo bus.
  - Added `C_BULK` (100 µF 1206 ceramic) to absorb high dynamic servo surge currents.
  - Added `D1` (B0520W Schottky) reverse-current isolation and `C8` (22 µF 0805) hold-up buffering on `+5V_MCU` to prevent brownouts.
  - Added `JP1` and `JP2` open solder jumpers on `B.Cu` to isolate +5V pins on `ESC1`/`ESC2` from onboard BEC.
- **RF & Testability:**
  - Dedicated antenna keepout zone across all 4 copper layers over the South antenna region of the XIAO module.
  - Exposed SWD test pads (`TP1`..`TP5`) and spare GPIOs D17..D19 (`TP6`..`TP8`) on `B.Cu`.
- **Firmware Synchronization:** GPIO mapping fully synchronized with `wingfc-rs` (`pins.rs`).

## [Rev B - v1.0.0] - 2026-09-25

### 🚀 Enhancements & Redesign
- **Rotated North-Facing USB-C Notch:** Re-oriented Seeed Studio XIAO nRF52840 Sense Plus (`U1`) 180° so the USB-C receptacle faces forward over a recessed edge notch, ensuring zero cable collision.
- **10 Actuator Channels:** Expanded servo breakout from 7 channels to 10 channels total (2 ESCs + 8 Servos) in a continuous 3x10 2.54mm rear header block.
- **Outward-Facing JST-SH Connectors:** Rotated horizontal 4-pin RC (`J_RC`) and 6-pin GPS (`J_GPS`) connectors 180° so cable latches face outward from the PCB edge.
- **Dedicated Barometer:** Integrated Infineon DPS310 high-precision barometric pressure sensor on the secondary I2C bus (`TWISPI1`).
- **Optimized Footprint:** Compact 34.0 mm × 40.0 mm outline with standard 25.5 × 25.5 mm M2 mounting pattern.

## [Rev A - v0.3.0] - Historical Baseline
- Initial Seeed Studio XIAO nRF52840 Sense carrier prototype with 7-channel PWM/DShot breakout and MP2315 BEC.
