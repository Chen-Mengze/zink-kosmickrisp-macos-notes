#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""packscan - 光影包 GS 依赖扫描器（Windows 可跑，仅标准库）

回答笔记里那个悬着的问题：这个 pack 里的 geometryShader 是硬依赖还是软依赖？

判定规则：
  HARD    存在独立的 geometry stage 文件（.gsh/.geom）。Iris/OptiFine 会无条件编译它。
  SOFT    GS 代码只出现在 #ifdef 之类的预处理块里，且没有独立 stage 文件。
  SUSPECT 在 .vsh/.fsh/.glsl 里出现了未加保护的 GS 内建，但没有 stage 文件（写法可疑）。
  NONE    没发现 GS。

用法：
    python packscan.py path/to/pack_dir
    python packscan.py path/to/pack.zip --json
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SHADER_SUFFIX = {
    ".vsh", ".fsh", ".gsh", ".csh", ".glsl", ".inc",
    ".vert", ".frag", ".geom", ".comp", ".tesc", ".tese",
}
STAGE_SUFFIX = {".gsh", ".geom"}
COMPUTE_SUFFIX = {".csh", ".comp"}

VERSION_RE = re.compile(r"^\s*#version\s+(\d+)", re.MULTILINE)
GUARD_RE = re.compile(r"^\s*#\s*(ifdef|ifndef|if)\b(.*)$")
ENDIF_RE = re.compile(r"^\s*#\s*endif\b")
GS_RE = re.compile(r"\b(EmitVertex|EndPrimitive|gl_PrimitiveIDIn|gl_in)\b")
XFB_RE = re.compile(r"\b(gl_BeginTransformFeedback|gl_TransformFeedbackVaryings|TransformFeedbackVaryings)\b")
SSBO_RE = re.compile(r"\blayout\s*\(\s*(?:std430|std140)[^)]*\)\s*(?:readonly\s+|writeonly\s+)?buffer\b")
COMPUTE_RE = re.compile(r"\blocal_size_[xyz]\s*=")


def iter_files(path):
    p = Path(path)
    if p.is_dir():
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in SHADER_SUFFIX and "__MACOSX" not in f.parts:
                yield f.relative_to(p).as_posix(), f.read_text(encoding="utf-8", errors="ignore")
    elif zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for name in sorted(z.namelist()):
                if name.endswith("/") or "__MACOSX" in name:
                    continue
                if Path(name).suffix.lower() in SHADER_SUFFIX:
                    yield name, z.read(name).decode("utf-8", "ignore")
    else:
        raise SystemExit(f"不是目录也不是 zip: {path}")


def scan_pack(path):
    versions, gs_stage, gs_guarded, gs_bare = [], [], [], []
    xfb, ssbo, compute = [], [], []

    for name, text in iter_files(path):
        suffix = Path(name).suffix.lower()

        for m in VERSION_RE.finditer(text):
            versions.append((int(m.group(1)), name, text[:m.start()].count("\n") + 1))

        if suffix in COMPUTE_SUFFIX:
            compute.append(name)
        elif COMPUTE_RE.search(text):
            compute.append(name)

        if SSBO_RE.search(text):
            ssbo.append(name)

        for i, line in enumerate(text.splitlines(), 1):
            if XFB_RE.search(line):
                xfb.append((name, i, line.strip()))

        guard = []
        has_main = re.search(r"\bvoid\s+main\s*\(", text) is not None
        for i, line in enumerate(text.splitlines(), 1):
            if GUARD_RE.match(line):
                guard.append(GUARD_RE.match(line).group(0).strip())
            elif ENDIF_RE.match(line):
                if guard:
                    guard.pop()
            if GS_RE.search(line):
                hit = (name, i, line.strip(), guard[-1] if guard else "")
                (gs_guarded if guard else gs_bare).append(hit)

        if suffix in STAGE_SUFFIX and has_main:
            gs_stage.append(name)

    if gs_stage:
        verdict = "HARD"
        reason = "存在独立 geometry stage 文件，Iris/OptiFine 会无条件编译"
    elif gs_guarded and not gs_bare:
        verdict = "SOFT"
        reason = "GS 内建只出现在预处理块内，无独立 stage 文件"
    elif gs_bare:
        verdict = "SUSPECT"
        reason = "非 stage 文件里出现未加保护的 GS 内建，写法需要作者确认"
    else:
        verdict = "NONE"
        reason = "未发现 geometry stage"

    return {
        "pack": str(path),
        "verdict": verdict,
        "reason": reason,
        "max_version": max((v[0] for v in versions), default=None),
        "gs_stage_files": gs_stage,
        "gs_guarded": gs_guarded[:5],
        "gs_bare": gs_bare[:5],
        "xfb": xfb[:5],
        "compute_files": sorted(set(compute)),
        "ssbo_files": sorted(set(ssbo)),
    }


def render(r, as_json):
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"\n=== {r['pack']}")
    print(f"  verdict        {r['verdict']}  ({r['reason']})")
    print(f"  #version max   {r['max_version'] if r['max_version'] else '?'}")
    print(f"  gs stage       {len(r['gs_stage_files'])} file(s)")
    for f in r["gs_stage_files"]:
        print(f"                 - {f}")
    if r["gs_guarded"]:
        print(f"  gs guarded     {len(r['gs_guarded'])}+ hit(s)")
        for name, line, text, cond in r["gs_guarded"]:
            print(f"                 {name}:{line}  under {cond}")
    if r["gs_bare"]:
        print(f"  gs unprotected {len(r['gs_bare'])}+ hit(s)")
        for name, line, text, _ in r["gs_bare"]:
            print(f"                 {name}:{line}  {text[:60]}")
    print(f"  xfb            {'yes' if r['xfb'] else 'no'}")
    for name, line, text in r["xfb"]:
        print(f"                 {name}:{line}  {text[:60]}")
    print(f"  compute        {len(r['compute_files'])} file(s)")
    print(f"  ssbo           {'yes' if r['ssbo_files'] else 'no'}")


def main():
    ap = argparse.ArgumentParser(prog="packscan")
    ap.add_argument("packs", nargs="+")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    for p in args.packs:
        render(scan_pack(p), args.json)


if __name__ == "__main__":
    main()
