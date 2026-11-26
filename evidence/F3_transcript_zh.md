# F3 文字转录

HMCL 维护者 [Glavo](https://github.com/Glavo) 在一台 Apple Silicon Mac 上提供的 F3 画面。原图随包，见 `screenshot_M6_F3_KosmicKrisp.jpg`；这里另存一份逐字转录，便于检索和复制，不含任何个人标识、路径或账号信息。

这里显示的 KosmicKrisp 后端由 HMCL 提供开启入口：选项默认隐藏，只有在系统里通过包管理器装好 KK 之后才会显示并允许切换启用。图片使用范围见根目录 `CREDITS_AND_LICENSE_zh.md`。

```text
Minecraft 26.3 (26.3/vanilla)
Java: 25.0.5.0.3
CPU: 12x Apple M6
GPU: Apple M6 (iGPU)
Vulkan: 1.4.363 KosmicKrisp   Mesa 26.3.1
119 fps  T: 120 (fifo) @120Hz
```

读法：

- `Vulkan 1.4.363 KosmicKrisp` / `Mesa 26.3.1` 是两条独立版本线：前者是驱动报的 Vulkan API 版本（跟着构建时用的 Vulkan-Headers 走），后者是 Mesa 构建版本。两个都不是 Vulkan SDK 包版本，也互不代表对方的能力。该构建不含 `geometryShader`（GS 在 2026-10-29 才合入 main，而 26.3 分支 10-14 就切了）。
- 定案靠的是驱动名那行，不是 `119 fps` —— 静默降级回苹果 OpenGL 也能跑出这个数。
- `119 fps T: 120 (fifo)` 只作画面状态旁证，不作为性能结论。

如需核对原图，直接看同目录下的 `screenshot_M6_F3_KosmicKrisp.jpg`。
