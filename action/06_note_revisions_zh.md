# 笔记 v2 建议修改（七处）

按「改完之后别人更容易接手」排序，不是按字数。

---

## 1. 附录 A 和构建 A 打架，先定案

附录 A 写 GL 3.0 要 `VK_EXT_transform_feedback`，Zink 官方文档也是这么写的，而且用的是最强措辞：

> For OpenGL 3.0 support, the following additional device extensions are **required to be exposed and fully supported**: `VK_EXT_transform_feedback`, `VK_EXT_conditional_rendering`.

注意「might not actually get verified」这句注记，官方是挂在 **3.2 和 3.3** 上的，不是 3.0。所以「A 没有 XFB 却报 3.1」比笔记里写的更刺眼——按文档它应该连 3.0 都过不去。

三种可能，一条命令就能分辨：

```bash
# 不用编 KK，用现成 SDK 的 KK 当当前驱动
zink_check_requirements
```

- missing 里有 XFB，实际却报 3.1 → 3.0 这一档的检查没有真正执行。
- missing 里没有 XFB → 构建 A 其实有 XFB，能力表要改。
- 直接报 2.1 → 「A 报 3.1」这个观察本身要重新核对来源。

**如果是第一种，这是全文最值钱的一条。** 它一句话解释了为什么社区里「GL 4.6」的数字互相打架，也解释了「装了最新 KK 就有 3.3」为什么会流传。建议单开一节，不要放在附录里。

---

## 2. 附录 B 只编了 Zink，没编 KK

`meson setup build -Dgallium-drivers=zink -Dtools=zink` 产出的是 Zink（GL 侧），不含 KosmicKrisp。所以按现在的附录 B，走不出「构建 B」——B 要真含 `14f59d06`，必须自编 KK。官方文档的命令是另一条：

```bash
meson setup build-kk . --buildtype=release \
  -Dplatforms=macos \
  -Dvulkan-drivers=kosmickrisp \
  -Dgallium-drivers= \
  -Dopengl=false \
  -Dzstd=disabled \
  --prefer-static
ninja -C build-kk
```

注意 `-Dgallium-drivers=` 是空的。两条命令分属两个 build 目录，别合在一起写，否则读者会以为一条命令能出全套。

顺带补一句 ICD manifest 的位置：`find build-kk -name '*.json'`，以及 `library_path` 相对路径的坑。

---

## 3. 「KK 基本无损」这句要收一收

现在这句在正文里是断言，但支撑它的材料都是别人机器上的单点数字。建议改成：

> KK 对原生 Metal 的损耗在 GPU-bound 场景下接近可忽略（LunarG 口径是「不远」，不是「无损」）；真正的开销集中在三处：GS 用 compute 跑两遍的语义降级、TBDR 上每帧 45+ 个 render encoder（MC-311557）、以及 PSO 编译与缓存。层数不是成本模型，降级策略才是。

理由：现在这句会被懂行的人当成外行话——因为「Zink 到 KK」之间并不存在一层翻译。Zink 吐 Vulkan 命令，KK 是 ICD，中间没有第三层。这个说法一旦被指出来，整份笔记的可信度会被连带打折。

---

## 4. GL 4.0 的两个卡点不要并列

`shaderFloat64`（Playport 0087）和 R32G32B32 texel buffer（Hadron 0054）现在并列摆着，读者不知道信哪个。两条路：

- 跑一次 `vkprofiles --compare` 定案，写结论；
- 或者明确写「未定案，复现命令如下」，把它降级成 open question，而不是事实。

并列而不裁决，是这份笔记里唯一一处「档案感」压过「工程感」的地方。

---

## 5. 加一张「三类要求」表

现在附录 A 是一张平表，把「缺了就降版本」「缺了不降但会炸」「缺了完全没提示」混在一起。建议加一列或分三组：

| 类型 | 表现 | 例子 |
|---|---|---|
| 硬门槛 | 版本号直接降 | `geometryShader` → 卡在 3.1 |
| 软要求 | 版本照报，用到才炸 | 待定：XFB（见第 1 条） |
| 不校验 | 静默渲染错误 | 2.1 基线里那批（`line_rasterization` 六项等） |

这张表是整份笔记里复用价值最高的东西——它可以直接变成 `zink_check_requirements` 的输出格式，也可以直接进上游文档。

---

## 6. Zink 官方文档的 macOS 章节现在只有一句话

原文：`Zink on macOS is experimental with very limited capabilities.` 这句话已经落后于事实了。提一个文档 MR 是最低门槛的上游动作：

- 不需要机器（改文档而已）
- 不需要维护者重新评估架构
- 一旦合入，所有后来者搜到的第一句话就变了

可以就补三段：KK 现状（GS 已合、XFB draft）、三套构建的口径区别、`zink_check_requirements` 在 macOS 上的用法。

---

## 7. HMCL 那条事实现在藏在图注里

「HMCL 检测到包管理器装了 KK 就显示切换入口、并允许切换」现在只出现在截图说明和附录 D 的括号里。这是整份笔记里**唯一一条已经打通用户侧的链路**，它应该是正文的一节，而不是图注。

它同时改变结论的措辞：不是「需要有人做 launcher 集成」，而是「需要有人把带 GS/XFB 的 KK 做成包」。前者听起来像要说服一个团队，后者是一个 formula 加一次 release 跟进。

顺带把发布判据写死：GS-only 的包会让版本号上涨，但用 XFB 的负载静默出错（见第 1 条）。判据是「GS + XFB + 要求类型有记录」，不是「GS 已合」。

---

## 7. 「新版把 Vulkan 设成默认」这个前提要改

正文「起因」里有一句「新版把原生 Vulkan 设成默认之后」。HMCL 的 `GraphicsAPI.getDefaultGraphicsAPI()` 把默认值的建模写死了：

- `< 26.2-snapshot-1`：`OPENGL`（所有版本只支持 GL）
- `26.2-snapshot-1` ~ `26.2-rc-2`：`VULKAN`
- `>= 26.2` 正式版：`OPENGL`（又切回去了）

所以 Vulkan 只是快照窗口里的默认，正式版默认仍是 GL。这不是措辞问题——它决定你怎么论证 Iris 的处境：不是「MC 都转 Vulkan 了，GL 用户被抛下」，而是「GL 仍是默认，但默认停在 4.1，且 Iris 没有 Vulkan 版本」。后者更站得住，也更难被反驳。

要更稳，补一句「以实机 `options.txt` 与 F3 为准」，把代码建模和 Mojang 的实际行为分开。

---

## 可选：README 顶部换一句话

现在「找三类人」在中段。建议在标题下面直接放一句：

> 目前最缺的一份数据：M1/M2 + macOS 26 上，main + !44928 的 `vulkaninfo` 与 Zink 能力差集。

维护者和测试者都只会读前三行。把「我要什么」放在前三行，比放在第三节有效。
