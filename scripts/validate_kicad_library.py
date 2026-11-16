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
        r'\\(name\\s+"([^"]+)"[^\\n]*\\n\\s*\\(number\\s+"(\\d+)"', tl431)]
    if dict(tl431pins) != {1: "CATHODE", 2: "REF", 3: "ANODE"} or len(tl431pins) != 3:
        raise ValueError(f"TL431AIDBZR pinout does not match TI DBZ: {tl431pins}")
    tl431fp = PRETTY / "TL431AIDBZR_SOT23_DBZ.kicad_mod"
    fpcontent = tl431fp.read_text(encoding="utf-8")
    balanced_sexpr(fpcontent, tl431fp)
    padpositions = [(int(n), float(x), float(y)) for n, x, y in re.findall(
        r'\\(pad\s+"(\\d+)"\s+smd\s+roundrect\s+\\(at\s+([-\\d.]+)\s+([-\\d.]+)\\)', fpcontent)]
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

    print("PASS: Static KiCad library format and pin/pad checks")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
