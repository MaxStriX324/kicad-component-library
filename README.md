# MaxStriX324 KiCad Component Library

Public reusable KiCad symbols, footprints and approximate 3D references.

## Files

- `MaxStriX324.kicad_sym` — UCC21750 symbol (pins 1–16).
- `MaxStriX324.pretty/UCC21750_SOIC16W_P1.27mm.kicad_mod` — wide SOIC-16 footprint.
- `MaxStriX324.pretty/EC3503_16P_THT.kicad_mod` — EC3503 16-pin transformer bobbin footprint.
- `MaxStriX324.3dshapes/EC3503_16P_THT.wrl` — **approximate** visual model; STEP to be added after separate verification.
- `install.bat`, `update.bat` — Windows installation and update.

## Windows install

1. Install Git for Windows and KiCad (8–10); launch KiCad once.
2. Run:

```powershell
git clone https://github.com/MaxStriX324/kicad-component-library.git
cd kicad-component-library
.\install.bat
```

3. Restart KiCad. Library nickname: `MaxStriX324`.

The installer sets the user environment variable `MAXSTRIX_KICAD_LIB` and adds the library to the newest installed KiCad global symbol and footprint tables, backing each up to `.bak` before a modification.

The `update.bat` script uses `git pull --ff-only`.

## Notes

**Verify before PCB fabrication:** EC3503 pad numbering is provisional (1–8 on left, 9–16 on right). The approximate 3D model is NOT an official mechanical CAD model. UCC21750 pads and schematic pin mapping should be cross-checked with the exact TI ordering code and datasheet.

For imported third-party component files, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

MIT license covers the newly authored code, footprints, and schematic symbol in this repository, not vendor documentation.
