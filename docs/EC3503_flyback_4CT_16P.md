# EC3503 flyback transformer for inverter gate drivers (DRAFT)

Symbol: `MaxStriX324:EC3503_Flyback_4CT_16P_DRAFT`
Footprint: `MaxStriX324:EC3503_16P_THT`

## Intended electrical structure

One flyback supply for **six UCC21750** drivers on a three-leg driver board:

- 1 primary winding (2 terminals) driven by a UC3843 / UC2843 controller.
- 1 auxiliary winding (2 terminals) to power the controller.
- 3 galvanically separate upper-driver secondary windings (each with a center tap).
- 1 secondary winding for a shared supply of the three lower drivers (center tap).

The AC secondary winding **must not** be labeled as directly producing regulated +15 V and -8 V: rectifiers, capacitors, and regulators generate the respective output rails.

Total pins = 2 + 2 + 4 × 3 = **16**.

## Preliminary symbol / footprint pin mapping

| Pins | Winding | Meanings |
|---|---|---|
| 1, 2 | Primary (PRI) | P_START, P_END |
| 3, 4 | Auxiliary (AUX) | AUX_START, AUX_END |
| 5, 6, 7 | Upper U | U_START, U_CT, U_END |
| 8, 9, 10 | Upper V | V_START, V_CT, V_END |
| 11, 12, 13 | Upper W | W_START, W_CT, W_END |
| 14, 15, 16 | Lower common | LOW_START, LOW_CT, LOW_END |

**This is NOT the manufacturer's pinout or a manufacturing-approved bobbin design.** The pin numbers refer only to the provisional EC3503 footprint. Turns, winding directions, dot polarity, insulation, and start/finish assignments remain to be engineered. The symbol and footprint now mark proposed starts with polarity dots. These dots are **designer conventions, not a verified winding orientation**.

## Pad markings and orientation

On the footprint, `START`/`END` are abbreviated `S`/`E` in the silkscreen pad-side text (e.g. `U.START`, `U.END`) and the centre tap is `CT`. Filled dots mark pins **1, 3, 5, 8, 11, 14**. Full terminal names appear on `F.Fab`.

The real PCB top view is provisional: pins 1–8 on the left (top-to-bottom), pins 9–16 on the right (bottom-to-top). The exact physical bobbin manufacturer's pin numbering must be checked. No drill sizes, pad centres, or electrical pad numbers were changed by this revision.

The silkscreen labels sit just outside the body and the footprint courtyard is expanded horizontally to 56 mm (±28 mm). Confirm the added footprint space in the PCB layout.

## CRITICAL physical-isolation concern

The currently drawn EC3503 footprint has **two rows of eight pads** (5.0 mm longitudinal pitch). With the draft pinout above:

- Primary and auxiliary contacts 1–4 share the same footprint side with secondary U contacts 5–7.
- Secondary V contacts 8–10 span both opposite footprint sides (pad 8 on one row, pads 9–10 on the other).

This means **the proposed 16-pad allocation must not be considered electrically isolated**, and it is unsuitable as a fabrication-ready pin assignment. A 16-pad count alone does not prove that four galvanically separate three-wire secondaries plus the primary and auxiliary can be safely terminated.

For a buildable transformer, review a larger bobbin with separated pin banks, isolated flying leads, fewer secondary wires (e.g. 2-terminal isolated windings with a locally generated negative bias), or separate transformers.

Do not finalize PCB routing, creepage/clearance, or the transformer build sheet using this tentative pinout. Check the actual bobbin, operating peak voltages, fault transients, insulation class, and applicable safety rules.

## More power-circuit considerations

- Each driver's VDD and VEE supply must be referred to that driver's actual **Kelvin emitter COM**, not logic GND.
- The three upper driver grounds must remain independent and isolated. Shared lower supply is possible only when its reference to DC- / Kelvin emitters is deliberate.
- A common lower secondary still needs local gate-drive bypass capacitors at each UCC21750.
- The primary-to-secondary insulation must be tested independently from the PCB footprint dimensions.
- The center taps require correctly phased rectification and proper turns ratios; the symbol does not imply the required winding calculation is complete.

## Next steps

1. Decide the transformer connection method and insulating construction.
2. Fix the manufacturer's **real** contact orientation / pin numbering on the bobbin.
3. Confirm all winding directions and rectify +15 V, 0 V and -8 V.
4. Update the symbol and footprint together, removing the `_DRAFT` suffix only when verified.
