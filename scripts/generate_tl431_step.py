#!/usr/bin/env python3
"""Generate approximate STEP (not an official TI model) for TL431AIDBZR DBZ SOT-23-3.
Requires: pip install cadquery
"""
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MaxStriX324.3dshapes" / "TL431AIDBZR_SOT23_DBZ.step"

body = cq.Workplane("XY").box(1.30, 2.90, 0.95, centered=(True, True, False)).translate((0, 0, 0.15)).val()
leads = []
for x, y in ((-1.0, -0.95), (-1.0, 0.95), (1.0, 0.0)):
    lead = cq.Workplane("XY").box(0.72, 0.44, 0.18, centered=(True, True, False)).translate((x, y, 0.0)).val()
    leads.append(lead)
index = cq.Workplane("XY").circle(0.085).extrude(0.006).translate((-0.44, -1.13, 1.095)).val()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
cq.exporters.export(cq.Compound.makeCompound([body, *leads, index]), str(OUTPUT), exportType="STEP")
print(OUTPUT)
