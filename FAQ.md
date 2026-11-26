# 常见问题

## 1. 为什么不用 MoltenVK？

Khronos 在 2026-11-25 弃用了 MoltenVK，同时收掉 Portability Initiative，`VK_KHR_portability_subset` 要从 spec 和 headers 里删掉，MVK 不再有新扩展。KosmicKrisp 是 Mesa 主线里的驱动，Vulkan 1.4 conformant，走 Metal 4，不需要 portability 那一套。

更实际的一条：**MVK 没有 geometryShader**。而 macOS 原生 GL 也从 3.2 core profile 起就没带过 GS。所以「GS 在 macOS 上从来没有存在过」这句话，对原生 GL、对 MVK 都成立。

MVK 仍然适用于 Intel Mac 和 macOS 26 以前的系统。

## 2. 为什么有人说 GL 4.6，有人说 2.1、3.3？

三套构建（B 再分出叠了 !44928 的 B+）混着说：

- **A**：SDK 1.4.363.1 里的 KK（Mesa 26.3.0-devel；截图里是 Homebrew 26.3.1），没有 GS，也没有 XFB，停在 2.1。
- **B**：Mesa main 含 `14f59d06`，有 GS，没有 XFB，仍是 2.1——3.0 先要求 XFB。
- **B+**：再叠 !44928，两个都有，作者口径 3.3。
- **C**：main 加第三方补丁，两个都有，报 4.6。

顺序要说对：XFB 挡 3.0，GS 挡 3.2；两个都缺是 2.1，不是 3.1。

再加上 `MESA_GL_VERSION_OVERRIDE` 可以把字符串改成任意值——那是显示层，不是能力层。看到一个「4.6」先问：哪套构建，有没有 override。

## 3. 两层翻译会不会很慢？

先纠正一个说法：**Zink 和 KK 之间没有第三层翻译**。Zink 吐出来就是标准 Vulkan 命令，KK 是 ICD，负责把命令变成 Metal。所以不存在「Zink 到 KK 的开销」。

真实开销在三个地方：

- **语义降级**：GS 在 Metal 上不存在，KK 先在 compute pass 里跑一遍数输出，再在光栅化 VS 里展开；XFB 同理。
- **提交形状**：TBDR 怕 encoder 频繁开关。MC 的 Vulkan 后端每帧 45+ 次 `vkCmdBeginRendering`，每次在 Metal 侧都是一个独立 encoder 加一次 tile memory 冲洗。
- **管线创建**：MSL 编译和 PSO 缓存，决定的是卡顿而不是平均帧。

参考值：Zink 在 Linux 上是原生 GL 的 86%–95%；KK 对原生 Metal，LunarG 的口径是「不远」，不是「无损」。GPU-bound 场景叠起来大概在原生 Metal 的七到九成。这是推算，不是实测。

## 4. Metal 没有 geometry shader，那 GS 是怎么跑的？

Metal 没有独立的 geometry stage。KK 接了 poly 现成的 lowering（Honeykrisp 同源），把 GS 拆成两遍：compute pass 先数出要发射多少顶点，光栅化 VS 再逐个展开。代价是**同一段 shader 要跑两遍**，帧时间形态和原生 GS 不一样。

这也是为什么 GS 是「能跑」和「跑得好」之间的分界线：功能上通了，性能上要按负载单独看。

## 5. 我能日常拿它玩游戏吗？

不能。这是实验性路径，默认关闭，已知问题包括灰屏、黑闪帧、二次启动崩、部分光影编译失败、静默回退到苹果 GL。

它的用途是：验证能力、跑基准、给上游交数据。不是日常驱动。

## 6. 这个和 CrossOver / Proton 的 DXVK 是什么关系？

两条不同的翻译链，终点相同：

- 游戏用 D3D → **DXVK** → Vulkan → KK → Metal
- 应用用 OpenGL → **Zink** → Vulkan → KK → Metal

DXVK 那条早就有人在 macOS 上折腾，steamac 为了 DXVK / vkd3d-proton 给 KK 打了 63 个补丁，补的正是 GS、transform feedback、LINEAR 渲染目标这些。所以「补能力」和「打包」都不是新课题，只是没人把 GL 这条链的记录对齐。

## 7. HMCL 已经能切 KK 了，为什么 GL 还是 4.1？

因为那个开关只做三件与 Vulkan 有关的事：选 ICD、把 Vulkan loader 指向 Homebrew 的 `libvulkan.1.dylib`、给游戏传 `--graphicsBackend vulkan`。GL 那条路一件都没做。

GL 走的是另一条入口：GL 函数由 LWJGL 从 Apple 的 `OpenGL.framework` 里加载，`VK_DRIVER_FILES` 指到 KK 也没用，因为 Mesa 的 `libGL` 根本没被加载。

更要小心的是：HMCL 的渲染器列表里**有** `Mesa Zink`（`Renderer.OpenGL.ZINK`），在 macOS 上也能选。但 `generateEnvVars()` 的 macOS 分支只处理 Vulkan 驱动，选了它不会设 `MESA_LOADER_DRIVER_OVERRIDE=zink`，也不会换 `libGL`，结果是空操作 + 静默回落到苹果 GL。

要让 GL 走 Zink，得同时做三件事：把 GL 库指向 Mesa 的 `libGL`、设 `MESA_LOADER_DRIVER_OVERRIDE=zink`、确认游戏走 GL 后端。启动器三件都没做。

## 8. 需要什么机器？

Apple Silicon（M1–M6），macOS 26 或 27（KK 走 Metal 4，macOS 26 起步），Xcode 命令行工具，15 GB 磁盘。

M1/M2 + macOS 26 是官方点名的最高风险配置，也是最缺数据的一档。

## 9. 现在谁在做，我能帮什么？

GS 已合（Junmin Lee，!44786），XFB 待评审（Willie Abrams，!44928，head `e56f2e43`），Hadron 有 GL 4.6 的 CTS 记录，LunarG 在做 KK 本体。

三种帮法，按成本排：

1. **10 分钟**：在现成 SDK 上跑一次检查工具，确认 A 停在 2.1（协议第 0.5 节）。
2. **40 分钟**：完整跑一遍构建 B+，交一份 `vulkaninfo` + 逐档结果（协议正文）。
3. **不定时**：如果你写光影，告诉我你的 pack 里 GS 是硬依赖还是软依赖（`tools/packscan.py` 能先给个初判）。

## 10. Minecraft 26.2 之后默认是 Vulkan 吗？

不是。HMCL 代码里对默认值的建模很清楚：`26.2-snapshot-1` 之前只有 OpenGL；`26.2-snapshot-1` 到 `26.2-rc-2` 默认 Vulkan；**26.2 正式版之后又切回 OpenGL**。Vulkan 是可选项，不是默认项。那张 `26.3 + Vulkan` 的截图，是显式选了 Vulkan 后端。

这条对项目的意义要说反了才危险：GL 仍是大多数 Mac 玩家的默认路径，所以「苹果 GL 停在 4.1」影响的是默认体验，不是少数人的折腾。这让 GL 4.6 更重要，不是更不重要。
