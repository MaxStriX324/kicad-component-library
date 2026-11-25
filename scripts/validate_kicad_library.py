#!/usr/bin/env python3
"""Static integrity validation for MaxStriX324 KiCad libraries.
This complements, but does not replace, parsing with native kicad-cli.
No third-party Python modules are required.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = ROOT / "MaxStriX324.kicad_sym"
PRETTY = ROOT / "MaxStriX324.pretty"
ALLOWED_FILL = {"none", "outline", "background", "color", "hatch",
                "reverse_hatch", "cross_hatch"}

def balanced_sexpr(text, filename):
    depth = 0
    quoted = False
    escaped = False
    for ch in text:
        if quoted:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
            continue
        if ch == '"':
            quoted = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"{filename}: unexpected closing parenthesis")
    if depth != 0 or quoted:
        raise ValueError(f"{filename}: unterminated S-expression or string")

def symbol_block(text, symbol_name):
    pattern = '(symbol "' + symbol_name + '"'
    start = text.find(pattern)
    if start == -1:
        raise ValueError(f"Missing symbol {symbol_name}")
    depth, quoted, escaped = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
            continue
        if ch == '"':
            quoted = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError(f"Unclosed symbol {symbol_name}")

def main():
    content = SYMBOLS.read_text(encoding="utf-8")
    if not content.startswith("(kicad_symbol_lib "):
        raise ValueError("Symbol library is missing the KiCad header")
    balanced_sexpr(content, SYMBOLS)
    fills = re.findall(r'\(fill\s+\(type\s+([\w-]+)\)', content)
    bad = [fill for fill in fills if fill not in ALLOWED_FILL]
    if bad:
        raise ValueError(f"Unsupported symbol fill modes: {bad}")

    for name in ("UCC21750", "EC3503_Flyback_4CT_16P_DRAFT"):
        block = symbol_block(content, name)
        pins = [int(n) for n in re.findall(r'\(number\s+"(\d+)"', block)]
        if sorted(pins) != list(range(1, 17)):
            raise ValueError(f"{name}: expected pins numbered 1..16 exactly once, got {pins}")
        print(f"PASS symbol {name}: 16 numbered pins")

    for name in ("UCC21750_SOIC16W_P1.27mm", "EC3503_16P_THT"):
        path = PRETTY / (name + ".kicad_mod")
        footprint = path.read_text(encoding="utf-8")
        balanced_sexpr(footprint, path)
        pads = [int(n) for n in re.findall(r'\(pad\s+"(\d+)"', footprint)]
        if sorted(pads) != list(range(1, 17)):
            raise ValueError(f"{name}: expected pads numbered 1..16 exactly once, got {pads}")
        print(f"PASS footprint {name}: 16 numbered pads")

    # TI TL431AIDBZR DBZ: verify against TI TL431 datasheet, section 5.
    # TL432 swaps pins 1 and 2, so an incorrect mapping is a functional defect.
    tl431 = symbol_block(content, "TL431AIDBZR")
    tl431pins = [(int(n), name) for name, n in re.findall(
        r'\(name\s+"([^"]+)"[^\n]*\n\s*\(number\s+"(\d+)"', tl431)]
    if dict(tl431pins) != {1: "CATHODE", 2: "REF", 3: "ANODE"} or len(tl431pins) != 3:
        raise ValueError(f"TL431AIDBZR pinout does not match TI DBZ: {tl431pins}")
    tl431fp = PRETTY / "TL431AIDBZR_SOT23_DBZ.kicad_mod"
    fpcontent = tl431fp.read_text(encoding="utf-8")
    balanced_sexpr(fpcontent, tl431fp)
    padpositions = [(int(n), float(x), float(y)) for n, x, y in re.findall(
        r'\(pad\s+"(\d+)"\s+smd\s+roundrect\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', fpcontent)]
    if padpositions != [(1, -1.05, -0.95), (2, -1.05, 0.95), (3, 1.05, 0.0)]:
        raise ValueError(f"TL431AIDBZR pad positions inconsistent with TI top view: {padpositions}")
    if "(size 1.30 0.60)" not in fpcontent:
        raise ValueError("TL431AIDBZR footprint lacks TI DBZ pad dimensions")
    if 'MaxStriX324.3dshapes/TL431AIDBZR_SOT23_DBZ.wrl' not in fpcontent:
        raise ValueError("TL431AIDBZR footprint missing linked 3D model")
    vrml = ROOT / "MaxStriX324.3dshapes" / "TL431AIDBZR_SOT23_DBZ.wrl"
    if not vrml.is_file() or not vrml.read_text(encoding="utf-8").startswith("#VRML V2.0 utf8"):
        raise ValueError("TL431AIDBZR linked VRML model is missing or invalid")
    print("PASS TL431AIDBZR: TI DBZ 1=K 2=REF 3=A, pads and linked VRML")

    transformer = symbol_block(content, "EC3503_Flyback_4CT_16P_DRAFT")
    assigned = dict((int(n), name) for name, n in re.findall(
        r'\(name\s+"([A-Z_]+)"\s+\(effects[^\n]*\)\s+\(number\s+"(\d+)"', transformer))
    expected = {1:'P_START', 2:'P_END', 3:'AUX_END', 4:'AUX_START',
                5:'U_END', 6:'U_CT', 7:'U_START', 8:'V_END', 9:'V_CT',
                10:'V_START', 11:'W_END', 12:'W_CT', 13:'W_START',
                14:'LOW_END', 15:'LOW_CT', 16:'LOW_START'}
    if assigned != expected:
        raise ValueError(f'Transformer winding START/END map invalid: {assigned}')
    dots = {(float(x), float(y)) for x,y in re.findall(
        r'\(circle\s+\(center\s+(-?[\d.]+)\s+(-?[\d.]+)\)', transformer)}
    expected_dots = {(-12.7,28.9), (-12.7,-28.9), (12.7,21.9),
                     (12.7,1.58), (12.7,-18.74), (12.7,-39.06)}
    if dots != expected_dots:
        raise ValueError(f'Transformer winding polarity dots invalid: {dots}')
    print('PASS: Flyback START/END and polarity-dot convention')

    lf = symbol_block(content, "LF1005S_CableExit")
    lf_pins = [int(n) for n in re.findall(r'\(number\s+"(\d+)"', lf)]
    if sorted(lf_pins) != [1, 2, 3, 4]:
        raise ValueError(f"LF1005-S cable symbol pins incorrect: {lf_pins}")
    if 'MaxStriX324:LF1005S_Cable_3x0.5_Shield_THT_Relief' not in lf:
        raise ValueError("LF1005-S cable symbol footprint reference incorrect")
    lf_fp = PRETTY / "LF1005S_Cable_3x0.5_Shield_THT_Relief.kicad_mod"
    lf_fptxt = lf_fp.read_text(encoding="utf-8")
    balanced_sexpr(lf_fptxt, lf_fp)
    lf_pads = re.findall(r'\(pad\s+"(\d+)"\s+thru_hole', lf_fptxt)
    if sorted(int(n) for n in lf_pads) != [1, 2, 3, 4]:
        raise ValueError(f"LF1005-S cable footprint pads incorrect: {lf_pads}")
    if len(re.findall(r'\(pad\s+""\s+np_thru_hole', lf_fptxt)) != 2:
        raise ValueError("LF1005-S cable strain relief needs two NPTH holes")
    print("PASS LF1005-S cable symbol/footprint: 4 pads + 2 NPTH")

    bav = symbol_block(content, "BAV199_215")
    bav_pins = [(int(n), label) for label, n in re.findall(
        r'\(name\s+"([^"]+)"[^\n]*\n\s*\(number\s+"(\d+)"', bav)]
    if bav_pins != [(1, "A1"), (2, "K2"), (3, "K1/A2")]:
        raise ValueError(f"BAV199 pinout inconsistent with Nexperia datasheet: {bav_pins}")
    bav_fp = PRETTY / "BAV199_215_SOT23.kicad_mod"
    bav_text = bav_fp.read_text(encoding="utf-8")
    balanced_sexpr(bav_text, bav_fp)
    bav_pads = [(int(n), float(x), float(y)) for n,x,y in re.findall(
        r'\(pad\s+"(\d+)"\s+smd\s+roundrect\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', bav_text)]
    if bav_pads != [(1,-0.95,1.05),(2,0.95,1.05),(3,0.0,-1.05)]:
        raise ValueError(f"BAV199 pads inconsistent with Nexperia orientation: {bav_pads}")
    if "BAV199_215_SOT23.wrl" not in bav_text:
        raise ValueError("Missing 3D model link on BAV199 footprint")
    model = ROOT / "MaxStriX324.3dshapes" / "BAV199_215_SOT23.wrl"
    if not model.is_file() or not model.read_text(encoding="utf-8").startswith("#VRML V2.0 utf8"):
        raise ValueError("BAV199 3D WRL missing or invalid")
    print("PASS BAV199: 3 series diode pins, footprint pads, linked WRL")
    # TI AMC1301 wide SOIC-8 DWV: manufacturer pinout + verified DWV land pads.
    amc = symbol_block(content, "AMC1301DWV")
    amc_pinmap = [(int(num), name) for name, num in re.findall(
        r'\(name\s+"([^"]+)"[^\n]*\n\s*\(number\s+"(\d+)"', amc)]
    if dict(amc_pinmap) != {1: "VDD1", 2: "INP", 3: "INN", 4: "GND1",
                            5: "GND2", 6: "OUTN", 7: "OUTP", 8: "VDD2"} or len(amc_pinmap) != 8:
        raise ValueError(f"AMC1301 incorrect DWV pinout: {amc_pinmap}")
    if "MaxStriX324:AMC1301_DWV_SOIC8" not in amc:
        raise ValueError("AMC1301 symbol missing custom wide SOIC8 footprint")
    amc_fp = PRETTY / "AMC1301_DWV_SOIC8.kicad_mod"
    amc_txt = amc_fp.read_text(encoding="utf-8")
    balanced_sexpr(amc_txt, amc_fp)
    matches = [(int(n), float(x), float(y)) for n,x,y in re.findall(
        r'\(pad\s+"(\d+)"\s+smd\s+roundrect\s+\(at\s+([\-\d.]+)\s+([\-\d.]+)\)', amc_txt)]
    expected_coords = {1: (-5.45,-1.905), 2: (-5.45,-0.635),
                       3: (-5.45,0.635), 4: (-5.45,1.905),
                       5: (5.45,1.905), 6: (5.45,0.635),
                       7: (5.45,-0.635), 8: (5.45,-1.905)}
    if len(matches) != 8 or any((x,y) != expected_coords.get(n) for n,x,y in matches):
        raise ValueError(f"AMC1301 DWV footprint pad geometry inconsistent: {matches}")
    if "(size 1.8 0.6)" not in amc_txt or "AMC1301_DWV_SOIC8.step" not in amc_txt:
        raise ValueError("AMC1301 missing TI pad sizes or linked WRL 3D")
    model = ROOT / "MaxStriX324.3dshapes" / "AMC1301_DWV_SOIC8.step"
    if not model.is_file() or model.stat().st_size < 1000:
        raise ValueError("AMC1301 linked STEP missing or invalid")
    for name in ("NTC_10K_JST_PH_2", "NTC_10K_Remote"):
        ntc = symbol_block(content, name)
        ntc_pins = [int(p) for p in re.findall(r'\(number\s+"(\d+)"', ntc)]
        if sorted(ntc_pins) != [1, 2]:
            raise ValueError(f"NTC connector/probe pinout bad: {name} {ntc_pins}")
    if "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical" not in symbol_block(content,"NTC_10K_JST_PH_2"):
        raise ValueError("Remote NTC symbol is not linked to stock KiCad JST PH footprint")
    if "(on_board no)" not in symbol_block(content, "NTC_10K_Remote"):
        raise ValueError("Remote NTC documentation symbol must not appear on PCB")
    print("PASS AMC1301 DWV reinforced package, 8 pin map/pads, WRL and NTC JST PH links")

    pesd = symbol_block(content, "PESD5V0S1BA_115")
    pesd_pins = [(int(n), label) for label, n in re.findall(
        r'\(name\s+"([^"]+)"[^\n]*\n\s*\(number\s+"(\d+)"', pesd)]
    if pesd_pins != [(1, "K1"), (2, "K2")]:
        raise ValueError(f"PESD5V0S1BA,115 pinout wrong: {pesd_pins}")
    if "MaxStriX324:PESD5V0S1BA_115_SOD323" not in pesd:
        raise ValueError("PESD5V0S1BA symbol/footprint binding lost")
    pesd_fp = PRETTY / "PESD5V0S1BA_115_SOD323.kicad_mod"
    pesd_txt = pesd_fp.read_text(encoding="utf-8")
    balanced_sexpr(pesd_txt, pesd_fp)
    pesd_pads = [(int(n),float(x),float(y)) for n,x,y in re.findall(
        r'\(pad\s+"(\d+)"\s+smd\s+roundrect\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)', pesd_txt)]
    if pesd_pads != [(1,-1.1,0.0),(2,1.1,0.0)] or pesd_txt.count("(size 0.6 0.6)") != 2:
        raise ValueError(f"PESD5V0S1BA reflow pads do not match datasheet: {pesd_pads}")
    if "PESD5V0S1BA_115_SOD323.step" not in pesd_txt:
        raise ValueError("PESD5V0S1BA missing linked WRL model")
    pesd_step = ROOT / "MaxStriX324.3dshapes" / "PESD5V0S1BA_115_SOD323.step"
    if not pesd_step.is_file() or pesd_step.stat().st_size < 1000:
        raise ValueError("PESD5V0S1BA linked STEP model missing")
    print("PASS PESD5V0S1BA,115: Nexperia pinout, SOD323 reflow pads, linked 3D")

    # AVTOSTAR: check every new footprint, symbol/footprint binding and RF rule area.
    av_layers = ["F.Cu"] + [f"In{i}.Cu" for i in range(1, 31)] + ["B.Cu"]
    for kind in ("SMD", "THT"):
        name = "AVTOSTAR_ESP12F_Debug_Module_" + kind
        path = PRETTY / (name + ".kicad_mod")
        fp = path.read_text(encoding="utf-8")
        balanced_sexpr(fp, path)
        pins = [int(n) for n in re.findall(r'\(number\s+"(\d+)"', symbol_block(content, name))]
        pads = [int(n) for n in re.findall(r'\(pad\s+"(\d+)"', fp)]
        if sorted(pins) != list(range(1, 13)) or sorted(pads) != list(range(1, 13)):
            raise ValueError(f"{name}: invalid pin/pad numbering")
        if f'MaxStriX324:{name}' not in symbol_block(content, name):
            raise ValueError(f"{name}: missing footprint binding")
        zone = fp.split("(zone ", 1)[1].split('\n  (pad ', 1)[0]
        expected_layers = "(layers " + " ".join(f'"{layer}"' for layer in av_layers) + ")"
        if expected_layers not in zone or "(net " in zone or "(net_name " in zone:
            raise ValueError(f"{name}: RF rule area requires explicit copper layers and no net")
        for rule in ("tracks", "vias", "pads", "copperpour", "footprints"):
            if f"({rule} not_allowed)" not in zone:
                raise ValueError(f"{name}: missing antenna restriction {rule}")
        if name + ".wrl" not in fp or not (ROOT / "MaxStriX324.3dshapes" / (name + ".wrl")).is_file():
            raise ValueError(f"{name}: missing model")
        print(f"PASS {name}: 12 pins/pads, local 32-layer antenna rule area and model")
    for suffix, expected_count in (("Castellated_PTH_0.8mm", 4), ("EdgeSMD_PTH_0.8mm", 3)):
        name = "AVTOSTAR_ESP12F_Module_" + suffix
        path = PRETTY / (name + ".kicad_mod")
        fp = path.read_text(encoding="utf-8")
        balanced_sexpr(fp, path)
        pads = [int(n) for n in re.findall(r'\(pad\s+"(\d+)"', fp)]
        if sorted(pads) != sorted(list(range(1, 13)) * expected_count):
            raise ValueError(f"{name}: incorrect repeated pad numbering")
        if fp.count("(drill 0.8)") != 12:
            raise ValueError(f"{name}: expected 12 internal holes")
        print(f"PASS {name}: 12 contacts with SMD/PTH pads")

    print("PASS: Static KiCad library format and pin/pad checks")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
