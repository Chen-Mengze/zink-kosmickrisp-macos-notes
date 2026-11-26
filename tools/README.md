# 两个能在 Windows 上跑的工具

笔记里有两个数据缺口，都不需要 Mac 就能先准备好工具：

1. **能力记录口径不一**——每个人贴的 `vulkaninfo` 格式不同，A/B/C 混着说。
2. **光影包的 GS 依赖没人定案**——作者说「必需」，但没说是硬依赖还是软依赖。

这两个工具把「等人肉回答」变成「跑一条命令」。全部仅标准库，Python 3.10+。

---

## kkcap.py — 能力记录整理器

### 它做什么

读 `vulkaninfo --json`（Vulkan Profiles 格式），输出：

- 20 项关键门槛的 ✓/✗/·，按 GL 档位排好
- 一份可以直接贴进 MR 的记录行
- 多条记录 → 一张跨机型/系统的对照表
- 两份记录 → 差异表（用来做同机 A/B）

### 用法

```bash
python kkcap.py one fixtures/device_a.json --chip "M1 Pro" --macos 26.2 --build "B" --md
python kkcap.py matrix fixtures/device_a.json fixtures/device_b.json fixtures/device_c.json
python kkcap.py diff fixtures/device_a.json fixtures/device_c.json
python kkcap.py gates          # 看门槛表本身
python kkcap.py selftest
```

每条记录可以配一个 `<name>.json.meta.json`，字段 `chip` / `macos` / `build` / `gl`。有 sidecar 时 `matrix` 才能填满表格。

### 它不做什么（重要）

- **不计算 GL 版本。** 算版本是 `zink_check_requirements` 的事；这个工具只整理证据。门槛表是筛选过的子集，不是 Zink 要求的全集。
- **不检查 format 和 limit。** 这两类要靠真正的 profile 比对（`vkprofiles --compare`）。
- 门槛表里的 `unknown` 类是**故意留的**：`VK_EXT_transform_feedback` 和 `shaderFloat64` 现在口径未定，标成确定的反而会误导。

---

## packscan.py — 光影包 GS 依赖扫描器

### 判定规则

| 结果 | 含义 |
|---|---|
| `HARD` | 存在独立 geometry stage 文件（`.gsh` / `.geom`）。Iris/OptiFine 会无条件编译它 |
| `SOFT` | GS 内建只出现在 `#ifdef` 之类的预处理块里，且没有独立 stage 文件 |
| `SUSPECT` | 非 stage 文件里出现未加保护的 GS 内建，写法需要作者确认 |
| `NONE` | 没发现 GS |

同时报告：`#version` 上限、compute 文件、SSBO、XFB 引用点。

### 用法

```bash
python packscan.py path/to/shaderpack
python packscan.py path/to/shaderpack.zip --json
python packscan.py packs/*/            # 批量
```

支持目录和 zip，跳过 `__MACOSX`。

### 局限

- 是**静态启发式**，不是编译器。宏展开、include 链、`shaders.properties` 里的条件都不解析。
- `HARD` 的判据是「文件存在且含 `void main`」。如果某个 pack 用 `.gsh` 但内容被整体 `#if 0` 包住，会误判——这种情况 `gs stage 1 file(s)` 后面会同时列出 guarded 命中，肉眼能看出来。
- XFB 只报「有没有引用」，不判断是否真的启用。

---

## 接到流程里

```
测试者交来  kk.json + meta
        ↓
kkcap matrix  →  一张跨机型表（贴仓库）
        ↓
kkcap one --md  →  一条 MR 记录
        ↓
packscan  →  HARD / SOFT，回答「值不值得继续投人」
```

两步合起来才能回答那个真正的问题：**目标负载是不是硬依赖 GS，而这条链在真机上到底报几。** 只回答一半，结论都会偏。

## 目录

```
kkcap.py
packscan.py
fixtures/
  device_a.json  (+ .meta.json)   构建 A：无 GS 无 XFB
  device_b.json  (+ .meta.json)   构建 B：有 GS 无 XFB
  device_c.json  (+ .meta.json)   构建 C：GS + XFB
  pack_hard/                      .gsh 独立文件
  pack_soft/                      #ifdef 包住的 GS
  pack_none/                      只有 compute + SSBO
```

`fixtures/device_*.json` 是**手写的演示数据**，不是实测。真实数据到位前不要引用里面的数字。
