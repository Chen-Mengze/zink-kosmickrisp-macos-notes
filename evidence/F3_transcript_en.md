# F3 Transcript

An F3 screen from an Apple Silicon Mac, provided by [Glavo](https://github.com/Glavo), maintainer of HMCL. The original screenshot ships with this package as `screenshot_M6_F3_KosmicKrisp.jpg`; this is a verbatim transcript of the relevant lines for search and copy, with no usernames, paths or account details.

```text
Minecraft 26.3 (26.3/vanilla)
Java: 25.0.5.0.3
CPU: 12x Apple M6
GPU: Apple M6 (iGPU)
Vulkan: 1.4.363 KosmicKrisp   Mesa 26.3.1
119 fps  T: 120 (fifo) @120Hz
```

How to read it:

- `Vulkan 1.4.363 KosmicKrisp` / `Mesa 26.3.1` are two independent version lines: the first is the Vulkan API version the driver reports (it follows the Vulkan-Headers version Mesa was built against), the second is the Mesa build version. Neither is the Vulkan SDK package version, and neither implies the other's capabilities. This build has no `geometryShader` (GS merged into main on 2026-10-29, while the 26.3 branch was cut on 10-14).
- What settles the case is the driver-name line, not `119 fps` — a silent fallback to Apple OpenGL runs at that rate too.
- `119 fps T: 120 (fifo)` is context for the picture, not a performance conclusion.

The KosmicKrisp backend shown here is exposed by HMCL: the option is hidden by default, and HMCL only displays it and allows switching once KosmicKrisp has been installed on the system through a package manager.

For the original image, see `screenshot_M6_F3_KosmicKrisp.jpg` in this directory. Image scope and takedown: `../CREDITS_AND_LICENSE_en.md`.
