# 索引

这个仓库现在有两类内容：**档案**（发生了什么）和**行动**（接下来做什么）。先看这张表，别从头读。

## 按目的找

| 你想 | 先看 | 再看 |
|---|---|---|
| 知道现在能不能用 | `STATUS.md` | 正文「结论」「版本口径」 |
| 花 10 分钟帮上忙（工具已就绪） | `action/02_test_protocol_zh.md` 第 0.5 节 | `action/01_upstream_ask_en.md` |
| 花 1–2 小时做完整验证 | `action/02_test_protocol_zh.md` | `data/README.md` |
| 判断某个光影包需不需要 GS | `tools/packscan.py` | `action/05_acceptance_criteria_zh.md` |
| 整理别人交来的 `vulkaninfo` | `tools/kkcap.py` | `data/README.md` |
| 核对某条引用 | `evidence/` | `action/06_note_revisions_zh.md` |
| 给上游提 issue / MR | `action/01_upstream_ask_en.md` | !44928、!44786 |
| 第一次听说这个项目 | `FAQ.md` | 正文「起因」「链路」 |

## 目录

| 路径 | 是什么 |
|---|---|
| `STATUS.md` | 状态表：公开数据现状、待办、谁手里有什么、什么时候该停 |
| `INDEX.md` | 本文件 |
| `FAQ.md` | 十个最常被问的问题，含「为什么 GL 4.6 有三种说法」 |
| 正文（中/英） | 工程笔记本体，2026-11-26 口径 |
| `action/01_upstream_ask_en.md` | 20 行英文，贴 !44928 用 |
| `action/02_test_protocol_zh.md` | 中文，轻量 10 分钟 / 完整 1–2 小时两档 |
| `action/03_test_protocol_en.md` | 英文同上 |
| `action/04_call_for_testers_zh.md` | 中文发帖正文 |
| `action/05_acceptance_criteria_zh.md` | 四列判据、性能第二轨、口径铁律、成立/停止条件 |
| `action/06_note_revisions_zh.md` | 正文 v2 还差的两处：三类要求表、HMCL 进正文 |
| `action/07_hmcl_integration_zh.md` | HMCL 里 KosmicKrisp / Zink 的确切代码位置、检测条件、缺口与改动点 |
| `tools/kkcap.py` | `vulkaninfo --json` → 记录行 / 矩阵 / diff |
| `tools/packscan.py` | 光影包 → HARD / SOFT / SUSPECT / NONE |
| `data/` | 真机记录，一条一个目录 |
| `evidence/` | 截图、转录、最短引用、反汇编复现方法 |

## 三条口径（读任何数字之前先看这个）

1. 说「GL 4.6」必须带构建标识：A（SDK）、B（main）、C（补丁）。
2. `GL_VERSION` 字符串可以被 `MESA_GL_VERSION_OVERRIDE` 覆盖，不算能力证据。
3. 一份 CTS 通过率不等于一个游戏能跑（Hadron 原话：A pass here does not mean a game works）。
