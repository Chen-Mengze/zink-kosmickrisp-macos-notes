# Test protocol (English)

Goal: **on Mesa main + !44928, what GL version does Zink actually report on KosmicKrisp, and what is missing?**

About 1–2 hours for the full track (a cold KK build is closer to two), plus 20–40 minutes if the checker also has to be built from scratch. No graphics development experience required.
The core steps do **not** launch a game or any GL application — `zink_check_requirements` queries the current Vulkan device and prints `Supported` / `UNSUPPORTED` per tier. That is a **conservative ceiling**: 3.0 and above follow hard gates, while 2.1 soft requirements (stock KK hides `VK_EXT_custom_border_color` behind `MESA_KK_EXPERIMENTAL=custom_border`) can make `gl21` report UNSUPPORTED even though Zink still reports 2.1. To confirm the actual GL version, run one GL app or `glxinfo` at the end.

---

## 0. Prerequisites

- Apple Silicon (M1–M6), macOS 26 or 27
- Xcode + Command Line Tools
- 15 GB free disk; a cold KK + Zink build takes about 1–2 hours (closer to two on an M1, faster on M4/M5)
- LunarG Vulkan SDK (`vulkaninfo`, and static `spirv-tools`; select the KosmicKrisp component during install and check that `$VULKAN_SDK/share/vulkan/icd.d/libkosmickrisp_icd.json` exists)
- Network access to `gitlab.freedesktop.org`

This is a one-off measurement. Unset the environment afterwards and the system is back to normal.

---

## 0.5 Check build A first (10 minutes to run; 20–40 minutes to build the tool from scratch)

Before touching KK, run the checker against the **stock SDK build** to confirm A misses the 3.0 hard gate. Expect `gl30` UNSUPPORTED; `gl21` may be Supported, or may fail on the 2.1 profile's WSI/soft requirements:

- Zink's 3.0 tier requires `VK_EXT_transform_feedback` and `VK_EXT_conditional_rendering`, with no "only fails when used" qualifier;
- !44928's description says adding it takes Zink on kk "from OpenGL 2.1 to 3.3 (ES 3.1)".

The 3.1 figure comes from an F3 screenshot that only shows the driver name; it has no GL version and cannot support the claim.

```bash
meson setup build-tools . --buildtype=release -Dplatforms=macos -Dtools=zink
ninja -C build-tools

# point the loader at KK explicitly, or it may enumerate MoltenVK first
export VULKAN_SDK=<the SDK's macOS directory>   # if setup-env.sh has not been sourced
export VK_DRIVER_FILES="$VULKAN_SDK/share/vulkan/icd.d/libkosmickrisp_icd.json"
# checker only: stock KK does not expose custom border by default, which fails every GL profile
export MESA_KK_EXPERIMENTAL=custom_border

./build-tools/src/gallium/drivers/zink/check_requirements/zink_check_requirements
```

It prints `Supported` / `UNSUPPORTED` per `VP_ZINK_*` profile. With both variables set, `gl21` may be Supported; `gl30` should still be UNSUPPORTED (no XFB). Even if `gl21` is UNSUPPORTED, that only means the strict 2.1 profile failed (it also requires `VK_KHR_incremental_present` and other WSI items); it does not mean Zink cannot report 2.1. It prints no version number and no missing-item table.

If `gl30` is also Supported, the SDK's KK already has XFB and the capability table needs changing. **Do this before spending 1–2 hours on build B+.**

---

## 1. Dependencies

```bash
brew install meson cmake pkg-config libclc llvm spirv-llvm-translator python@3

python3 -m venv ~/venv_mesa
source ~/venv_mesa/bin/activate
pip install mako packaging pyyaml

llvm-config --version     # must be >= 20.1.8
```

Prefer the static `spirv-tools` from the Vulkan SDK; the Homebrew package is usually shared-only.

---

## 2. Source + !44928

```bash
git clone https://gitlab.freedesktop.org/mesa/mesa.git ~/mesa-kk
cd ~/mesa-kk

git fetch origin refs/merge-requests/44928/head:mr44928
git checkout -b kk-xfb mr44928

git log --oneline -3 | tee ~/kk-commit.txt   # include this in your report
```

---

## 3. Build KosmicKrisp

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

`-Dgallium-drivers=` is intentionally empty: this builds KK only, no GL driver.

---

## 4. Activate it and dump capabilities

```bash
find build-kk -name '*.json' | grep -i -E 'icd|kosmic'

export VK_DRIVER_FILES=<absolute path to that json>
export MESA_SHADER_CACHE_DIR=~/kk-cache-$(date +%s)
unset MESA_KK_EXPERIMENTAL   # stock behaviour for vulkaninfo; step 5 sets custom_border for the checker only

vulkaninfo --json > ~/kk-xfb.json

grep -c VK_EXT_transform_feedback ~/kk-xfb.json   # expect >= 1
vulkaninfo | grep -E 'driverName|driverInfo|apiVersion'
```

A count of 0 is a valid result — report it and skip to step 6.

---

## 5. Read the per-tier result (the actual evidence)

