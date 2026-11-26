# Test protocol (English)

Goal: **on Mesa main + !44928, what GL version does Zink actually report on KosmicKrisp, and what is missing?**

About 40 minutes. No graphics development experience required.
The core steps do **not** launch a game or any GL application — `zink_check_requirements` computes the GL ceiling from the Vulkan capability table. Running an app is optional.

---

## 0. Prerequisites

- Apple Silicon (M1–M6), macOS 26 or 27
- Xcode + Command Line Tools
- 15 GB free disk; 15–25 min build
- LunarG Vulkan SDK (`vulkaninfo`, and static `spirv-tools`)
- Network access to `gitlab.freedesktop.org`

This is a one-off measurement. Unset the environment afterwards and the system is back to normal.

---

## 0.5 Check build A first (10 minutes, tool only, no KK build)

Before touching KK, run the checker against the **stock SDK build**. It answers the open question: why does build A (Mesa 26.3.1), which lacks XFB, report GL 3.1?

The Zink documentation attaches "some of these might not actually get verified" to **3.2 and 3.3**, while 3.0 is stated as "required to be exposed and fully supported". So there are three possibilities:

- The checker lists XFB as missing, yet the driver reports 3.1 → the 3.0 check is not actually enforced.
- The checker says XFB is present → the capability table in the notes is wrong, and the "two blockers" framing needs revision.
- The checker reports 2.1 → the observation "A reports 3.1" needs re-verification.

```bash
meson setup build-tools . --buildtype=release -Dplatforms=macos -Dtools=zink
ninja -C build-tools
./build-tools/src/gallium/drivers/zink/check_requirements/zink_check_requirements
```

No KK build, no special hardware. **Do this before spending 25 minutes on build B.**

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
unset MESA_KK_EXPERIMENTAL

vulkaninfo --json > ~/kk-xfb.json

grep -c VK_EXT_transform_feedback ~/kk-xfb.json   # expect >= 1
vulkaninfo | grep -E 'driverName|driverInfo|apiVersion'
```

A count of 0 is a valid result — report it and skip to step 6.

---

## 5. Compute the GL ceiling (the actual evidence)

```bash
meson setup build-zink . --buildtype=release -Dplatforms=macos -Dtools=zink
ninja -C build-zink

./build-zink/src/gallium/drivers/zink/check_requirements/zink_check_requirements --help

./build-zink/src/gallium/drivers/zink/check_requirements/zink_check_requirements \
  > ~/kk-zink-requirements.txt 2>&1
```

Fallback:

```bash
vkprofiles --compare VP_ZINK_requirements.json ~/kk-xfb.json > ~/kk-diff.txt
```

Record two things: the computed GL version, and whether the missing list contains `VK_EXT_transform_feedback` / `geometryShader`.

---

## 6. Report (post on !44928)

```
Chip / macOS:        M1 Pro / 26.2
Build:               mesa main @ <base commit>, MR !44928 head <sha>
driverName / API:    KosmicKrisp / 1.4.xxx
vulkaninfo XFB:      present | absent
Zink GL version:     4.6 core | 3.1 | ...
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
2. **Then interpose**: `DYLD_INSERT_LIBRARIES` plus a `dlsym` hook on `glGenBuffers` (the route the gist's nine problems took). Expect `NSViewBackingLayer` → `CAMetalLayer` replacement and `dispatch_sync_f()` on the main thread; not a ten-minute job.
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
