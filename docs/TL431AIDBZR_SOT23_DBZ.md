# Texas Instruments TL431AIDBZR: DBZ SOT-23-3

**This entry is specific to TL431AIDBZR** (A-grade, TI DBZ 3-pin package). This is *not* a TL432 and must not be used with TL432 pinouts.

## Authoritative documents

- [TI TL431 / TL432 datasheet, §5, Table 5-1](https://www.ti.com/lit/ds/symlink/tl431.pdf)
- [TI DBZ0003A package drawing 4214838/F, land pattern example](https://www.ti.com/lit/ml/mpds108g/mpds108g.pdf)
- [TL431AIDBZR product](https://www.ti.com/product/TL431/part-details/TL431AIDBZR)

## Verified pin mapping

| Physical pad number | Symbol pin | Function | Top-view position |
|---|---|---|---|
| **1** | 1 | **CATHODE (K)** | Upper-left |
| **2** | 2 | **REF** | Lower-left |
| **3** | 3 | **ANODE (A)** | Right, center |

TI **TL432** in the *same* DBZ package has **pin 1 REF and pin 2 CATHODE** instead. Compare the exact ordering code before using this symbol with a different TL43x part.

### Footprint

`MaxStriX324:TL431AIDBZR_SOT23_DBZ`

- Three surface-mount pads, each **1.30 × 0.60 mm** (TI land pattern).
- 0.95 mm between center-to-midpoint of the top/bottom pad rows; **1.90 mm between pad 1 and pad 2**.
- Left-to-right pad-centre distance: **2.10 mm**.
- Pad 1 marker on silkscreen and chamfer on fabrication outline.
- Footprint origin centered on the body and pad arrangement, pad 1 at (-1.05, -0.95) in KiCad footprint coordinates.
- Simplified 3D `.wrl` model is linked in the footprint and automatically installed. Its molded body and lead dimensions are approximate. A CadQuery script can export an optional `.step` file with the same approximate geometry.

## Safety and use

When replacing an **existing** schematic symbol, verify the pin-to-net connections *after* symbol replacement; KiCad does not automatically swap TL432/alternate-library pin names to compensate for differing physical pin numbers.

For the +20 V RAW flyback feedback: K attaches to the TL431/opto LED cathode node; REF to the sensing-divider midpoint; A to isolated LOW_COM.

3D model is for visual/mechanical layout assistance, not manufacturing dimension certification.
