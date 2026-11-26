# 如何自行复现 `renderpearl` 的静态分析

这份文件只给方法，不带任何反汇编产物。笔记正文「链路，两个会踩的坑」和附录 E.2 用到的事实，都可以按下面步骤自己验一遍；版本相关的内容人人可查，不需要别人给材料。

**先说边界**：客户端 jar 及其字节码属于专有内容，反汇编是它的派生件。请自行确认这样做符合游戏 EULA 与适用法律，产物只留在自己机器上用于研究或互操作分析，不要随文档、仓库或公开包分发。本包不提供、也不鼓励分发这类产物。

## 1. 拿到 jar

用官方启动器或版本清单下载对应版本的 client jar（版本 JSON 里 `downloads.client.url`），放在本地目录即可。不需要 Mac，Windows / Linux 都能做，jar 是 zip。

## 2. 定位类

```bash
unzip -l <client.jar> | grep 'com/mojang/renderpearl/backend/vulkan/'
```

要看的是这几个：

- `VulkanBackend.class` — 装载、`findPhysicalDevice`、`createDevice`
- `VulkanInstance.class` — instance 扩展构造
- `VulkanDevice.class` — 设备与能力查询
- `VulkanFeatureSets.class` — required / requiredIfAvailable / optional 三组集合
- `init/FeatureSet.class` — `isSupported` / `checkCondition`

另外 `net/minecraft/client/Minecraft.class`、`Options.class`、`main/Main.class` 里有图形后端偏好与 validation 开关的字符串，想顺带看可以一起取。

## 3. 取字节码

有 JDK 时最直接：

```bash
unzip -o <client.jar> 'com/mojang/renderpearl/backend/vulkan/*' -d classes/
javap -c -p -classpath classes com.mojang.renderpearl.backend.vulkan.VulkanBackend
javap -c -p -classpath classes com.mojang.renderpearl.backend.vulkan.VulkanFeatureSets
javap -c -p -classpath classes com.mojang.renderpearl.backend.vulkan.VulkanInstance
```

想看源码形态可以换 CFR / Vineflower，但**判断条件分支用 `javap -c` 更可靠**：不受混淆和变量名影响，能直接看到某个字符串常量有没有被 `ifeq` 跳过。

没有 JDK 也能做：class 文件是标准格式，用任意 zip 库取出 `.class`，解析常量池（注意 Long/Double 占两个槽）再反汇编 `Code` 属性即可，纯标准库就能写。

## 4. 对着附录 E.2 逐条确认

| 看哪里 | 找什么 |
|---|---|
| `VulkanBackend.loadLibrary()` | 传给 `SDL_Vulkan_LoadLibrary` 的是 `SharedLibrary.getPath()` 还是字面量路径；随后有没有取两次 `vkGetInstanceProcAddr` 地址做比较、不等就抛异常并 unload |
| `VulkanBackend.createDevice()` | 是否先 `VulkanUtils.enumerateExtensions`，再逐个 `FeatureSet.isSupported`，通过才 `Set.add` 并打 `Enabling ... FeatureSet` 日志 |
| `VulkanFeatureSets` | 三个集合方法各自返回什么；`optionalFeatureSets()` 是不是 6 项 |
| `VulkanInstance.<init>` | `VK_KHR_portability_enumeration` 是遍历时先排除、再按 `IS_MACOS && available.contains(...)` 条件加回，还是无条件加入 |
| 预检失败路径 | `isVulkanLoaderAvailable()` 的 catch 分支、以及 backend 选择处是否回落 OpenGL |

## 5. 别把产物放进公开包

核对完把 `classes/` 和反汇编输出留在本地。要写结论就写「哪个方法、什么条件、结果如何」，像附录 E.2 那样；类名、方法名、字符串常量是事实描述，但整段字节码文本不要贴进公开文档。

---

许可与引用范围见根目录 `CREDITS_AND_LICENSE_zh.md`。
