# HMCL 的 KosmicKrisp / Zink 接入点

> 抓取于 2026-11-27，`HMCL-dev/HMCL` 的 `main` 分支。只给符号名，不给行号（行号会漂移）。
> Fetched 2026-11-27 from `HMCL-dev/HMCL`, `main` branch. Symbols only; line numbers drift.

## 1. 四层结构 | Four layers

HMCL 的「KosmicKrisp 后端」不是一个布尔开关，而是 `Renderer` 枚举里的常量，依次经过检测、设置模型、UI、启动参数四层。检测决定它出不出现，UI 只负责列出来。

HMCL's “KosmicKrisp backend” is not a boolean toggle but a constant in the `Renderer` enum, passing through detection, settings model, UI and launch arguments. Detection decides whether it exists; the UI only lists it.

| 层 Layer | 文件 File | 符号 Symbols |
|---|---|---|
| 检测 / 枚举 Detection / enum | `HMCLCore/src/main/java/org/jackhuang/hmcl/game/Renderer.java` | `Renderer.Vulkan.KOSMICKRISP`, `Vulkan.Holder`, `icdFile()` |
| 设置模型 Settings model | `HMCLCore/src/main/java/org/jackhuang/hmcl/game/LaunchOptions.java` | `renderer`, `graphicsBackend`, `setRenderer()` |
| UI | `HMCL/src/main/java/org/jackhuang/hmcl/ui/game/GameSettingsPage.java` | `vulkanRendererPane`, `openGLRendererPane` |
| 启动 Launch | `HMCLCore/src/main/java/org/jackhuang/hmcl/launch/DefaultLauncher.java` | `generateCommandLine()`, `generateEnvVars()` |
| 路径 Paths | `HMCLCore/src/main/java/org/jackhuang/hmcl/util/platform/macos/HomebrewUtils.java` | `HOMEBREW_PREFIX`, `LIB_VULKAN` |

## 2. 检测：为什么装好才出现 | Detection: why it appears only after install

「隐藏」不是 `setVisible(false)`，而是这个常量没被加进 `SUPPORTED`。macOS 上要两个文件同时存在：`/opt/homebrew/lib/libvulkan.1.dylib`（ARM64；x86 是 `/usr/local`），以及 `/opt/homebrew/share/vulkan/icd.d/kosmickrisp_mesa_icd.aarch64.json`。

“Hidden” is not `setVisible(false)`; the constant is never added to `SUPPORTED`. On macOS two files must both exist: `/opt/homebrew/lib/libvulkan.1.dylib` (ARM64; `/usr/local` on x86) and `/opt/homebrew/share/vulkan/icd.d/kosmickrisp_mesa_icd.aarch64.json`.

```java
KOSMICKRISP("kosmickrisp_mesa") {
    @Override
    public boolean isSupported(NativePlatform platform, @Nullable List<GraphicsCard> cards) {
        return platform.os() == OperatingSystem.MACOS && platform.arch() == Architecture.ARM64;
    }
},
// Holder 静态初始化 / static initializer
if (Files.isRegularFile(HomebrewUtils.LIB_VULKAN)) {
    Path kosmickrispIcd = HomebrewUtils.HOMEBREW_PREFIX.resolve(
        "share/vulkan/icd.d/kosmickrisp_mesa_icd." + archName + ".json");
    if (Files.isRegularFile(kosmickrispIcd)) {
        driverToIcdFile.put(KOSMICKRISP, kosmickrispIcd);
        supported.add(KOSMICKRISP);
    }
}
```

两个实用后果。一是静态初始化：运行期间装 KK 不会出现选项，必须重启 HMCL。二是 Homebrew 前缀硬编码，代码里留着 `// TODO: custom Homebrew prefix for macOS`，装在 `~/homebrew` 之类的位置不会被识别。

Two practical consequences. First, static initialization: installing KK while HMCL runs will not surface the option until restart. Second, the Homebrew prefix is hard-coded, with `// TODO: custom Homebrew prefix for macOS` left in the code; a prefix such as `~/homebrew` is not detected.

## 3. UI 与文案 | UI and strings

选项在「游戏设置 → 高级 → 图形」，由 `GameSettingsPage` 的 `graphicsSettings` 构建。Vulkan 项是 `vulkanRendererPane`，候选项来自 `Renderer.getSupported(GraphicsAPI.VULKAN)`。单项键 `settings.advanced.renderer.kosmickrisp`，中文值 `KosmickKrisp`——多了一个 `k`，正确拼写是 `KosmicKrisp`；描述为「基于 Metal 4 的 Vulkan 渲染器 (实验性)」。

The option sits under “Game Settings → Advanced → Graphics”, built by `graphicsSettings` in `GameSettingsPage`. The Vulkan entry is `vulkanRendererPane`, with candidates from `Renderer.getSupported(GraphicsAPI.VULKAN)`. The per-item key is `settings.advanced.renderer.kosmickrisp`, whose Chinese value is `KosmickKrisp` — one extra `k`; the correct spelling is `KosmicKrisp`. The description reads “Metal 4-based Vulkan renderer (experimental)”.

可见性只跟版本有关：后端选择器要求 ≥ `26.2-snapshot-2`；Vulkan 渲染器要求 `GraphicsAPI.VULKAN.isSupported(version)`，即 ≥ `26.2-snapshot-1`。能不能选，仍由第 2 节决定。

Visibility depends only on the game version: the backend selector requires ≥ `26.2-snapshot-2`; the Vulkan renderer requires `GraphicsAPI.VULKAN.isSupported(version)`, i.e. ≥ `26.2-snapshot-1`. Whether it can be chosen is still decided by section 2.

## 4. 启动时设了什么 | What launch sets

