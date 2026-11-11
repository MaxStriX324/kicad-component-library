"""Generate approximate EC3503 and UCC21750 STEP models (not manufacturer CAD).
Requires: pip install cadquery
"""
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MaxStriX324.3dshapes"
OUT.mkdir(exist_ok=True)

def ec3503():
    lower = cq.Workplane("XY").box(42.8, 39.8, 3, centered=(True, True, False))
    upper = cq.Workplane("XY").box(42.8, 39.8, 3, centered=(True, True, False)).translate((0, 0, 25.8))
    spool = cq.Workplane("XY").box(29, 30, 22.8, centered=(True, True, False)).translate((0, 0, 3))
    body = lower.union(upper).union(spool)
    bore = cq.Workplane("XY").box(17, 17, 36, centered=(True, True, False)).translate((0, 0, -2))
    body = body.cut(bore)
    pins = []
    for i in range(16):
        x = -17.5 if i < 8 else 17.5
        y = -17.5 + i * 5 if i < 8 else 17.5 - (i - 8) * 5
        pins.append(cq.Workplane("XY").box(1, 1, 7, centered=(True, True, False)).translate((x, y, -4)).val())
    cq.exporters.export(cq.Compound.makeCompound([body.val()] + pins), str(OUT / "EC3503_16P_THT.step"))

def ucc21750():
    body = cq.Workplane("XY").box(7.5, 10.3, 2.65, centered=(True, True, False)).translate((0, 0, 0.30))
    pins = []
    for x in (-4.64, 4.64):
        for i in range(8):
            y = -4.445 + i * 1.27
            pins.append(cq.Workplane("XY").box(2.06, 0.60, 0.25, centered=(True, True, False)).translate((x, y, 0)).val())
    cq.exporters.export(cq.Compound.makeCompound([body.val()] + pins), str(OUT / "UCC21750_SOIC16W_P1.27mm.step"))

def update_footprint_models():
    pretty = ROOT / "MaxStriX324.pretty"
    ec = pretty / "EC3503_16P_THT.kicad_mod"
    src = ec.read_text(encoding="utf-8")
    src = src.replace("EC3503_16P_THT.wrl", "EC3503_16P_THT.step")
    ec.write_text(src, encoding="utf-8")
    ucc = pretty / "UCC21750_SOIC16W_P1.27mm.kicad_mod"
    src = ucc.read_text(encoding="utf-8")
    mdl = '  (model "${MAXSTRIX_KICAD_LIB}/MaxStriX324.3dshapes/UCC21750_SOIC16W_P1.27mm.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'
    if "UCC21750_SOIC16W_P1.27mm.step" not in src:
        src = src.rstrip()[:-1] + mdl + ")\n"
        ucc.write_text(src, encoding="utf-8")

ec3503()
ucc21750()
for name in ("EC3503_16P_THT.step", "UCC21750_SOIC16W_P1.27mm.step"):
    path = OUT / name
    solids = cq.importers.importStep(str(path)).solids().vals()
    assert len(solids) == 17, (name, len(solids))
    print(f"Validated {path.name}: {len(solids)} solids, {path.stat().st_size} bytes")
update_footprint_models()
