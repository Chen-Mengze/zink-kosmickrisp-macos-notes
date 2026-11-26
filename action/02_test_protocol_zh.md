# 真机验证协议（中文）

目标只有一个：**在 Mesa main + !44928 上，Zink 到底能报到 GL 几？卡在哪一项？**

完整档约 1–2 小时（首次编 KK 偏上限）；若检查工具也要从零编，另加 20–40 分钟。不需要图形开发经验，会复制命令就行。
核心步骤**不需要启动任何游戏或应用**——`zink_check_requirements` 直接问当前 Vulkan 设备，逐档打 `Supported` / `UNSUPPORTED`。它给的是**保守上限**：3.0 以上按硬门槛，2.1 档的软要求（stock KK 的 `VK_EXT_custom_border_color` 藏在 `MESA_KK_EXPERIMENTAL=custom_border` 后面）可能让 `gl21` 报 UNSUPPORTED，但 Zink 实际仍可能报 2.1。要确认实际 GL 版本，最后跑一次 GL 应用或 `glxinfo`。

---

## 0. 前置条件

- Apple Silicon（M1–M6），macOS 26 或 27
- Xcode + Command Line Tools
- 磁盘 ≥ 15 GB；首次编 KK + Zink 约 1–2 小时（M1 冷构建偏上限，M4/M5 快一些）
- 已装 LunarG Vulkan SDK（要里面的 `vulkaninfo`，以及静态 `spirv-tools`；装的时候勾上 KosmicKrisp 组件，确认 `$VULKAN_SDK/share/vulkan/icd.d/libkosmickrisp_icd.json` 存在）
- 网络能访问 `gitlab.freedesktop.org`

> 不建议在你的日常系统上长期启用。这是一次性验证，跑完把环境变量删掉就回到原状。

---

## 0.5 先测构建 A（检查 10 分钟；从零编工具 20–40 分钟）

在动 KK 之前，先用**现成的 SDK 版本**跑一次检查工具，确认 A 的 3.0 硬门槛没过。预期 `gl30` UNSUPPORTED；`gl21` 可能 Supported，也可能因 2.1 profile 的 WSI/软要求报 UNSUPPORTED：

- Zink 的 3.0 档要求 `VK_EXT_transform_feedback` 和 `VK_EXT_conditional_rendering`，没有「用到才炸」的余地；
- !44928 的描述也写明，加上它才 “from OpenGL 2.1 to 3.3 (ES 3.1)”。

3.1 这个数来自一张只显示驱动名的 F3 截图，截图里没有 GL 版本，不能作为证据。

```bash
meson setup build-tools . --buildtype=release -Dplatforms=macos -Dtools=zink
ninja -C build-tools

# 必须显式指向 KK 的 ICD，否则 loader 可能先枚举到 MoltenVK
export VULKAN_SDK=<SDK 的 macOS 目录>   # 若还没 source setup-env.sh
export VK_DRIVER_FILES="$VULKAN_SDK/share/vulkan/icd.d/libkosmickrisp_icd.json"
# 只给 checker 用：stock KK 默认不暴露 custom border，会让所有 GL profile 一起 UNSUPPORTED
export MESA_KK_EXPERIMENTAL=custom_border

./build-tools/src/gallium/drivers/zink/check_requirements/zink_check_requirements
```

它会把 `VP_ZINK_*` profile 逐个打 `Supported` / `UNSUPPORTED`。设了上面两个变量后，`gl21` 可能 Supported；`gl30` 仍应 UNSUPPORTED（XFB 缺）。`gl21` 就算 UNSUPPORTED，也只说明 2.1 strict profile 没过（还要求 `VK_KHR_incremental_present` 等 WSI 项），不等于 Zink 报不到 2.1。它不打印版本号，也不打印缺项。

如果 `gl30` 也 Supported，说明 SDK 里的 KK 已经有 XFB，能力表要改。这一步不需要编 KK，**先做它，再决定要不要花 1–2 小时编 B+。**

---

## 1. 依赖

