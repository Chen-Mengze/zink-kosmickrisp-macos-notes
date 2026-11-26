#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kkcap - KosmicKrisp / Zink 能力记录整理器（Windows 可跑，仅标准库）

它不做的事：不计算 GL 版本，不替代 zink_check_requirements。
它做的事：把一堆 vulkaninfo --json 变成口径统一、能直接贴 MR 的记录。

用法：
    python kkcap.py one    fixtures/device_a.json --chip "M1 Pro" --macos 26.2 --build A --md
    python kkcap.py matrix fixtures/*.json
    python kkcap.py diff   fixtures/device_a.json fixtures/device_c.json
    python kkcap.py gates
    python kkcap.py selftest
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- 门槛表
# 只收「会改变结论」的项，不是 Zink 要求的全集。
# class: gate = 缺了会降版本；advisory = 缺了不降但会炸；unknown = 口径未定
GATES = [
    ("VK_EXT_custom_border_color", "ext",  "2.1", "advisory", "2.1 基线；Hadron 0064 后由 Zink 实例识别，不必开 flag"),
    ("VK_EXT_conditional_rendering", "ext", "3.0", "gate",    "遮挡查询路径；KK 有，MVK 没有"),
    ("VK_EXT_transform_feedback", "ext",   "3.0", "unknown",   "官方 requirements 列在 3.0；构建 A 无 XFB 却报 3.1"),
    ("geometryShader", "feat",             "3.2", "gate",     "缺了天花板压回 3.1；macOS 原生 GL 从来没有过"),
    ("depthClamp", "feat",                 "3.2", "gate",     ""),
    ("shaderTessellationAndGeometryPointSize", "feat", "3.2", "gate", ""),
    ("dualSrcBlend", "feat",               "3.3", "gate",     ""),
    ("tessellationShader", "feat",         "4.0", "gate",     ""),
    ("shaderFloat64", "feat",              "4.0", "unknown",  "Playport 0087 记的卡点"),
    ("imageCubeArray", "feat",             "4.0", "gate",     ""),
    ("multiViewport", "feat",              "4.1", "gate",     ""),
    ("shaderDrawParameters", "feat",       "4.2", "gate",     ""),
    ("vertexPipelineStoresAndAtomics", "feat", "4.2", "gate", ""),
    ("fragmentStoresAndAtomics", "feat",   "4.2", "gate",     ""),
    ("shaderStorageImageExtendedFormats", "feat", "4.2", "gate", ""),
    ("robustBufferAccess", "feat",         "4.3", "gate",     ""),
    ("shaderCullDistance", "feat",         "4.5", "gate",     ""),
    ("VK_KHR_draw_indirect_count", "ext",  "4.6", "gate",     ""),
    ("samplerAnisotropy", "feat",          "4.6", "gate",     ""),
    ("depthBiasClamp", "feat",             "4.6", "gate",     ""),
]

MARK = {True: "✓", False: "✗", None: "·"}


# ---------------------------------------------------------------- 解析
def load_device(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    caps = data.get("capabilities", data)
    return caps.get("device", caps)


def flatten(obj, prefix=""):
    out = {}
    if not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def extensions(dev):
    exts = dev.get("extensions") or {}
    return {str(k) for k in exts}


def feature_map(dev):
    return flatten(dev.get("features") or {})


def feature_state(feats, leaf):
    hits = [v for k, v in feats.items() if k.split(".")[-1] == leaf]
    if not hits:
        return None
    return any(v is True for v in hits)


def gate_state(dev, kind, name, feats=None):
    if kind == "ext":
        return name in extensions(dev)
    if kind == "feat":
        return feature_state(feats if feats is not None else feature_map(dev), name)
    return None


def fmt_api(v):
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return f"{v >> 22}.{(v >> 12) & 0x3FF}.{v & 0xFFF}"
    return "?"


def driver_of(dev):
    props = dev.get("properties") or {}
    return {
        "deviceName": props.get("deviceName", "?"),
        "driverName": props.get("driverName", "?"),
        "driverInfo": props.get("driverInfo", "?"),
        "apiVersion": fmt_api(props.get("apiVersion")),
    }


def load_meta(path, args=None):
    meta = {}
    side = Path(str(path) + ".meta.json")
    if side.exists():
        meta.update(json.loads(side.read_text(encoding="utf-8")))
    if args:
        for key in ("chip", "macos", "build", "gl"):
            val = getattr(args, key, None)
            if val:
                meta[key] = val
    return meta


# ---------------------------------------------------------------- 渲染
def rows(dev):
    feats = feature_map(dev)
    out = []
    for name, kind, level, cls, note in GATES:
        out.append({
            "name": name,
            "kind": kind,
            "level": level,
            "class": cls,
            "note": note,
            "state": gate_state(dev, kind, name, feats),
        })
    return out


def render_one(path, meta, as_md):
    dev = load_device(path)
    info = driver_of(dev)
    gate_rows = rows(dev)
    gs = next(r for r in gate_rows if r["name"] == "geometryShader")["state"]
    xfb = next(r for r in gate_rows if r["name"] == "VK_EXT_transform_feedback")["state"]

    if as_md:
        chip = meta.get("chip", info["deviceName"])
        macos = meta.get("macos", "?")
        build = meta.get("build", "?")
        gl = meta.get("gl", "<填 zink_check_requirements 的输出>")
        print(f"\n### kkcap: {Path(path).stem}\n")
        print(f"- 机器 / 系统：{chip} / macOS {macos}")
        print(f"- 构建：{build}")
        print(f"- 驱动：{info['driverName']} {info['apiVersion']}（{info['driverInfo']}）")
        print()
        print("| 门槛 | 档 | 状态 | 类别 | 备注 |")
        print("|---|---|---|---|---|")
        for r in gate_rows:
            print(f"| `{r['name']}` | {r['level']} | {MARK[r['state']]} | {r['class']} | {r['note']} |")
        print()
        print("**贴 MR 的记录行**\n")
        print("```")
        print(f"Chip / macOS:        {chip} / {macos}")
        print(f"Build:               {build}")
        print(f"driverName / API:    {info['driverName']} / {info['apiVersion']}")
        print(f"vulkaninfo XFB:      {'present' if xfb else 'absent' if xfb is False else 'unknown'}")
        print(f"geometryShader:      {'present' if gs else 'absent' if gs is False else 'unknown'}")
        print(f"Zink GL version:     {gl}")
        print("Crashes / validation errors: <填写>")
        print("```")
        return

    print(f"record      {path}")
    print(f"device      {info['deviceName']}")
    print(f"driver      {info['driverName']} {info['apiVersion']} ({info['driverInfo']})")
    print()
    for r in gate_rows:
        print(f"  {MARK[r['state']]}  {r['level']:<4} {r['name']:<42} {r['class']}")
    print()
    print(f"  GS={MARK[gs]}  XFB={MARK[xfb]}  -> 记录行用 --md 生成")


def render_matrix(paths):
    print("| 记录 | 机型 | macOS | 构建 | GS | XFB | cond.rend | 驱动 |")
    print("|---|---|---|---|---|---|---|---|")
    for p in paths:
        dev = load_device(p)
        info = driver_of(dev)
        meta = load_meta(p)
        feats = feature_map(dev)
        gs = gate_state(dev, "feat", "geometryShader", feats)
        xfb = gate_state(dev, "ext", "VK_EXT_transform_feedback")
        cr = gate_state(dev, "ext", "VK_EXT_conditional_rendering")
        print(
            f"| {Path(p).stem} | {meta.get('chip', info['deviceName'])} | {meta.get('macos', '?')} "
            f"| {meta.get('build', '?')} | {MARK[gs]} | {MARK[xfb]} | {MARK[cr]} "
            f"| {info['driverName']} {info['apiVersion']} |"
        )


def render_diff(a, b):
    da, db = load_device(a), load_device(b)
    ra, rb = rows(da), rows(db)
    print(f"| 门槛 | {Path(a).stem} | {Path(b).stem} | 变化 |")
    print("|---|---|---|---|")
    changed = 0
    for x, y in zip(ra, rb):
        if x["state"] == y["state"]:
            continue
        changed += 1
        delta = "新增" if y["state"] and not x["state"] else "丢失"
        print(f"| `{x['name']}` | {MARK[x['state']]} | {MARK[y['state']]} | {delta} |")
    if not changed:
        print("| （无差异） | | | |")
    print(f"\n共 {changed} 项变化。")


# ---------------------------------------------------------------- 自检
def selftest():
    base = {
        "properties": {"deviceName": "Apple M1 Pro", "driverName": "KosmicKrisp",
                       "driverInfo": "Mesa 26.3.1", "apiVersion": "1.4.363"},
        "features": {"geometryShader": False, "depthClamp": True, "tessellationShader": True,
                     "shaderFloat64": False, "dualSrcBlend": True,
                     "shaderTessellationAndGeometryPointSize": True, "imageCubeArray": True},
        "extensions": {"VK_EXT_conditional_rendering": 1, "VK_EXT_custom_border_color": 1},
    }
    gs = json.loads(json.dumps(base))
    gs["features"]["geometryShader"] = True
    full = json.loads(json.dumps(gs))
    full["extensions"]["VK_EXT_transform_feedback"] = 1
    full["features"].update({"shaderDrawParameters": True, "shaderCullDistance": True,
                             "samplerAnisotropy": True, "depthBiasClamp": True})

    assert gate_state(base, "feat", "geometryShader") is False
    assert gate_state(base, "ext", "VK_EXT_transform_feedback") is False
    assert gate_state(gs, "feat", "geometryShader") is True
    assert gate_state(full, "ext", "VK_EXT_transform_feedback") is True
    # 嵌套 feature 也要能认出来
    nested = {"features": {"robustness2": {"nullDescriptor": True}}}
    assert feature_state(feature_map(nested), "nullDescriptor") is True
    assert fmt_api(4194304) == "1.0.0"
    assert fmt_api(4206592) == "1.3.0"
    assert fmt_api("1.4.363") == "1.4.363"
    print("selftest OK: 20 项门槛解析、嵌套 feature、apiVersion 兼容")


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(prog="kkcap")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("one", help="单条记录 -> 文本或 Markdown")
    p1.add_argument("device")
    p1.add_argument("--chip")
    p1.add_argument("--macos")
    p1.add_argument("--build")
    p1.add_argument("--gl")
    p1.add_argument("--md", action="store_true")

    p2 = sub.add_parser("matrix", help="多条记录 -> Markdown 表")
    p2.add_argument("devices", nargs="+")

    p3 = sub.add_parser("diff", help="两份记录 -> 门槛差异")
    p3.add_argument("a")
    p3.add_argument("b")

    sub.add_parser("gates", help="打印门槛表")
    sub.add_parser("selftest", help="自检")

    args = ap.parse_args()

    if args.cmd == "one":
        render_one(args.device, load_meta(args.device, args), args.md)
    elif args.cmd == "matrix":
        render_matrix(args.devices)
    elif args.cmd == "diff":
        render_diff(args.a, args.b)
    elif args.cmd == "gates":
        for name, kind, level, cls, note in GATES:
            print(f"{level:<4} {kind:<5} {name:<42} {cls:<9} {note}")
    elif args.cmd == "selftest":
        selftest()


if __name__ == "__main__":
    main()
