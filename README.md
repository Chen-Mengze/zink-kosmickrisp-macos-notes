# 在 macOS 上用 Zink + KosmicKrisp 跑桌面 OpenGL

> **现在最缺的一份数据**：M1/M2 + macOS 26 上，`main + !44928` 的 `vulkaninfo` 与 Zink 能力差集。
> 轻量版（不编 KK；检查 10 分钟，首次编工具 20–40 分钟）见 [action/02_test_protocol_zh.md](action/02_test_protocol_zh.md)；整体状态见 [STATUS.md](STATUS.md)，目录见 [INDEX.md](INDEX.md)。

**工程笔记 · 中英双语 · 2026-11-26**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Apple Silicon 的 macOS 上，用 `Zink → KosmicKrisp → Metal 4` 这条链把桌面 OpenGL 顶起来：链路怎么走、别人已经做到哪一步、真要动手还差什么。中文正文与英文版并列，附证据材料与引用说明。

> **结论**：链路是通的，当前发布版还不能当开箱功能发。最靠前的两个门槛是 `geometryShader` 与 transform feedback 没进 SDK；再往上的 4.x 还压着一组 Hadron 补丁。

## 先交代底细

作者没有 Mac，也没写过 Mesa 驱动。文中内容基本是读别人的 MR、findings、gist 和反汇编拼出来的，加上别人提供的截图。凡是没亲手跑过的都标了出处；版本、CTS 数字、补丁编号以一手材料为准，转述错的地方欢迎直接改。

笔记内容截至 2026-11-26。上游变化很快（12 月中还有一版 SDK），过了这个点请以一手材料为准。

## 目录

| 文件 | 内容 |
|---|---|
| [`Zink_KosmicKrisp_on_macOS_zh.md`](Zink_KosmicKrisp_on_macOS_zh.md) | 中文正文。起因、已有工作、链路与两个坑、Zink 逐档需求、版本口径、实施计划、已知的坑、附录 A–E |
| [`Zink_KosmicKrisp_on_macOS_en.md`](Zink_KosmicKrisp_on_macOS_en.md) | English version of the same note |
| [`CREDITS_AND_LICENSE_zh.md`](CREDITS_AND_LICENSE_zh.md) | 许可、第三方归属、图片使用范围、未随包材料的去处、移除请求渠道 |
| [`CREDITS_AND_LICENSE_en.md`](CREDITS_AND_LICENSE_en.md) | 同上，英文版 |
| [`evidence/`](evidence) | 证据材料：F3 截图与文字转录、Mesa !44786 最短引用摘录、反汇编复现方法（中英各一份） |
| [`LICENSE`](LICENSE) | CC BY 4.0 全文，只覆盖原创文字部分 |

## 怎么读

按你手里有什么来选：

- **只想知道「现在能不能用」** → 正文的「结论」「已有工作」「版本口径」三节。重点是分辨 A/B/C 三套构建，社区里那些「GL 4.6」不是一回事。
- **想自己复现** → 附录 B 的命令行 + [`evidence/how_to_reproduce_disassembly_zh.md`](evidence/how_to_reproduce_disassembly_zh.md)；包布局照 LunarG 十月的《State of Vulkan on Apple》抄，`pauyedin/kosmickrisp-minecraft-macos` 是现成可跑的 kit。
- **想核对引用** → [`evidence/`](evidence) 下的转录与最短引用，每条标了作者和出处；没随包的整页存档、字节码产物去哪拿，写在许可说明第二部分。
- **想回传数据** → 附录 C 的回传模板。现在缺的就是 Apple Silicon 机器上的 `vulkaninfo` 和固定样本结果。

## 链路

```text
GL 应用 / 光影 / 模组
  → Zink (Mesa Gallium, GL → Vulkan)
  → libvulkan.1.dylib + KosmicKrisp ICD
  → KosmicKrisp (Vulkan → Metal 4)
  → Apple Silicon GPU
```

能力是 Zink 按 `VP_ZINK_requirements.json` 逐档查底层驱动的，查询方是 Zink 和 GLSL 负载，不是上层应用那份 Vulkan 扩展白名单。所以「上游应用用不到这些扩展、加了也没用」在原生 Vulkan 后端里成立，在这条链上不成立——底层多一个 feature 位，GL 侧就多一档语义，就多一个能编译出画面的 shader。

## 版本口径：三套构建（B 再分 B+）不能混着说

| 构建 | 是什么 | `geometryShader` | transform feedback | 参考 GL 上限 |
|---|---|---|---|---|
| **A** | SDK 1.4.363.1 内置 KK（Mesa 26.3.0-devel）；截图里是 Homebrew Mesa 26.3.1 | ✗ | ✗ | 2.1（3.0 起就要求 XFB） |
| **B** | Mesa main 自编译（含 `14f59d06`） | ✓ | ✗ | 2.1（只多一个 GS 位，3.0 仍被 XFB 卡住） |
| **B+** | B 再叠 !44928（head `e56f2e43`） | ✓ | ✓ | 3.3（!44928 作者口径，待实机复核） |
| **C** | main + Hadron 0038–0083 补丁 | ✓ | ✓ | 4.6（Hadron 记录） |

C 的结果不能拿去说 A 支持什么。这一条同时写在正文、能力声明和回传模板里。

补一句容易看岔的：Mesa 的 feature release 在第一个 RC 那天就从 main 切了分支，GS 是 10-29 合的、26.3.1 是 11-18 发的，看着像赶上了，其实没进。所以「装了最新 KK 就有 GS」目前不成立。退一步说，就算装到带 GS 的构建，GL 也还是 2.1——3.0 先要求 XFB，3.2 才轮到 GS。

## 找三类人

公开这份笔记是想找：

