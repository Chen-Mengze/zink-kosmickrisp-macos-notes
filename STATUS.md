# 跟进

> 更新于 2026-11-27。有新数据就改这张表，别改正文；正文是档案，这张表是状态。

## 一句话

链路是通的，卡在最靠前的两个能力位：XFB 挡 3.0，GS 挡 3.2。现在的瓶颈不是研究，是**没有人在真机上把「Vulkan 能力表 / Zink 差集 / 实际 GL 版本」这三样东西在同一台机器上对齐过一次**。

## 公开数据现状

| 构建 | 定义 | GS | XFB | 观测/推算的 GL | 来源与可信度 |
|---|---|---|---|---|---|
| A | SDK 1.4.363.1 内置 KK（Mesa 26.3.0-devel）；截图里是 Homebrew Mesa 26.3.1 | ✗ | ✗ | 2.1 | !44928 描述 + Zink 3.0 档硬要求 XFB；F3 截图只证明驱动名，不含 GL 版本 |
| B | main + `14f59d06` | ✓ | ✗ | 2.1 | 同上；实机数据仍为零 |
| B+ | main + `14f59d06` + !44928 | ✓ | ✓ | 3.3（作者口径） | !44928 描述：“from OpenGL 2.1 to 3.3 (ES 3.1)”；待实机复核 |
| C | main + Hadron 0038–0083 | ✓ | ✓ | 4.6 | Hadron findings + CTS 15,304 pass / 1 fail |

之前表里 A 写 3.1，是转述时加上去的：那张 F3 截图只有 `Vulkan 1.4.363` / `Mesa 26.3.1`，没有 GL 版本。按 Zink 3.0 档的要求，没有 `VK_EXT_transform_feedback` 连 3.0 都过不去，所以 A 和 B 都停在 2.1；!44928 作者自己写的也是「加上它才从 2.1 到 3.3」。这条更正同时说明：只带 GS 的包不会抬高版本号。

## 待办（按顺序，每条都有判据）

1. **10 分钟复核构建 A** — 不需要编 KK，只编 `-Dtools=zink`，用现成 SDK 的 KK 跑 `zink_check_requirements`。
   判据：`VP_ZINK_gl21_baseline` Supported、`VP_ZINK_gl30_baseline` UNSUPPORTED。若 3.0 也 Supported，说明 SDK 里已经有 XFB，能力表要改。
2. **40 分钟测构建 B+** — 叠 !44928（head `e56f2e43`），出 `vulkaninfo --json` 和逐档结果。
   判据：GL 能不能到 3.3；不能的话缺哪一项。B（只有 GS、没有 XFB）预期仍是 2.1。
3. **光影包定性** — 用 `tools/packscan.py` 扫目标 pack，得到 HARD / SOFT / NONE。
   判据：至少两个 SSPT/体素类 pack + 一个真 GS 负载，硬依赖占比是多少。
4. **上游问询** — 把 1、2 的结果贴到 !44928，并问 12 月中 SDK 是否含 `14f59d06`。
   判据：拿到维护者一句明确答复（含或不含）。
5. **文档 MR** — 把 Zink 文档的 macOS 章节从一句话扩成现状 + 差集方法。
   判据：MR 提交，不论是否合入。

## 谁手里有什么

| 人 / 项目 | 已有的东西 | 缺的东西 |
|---|---|---|
| Junmin Lee | GS，!44786 已合，`14f59d06` | — |
| Willie Abrams | XFB，!44928 待评审（head `e56f2e43`） | 真机验证结果与回帖 |
| Hadron | GL 4.6 + 19,714 项 CTS 里 15,304 pass / 1 fail；补丁已在公开仓库的 `patches/mesa` | 哪些补丁能上游、跨机型复现 |
| squidbus | M4 Max 上 GS 全量 CTS 零失败 | — |
| Aitor Camacho (LunarG) | M5 Pro / macOS 27 的 float16 失败样本 | M1/M2 数据、复现确认 |
| pauyedin | 可跑 kit + 缓存/闪烁补丁 | 通用化（去掉具体应用假设） |
| Glavo / HMCL | 条件式 KK 开关（只覆盖 Vulkan 后端） | GL 路径的三件套开关 + 带 GS/XFB 的包 |

## 顺手能做的上游 PR

都不用 Mac，也不用等任何数据：

1. **i18n 拼写**：`settings.advanced.renderer.kosmickrisp=KosmickKrisp` 多了一个 `k`。一行，改完就是对的。
2. **Homebrew 自定义前缀**：`HomebrewUtils` 里留着 `// TODO: custom Homebrew prefix for macOS`，现在只认 `/opt/homebrew` 和 `/usr/local`。
3. **macOS 的 GL/Zink 分支**：`Renderer.OpenGL.ZINK` 在 macOS 可见但空操作。补 `MESA_LOADER_DRIVER_OVERRIDE` 和 `-Dorg.lwjgl.opengl.libname` 两个点即可；前提是有一个可用的 Mesa `libGL.dylib`。细节在 `action/07_hmcl_integration_zh.md`。

前两个是「一定能合」的，第三个要先解决 `libGL` 来源，别急着提。

## 什么时候该停

提前写死，避免沉没成本：

- 目标负载**全是** GS 硬依赖，而 XFB 长期没有上游路径；
- 或者 B+（叠了 !44928）在 M1/M2、M3/M4、M5/M6 三类上都报不回 3.2 以上。

命中任一条，就关掉实施分支，只保留调查结论和上游票。

## 更新规则

- 每条数据必须带：芯片、macOS、构建标识、commit、抓取日期。
- 不混 A/B/C；`MESA_GL_VERSION_OVERRIDE` 出来的数字不进表。
- 表格只收「有人跑过」的；推测写进正文，不进表。
- 新记录放 `data/`，格式见 `data/README.md`。
