# Credits, Licence and Citation Notes

For anyone reposting, quoting, or pulling this material into their own project. The aim is simple: let these notes circulate publicly without bundling other people's full-page archives or proprietary artefacts. The only third-party image retained is one F3 screenshot used to establish the driver name; its scope of use is below.

## What we wrote ourselves

- `Zink_KosmicKrisp_on_macOS_EN.md` (the English text, including the analysis conclusions folded into Appendix E.2)
- the arrangement and annotations in `证据/MR44786_public_quotes_EN.md`
- `证据/F3_transcript_EN.md` and `证据/How_to_reproduce_disassembly_EN.md`
- the Chinese counterparts: `macOS上跑Zink和KosmicKrisp_工程笔记.md`, `版权与引用说明.md`, and the Chinese evidence files

All of the above are released under **CC BY 4.0**: repost, split, rewrite, use in docs or a wiki, just credit the source. Use the author name shown at the place of publication for attribution.

This notice is CC BY 4.0 as well.

## Third-party material

Technical facts, version dates, CTS counts, patch numbers, commit titles and short discussion quotes come from the public sources below. Copyright stays with their respective authors or projects. **We use factual citation, short quotes and links only — no copied passages, full-page archives or code**; the one exception is the F3 screenshot in the last row.

| Source | What we took | Where |
|---|---|---|
| Mesa / GitLab !44786, !44928 | the framing sentence from the MR description, merge time, commit titles, a few short comments | https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44786 , https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44928 |
| Mesa docs, release notes, release calendar | Zink's per-tier requirements, branch cut dates, 26.3.1 `New features: None` | https://docs.mesa3d.org/drivers/zink.html , https://mesa3d.org/release-calendar.html |
| LunarG / Khronos | KK's positioning, 1.4 conformance, bundle layout, MVK deprecation | https://www.lunarg.com/products/kosmickrisp , https://www.khronos.org/news/archives/kosmickrisp-achieves-vulkan-1.4-conformance-on-apple-silicon |
| Blender developer portal | GS limitation on macOS, experimental positioning | https://developer.blender.org/docs/features/gpu/vulkan/kosmic_krisp |
| Mojira MC-311557, Minecraft Feedback | timing of the structural issue and the community proposal | https://bugs.mojang.com/browse/MC/issues/MC-311557 , https://feedback.minecraft.net/hc/en-us/community/posts/44920984456717-Using-kosmickrisp-instead-of-moltenvk-for-vulkan-in-macos |
| GitHub Gist *Running Minecraft on macOS with Zink + KosmicKrisp* | conclusions of the nine debug problems, 70fps, 2–3% | see the Gist itself; the text paraphrases facts only |
| Hadron `findings.md` / conformance records, Playport 0087 / 0093 | 0038–0083 numbering and conclusions, CTS counts, fans/quads result | each project's repo; the text paraphrases facts only |
| `pauyedin/kosmickrisp-minecraft-macos`, steamac | cache-key scheme, 0001–0003/0021, 63 patches | https://gitlab.com/pauyedin/kosmickrisp-minecraft-macos/-/tree/main and others |
| F3 screenshot provided by [Glavo](https://github.com/Glavo), HMCL maintainer | confirms the actual driver name, machine and picture state (`证据/截图2_M6_F3_KosmicKrisp.jpg`); the KK backend is exposed by HMCL and only shown / switchable once KK has been installed through a package manager | https://github.com/Glavo , https://glavo.site/about/ ; the image copyright stays with its respective rights holders |

Two things that are easy to get wrong:

- Mesa source is MIT, but **MR descriptions and comments are user-generated content whose text belongs to the speakers**; it doesn't automatically follow the code licence. That's why only the shortest necessary quotes are here, attributed, with links to full context.
- The community prior-art findings in the text are **paraphrased conclusions and numbers**, not copied passages. If you want their original text in your own document, check the licence in each repo.

Personal email addresses from public comments have been removed from this package. Both the F3 image and its transcript serve only to establish hardware, driver and version information: the picture contains no usernames, paths or account details, and nothing has been cropped or altered. The screenshot was provided and cleared for this purpose by [Glavo](https://github.com/Glavo), HMCL maintainer. The KK backend shown is exposed by HMCL: hidden by default, it only appears and can be switched on once KK is installed through a package manager. The image is factual illustration only — no product promotion, no derivative artwork. If the provider objects, use the takedown channel below.

## What is not bundled

The public release deliberately omits the following, because they are copies of third-party works or derivatives of proprietary content:

| Original | How to get it | Why not |
|---|---|---|
| Full-page GitLab !44786 archive (`.mht`, with site CSS, avatars, UI text) | save the page yourself from the MR link above | redistributing a whole page drags the site chrome, icons and avatars along |
| 647-line plain-text extract of that page | same | same; avoid a full-text copy |
| `renderpearl` disassembly (2457 lines) and its excerpt | generate via `证据/How_to_reproduce_disassembly_EN.md` | derivative of proprietary game-client bytecode, not shipped |
| Earlier disassembly conclusion draft | not needed; corrected conclusions are in the main text and Appendix E.2 | it contained bytecode fragments and local paths, and several judgements were later disproved |

**On the disassembly**: `证据/How_to_reproduce_disassembly_EN.md` gives a method, not an artefact. Before generating or using such output, satisfy yourself that it complies with the game EULA and applicable law. This package neither provides nor encourages distributing client bytecode or its disassembly.

**The F3 screenshot is bundled** (`证据/截图2_M6_F3_KosmicKrisp.jpg`) and inlined in the text. A separate transcript is provided for searchability. When reposting, keep the image together with its attribution and this notice; if the provider raises an objection, take it down via the channel below and fall back to `证据/F3_transcript_EN.md` (or `证据/F3_文字转录.md` for the Chinese version).

## Corrections, takedowns, reuse

- A factual paraphrase is wrong: leave a comment or open an issue where this is published; it'll be corrected against first-hand records.
- You wrote one of the quotes or findings, or you are the F3 screenshot's provider [Glavo](https://github.com/Glavo), and you'd rather not be quoted or shown: say so in the same place; it'll be removed or replaced with a link.
- You want to fold these notes into a wiki, documentation or your own project: CC BY 4.0, just credit it, no need to ask.

Put contact details at the place of publication (repo issues, a discussion thread, or email).

---

This is not legal advice. Before reposting to a particular platform, or bundling third-party material of your own, check that platform's rules and the licences of the material itself once more.
