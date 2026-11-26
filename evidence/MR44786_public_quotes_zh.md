# Mesa !44786 公开引用摘录

出处：https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44786

这里只留核对结论所必需的最短引用。页面文字版权归各自发言者（MR 描述归 Junmin Lee，评论归各发言人），不随代码许可走；完整上下文、时间线和未引用的讨论请点上面的链接。站点界面文案、头像、图标等一概未收录。个人邮箱已去掉。

---

## 页面状态与计数（按 GitLab API 核对）

```text
已合并
kk: Add geometry shader support
Junmin Lee 请求合并 junminlee2004/mesa:kk-geometry 到 main
6 提交 / 15 流水线 / 40 条评论
```

> "This MR adds geometry shader support to the KosmicKrisp Vulkan driver
> (mesa/mesa#14251) by wiring up poly's existing emulation used by
> Honeykrisp for KosmicKrisp."  — Junmin Lee, MR description

描述里另列了四条附加改动：exact-thread 间接 compute dispatch、无 GS 管线的 adjacency 索引重写、tess→GS 的 primitive ID、GS side effects 只执行一次并剥掉 image store 后的 fence。这四条在笔记正文按事实转述，不整段复制；需要原文请点链接。

## 合并记录

```text
合并者: Marge Bot (2026年10月29日 GMT+8 22:39:18)
已合并到 main 的 14f59d06 的变更。
14f59d06 - kk: Advertise geometryShader
Aitor Camacho assigned to @marge-bot
Marge Bot merged
```

计数说明：提交数、流水线数与评论数按 GitLab API 于 2026-11-27 核对（6 / 15 / 40）。14f59d06 是源分支 head，合入方式为 fast-forward，没有单独的 merge commit。

最终一批里的关键提交标题（事实信息）：

```text
kk: Add exact-thread indirect compute dispatch
kk: Implement geometry shaders with poly
kk: Draw adjacency topologies without a geometry shader
poly: Strip KosmicKrisp image fences with geometry shader stores
poly: Use the patch index as the geometry shader primitive ID
kk: Advertise geometryShader
```

## 讨论短句

```text
squidbus: As mentioned in the description, I ran full CTS on an M4 Max and
          did not encounter any failures.

Mary Guillemard: poly patch is Reviewed-by: Mary Guillemard

Aitor Camacho: Currently seeing a failure in
          dEQP-VK.spirv_assembly.instruction.graphics.float16.logical_nan.opfordequal_vector_geom
          with M5 Pro on macOS 27. I'll try to find some time to investigate,
          probably a Metal compiler bug not present in M3-4.

Aitor Camacho: Enabling geometryShader should be the last commit. Mostly to
          facilitate bisections in the future.

Junmin Lee: I've now removed the mentioned poly changes for a separate MR and
          reordered the commits so enabling GeometryShader is the last commit.

Willie Abrams: I have transform feedback working on top of this MR. Should I
          open it as a draft on top of this now, or wait until this lands?

Willie Abrams: Here is a draft: !44928 Implement VK_EXT_transform_feedback

Mary Guillemard: Working fine on HK and fixing
          dEQP-VK.geometry.builtin_variable.primitive_id.matching too.
          Reviewed-by: Mary Guillemard for poly patches.
```

---

引用范围与移除渠道见根目录 `CREDITS_AND_LICENSE_zh.md`。
