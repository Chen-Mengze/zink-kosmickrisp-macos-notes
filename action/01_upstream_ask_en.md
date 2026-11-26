# One hour of M-series time: does !44928 close the last gap?

**Where this stands.** `geometryShader` landed in `14f59d06` (!44786). KosmicKrisp now advertises it, so Zink's GL 3.2 gate is clear in principle. `VK_EXT_transform_feedback` is still a draft (!44928). Zink's GL 3.0 requirement list includes it, which means GL 3.2+ is not reachable in practice until it lands — and GL 4.x is gated on both.

**Why anyone should care.** macOS has been stuck at OpenGL 4.1 since 2013, and Apple's 3.2 core profile never shipped geometry shaders at all. `Zink -> KosmicKrisp -> Metal 4` is the only open path to GL 4.6 on Apple Silicon. Everything except these two capability bits is already in place: GS is in main, a third-party patch set reports GL 4.6 with 15,304 of 19,714 Khronos GL CTS tests passing (1 fail), and `zink_check_requirements` (!36061) can produce the capability diff mechanically.

The user-facing path is wired too: HMCL already ships a conditional KosmicKrisp toggle that appears once KK is installed through a package manager. What it lacks is a package worth toggling on.

**What is missing is one measurement, not more design.** Nobody has published, on the same machine: main + !44928, `vulkaninfo --json`, the Zink requirement diff, and the resulting GL version. Every claim currently circulating ("GL 4.6 on KK") is either a patched tree, an override, or an unverified report.

There is also a concrete anomaly worth ten minutes on its own: a stock SDK build (Mesa 26.3.1, no XFB) has been observed reporting GL 3.1, while the Zink docs list XFB as *required and fully supported* for 3.0. Either that check is not enforced at runtime, or the observation is wrong. One `zink_check_requirements` run against the stock driver settles it — no KK build needed.

**The ask — about 40 minutes, any M1–M6 on macOS 26 or 27:**

1. `git fetch origin refs/merge-requests/44928/head:mr44928 && git checkout -b kk-xfb mr44928`
2. Build KK: `meson setup build-kk . -Dplatforms=macos -Dvulkan-drivers=kosmickrisp -Dgallium-drivers= -Dopengl=false -Dzstd=disabled --prefer-static && ninja -C build-kk`
3. `VK_DRIVER_FILES=<generated icd json>` then `vulkaninfo --json > kk.json`. Does it list `VK_EXT_transform_feedback`?
4. Build the checker (`-Dtools=zink`) and run `zink_check_requirements` against that device. Paste the missing-items table and the GL version it computes.
5. Optional: start one GL 4.6 workload and report four columns — compiles / draws / correct / error.

**A log is a result, and a negative result is the useful one.** If XFB is advertised but Zink still reports 3.1, that is exactly the finding this needs.

**Highest-value configurations, in order:** M1 or M2 on macOS 26 (the KosmicKrisp docs flag this as where extension regressions concentrate, and it is the one nobody has reported); M5 or M6 on macOS 27 (the float16 `vector_geom` failure Aitor saw); anything else still counts.

Comment on !44928, or open an issue at
https://github.com/Chen-Mengze/zink-kosmickrisp-macos-notes

Protocol and report template: `03_test_protocol_en.md` in this folder.
