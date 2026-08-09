# cnipa-patent-writer

> **Cursor / Claude Code Agent Skill**：撰写中国发明专利（CNIPA）申请文档（`.docx`）。  
> **只借模板版式，绝不抄模板技术内容**——正文与配图全部据你的技术方案重新生成。

一个用于撰写**中国发明专利**申请文档的 Agent Skill。有模板时严格套用页眉页脚、分节、字体字号、缩进行距、分页与附图编排；无模板时按 CNIPA 标准版式生成。覆盖**说明书摘要 / 摘要附图（参考模板） / 权利要求书 / 说明书 / 说明书附图**，并支持白底黑线配图与逐页渲染校验。

## 亮点

- **红线**：只借格式、绝不抄模板里的具体技术（架构、模块、流程、配图种类与数量）。
- **双装配器**：有模板 → `build_patent.py` 克隆版式；无模板 → `build_patent_cnipa.py` 按 CNIPA 标准生成。
- **Word 原生公式**：正文中的 `$...$`、`\(...\)` LaTeX 自动转为 Word 可编辑公式（OMML，依赖 `math2docx`）。
- **配图据内容生成**：matplotlib / graphviz，单列竖排、框随文字自适应、纯黑白。
- **可视化校验**：`docx → pdf → 逐页 png`，逐页核对页眉、页码、字体与配图。
- **成稿公式校验**：`validate_patent_docx.py` 检查 `$` 残留、公式内中文、草稿痕迹、**说明书内双份权项**、独立「有益效果」标题。
- **踩坑防再发**：`lessons-learned.md`（装配顺序、实施方式提纲化、公式「其中」、中文优先、AI I/O 等）。
- **审查加固清单**：`hardening-checklist.md` 覆盖审查员/数学/算法/业务视角。

## 仓库结构

```
cnipa-patent-writer/
├── SKILL.md                       技能入口（工作流、原则、资源索引）
├── requirements.txt               Python 依赖
├── references/
│   ├── writing-style.md           行文范式、反面清单
│   ├── docx-format.md             克隆复刻、页眉分节、页码
│   ├── cnipa-format-spec.md       CNIPA 精确版式参数
│   ├── figures.md                 配图硬规则
│   └── omml-equations.md          OMML 公式 / 空角标排查
├── 参考模板.docx                  默认版式基准（只借格式）
└── scripts/
    ├── inspect_template.py        扒模板版式（只读格式）
    ├── build_patent.py            有模板装配器
    ├── build_patent_cnipa.py      无模板装配器
    ├── omml_utils.py              OMML 公式构建
    ├── make_figures.py            matplotlib 配图
    ├── gen_figures_graphviz.py    graphviz 流程/架构图
    ├── gen_json_figs.py           JSON 面板图
    └── render_check.py            docx 逐页渲染校验
```

## 安装

### 方式一：Cursor 个人技能（推荐）

```bash
git clone https://github.com/Trisyp/cnipa-patent-writer.git
cp -r cnipa-patent-writer ~/.cursor/skills/cnipa-patent-writer
# Windows PowerShell:
# Copy-Item -Recurse cnipa-patent-writer $env:USERPROFILE\.cursor\skills\cnipa-patent-writer
```

装好后在 Cursor 里说「写专利」「起草发明专利」，或 `@cnipa-patent-writer` 手动附加技能。

### 方式二：`npx`（Claude Code 等）

```bash
npx github:Trisyp/cnipa-patent-writer
npx github:Trisyp/cnipa-patent-writer --project    # 装到当前项目
npx github:Trisyp/cnipa-patent-writer --force      # 覆盖已有安装
```

### 方式三：手动复制

将 `SKILL.md`、`references/`、`scripts/`、`requirements.txt` 拷入你的 agent 技能目录即可。

## 依赖

**Python**（必装）：

```bash
pip install -r requirements.txt
```

| 包 | 用途 |
|---|---|
| `python-docx` | 生成 / 装配 `.docx` |
| `matplotlib`、`Pillow` | 配图 |
| `math2docx` | LaTeX → Word 原生公式 |
| `graphviz`（可选） | 复杂流程/架构图，另需系统 `dot` |

**系统依赖**（渲染校验，可选但强烈建议）：

```bash
# Debian/Ubuntu
sudo apt-get install -y graphviz libreoffice-writer poppler-utils fonts-noto-cjk
# macOS
brew install graphviz poppler && brew install --cask libreoffice
# Windows：安装 LibreOffice、poppler for Windows，并确保系统有中文字体（宋体/黑体或 Noto CJK）
```

**中文字体**：配图与 `docx→pdf` 都需要，否则中文变豆腐块 □。推荐 [Noto Sans CJK](https://github.com/notofonts/noto-cjk)；勿将微软专有字体提交到仓库。

## 数学公式写法

装配时自动把 LaTeX 转为 Word 原生公式（可在 Word 公式编辑器中修改）：

```text
损失函数为 $L=\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2$。
相关系数 \(\rho=\frac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y}\) 用于衡量相关性。
```

未用 `$...$` 或 `\(...\)` 包裹的 `x^2` 等纯文本**不会**自动转换。

## 用法（要点）

1. 自备一份**模板专利** `.docx`（可选，作格式参照；仓库不含模板）。
2. 提供技术方案（代码库、设计文档或交底材料）。
3. 技能执行：扒版式 → 写正文 → 生成配图 → 装配 docx → 渲染逐页校验。
4. 产物：排版规范的 `.docx`（含配图）。

## 重要提示

- **自备模板**：不要把含真实技术或他人 IP 的模板提交到公开仓库。
- **不提交专有字体**（SimSun/SimHei 等）。
- 仓库仅含通用格式机制与行文方法，**不含任何特定专利的技术内容**。

## 致谢

基于 [fnjialun/cnipa-patent-writer](https://github.com/fnjialun/cnipa-patent-writer) 扩展，新增 Cursor 技能路径说明、Word 原生公式（`math2docx`）等能力。

## License

[MIT](./LICENSE)
