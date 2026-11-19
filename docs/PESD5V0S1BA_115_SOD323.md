# Nexperia PESD5V0S1BA,115 (bidirectional ESD TVS), SOD323

- Symbol: `MaxStriX324:PESD5V0S1BA_115`
- Footprint: `MaxStriX324:PESD5V0S1BA_115_SOD323`
- 3D: `MaxStriX324.3dshapes/PESD5V0S1BA_115_SOD323.step` (linked; generated simplified CAD, not manufacturer model). A WRL fallback is also included. STEP is reproducible via `scripts/generate_3d_models.py`.
- Official datasheet: https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf (Nexperia, 26 Apr 2024, v6)
- Manufacturer part number: `PESD5V0S1BA,115` (tape-and-reel suffix 115).
- Bidirectional ESD protector. Pins **1=K1** and **2=K2** per manufacturer pinning table. Protection is symmetric; either pin may connect to GNDA or signal electrically, but keep PCB marking consistent.

## SOD323 footprint geometry

Manufacturer datasheet Figure 9: body approximately 1.7 x 1.25 mm, height up to 1.1 mm, overall lead span 2.3–2.7 mm. Fig. 10 reflow land pattern: two copper pads 0.6 x 0.6 mm, at x ±1.1 mm (pad center distance 2.2 mm). Pin 1 is on the left when viewed from the top. Pad y coordinates are 0. Silkscreen mark is for PCB pin identification only.

3D model simplification: rectangular black body 1.7 x 1.25 x 0.95 mm plus two metal leads; not supplier certified mechanical CAD. Actual lead shapes are curved. Verify final placement and solderability against the physical diode and PCB assembly process.

## Use on Measurement_board_v_1 NTC probes

Place one TVS immediately next to each JST PH incoming NTC cable:
- D4: pin1 `NTC_1_RAW` at JST pin 1; pin2 `GNDA` at JST pin 2.
- D5: pin1 `NTC_2_RAW`; pin2 `GNDA`.
- D6: pin1 `NTC_3_RAW`; pin2 `GNDA`.

This single device is for short transient ESD/EFT suppression and should have a very short transient return trace. It is **not** an accurate 0–3.3V input clamp; clamping voltage for large surges can be substantially higher than 3.3 V, and it cannot safely handle continuous connection to high voltage. The NTC line must still be current-limited into the MCU and may need an additional local clamp/RC filter, checked against maximum ADC injection current. GNDA return path must not share high-current LF1005 sensor load loops.

Electrical rating: 5V maximum reverse standoff, typical capacitance 35pF, 130W peak 8/20us, per Nexperia datasheet; these are pulse ratings, not continuous.