```bash
brew install meson cmake pkg-config libclc llvm spirv-llvm-translator python@3

python3 -m venv ~/venv_mesa
source ~/venv_mesa/bin/activate
pip install mako packaging pyyaml

llvm-config --version     # 必须 >= 20.1.8
```

`spirv-tools` 优先用 Vulkan SDK 里的静态库；Homebrew 的包通常只有动态库，可能不够。

---

## 2. 取代码，叠上 !44928

```bash
git clone https://gitlab.freedesktop.org/mesa/mesa.git ~/mesa-kk
cd ~/mesa-kk

git fetch origin refs/merge-requests/44928/head:mr44928
git checkout -b kk-xfb mr44928

git log --oneline -3 | tee ~/kk-commit.txt   # 回帖要贴这两行
```

如果 `refs/merge-requests/...` 拉不下来，用 MR 页面上的 "Check out branch" 命令。

---

## 3. 编 KosmicKrisp

```bash
meson setup build-kk . \
  --buildtype=release \
  -Dplatforms=macos \
  -Dvulkan-drivers=kosmickrisp \
  -Dgallium-drivers= \
  -Dopengl=false \
  -Dzstd=disabled \
  --prefer-static

ninja -C build-kk
```

> 这是官方文档的命令，`-Dgallium-drivers=` 是**空的**——这一条只编 KK，不编任何 GL 驱动。GL 侧另编。

---

## 4. 让它生效，并抓能力表

```bash
# 找到 ICD manifest（名字类似 kosmickrisp_mesa_driver.json）
find build-kk -name '*.json' | grep -i -E 'icd|kosmic'

export VK_DRIVER_FILES=<上面那个 json 的绝对路径>
export MESA_SHADER_CACHE_DIR=~/kk-cache-$(date +%s)   # 别复用旧缓存
unset MESA_KK_EXPERIMENTAL                            # 抓 vulkaninfo 用 stock 行为；第 5 步只给 checker 设 custom_border

vulkaninfo --json > ~/kk-xfb.json

grep -c VK_EXT_transform_feedback ~/kk-xfb.json       # 期望 >= 1
vulkaninfo | grep -E 'driverName|driverInfo|apiVersion'
```

如果 `grep` 结果是 0，说明这个 MR 没把 XFB 宣告出来——**这本身就是一个有效结果**，直接跳到第 6 步回帖。

---

## 5. 读逐档结果（核心证据）

```bash
meson setup build-zink . --buildtype=release -Dplatforms=macos -Dtools=zink
ninja -C build-zink

# 只给 checker 用：让 2.1 profile 的 custom border 软要求过关；不要给应用开
export MESA_KK_EXPERIMENTAL=custom_border

# 不带参数：枚举编译进去的 profile，逐个对当前设备检查
./build-zink/src/gallium/drivers/zink/check_requirements/zink_check_requirements \
  | tee ~/kk-zink-requirements.txt
```

输出形如 `Checking profile VP_ZINK_gl33_baseline` 加 `Supported` / `UNSUPPORTED physical device`。**最高的 Supported 档是保守上限**：`gl21` = 2.1，`gl30` = 3.0，`gl33` = 3.3，`gl46` = 4.6。2.1 档的软要求可能让 `gl21` 偏低，实际版本以应用报的为准。

它不打印版本号，也不打印缺项表。要缺项就把 `~/kk-xfb.json` 和 `VP_ZINK_requirements.json` 对照，或先跑：

```bash
python tools/kkcap.py one ~/kk-xfb.json --md
```

**要记下来的两件事**：最高 Supported 的 profile（保守上限）；`VK_EXT_transform_feedback` 和 `geometryShader` 在不在 `vulkaninfo` 里。

---

## 6. 回帖（贴到 !44928）

