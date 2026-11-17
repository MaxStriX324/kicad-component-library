#!/usr/bin/env python3
"""Approximate BAV199,215 SOT23 STEP from original parametric geometry (not manufacturer CAD)."""
from pathlib import Path
import cadquery as cq
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MaxStriX324.3dshapes" / "BAV199_215_SOT23.step"
body = cq.Workplane("XY").box(2.9, 1.3, 0.9, centered=(True, True, False)).translate((0, 0, 0.18)).val()
leads = [
    cq.Workplane("XY").box(0.45, 0.8, 0.16, centered=(True, True, False)).translate((x, y, 0)).val()
    for x, y in ((-0.95, 1.05), (0.95, 1.05), (0, -1.05))
]
OUT.parent.mkdir(parents=True, exist_ok=True)
cq.exporters.export(cq.Compound.makeCompound([body, *leads]), str(OUT), exportType="STEP")
assert len(cq.importers.importStep(str(OUT)).solids().vals()) == 4
print(OUT)
