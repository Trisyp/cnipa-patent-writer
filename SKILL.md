---
name: cnipa-patent-writer
description: >-
  撰写中国发明专利申请文档（.docx）：默认严格套用技能目录「参考模板.docx」五节版式（说明书摘要/
  摘要附图/权利要求书/说明书/说明书附图），无该模板时用用户模板或 CNIPA 四节兜底——**只借格式、
  绝不抄技术内容**。权利要求强制合计10条（多则合并不删创新点）；术语全篇一致；总页数≤45；内容据
  待保护技术方案重新生成。覆盖摘要·权利要求·说明书各章·附图。Use when user asks to write/draft/写/
  起草 patent/专利/发明专利/权利要求书/说明书，或「套用参考模板」「把项目写成专利」。
---

# 中国发明专利撰写（套用模板格式 / 无模板按 CNIPA 标准）

帮助撰写一篇**新的**发明专利申请文档（`.docx`）：套用页眉/页脚、分节、字体字号、缩进行距、分页与附图编排
等**版式**，但**内容据待保护的技术方案重新写**——模板只提供格式与行文风格，**其技术内容一律不抄**。

## 技能路径与调用

- 个人技能目录：`~/.cursor/skills/cnipa-patent-writer/`（本 `SKILL.md` 所在目录记为 `SKILL_ROOT`）。
- 下次使用：对话中说「写专利」「起草发明专利」「把这个项目写成专利」等即可自动匹配；也可在消息里 `@cnipa-patent-writer` 手动附加。
- **运行脚本/读参考**：下文 `scripts/`、`references/` 均相对 `SKILL_ROOT`；从任意项目工作时用绝对路径，例如
  `python ~/.cursor/skills/cnipa-patent-writer/scripts/inspect_template.py 模板.docx`。
- 依赖：`pip install -r ~/.cursor/skills/cnipa-patent-writer/requirements.txt`（缺包先装）。
- **产物**（`.docx`、配图 PNG、校验页图）写在**当前项目目录**，不要写进 `SKILL_ROOT`。

## 何时用 / 输入
- **默认**：技术方案 + 技能自带 `参考模板.docx` → `build_patent.py`，五节版式 1:1。
- 用户另给模板 `.docx`：以用户模板为准（同样只借格式）。
- 完全无模板：`build_patent_cnipa.py` 四节兜底。
- 目标：排版对齐模板、权利要求 10 条、术语一致、总页数 ≤45 的可提交 `.docx`。

## 依赖（缺则先装；装包注意 proxy）
- 必装：`python-docx`、`matplotlib`、`Pillow`、`math2docx`（`pip install -r requirements.txt`）。
  `math2docx` 负责把正文里的 `$...$` / `\(...\)` LaTeX 转为 Word 原生公式(OMML)。
- 可选：`graphviz`（用 `gen_figures_graphviz.py` 画复杂流程/架构图时）——除 `pip install graphviz`（python 封装）
  外**还需系统二进制 `dot`**：`sudo apt-get install -y graphviz`，否则渲染报错。不画 graphviz 图则无需安装。
- **CJK 字体**：matplotlib/graphviz 画中文必须有中文字体（如 Noto Sans CJK / 宋体），否则中文渲染成豆腐块。
- **可视化校验工具**（强烈建议）：`libreoffice-writer`（提供 `soffice`，docx→pdf）+ `poppler-utils`
  （提供 `pdftoppm`，pdf→png）+ 中文字体（如 `fonts-noto-cjk`，或把 Windows 宋体/黑体拷进 `~/.fonts` 后
  `fc-cache -f`）。这些一般需 `sudo apt-get install`；无 sudo 时请用户手动装。

## 核心原则（先读这几条，避免返工）
1. **版式严格对齐 `参考模板.docx`（有模板时）**：技能目录已放默认模板
   `~/.cursor/skills/cnipa-patent-writer/参考模板.docx`。该模板为**五节**：说明书摘要 / **摘要附图** /
   权利要求书 / 说明书 / 说明书附图。装配必须复刻其页眉、分节、页脚页码、字体字号、缩进与行距（宋体小四、
   1.5 倍行距、首行缩进等以 `inspect_template.py` 实测为准）。用户另给模板时以用户模板为准；**只借格式，
   绝不抄模板技术内容**。
2. **权利要求合计 10 条；多则合并、禁止删创新点**：默认骨架见 `references/claims-quality.md`
   （方法独立1 + 从属2–7 + 多引8 + 系统9 + 设备/介质10）。草稿 >10 条时把同一步骤细化、并行可选、弱从属
   **合并进既有项的分号子句**，确保每个区别技术点仍在 1–10 某条中出现。
3. **术语前后一致 + 思路严谨连贯**：动笔前锁定术语表；claim ↔ 发明内容「进一步地」↔ 实施例
   **同一概念同一用词**（体裁不同：正式权项句式只在权利要求书）。叙述链：背景痛点 → 必要特征 → 从属完善
   → 实施例可实施，无逻辑跳跃。
