# MaxStriX324 KiCad Component Library

Reusable KiCad symbols, footprints and 3D models. The library is stored on GitHub so it can be restored after reinstalling Windows.

## Library structure

- `MaxStriX324.kicad_sym` — custom schematic symbols.
- `MaxStriX324.pretty/` — custom PCB footprints.
- `MaxStriX324.3dshapes/` — local 3D models.
- `install.bat` — register the library in KiCad on Windows.
- `update.bat` — fetch new components.

## Install

```powershell
git clone https://github.com/MaxStriX324/kicad-component-library.git
cd kicad-component-library
.\install.bat
```

Restart KiCad after installation. Registered library nickname: `MaxStriX324`.

## Initial components

- EC3503: 16-pin THT transformer bobbin; check the manufacturer's mechanical drawing and **verify pin numbering** before fabrication.
- UCC21750: TI isolated IGBT gate driver. Match the footprint and the exact ordered package to the TI datasheet.

**Engineering warning:** All footprints and 3D shapes require physical verification; a 3D model does not prove creepage or clearance suitability for high voltage.

## Third-party CAD files

Do not upload third-party CAD models without checking redistribution permissions. Use original vendor sources where redistribution is restricted.
