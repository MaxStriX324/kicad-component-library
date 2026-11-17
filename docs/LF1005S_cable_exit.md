# LF1005-S cable exit

For the **Measurement_board_v_1** measurement PCB. The shielded cable is soldered directly to PCB pads, while a mating connector is fitted at the **LEM LF1005-S sensor**. The footprint is *not* a PCB-mounted connector.

- Symbol: `MaxStriX324:LF1005S_CableExit`
- Footprint: `MaxStriX324:LF1005S_Cable_3x0.5_Shield_THT_Relief`
- Suggested cable: LAPP UNITRONIC LiYCY 3×0.5 mm², example part number 0034603; verify cable diameter and current availability.

| Pad | Net | Remote connection |
|---|---|---|
| 1 | M | Current-output terminal M |
| 2 | +24V_SENS | Sensor + |
| 3 | -24V_SENS | Sensor − |
| 4 | CHASSIS/SHIELD | Cable braid **at controller only**; not connected to sensor |

Pads 1–3: plated through-hole drill 1.5 mm, copper diameter 3.2 mm; pitch 4.5 mm. Pad 4: plated through-hole drill 1.3 mm, copper diameter 2.8 mm. Mechanical strain relief: two **non-plated** 3.2 mm holes at 13 mm pitch for a cable tie. The assumed cable outer diameter is ~5.9 mm.

**Electrical:** LF1005-S output M is a **current-output** terminal. Place burden resistors next to the cable entry and filter voltage downstream of the burden. Do not add an arbitrary series inductance in the M line. Keep cable away from phase terminals, DC bus conductors and gate lines.

**Mechanical:** confirm wire gauge versus hole diameter, cable jacket OD, tie size, board-edge clearance and realistic cable-bend radius using a sample **before PCB manufacture**. The board edge is not defined by this footprint, and there is no 3D model. The sensor-end mating connector needs confirmation from the actual sensor revision.

KiCad native CLI validation and mechanical fit have not yet been performed.