三件事，缺一不可：`-Dorg.lwjgl.vulkan.libname=<libvulkan.1.dylib>`（绕开 LWJGL 自带的 MoltenVK）、`VK_ICD_FILENAMES` / `VK_DRIVER_FILES`（ICD 绝对路径）、`--graphicsBackend vulkan`（版本 ≥ `26.2-snapshot-2`）。

Three things, all required: `-Dorg.lwjgl.vulkan.libname=<libvulkan.1.dylib>` (bypassing LWJGL's bundled MoltenVK), `VK_ICD_FILENAMES` / `VK_DRIVER_FILES` (absolute ICD path), and `--graphicsBackend vulkan` (version ≥ `26.2-snapshot-2`).

```java
} else if (SystemInfo.CURRENT_OS == OperatingSystem.MACOS) {
    if (options.getJava().getArchitecture() == SystemInfo.SYSTEM_ARCH
            && driver instanceof Renderer.Vulkan vulkanDriver
            && vulkanDriver != Renderer.Vulkan.MOLTENVK
            && vulkanDriver.icdFile() != null) {
        String absolutePath = FileUtils.getAbsolutePath(vulkanDriver.icdFile());
        env.put("VK_ICD_FILENAMES", absolutePath);
        env.put("VK_DRIVER_FILES", absolutePath);
    }
}
```

`MOLTENVK` 的 `icdFile()` 为 `null`，所以不会设这两个变量——它由 LWJGL 自带。这也解释了 F3 截图为什么能显示 KosmicKrisp：ICD、loader、后端参数都是启动器设的。

`MOLTENVK` has no `icdFile()`, so these variables are not set for it — it ships with LWJGL. This also explains the F3 screenshot: the ICD, the loader and the backend argument are all set by the launcher.

## 5. 缺口：`ZINK` 在 macOS 是空操作 | The gap: `ZINK` is a no-op on macOS

`Renderer.OpenGL.ZINK` 存在，文案也写好了（「Mesa Zink / 基于 Vulkan 的 OpenGL 渲染器」），在 macOS 上也可见。但 `generateEnvVars()` 的 macOS 分支只匹配 `Renderer.Vulkan`，不会设 `MESA_LOADER_DRIVER_OVERRIDE=zink`；`generateCommandLine()` 也只设 `org.lwjgl.vulkan.libname`，从不设 `org.lwjgl.opengl.libname`。选了等于什么都没发生，然后静默回落到苹果 GL。

`Renderer.OpenGL.ZINK` exists, with a ready label (“Mesa Zink / OpenGL renderer based on Vulkan”), and it is visible on macOS. But the macOS branch of `generateEnvVars()` matches only `Renderer.Vulkan` and never sets `MESA_LOADER_DRIVER_OVERRIDE=zink`; `generateCommandLine()` only sets `org.lwjgl.vulkan.libname`, never `org.lwjgl.opengl.libname`. Selecting it does nothing, then silently falls back to Apple GL.

最小改动三点：

```java
// 1) generateEnvVars() 的 macOS 分支 / macOS branch
if (driver == Renderer.OpenGL.ZINK) {
    env.put("MESA_LOADER_DRIVER_OVERRIDE", "zink");
}

// 2) generateCommandLine() 的 macOS 分支 / macOS branch
if (options.getRenderer() == Renderer.OpenGL.ZINK) {
    // 需要一个配置项指向可用的 libGL.dylib，别硬编码 Homebrew 路径
    // needs a setting pointing at a usable libGL.dylib; do not hard-code Homebrew
}

// 3) 确保 --graphicsBackend 不是 vulkan
// ensure --graphicsBackend is not vulkan
```

未决前提：Homebrew 的 mesa 是否提供可用于 Zink 的 `libGL.dylib`，没验证。如果没有，就得指向自编译产物（协议第 3 节那套）。

Open prerequisite: whether Homebrew's mesa ships a `libGL.dylib` usable by Zink is unverified. If not, the path must point at a self-built artifact (the build in protocol section 3).

边界：启动器只能解决「库指向」和「环境变量」。GL 上下文与 surface 的整合（`NSViewBackingLayer` → `CAMetalLayer`）仍在应用或驱动一侧，Gist 里那十个问题不会因为改了 HMCL 就消失。

Boundary: a launcher can only fix “which library” and “which variables”. GL context and surface integration (`NSViewBackingLayer` → `CAMetalLayer`) remains on the application or driver side; the gist's ten problems do not disappear because HMCL changed.

## 6. 核对方法 | How to verify

```bash
git clone --depth 1 https://github.com/HMCL-dev/HMCL.git
cd HMCL
grep -rn "KOSMICKRISP\|kosmickrisp" --include=*.java --include=*.properties .
```

主要文件：`Renderer.java`、`LaunchOptions.java`、`DefaultLauncher.java`、`GameSettingsPage.java`、`HomebrewUtils.java`；中文文案在 `HMCL/src/main/resources/assets/lang/I18N_zh_Hans.properties`。

Key files: `Renderer.java`, `LaunchOptions.java`, `DefaultLauncher.java`, `GameSettingsPage.java`, `HomebrewUtils.java`; Chinese strings live in `HMCL/src/main/resources/assets/lang/I18N_zh_Hans.properties`.

补充：`Renderer.of()` 按枚举名解析，所以配置文件里存的是 `"KOSMICKRISP"`，不是 `"kosmickrisp_mesa"`。后者是 `icdName()`，只用于拼 ICD 文件名。

Note: `Renderer.of()` parses enum names, so the config stores `"KOSMICKRISP"`, not `"kosmickrisp_mesa"`. The latter is `icdName()`, used only to build the ICD filename.