4. **正式权利要求只写一遍；总页数 ≤45**：禁止在发明内容/实施例粘贴「根据权利要求…」「1.一种…其特征在于」。
   发明内容用步骤概述 +「进一步地」；优点写在发明内容末「显著优点（1）（2）…」（**无**独立有益效果标题）；
   超页优先去重（见 `writing-style.md` 第四节）。
5. **只借格式、绝不抄技术内容**：模板的技术方案、模块名、步骤编排、配图种类一律不得搬入新专利；
   一切文本与配图据用户真实方案生成。
6. **结构校验 ≠ 视觉校验**：完稿必须 `render_check.py` 逐页看页眉/页码/豆腐块/图越界（见第7步）。
7. **权利要求上位、参数进实施例**：claims 用「预设阈值」等上位词；真实数值/型号只在实施例「例如/优选」。
8. **创新点进权利要求1**：最硬区别特征写入独立项必要特征，不藏从属。
9. **公式手工 `$...$` LaTeX**；涉 AI/模型时说明书写清模块或输入—输出关联（指南 2025 修改，见 claims-quality）。
10. **授权加固三重视角**：审查员（新颖性/创造性/支持）+ 数学（量纲/边界）+ 业务闭环（异常复核/质量评分）。

## 工作流

### 1. 学习格式基准（务必先做）
读 `references/docx-format.md` 与 `references/cnipa-format-spec.md`。然后：
- **默认模板**：`SKILL_ROOT/参考模板.docx`（用户未另给模板时必须用它）。
- 跑 `python scripts/inspect_template.py 参考模板.docx`（或用户模板）扒版式——**确认节数与页眉**
  （参考模板为五节：说明书摘要 / 摘要附图 / 权利要求书 / 说明书 / 说明书附图）、页脚页码、字体字号、
  缩进行距、正文段长。`build_patent.py` 按实测复刻；含「摘要附图」时须调用 `abstract_figure`。
- **无任何模板**：用 `build_patent_cnipa.py` + `cnipa-format-spec.md`（四节兜底）。
- `inspect_template.py` **只读版式，不复制技术内容**。

### 2. 与用户确认关键决策（动笔前）
- **发明名称**：凝练、含核心创新词。
- **独立权利要求1 落点**：端到端方法 / 最硬子方法 / 系统（通常方法独立 + 系统独立）。
- **技术细节颗粒度**：实施例真实参数还是脱敏。
- **输出**：.docx + 配图；提醒目标**总页数 ≤45**、权利要求**10 条（多则合并）**。

### 3.（若来自真实系统）取真实事实供实施例
扒真实参数、schema、接口、模型名及 `file:line`。权利要求上位，实施例可实施。

### 4. 锁术语 + 写 10 条权利要求 + solo 写正文
1. 读 `references/claims-quality.md` + `references/writing-style.md`。
2. **先写术语表**（内部名 → 专利用语），全文只许专利用语。
3. **先写满区别点草稿，再合并为恰好 10 条**（合并规程见 claims-quality；禁止删创新点）。
4. 再写说明书：摘要 →（摘要附图）→ 技术领域 / 背景技术 / 发明内容（步骤概述 +「进一步地」+ 末尾显著优点）/
   附图说明 / 具体实施方式。**勿**再写正式权项；细节用「具体地/例如/优选」。
5. 自查：全文检索「根据权利要求」仅在权利要求书；术语一致；思路连贯；预估页数 ≤45。

### 4.5 审查员视角加固（已有草稿/用户手改 Word 时必做）
读 `references/hardening-checklist.md` 与 `claims-quality.md`：
- 最硬组合进权利要求1；从属覆盖质量评分、异常复核、时间同步等闭环；合计仍为 10 条（多则合并）。
- 无具体数值/产品名进权利要求；AI 方案说明书写清输入—输出关联。
- 用户手改 Word 后反向同步生成源；分案写清边界。

### 5. 生成配图（数量与类型按内容定，不照搬模板图）
读 `references/figures.md`（**含六条硬规则 + 强制自查清单，画图前必读**）。**先想清楚这篇发明需要哪些图**——
画几张、哪些类型由技术方案决定，**不是每篇都要 5 张、也不一定有架构图或 JSON 图**；模板的图只参考画风与排版。
- **流程图/模块架构图优先直接调用** `make_figures.py` 的 `vflow` / `vmodules`：它们**框随文字自适应不溢出、单列
  竖排、纯黑粗线、画布贴近页宽字够大、回流/分组标签横排带白底不压线**，把最容易翻车的几条规则内置好了——
  **别手搓固定尺寸的盒子**（手搓最常见的就是文字溢出、字太小、压线）。曲线类图（谱/特性曲线）自己用 matplotlib
  画时同样守六规则（粗黑线、标注用引线引到留白处加白底、语义正确）。复杂自动布局可用 `gen_figures_graphviz.py`。
- **每画完一张必须单独 `Read` 这张 PNG，逐条核对六规则**（纯黑/不溢出/单列字大/不压线/线与字都完整/图文匹配），
  不合格就改了重画再嵌入。这一步是"稳定出好图"的关键，**不可跳过**（跳过就会出溢出、压线、小字）。