```
Chip / macOS:        M1 Pro / 26.2
Build:               mesa main @ <base commit>, MR !44928 head <sha>
driverName / API:    KosmicKrisp / 1.4.xxx
vulkaninfo XFB:      present | absent
Zink profile ceiling: 3.3 | 2.1 | ...（checker 保守值；实际 GL 版本另填）
Missing (hard):      <逐项>
Missing (unchecked): <逐项>
Crashes / validation errors: none | <简述>
```

附件：`kk-xfb.json`、`kk-zink-requirements.txt`、`kk-commit.txt`。
回帖前删掉日志里的用户名和绝对路径。

---

## 7. 可选：真跑一个应用

只有这一档需要处理注入，也是最容易失败的一步。别把它放在核心目标里。

### 先分清 HMCL 的 KK 开关管什么

它在 `Renderer.Vulkan` 里是一个枚举常量 `KOSMICKRISP`。选中后，启动时做三件事：

1. 加 `-Dorg.lwjgl.vulkan.libname=<Homebrew 的 libvulkan.1.dylib>`，绕开 LWJGL 自带的 MoltenVK；
2. 设 `VK_ICD_FILENAMES` / `VK_DRIVER_FILES` 为 ICD 绝对路径；
3. 版本 ≥ `26.2-snapshot-2` 时追加 `--graphicsBackend vulkan`。

这三件只服务 Vulkan 后端。GL 那条路一件都没做：

| HMCL 做的事 | 对 GL 路径有用吗 |
|---|---|
| 选 ICD | 没用：GL 调用根本没进 Vulkan |
| 换 Vulkan loader | 没用：那是 Vulkan 的 loader，不是 `libGL` |
| 传 `--graphicsBackend vulkan` | 反向：会把游戏推离 GL |

还有一个容易误判的点：`Renderer.OpenGL.ZINK` 在 macOS 上**是可见的**，但 `generateEnvVars()` 的 macOS 分支只处理 `Renderer.Vulkan`，选了等于空操作，最后静默回落到苹果 GL。别把「列表里有 Mesa Zink」当成「已经接通」。

检测是静态初始化：装完 KK 要重启 HMCL，选项才会出现。

### 试的顺序

1. **先试 JVM 参数**：确认 MC 不是 Vulkan 后端，加 `-Dorg.lwjgl.opengl.libname=<libGL.dylib 绝对路径>`。
2. **不行就上 interpose**：`DYLD_INSERT_LIBRARIES` + `dlsym` 钩 `glGenBuffers` 那套（Gist 的十问就是这么走通的）。这一步会碰到 `NSViewBackingLayer` → `CAMetalLayer` 的替换和主线程 `dispatch_sync_f()`，不是十分钟能搞定的。
3. **两步都失败也算结果**，把报错贴出来；不要为了跑通去改渲染器行为。

进游戏后按 F3，右上角必须显示 KosmicKrisp；显示 Apple 就是静默降级，结果作废。

- **其它 GL 应用**：需要一个链到 Mesa `libEGL`/`libGL` 的小程序，成本比上面高。
- 记录四列：编译通过 / 出画面 / 渲染正确 / 报错类型。

---

## 8. 已知会踩的坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 进程直接 segfault | 两套 ICD 同时被加载 | 只留 `VK_DRIVER_FILES` 指的那一个，清掉 `VK_ICD_FILENAMES` |
| 第二次启动崩 | KK 旧版磁盘缓存里存了进程相关 PSO 指针 | 换 `MESA_SHADER_CACHE_DIR`，或临时 `MESA_SHADER_CACHE_DISABLE=true` |
| 画面正常但性能像核显 | 静默降级回 Apple GL | 看 F3 / 日志里的驱动名，不看帧数 |
| 特性忽然多了 | `MESA_KK_EXPERIMENTAL` 污染 | 取消该变量，它作用于整个进程 |
| 编译过不了 | `llvm-config` 版本太低 / 缺静态 spirv-tools | 回到第 1 步 |

---

## 9. 失败也算结果

编译失败、`vulkaninfo` 崩、GL 版本反而降了——都把报错原文贴出来。这份数据的价值在于「第一次在同一台机器上把三件事对齐」，不在于结论必须是好消息。
