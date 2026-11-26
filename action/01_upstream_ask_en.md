# About 1–2 hours on an M-series Mac: does !44928 close the last gap?

**Where this stands.** `geometryShader` landed in `14f59d06` (!44786). `VK_EXT_transform_feedback` is still unmerged (!44928, open, head `e56f2e43`). Zink requires XFB at 3.0 and GS at 3.2, so a GS-only build is still GL 2.1; with both, the MR author reports 3.3.

**Why anyone should care.** macOS has been stuck at OpenGL 4.1 since 2013; the native stack has geometry shaders and transform feedback, but not the GL 4.2+ image/atomic features or the GL 4.3 compute/SSBO features that modern shaderpacks use. `Zink -> KosmicKrisp -> Metal 4` is the only open path past that ceiling on Apple Silicon. The two nearest gaps are capability bits: GS is in main, a third-party patch set reports GL 4.6 with 15,304 of 19,714 Khronos GL CTS tests passing (1 fail), and `zink_check_requirements` (!36061) checks every profile tier mechanically. Beyond those bits, 4.x still needs the Hadron patch set.

The user-facing path is wired too: HMCL already ships a conditional KosmicKrisp toggle that appears once KK is installed through a package manager. What it lacks is a package worth toggling on.

**What is missing is one measurement, not more design.** Nobody has published, on the same machine: main + !44928, `vulkaninfo --json`, the per-tier Zink result, and the resulting GL version. Every claim currently circulating ("GL 4.6 on KK") is either a patched tree, an override, or an unverified report.

There is also a number in circulation that needs correcting: a stock SDK build (Mesa 26.3.0-devel / Homebrew 26.3.1, no XFB) has been described as reporting GL 3.1. The upstream A/B says it can't — Zink's GL 3.0 tier requires `VK_EXT_transform_feedback`, and !44928's own description says it takes Zink on kk "from OpenGL 2.1 to 3.3". So A and B are 2.1 on the upstream tree. One `zink_check_requirements` run in ten minutes once the checker is built will show `VP_ZINK_gl30_baseline` UNSUPPORTED; `gl21` may also be UNSUPPORTED because stock KK hides `VK_EXT_custom_border_color` behind `MESA_KK_EXPERIMENTAL=custom_border`, so also report the GL version a real app prints.

**The ask — about 1–2 hours, any M1–M6 on macOS 26 or 27** (a cold build on an M1 is closer to two hours; a warm tree is faster):

1. `git fetch origin refs/merge-requests/44928/head:mr44928 && git checkout -b kk-xfb mr44928`
2. Build KK: `meson setup build-kk . -Dplatforms=macos -Dvulkan-drivers=kosmickrisp -Dgallium-drivers= -Dopengl=false -Dzstd=disabled --prefer-static && ninja -C build-kk`
3. `VK_DRIVER_FILES=<generated icd json>` then `vulkaninfo --json > kk.json`. Does it list `VK_EXT_transform_feedback`?
4. Build the checker (`-Dtools=zink`) and run `zink_check_requirements` against that device with `MESA_KK_EXPERIMENTAL=custom_border` set (checker only; stock KK otherwise fails every GL profile on the 2.1 soft requirements). Paste the per-tier `Supported` / `UNSUPPORTED` lines; the highest Supported tier is the conservative profile ceiling, not necessarily the driver's reported GL version — also attach the GL version a real app prints. It does not print a missing-items table — attach `vulkaninfo` and we'll diff it.
5. Optional: start one GL 3.3 workload (a `#version 330` shaderpack is ideal) and report four columns — compiles / draws / correct / error.

**A log is a result, and a negative result is the useful one.** If XFB is advertised but Zink still stops at 2.1, that is exactly the finding this needs.

**Highest-value configurations, in order:** M1 or M2 on macOS 26 (the KosmicKrisp docs flag this as where extension regressions concentrate, and it is the one nobody has reported); M5 or M6 on macOS 27 (the float16 `vector_geom` failure Aitor saw); anything else still counts.

Comment on !44928, or open an issue at
https://github.com/Chen-Mengze/zink-kosmickrisp-macos-notes

Protocol and report template: `03_test_protocol_en.md` in this folder.