### 6. 装配 docx（按模板实测分节 + 页码）
- **有模板（默认参考模板）** → `scripts/build_patent.py`：
  - `PatentBuilder("…/参考模板.docx")`（或用户模板）
  - `abstract*` → 若 `b.has_abstract_figure`：`abstract_figure` + `abstract_caption` → `claim*`（10 条）→
    说明书 API → `figure`/`caption`
  - 自动按模板复刻五节（或四节）页眉与页脚页码；嵌图；清孤儿图；剥离内嵌字体。
- **无模板** → `scripts/build_patent_cnipa.py`（区块 JSON，四节兜底）。
- 用法见脚本 docstring 与 `references/docx-format.md`。装配后必做第 7 步。

### 7. 可视化校验（不可跳过）
用 `scripts/render_check.py` 渲染逐页 PNG，**逐页 Read**：
- 页眉是否与模板一致（参考模板五节：说明书摘要 / 摘要附图 / 权利要求书 / 说明书 / 说明书附图）；
  权利要求书/说明书页码是否各自从 1 重起（以模板为准）；
- **总页数 ≤45**；若超页，按 writing-style 去重后重装；
- 发明名称无豆腐块；正文宋体/缩进/行距对齐模板；图不越界、图号正确；无标题孤行。
发现问题→改内容/脚本→重渲染。**看过渲染页才算完成。**

### 7.5 公式与草稿痕迹校验
生成 `.docx` 后运行：
```bash
python scripts/validate_patent_docx.py 成稿.docx
```
要求 `dollar_xml=0`、`plain_backslash=0`、`formula_cjk_or_cn_punct=0`、`internal_terms=0`。若失败，回到源内容用显式
LaTeX 修公式边界；不要直接在 Word 里改完就结束，除非同步回生成源文件。

### 8. 完成
把最终 .docx 路径交给用户，并请其在 Word/WPS 通览。建议保留你的两个生成脚本（图、装配）以便迭代。

## 资源
- `参考模板.docx` — **默认版式基准**（五节：摘要/摘要附图/权利要求书/说明书/说明书附图）。
- `references/claims-quality.md` — **10 条骨架、合并规程、CNIPA/指南高质量权利要求要点**（写权项前必读）。
- `references/writing-style.md` — 行文范式、页数≤45 去重、术语与反面清单（写正文前必读）。
- `references/docx-format.md` — 克隆复刻、五节/四节页眉、页码页脚（装配前必读）。
- `references/cnipa-format-spec.md` — CNIPA 精确版式参数（无模板时为准）。
- `references/figures.md` — 配图硬规则（画图前必读）。
- `references/hardening-checklist.md` — 审查员/数学/算法/业务加固。
- `scripts/inspect_template.py` — 扒模板版式（只读版式）。
- `scripts/build_patent.py` — 有模板装配器（支持摘要附图节）。
- `scripts/build_patent_cnipa.py` — 无模板四节兜底。
- `scripts/make_figures.py` / `gen_figures_graphviz.py` / `gen_json_figs.py` — 配图。
- `scripts/docx_math.py` / `validate_patent_docx.py` / `render_check.py` — 公式与校验。

> 提交前逐条排查 `writing-style.md` 反面清单 + `claims-quality.md` 合并自检。

## 易踩坑速查
- 中文豆腐块：matplotlib 未注册 CJK 字体；或图里用了 `family="monospace"`（等宽字体无中文字形）——含中文的
  代码/JSON 直接用 CJK 字体渲染，别用 monospace。
- **发明名称/黑体字豆腐块（套模板专属坑）**：模板用 Word 内嵌了字体子集（`word/fonts/*.odttf` + settings 的
  `embedTrueTypeFonts`），子集只含模板原有文字；克隆后本专利模板没有的字（黑体发明名称最典型）→ □。
  `build_patent.py` 的 `save()` 已自动剥离内嵌字体根治；若你绕过它自行存盘，记得去掉内嵌或用系统完整字体。
- 图越界：图宽 > 版心宽（`page_width-左边距-右边距`）。嵌入宽统一 ≤ 版心宽。
- 全篇同一个页眉：克隆模板清空 body 塌成 1 节所致——必须按 §6 按模板实测建齐各节并挂 headerReference（参考模板为五节）。
- 文件臃肿/夹带模板配图：克隆模板遗留未引用的 `word/media/imageN`——保存前清掉未被 `a:blip` 引用的图片关系。
- 字太小：图画布太宽、嵌入后缩太狠——画布宽贴近嵌入宽 + 加大字号（见 §5 公式）。
- 经纬度/单位类换序：若涉及坐标，注意"经度在前/纬度在后"等顺序与范围校验，避免写反（这类细节进实施例）。
- 自动公式识别误伤：`P_12(h|航道)`、`E[W|L,W_obs]`、`\frac{...}{...}`、`argmax`、带中文条件的公式要手工 LaTeX。
- 用户手改 Word 后要"反向同步"：把 Word 内容、公式和标点修回生成脚本/JSON/图脚本；否则下一次生成会覆盖手改成果。
