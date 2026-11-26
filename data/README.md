# 数据

真机记录，一条一个目录。目录名格式：

```
YYYY-MM-DD_<芯片>_macOS<版本>_<构建>
例：2026-12-01_M1Pro_macOS26.2_B
```

## 一条记录里有什么

| 文件 | 必需 | 内容 |
|---|---|---|
| `kk.json` | 是 | `vulkaninfo --json` 原样输出，不要手改 |
| `kk.json.meta.json` | 是 | 机器、系统、构建、commit、GL 版本 |
| `requirements.txt` | 是 | `zink_check_requirements` 的逐档输出（Supported / UNSUPPORTED） |
| `notes.md` | 否 | 异常、复现步骤、截图说明 |
| `screenshot.png` | 否 | F3 或驱动信息截图，必须能读到驱动名 |

`kk.json.meta.json` 的字段（`tools/kkcap.py` 直接认这个命名）：

```json
{
  "chip": "Apple M1 Pro",
  "macos": "26.2",
  "build": "B (main + 14f59d06)",
  "commit": "14f59d06",
  "mr": "!44928 head <sha>",
  "date": "2026-12-01",
  "tester": "github handle（可留空）",
  "gl": "3.2",
  "gl_source": "zink_check_requirements / MESA_GL_VERSION_OVERRIDE / 目测",
  "samples": [
    {
      "name": "pack 名 + 版本",
      "compiles": true,
      "draws": true,
      "correct": false,
      "error": "第一条错误原文"
    }
  ],
  "perf": {
    "baseline": "Apple GL 4.1 / 平均帧 / 1% low",
    "zink_kk": "平均帧 / 1% low / 尖峰次数"
  },
  "notes": "一句话"
}
```

`gl_source` 必填。`MESA_GL_VERSION_OVERRIDE` 出来的数字要标出来，不能和真能力混在一起。

## 提交前

- 删掉日志里的用户名、绝对路径、任何账号信息。
- 确认 `kk.json` 里的 `driverName` 是 `KosmicKrisp`；是 `Apple` 就说明静默降级了，这条记录无效。
- 一次提交只放一条记录，不要混机型。

## 提交方式

- 会 git：开 PR，目录按上面的命名。
- 不会 git：用 issue 模板「真机记录」，把 JSON 作为附件贴进去。

## 汇总

```bash
python tools/kkcap.py matrix data/*/kk.json
```

输出一张跨机型表，直接贴进 `STATUS.md`。

## 许可

提交即表示同意这些能力数据以 CC BY 4.0 公开汇总（不含日志里的个人信息）。不想公开就写一句「仅供核对」，照样有用。
