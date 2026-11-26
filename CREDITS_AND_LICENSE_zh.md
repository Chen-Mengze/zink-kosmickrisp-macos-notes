# 版权与引用说明

这份说明是给要转发、引用、或者把材料接到自己项目里的人看的。目标只有一个：让这份笔记能公开传，又不把别人的整页存档、专有产物顺手打包带走。唯一保留的第三方图像是一张用于说明驱动名的 F3 截图，使用范围写在下面。English version: `CREDITS_AND_LICENSE_en.md`。

## 本文自己写的东西

- `Zink_KosmicKrisp_on_macOS_zh.md`（正文，含附录 E.2 收编后的分析结论）
- `evidence/MR44786_public_quotes_zh.md` 里的编排与注释
- `evidence/F3_transcript_zh.md`、`evidence/how_to_reproduce_disassembly_zh.md`

以上按 **CC BY 4.0** 放出：可以转载、拆分、改写、拿去做文档或 wiki 页面，标一下出处即可。署名按发布处的作者名填写。

本说明同样按 CC BY 4.0。

## 第三方材料

正文里的技术事实、版本日期、CTS 数字、补丁编号、提交标题、讨论短句，分别来自下面这些公开来源。版权归各自作者或项目，**本文只做事实性引用、短引与链接，没有复制原文段落、整页存档或代码**；例外是下表最后一行那张 F3 截图。

| 来源 | 本文取了什么 | 出处 |
|---|---|---|
| Mesa / GitLab !44786、!44928 | MR 描述定调句、合并时间、提交标题、几条讨论短句 | https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44786 、https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44928 |
| Mesa 文档、release notes、release calendar | Zink 逐档需求、分支切割日期、26.3.1 `New features: None` | https://docs.mesa3d.org/drivers/zink.html 、https://mesa3d.org/release-calendar.html |
| LunarG / Khronos | KK 定位、1.4 conformance、bundle 布局、MVK 弃用 | https://www.lunarg.com/products/kosmickrisp 、https://www.khronos.org/news/archives/kosmickrisp-achieves-vulkan-1.4-conformance-on-apple-silicon 、https://www.khronos.org/blog/from-portability-to-conformance-a-new-chapter-for-layered-vulkan-on-apple |
| Blender 开发者门户 | macOS 上的 GS limitation、实验性定位 | https://developer.blender.org/docs/features/gpu/vulkan/kosmic_krisp |
| Mojira MC-311557、Minecraft Feedback | 结构性问题与社区提议的时间点 | https://bugs.mojang.com/browse/MC-311557 、https://feedback.minecraft.net/hc/en-us/community/posts/44920984456717-Using-kosmickrisp-instead-of-moltenvk-for-vulkan-in-macos |
| GitHub Gist《Running Minecraft on macOS with Zink + KosmicKrisp》 | 十个 debug 问题的结论、70fps、2–3% | https://gist.github.com/lucamignatti/5312f5e937de2ba44256ecba6de54cc2 ；正文只作事实转述 |
| Hadron `findings.md` / conformance 记录、Playport 0087 / 0093 | 0038–0083 的编号与结论、CTS 数字、fans/quads 的收益 | https://github.com/IvanKarpan/hadron 、https://github.com/playportdev/playport ；正文只作事实转述 |
| `pauyedin/kosmickrisp-minecraft-macos`、steamac | 缓存 key 口径、0001–0003/0021、63 补丁 | https://gitlab.com/pauyedin/kosmickrisp-minecraft-macos/-/tree/main 等 |
| HMCL 维护者 [Glavo](https://github.com/Glavo) 提供的 F3 截图 | 确认实际驱动名、机型与画面状态（`evidence/screenshot_M6_F3_KosmicKrisp.jpg`）；该 KK 后端由 HMCL 提供开启入口，需先经包管理器安装 KK 才显示并允许切换 | https://github.com/Glavo 、https://glavo.site/about/ ；画面版权归各自权利人 |

两点容易搞混，写清楚：

- Mesa 源码是 MIT，但 **MR 描述和评论是用户生成内容，文字版权归发言者**，不自动跟着代码许可走。所以这里只放必要的最短引用并标作者，完整上下文请点链接看。
- 正文里那些社区先行者的 findings，是**转述结论和数字**，不是复制段落。若要把它们的原文并到自己的文档里，请直接去各自仓库看许可。

公开评论里出现的个人邮箱已在本包中去掉。F3 原图与文字转录都只用于说明硬件、驱动和版本信息，画面里没有任何用户名、路径或账号信息，也没有裁掉或改动内容。图由 HMCL 维护者 [Glavo](https://github.com/Glavo) 提供并确认可用于说明驱动名；图中显示的 KK 后端由 HMCL 提供开启入口，默认隐藏，需先经包管理器安装 KK 才显示并允许切换。图片仅作事实性展示，不作任何产品宣传或画面再创作；若提供者不希望公开，按下面的移除渠道撤下即可。

## 没有随包分发的东西

公开版刻意不带下面几类，原因是它们属于第三方作品的复制件或专有内容的派生件：

| 原件 | 怎么拿到 | 不附的原因 |
|---|---|---|
| GitLab !44786 整页存档（`.mht`，含站点样式、头像、界面文案） | 上面的 MR 链接，自行保存页面 | 整页再分发会连站点界面、图标、头像一起带出去 |
| 该页抽出的 647 行纯文本 | 同上 | 同上，避免整页文本的复制件 |
| `renderpearl` 反汇编全文（2457 行）及切行版 | 按 `evidence/how_to_reproduce_disassembly_zh.md` 自行生成 | 游戏客户端专有字节码的派生内容，不随公开包分发 |
| 早期反编译结论稿 | 不需要了，修正后的结论已并入正文与附录 E.2 | 原稿含字节码片段和本机路径，且有几条判断后来被证伪 |

**反汇编那部分请留意**：`evidence/how_to_reproduce_disassembly_zh.md` 给的是方法，不是产物。生成和使用这类产物前，请自行确认符合游戏 EULA 与适用法律；本包不提供、也不鼓励分发任何客户端字节码或其反汇编文本。

**F3 截图随包**（`evidence/screenshot_M6_F3_KosmicKrisp.jpg`），并在正文内联。文字转录另存一份便于检索。转发时请连这张图一起保留出处与本节说明；若提供者提出异议，按下一节渠道撤下，届时改用 `evidence/F3_transcript_zh.md`。

## 想改、想撤、想纠错

- 事实转述错了：直接在发布处留言或开 issue，会按一手材料改。
- 你是某段引用、某份 findings 的作者，或 F3 截图的提供者 [Glavo](https://github.com/Glavo)，不希望被引用或展示：同样在发布处说一声，会移除或改写成链接。
- 想把这份笔记并进 wiki / 文档 / 自己的项目：CC BY 4.0，标出处即可，不用单独来问。

联系方式按发布处填写（仓库 issue、讨论区或邮件皆可）。

---

这不是法律意见。转载到特定平台、或要把第三方材料一并收入之前，请按该平台规则和材料自身的许可再确认一次。
