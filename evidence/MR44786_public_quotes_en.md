# Mesa !44786 — Public Quote Sheet

Source: https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44786

Only the shortest quotes needed to verify the conclusions. Page text belongs to its respective speakers (the MR description to Junmin Lee, comments to their authors) and does not follow the code licence; full context, timeline and unquoted discussion are at the link above. Site chrome, avatars and icons are not included. Personal email addresses have been removed.

---

## Page status and the framing sentence

```text
Merged
kk: Add geometry shader support
Junmin Lee requested to merge junminlee2004/mesa:kk-geometry into main
40 commits / 6 pipelines / 15 reports
```

> "This MR adds geometry shader support to the KosmicKrisp Vulkan driver
> (mesa/mesa#14251) by wiring up poly's existing emulation used by
> Honeykrisp for KosmicKrisp."  — Junmin Lee, MR description

The description lists four additional changes: exact-thread indirect compute dispatch, adjacency index rewriting for pipelines without a GS, tess→GS primitive ID, and GS side effects running once with the fence after image stores stripped. The main note paraphrases these as facts instead of copying the block; see the link for the original text.

## Merge record

```text
Merged by: Marge Bot (2026-10-29 22:39:18 GMT+8)
Changes from 14f59d06 merged into main.
14f59d06 - kk: Advertise geometryShader
Aitor Camacho assigned to @marge-bot
Marge Bot merged
```

Key commit titles from the final push (factual information):

```text
kk: Add exact-thread indirect compute dispatch
kk: Implement geometry shaders with poly
kk: Draw adjacency topologies without a geometry shader
poly: Strip KosmicKrisp image fences with geometry shader stores
poly: Use the patch index as the geometry shader primitive ID
kk: Advertise geometryShader
```

## Short comments

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

Scope of citation and takedown channel: `../CREDITS_AND_LICENSE_en.md`.
