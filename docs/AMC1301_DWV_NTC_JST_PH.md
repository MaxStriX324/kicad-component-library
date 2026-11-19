# TI AMC1301DWV / AMC1301DWVR and remote NTC via JST PH

## AMC1301 (DWV package only)

- **Symbol:** `MaxStriX324:AMC1301DWV`
- **Footprint:** `MaxStriX324:AMC1301_DWV_SOIC8`
- **3D model:** linked `MaxStriX324.3dshapes/AMC1301_DWV_SOIC8.wrl` (original *approximate* model); a STEP may be generated in GitHub Actions by `scripts/generate_3d_models.py`.
- Exact package per TI is `DWV0008A`, not `SOIC-8_3.9x4.9mm_P1.27mm`. Body 7.5 × 5.85 mm; lead-to-lead 11.5 mm typical; height 2.8 mm max.
- TI official DWV land pattern: 8 pads 1.8 × 0.6 mm, 1.27 mm vertical pitch, 10.9 mm horizontal pad center spacing. Nominal metal-pad edge gap **9.1 mm** between high and low isolation domains. Footprint pad1=(-5.45,-1.905), pad8=(+5.45,-1.905), bottom-left pad4=(-5.45,+1.905), bottom-right pad5=(+5.45,+1.905).

| Pin | Net | Isolation side |
|---|---|---|
| 1 | VDD1, isolated high-side 3.3 or 5V | HV |
| 2 | INP | HV |
| 3 | INN | HV |
| 4 | GND1 | HV |
| 5 | GND2 | LV |
| 6 | OUTN | LV |
| 7 | OUTP | LV |
| 8 | VDD2, 3.3 or 5V | LV |

**Important:** AMC1301 input full-scale is ±250 mV, *not* an HV-tolerant input. Use an appropriately designed HV divider, protective parts, adequate voltage rating per resistor, and check the ~18 kΩ input impedance and bias-current effects. An isolated power source and an independent GND1 are needed for each HV domain (three phase-neutral and DC bus). **Do not bridge GND1 to GND2 with copper, planes, traces or 3D component.** Respect 9.1 mm nominal package clearance/creepage, but board-level pollution/coating/insulation coordination requires a separate review. Include local power bypass at both supply pairs. For ±U–N bipolar channels the divider and common-mode constraints need separate calculation.

Manufacturer documentation: https://www.ti.com/lit/ds/symlink/amc1301.pdf (Figure 5-1, DWV0008A package outline and land pattern).

## Remote 10k NTC on JST PH (2.0mm pitch)

- **PCB symbol:** `MaxStriX324:NTC_10K_JST_PH_2`.
- **Stock KiCad footprint:** `Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical`. Standard KiCad footprint has its own official KiCad 3D model.
- **Board header actual part:** JST `B2B-PH-K-S(LF)(SN)`, 2 pins vertical (through-hole).
- **Cable housing:** `PHR-2` (mates with header), with two `SPH-002T-P0.5S` contacts when selected wire gauge is within terminal specification.
- **Optional documentation-only symbol for physical probe**: `MaxStriX324:NTC_10K_Remote` (excluded from PCB and board BOM; no footprint).

Pin 1 `NTC_SENSE`, pin 2 `NTC_RETURN` / GNDA (current reference; make chosen ground nets explicit on PCB). At the board side, add a 10 kΩ 1% pull-up to +3.3VA at pin 1, filtered ADC path, cable ESD protection and short/open diagnostics as appropriate. Keep analog return paths under control. Suggested bulk board components: `R_pullup=10k E24`, `R_series=1k E24`, `C_ADC=100nF E24`. Choose exact values after ADC sampling design and grounding decisions.

### Two valid probe types

| Manufacturer reference | Typical orderable version | R25 | R tolerance | B25/100 |
|---|---|---|---|---|
| EPCOS/TDK B57045-K 103-K | `B57045K0103K000` | 10 kΩ | ±10% | 4300 K |
| EPCOS/TDK B57703-M 103-G | `B57703M0103G040` | 10 kΩ | ±2% | 3988 K |

Firmware calibration **must select different R(T) curve for the installed sensor**; these probes are not measurement-identical merely because both are 10k at 25°C. Make each sensor connector clearly labelled TEMP_1 / TEMP_2 / TEMP_3. Verify mounting, insulation to energized IGBT terminals, wire length and local EMC before production.

JST PH official: https://www.jst.com/wp-content/uploads/2025/06/ePH.pdf

TI datasheet package and TDK probe datasheets should be checked for updated revisions before manufacturing.
