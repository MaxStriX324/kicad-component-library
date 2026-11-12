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
