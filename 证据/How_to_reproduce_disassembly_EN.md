# How to Reproduce the `renderpearl` Static Analysis

This file gives a method only and contains no disassembly output. Everything used in "The chain, and two integration traps" and Appendix E.2 can be checked with the steps below; version information is publicly verifiable and needs no material from anyone else.

**Boundary first**: the client jar and its bytecode are proprietary content, and a disassembly is a derivative of it. Satisfy yourself that this complies with the game EULA and applicable law, keep the output on your own machine for research or interoperability analysis, and don't ship it with documents, repos or public packages. This package neither provides nor encourages distributing such output.

## 1. Get the jar

Download the client jar for the version in question with the official launcher or from the version manifest (`downloads.client.url` in the version JSON) and put it in a local directory. No Mac required — Windows and Linux both work, a jar is a zip.

## 2. Locate the classes

```bash
unzip -l <client.jar> | grep 'com/mojang/renderpearl/backend/vulkan/'
```

The ones that matter:

- `VulkanBackend.class` — loading, `findPhysicalDevice`, `createDevice`
- `VulkanInstance.class` — instance extension construction
- `VulkanDevice.class` — device and capability queries
- `VulkanFeatureSets.class` — the required / requiredIfAvailable / optional sets
- `init/FeatureSet.class` — `isSupported` / `checkCondition`

`net/minecraft/client/Minecraft.class`, `Options.class` and `main/Main.class` hold the graphics-backend preference and validation-switch strings, if you want them too.

## 3. Read the bytecode

With a JDK installed:

```bash
unzip -o <client.jar> 'com/mojang/renderpearl/backend/vulkan/*' -d classes/
javap -c -p -classpath classes com.mojang.renderpearl.backend.vulkan.VulkanBackend
javap -c -p -classpath classes com.mojang.renderpearl.backend.vulkan.VulkanFeatureSets
javap -c -p -classpath classes com.mojang.renderpearl.backend.vulkan.VulkanInstance
```

CFR or Vineflower give a source-like view, but **for conditional branches `javap -c` is more reliable**: it isn't affected by obfuscation or variable names, and shows directly whether a string constant is skipped by an `ifeq`.

Without a JDK it's still doable: a class file is a standard format, so pull the `.class` entries out with any zip library, parse the constant pool (note that Long/Double take two slots) and disassemble the `Code` attribute — plain standard-library code is enough.

## 4. Check each item against Appendix E.2

| Where | What to look for |
|---|---|
| `VulkanBackend.loadLibrary()` | is `SDL_Vulkan_LoadLibrary` given `SharedLibrary.getPath()` or a literal path; are the two `vkGetInstanceProcAddr` addresses compared, with an exception and unload on mismatch |
| `VulkanBackend.createDevice()` | does it call `VulkanUtils.enumerateExtensions` first, then run `FeatureSet.isSupported` over each item, adding and logging `Enabling ... FeatureSet` only on success |
| `VulkanFeatureSets` | what the three set methods return; whether `optionalFeatureSets()` has exactly six entries |
| `VulkanInstance.<init>` | is `VK_KHR_portability_enumeration` excluded during iteration and added back conditionally on `IS_MACOS && available.contains(...)`, or added unconditionally |
| Preflight failure path | the catch branch of `isVulkanLoaderAvailable()`, and whether backend selection falls back to OpenGL |

## 5. Keep the output out of public packages

Leave `classes/` and the disassembly on your machine. Write conclusions as "which method, what condition, what result", as Appendix E.2 does; class names, method names and string constants are factual descriptions, but don't paste blocks of bytecode into public documents.

---

Licence and citation scope: `../CREDITS_AND_LICENSE_EN.md`.
