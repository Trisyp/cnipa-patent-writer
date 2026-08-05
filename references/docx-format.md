# 模板版式规范 与 docx 装配（克隆原型 + 按模板实测分节）

目标：产出的 .docx 与模板**视觉上一模一样**——页眉/页脚、分节、字体字号、缩进行距、分页、附图编排全继承。
关键手段是**克隆模板里真实存在的段落作"原型"**（而不是用 python-docx 从零设样式去"近似"）。

**默认格式基准**：技能目录 `参考模板.docx`（先 `inspect_template.py`）。该模板为**五节五运行页眉**：

## 一、中国发明专利的标准版式（以参考模板为准）
- **五个部分 = 五节（section），各有独立运行页眉**（无「摘要附图」的模板则退回四节）：
  1. 说明书摘要（页眉"说 明 书 摘 要"）
  2. **摘要附图**（页眉"摘 要 附 图"）—— 摘要配图；`PatentBuilder.has_abstract_figure` 为真时必写
  3. 权利要求书（页眉"权 利 要 求 书"）
  4. 说明书（页眉"说 明 书"）—— 一级标题仅：技术领域 / 背景技术 / 发明内容 / 附图说明 / 具体实施方式  
     （参考模板**无**独立「有益效果」标题；优点写在发明内容末「显著优点为：（1）…」）
  5. 说明书附图（页眉"说 明 书 附 图"）—— 仅放附图与图号
  每节之间是**另起一页的分节符**；权利要求书/说明书通常各有 PAGE 域页码（各自从 1 起）——以模板实测为准。
  摘要、附图是否带页码**因模板而异**——以 `inspect_template.py` 实测为准。
- **段落样式（典型字号，按模板实测为准）**：
  - 正文：宋体、小四(12pt)、1.5 倍行距、首行缩进 2 字符；摘要/权利要求/发明内容/实施例正文多为
    `Normal` 样式，技术领域/背景技术正文常为"缺省文本"样式（两端对齐 justify）。
  - 章节标题（技术领域/背景技术/发明内容/附图说明/具体实施方式）：四号(14pt)、**加粗**、段前后小段距。
  - 发明名称（说明书标题，在"技术领域"前出现**一次**）：四号(14pt)、**居中**、**不加粗**。
  - 实施例子标题（若用）：小四(12pt)、**加粗**、首行缩进。
  - 图号（图1）：小四(12pt)、**居中**。
  - 说明书摘要/权利要求书部分**没有**"摘要""权利要求书"这种正文小标题——摘要就是首段，权利要求直接从
    "1.一种……"开始（标签靠运行页眉体现）。**正式权项句式只出现在权利要求书节。**

> 不同模板字号/样式名可能略有差异——**务必先用 python-docx 实测模板**每类段落的 style/字号/加粗/对齐/缩进，
> 再据实调整 `build_patent.py` 里的原型匹配（脚本默认按上述标准结构识别）。

## 二、拆解模板（动手前先量）
```bash
# 看运行页眉文本 与 分节数
unzip -p template.docx word/header1.xml | grep -o '<w:t[^>]*>[^<]*</w:t>'
unzip -p template.docx word/document.xml | grep -o 'w:sectPr' | wc -l   # 通常 ≥4
```
```python
import docx; from docx.oxml.ns import qn
d=docx.Document("template.docx")
for p in d.paragraphs:
    t=p.text.strip()
    if t in ("技术领域","背景技术") or t.startswith(("本发明公开","实施例1","图1")):
        r=next((x for x in p.runs if x.text.strip()),None)
        print(repr(t[:12]), p.style.name, r.font.size.pt if r and r.font.size else None,
              r.font.bold if r else None, p.paragraph_format.alignment)
```

## 三、为什么"克隆原型"而不是"重设样式"
python-docx 设 `font.size/bold/alignment` 只能近似；而模板真实段落里还藏着 docDefaults 字体(宋体)、首行缩进
按"字符数"(firstLineChars)、行距规则、样式继承等，逐一复刻极易漏。**深拷贝模板里一个该类型的真实段落、只换
文字**，可 100% 继承其 pPr/rPr。`build_patent.py` 已实现：开局抓 6 类原型（正文 Normal、正文缺省文本、章节
标题、发明名称、子标题、图号），之后每段都 clone 对应原型。