1. 手上有 Apple Silicon 机器、愿意按附录 C 回传一份 `vulkaninfo` 和固定样本结果的；
2. 写光影包、能说清自己那个 pack 里 GS 是硬依赖（真 `OpEntryPoint Geometry`）还是软依赖的；
3. 下面引到的那几份材料的作者——哪条转述错了，或者愿意把各自的 findings 互相挂个链接。

不要求加入什么项目，也不需要统一口径，各做各的、把结果放回公开处就够。勘误和补充直接开 issue 或 PR。

## 许可与引用

- **原创文字**（中英正文、引用摘录的编排、转录、复现方法）按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 放出：可以转载、拆分、改写，标个出处即可。
- **第三方材料**只做事实性引用与短引并给链接，版权归各自作者，没有复制段落、整页存档或代码。
- **第三方图像**只有一张用于说明驱动名的 F3 截图，由 HMCL 维护者 [Glavo](https://github.com/Glavo) 提供；使用范围与撤回方式见 [`CREDITS_AND_LICENSE_zh.md`](CREDITS_AND_LICENSE_zh.md)。

引用建议：

```text
Chen-Mengze. 在 macOS 上用 Zink + KosmicKrisp 跑桌面 OpenGL：工程笔记. 2026-11-26.
https://github.com/Chen-Mengze/zink-kosmickrisp-macos-notes
```

---

## English

**Engineering notes: desktop OpenGL on macOS via Zink + KosmicKrisp (bilingual, 2026-11-26)**

On Apple Silicon, desktop OpenGL can be served by the chain `Zink → KosmicKrisp → Metal 4`. This repository records how that chain is wired, how far others have already got, and what is still missing before anyone can ship it.

> **TL;DR** — the chain works; the current release cannot be shipped as an out-of-the-box feature. The first two gates are `geometryShader` and transform feedback, neither in the SDK; 4.x above that also waits on a set of Hadron patches.

The author has no Mac and has never written a Mesa driver. Everything here is assembled from other people's merge requests, findings documents, gists and disassembly, plus a screenshot provided by someone else. Anything not run first-hand is attributed; versions, CTS numbers and patch IDs defer to the primary material. Corrections are welcome.

### Contents

| File | What it is |
|---|---|
| [`Zink_KosmicKrisp_on_macOS_en.md`](Zink_KosmicKrisp_on_macOS_en.md) | The English note: background, prior work, the chain and two integration traps, per-version Zink requirements, version bookkeeping, plan, known traps, appendices A–E |
| [`Zink_KosmicKrisp_on_macOS_zh.md`](Zink_KosmicKrisp_on_macOS_zh.md) | Chinese version of the same note |
| [`CREDITS_AND_LICENSE_en.md`](CREDITS_AND_LICENSE_en.md) | Licence, third-party attribution, image scope, where non-bundled material lives, takedown channel |
| [`CREDITS_AND_LICENSE_zh.md`](CREDITS_AND_LICENSE_zh.md) | The same, in Chinese |
| [`evidence/`](evidence) | Evidence: the F3 screenshot and its transcript, shortest-quote excerpts from Mesa !44786, a method to regenerate the disassembly |
| [`LICENSE`](LICENSE) | Full CC BY 4.0 text, covering original writing only |

### How to read it

- **Just want to know whether it works today** → "Conclusion", "Prior work" and "Version bookkeeping" in the note. The key point is to separate builds A/B/C; the "GL 4.6" claims floating around are not the same thing.
- **Want to reproduce it** → commands in Appendix B, plus [`evidence/how_to_reproduce_disassembly_en.md`](evidence/how_to_reproduce_disassembly_en.md). Use LunarG's bundle layout; `pauyedin/kosmickrisp-minecraft-macos` is a working setup kit.
- **Want to check a citation** → [`evidence/`](evidence) holds the transcripts and shortest necessary quotes, each attributed.
- **Want to contribute data** → the report template in Appendix C.

### Builds A/B/C (B split into B and B+)

| Build | What it is | `geometryShader` | transform feedback | GL ceiling |
|---|---|---|---|---|
| **A** | KK inside SDK 1.4.363.1 (Mesa 26.3.0-devel); the screenshot shows Homebrew Mesa 26.3.1 | no | no | 2.1 (XFB is required from 3.0 on) |
| **B** | Mesa main, self-built (includes `14f59d06`) | yes | no | 2.1 (one more GS bit; 3.0 is still blocked by XFB) |
| **B+** | B plus !44928 (head `e56f2e43`) | yes | yes | 3.3 (per the !44928 author; to be confirmed on hardware) |
| **C** | main + Hadron patches 0038–0083 | yes | yes | 4.6 (per Hadron records) |

Results from C cannot be used to claim anything about A. Even a build with GS but without XFB stays at 2.1: 3.0 already requires transform feedback.

### Contribute

Three kinds of people are wanted: owners of Apple Silicon machines willing to return a `vulkaninfo` dump plus fixed-sample results (Appendix C); shader-pack authors who can say whether GS is a hard or soft dependency in their pack; and the authors of the material cited here — if a paraphrase is wrong, or if you would like the findings cross-linked. No project membership and no shared messaging required: do your own thing and put the results back in public. Issues and PRs are open for corrections.

### Licence

Original writing is released under **CC BY 4.0**. Third-party material is cited factually and briefly, with links; copyright stays with its authors. The only third-party image is the F3 screenshot provided by [Glavo](https://github.com/Glavo), HMCL maintainer — scope and takedown are in [`CREDITS_AND_LICENSE_en.md`](CREDITS_AND_LICENSE_en.md).

```text
Chen-Mengze. Engineering notes: desktop OpenGL on macOS via Zink + KosmicKrisp. 2026-11-26.
https://github.com/Chen-Mengze/zink-kosmickrisp-macos-notes
```