```bash
meson setup build-zink . --buildtype=release -Dplatforms=macos -Dtools=zink
ninja -C build-zink

# checker only: lets the 2.1 profile's custom-border soft requirement pass; do not set it for the app
export MESA_KK_EXPERIMENTAL=custom_border

# no arguments: enumerate the compiled-in profiles and check the current device
./build-zink/src/gallium/drivers/zink/check_requirements/zink_check_requirements \
  | tee ~/kk-zink-requirements.txt
```

The output reads `Checking profile VP_ZINK_gl33_baseline` followed by `Supported` / `UNSUPPORTED physical device`. **The highest Supported tier is a conservative ceiling**: `gl21` = 2.1, `gl30` = 3.0, `gl33` = 3.3, `gl46` = 4.6. The 2.1 soft requirements can make `gl21` read low; use the version an app reports as the actual value.

It prints neither a version number nor a missing-item table. For missing items, compare `~/kk-xfb.json` against `VP_ZINK_requirements.json`, or run:

```bash
python tools/kkcap.py one ~/kk-xfb.json --md
```

**Record two things**: the highest Supported profile (a conservative ceiling), and whether `VK_EXT_transform_feedback` / `geometryShader` appear in `vulkaninfo`.

---

## 6. Report (post on !44928)

```
Chip / macOS:        M1 Pro / 26.2
Build:               mesa main @ <base commit>, MR !44928 head <sha>
driverName / API:    KosmicKrisp / 1.4.xxx
vulkaninfo XFB:      present | absent
Zink profile ceiling: 3.3 | 2.1 | ... (checker conservative value; add the actual GL version)
Missing (hard):      <items>
Missing (unchecked): <items>
Crashes / validation errors: none | <short>
```

Attach `kk-xfb.json`, `kk-zink-requirements.txt`, `kk-commit.txt`.
Strip usernames and absolute paths before posting.

---

## 7. Optional: run one workload

Only this step needs injection, and it is where most attempts fail. Keep it out of the core goal.

### What the HMCL KK toggle actually does

It is an enum constant `KOSMICKRISP` inside `Renderer.Vulkan`. When selected, launch does three things:

1. adds `-Dorg.lwjgl.vulkan.libname=<Homebrew libvulkan.1.dylib>`, bypassing LWJGL's bundled MoltenVK;
2. sets `VK_ICD_FILENAMES` / `VK_DRIVER_FILES` to the absolute ICD path;
3. appends `--graphicsBackend vulkan` for versions ≥ `26.2-snapshot-2`.

All three serve the Vulkan backend only. The GL path gets none of them:

| What HMCL does | Useful for the GL path? |
|---|---|
| Selects an ICD | No: GL calls never enter Vulkan |
| Swaps the Vulkan loader | No: that is the Vulkan loader, not `libGL` |
| Passes `--graphicsBackend vulkan` | The opposite: it pushes the game away from GL |

One more trap: `Renderer.OpenGL.ZINK` **is visible** on macOS, but the macOS branch of `generateEnvVars()` only handles `Renderer.Vulkan`. Selecting it is a no-op and silently falls back to Apple GL. Do not read “Mesa Zink is in the list” as “it is wired up”.

Detection runs in a static initializer: after installing KK, HMCL must be restarted before the option appears.

### Order to try

1. **JVM property first**: confirm MC is not on the Vulkan backend, add `-Dorg.lwjgl.opengl.libname=<absolute path to libGL.dylib>`.
2. **Then interpose**: `DYLD_INSERT_LIBRARIES` plus a `dlsym` hook on `glGenBuffers` (the route the gist's ten problems took). Expect `NSViewBackingLayer` → `CAMetalLayer` replacement and `dispatch_sync_f()` on the main thread; not a ten-minute job.
3. **Failing both is still a result.** Paste the error; don't change renderer behaviour to force it through.

Press F3: the top-right must read KosmicKrisp. If it reads Apple, the run is a silent fallback and invalid.

- **Any other GL app**: requires a small program linked against Mesa's `libEGL`/`libGL`; higher cost than the above.
- Record four columns: compiles / draws / correct / error.

---

## 8. Known traps

| Symptom | Cause | Fix |
|---|---|---|
| Segfault on start | Two ICDs loaded at once | Keep only `VK_DRIVER_FILES`; unset `VK_ICD_FILENAMES` |
| Crashes on second launch | Old KK disk cache stores process-local PSO pointers | New `MESA_SHADER_CACHE_DIR`, or `MESA_SHADER_CACHE_DISABLE=true` |
| Looks fine, performs like integrated graphics | Silent fallback to Apple GL | Check the driver name, not the frame rate |
| Extra features appear | `MESA_KK_EXPERIMENTAL` leaking | Unset it; it is process-wide |
| Build fails | Old `llvm-config` / missing static spirv-tools | Back to step 1 |

---

## 9. Negative results count

Build failure, `vulkaninfo` crash, or a GL version that goes *down* — paste the raw error. The value of this run is that it is the first time these three artifacts are aligned on one machine, not that the answer is good news.