## 四、五节（或四节）多页眉是怎么做出来的（核心，别塌成一节）
克隆模板后若"清空 body 只留一个 sectPr"，整篇会塌成**一节→所有页同一个页眉**（典型错误：全渲染成"说明书
附图"）。正确做法（`build_patent.py` 已实现）：
1. 保存前先抓模板 **body 级 sectPr** 作 `base_sectPr`（含页面尺寸/页边距/页脚引用）。
2. 抓**各运行页眉的 rId**：遍历 `doc.part.rels`，对 `reltype` 以 `/header` 结尾者，取其 `w:t` 文本归一化
   （去空格）→ 得到 {说明书摘要, [摘要附图], 权利要求书, 说明书, 说明书附图} 的 rId 映射。
3. **开局逐节扒模板真实的页脚/页码配置**（`_capture_section_configs()`，须在清空 body 前做）：遍历模板各
   `sectPr`，按其页眉文字归档 `{ftr_rid, pgnum_start}`。
4. `make_sectPr(页眉文本)`：deepcopy `base_sectPr` → 删原 header/footer/`pgNumType` → 插入目标页眉 →
   `<w:type w:val="nextPage"/>` → **按该节 cfg 复刻页脚/页码**。
5. 把除最后一节外各节的 sectPr **塞进该部分末段的 `w:pPr`**（摘要末 / 摘要附图末 / 最后一条权利要求 /
   说明书末）；最后一节（附图）用 body 级 sectPr 收尾。
6. **页码页脚**：`base_sectPr` 取自模板最后一节；若各节都照它复制会丢正文页码。须按 §四.3 逐节 cfg 复刻。
   子元素顺序：`headerRef → footerRef → type → pgSz → pgMar → pgNumType → cols`。改完务必渲染核对。

## 五、清理克隆带入的孤儿图（避免臃肿/夹带模板配图）
克隆模板会把模板原有的 `word/media/imageN` 一起带进来；清空 body 后它们成为未被引用的孤儿，使文件臃肿且
可能误显模板图。保存前清掉：扫 body 内所有 `a:blip` 的 `r:embed` 收集在用 rId，对 `doc.part.rels` 中 reltype
含 `image` 且不在用的 `drop_rel`。`build_patent.py` 的 `save()` 已自动做。

## 五·补、剥离模板内嵌字体（**跨主题套模板必踩的隐形坑**）
很多专利模板用了 Word 的"将字体嵌入文件"——`settings.xml` 有 `<w:embedTrueTypeFonts/>`，并把**模板原有文字
的字形子集**存进 `word/fonts/*.odttf`（子集很小，几百 KB）。克隆后这些子集被沿用，可你的专利有模板里**没有
的字**（换个主题尤其多）；消费端优先用内嵌子集 → 这些字渲染/在 Word 打开**全变豆腐块 □**，**最典型的是黑体
发明名称**（其子集往往最小，整行标题报废）。这坑很隐蔽：同样的字在正文宋体（子集较全）可能正常，唯独黑体标题
全 □，且**只在主题与模板不同的新专利里暴露**（同主题字基本重合，不易发现）。根治：保存前关掉内嵌（删
settings 的 `embedTrueTypeFonts/embedSystemFonts/saveSubsetFonts`），并清掉 `fontTable` 的 embed 引用与
`fonts/*.odttf`，让消费端改用系统完整字体。`build_patent.py` 的 `save()`（`_strip_embedded_fonts`）已自动做；
渲染校验时**务必逐字确认发明名称那行无豆腐块**。

## 六、配图嵌入宽度别越界
版心宽 = `section.page_width - left_margin - right_margin`（A4+常见页边距≈5.6–6.0 in）。所有嵌入图宽 **≤ 版心宽**
（留 0.1 in 余量），否则图越右边距。竖向长图按高度自适应即可。

## 七、build_patent.py 用法（PatentBuilder）
脚本顶部 docstring 有完整示例。要点：
```python
from build_patent import PatentBuilder
b = PatentBuilder("template.docx")
b.abstract("本发明公开了……")                 # 摘要(可多段)；归"说明书摘要"节
if b.has_abstract_figure:                     # 参考模板等五节模板必填
    b.abstract_figure("abs.png", 4.8); b.abstract_caption("图1")
for c in claim_paragraphs: b.claim(c)         # 每条权利要求段；归"权利要求书"节（合计10条）
b.spec_title("一种……方法及系统")             # 说明书标题(技术领域前,居中)；以下归"说明书"节
b.heading("技术领域"); b.body_justify("本发明涉及……")
b.heading("背景技术"); b.body_justify("……")
b.heading("发明内容"); b.body("……")           # 步骤概述+进一步地；勿写「根据权利要求」
b.body("本发明与现有技术相比，其显著优点为：")  # 优点在发明内容末；勿另开「有益效果」标题
b.body("（1）……"); b.body("（2）……")
b.heading("附图说明"); b.body("图1为……示意图；")
b.heading("具体实施方式"); b.body("……")
b.body("步骤1：……"); b.body("进一步地，在其中一个实施例中，……"); b.body("具体地：……")
b.figure("figN.png", width_in=4.8); b.caption("图N")   # 归"说明书附图"节
b.save("输出.docx")     # 自动:按模板挂五节/四节页眉 + 页脚页码 + 嵌图 + 清孤儿图
```
- `body()` 用 Normal 原型；`body_justify()` 用"缺省文本"原型（技术领域/背景技术正文）。
- 节的归属由调用顺序决定：abstract* → 摘要节；abstract_figure*/abstract_caption* → 摘要附图节（若有）；
  claim* → 权利要求书节；spec_title/heading/body/subhead* → 说明书节；figure/caption* → 说明书附图节。
- 若模板缺某运行页眉，脚本会回退并告警——此时手工核对。
- 完稿渲染后总页数应 ≤45（超页先去重，见 `writing-style.md` 第四节）。

## 八、完成后务必渲染校验
见 `figures.md`/SKILL.md 第7步：`render_check.py` 渲染逐页 PNG，Read 逐页核对页眉/版式/配图/分页。
**结构正确不代表视觉正确**——这是必须亲眼看渲染页的根本原因。

## 九、没有模板时：`build_patent_cnipa.py`（无模板兜底装配器）
若用户**没给模板**，用 `build_patent_cnipa.py` 按 CNIPA 标准版式从零生成（参数见 `cnipa-format-spec.md`，已内置）。
它与 `build_patent.py` 的区别只在**格式来源**：克隆版继承模板真实段落（有模板时首选，视觉 100% 一致）；
兜底版用内置标准参数（无模板时用）。有「摘要附图」的模板产出五节；兜底一般为四节（摘要/权利要求书/说明书/
说明书附图）。正文宋体 12pt、首行缩进 2 字、1.5 倍行距；权利要求书/说明书各自页码从 1 起（以实测为准）。
- 输入是**区块 JSON**（`{"title":…, "blocks":[["abstract",…],["claim",…],["title",…],["h1",…],["body",…],
  ["code",…],["figure",…]]}`），而非 PatentBuilder 的链式 API。用法：`python build_patent_cnipa.py blocks.json 输出.docx`。
- **区块顺序硬约束**：`abstract* → claim* → title → h1/body… → figure*`。  
  脚本把**第一个 `title` 起**写入说明书；`title` 若在 `claim` 前，权项会进说明书 → **双份权利要求**（见 `lessons-learned.md` L1）。  
  `build_patent_cnipa.py` 已对错误顺序 `raise SystemExit`。
- 它会自动按句拆长段、按分号拆权利要求、半角标点归全角（同克隆版逻辑）。
- 附图节默认**清空页脚=无页码**（无模板可参照时的合理缺省）；克隆版则**据模板实测逐节复刻**附图页码处理
  （可能续接、可能独立无页码），二者差异仅因兜底版没有模板可还原——无模板时按标准缺省即可。
> 不管用哪个装配器，**内容都据用户的真实技术方案写**，区块 JSON 里不要塞任何范文/模板的技术内容。
