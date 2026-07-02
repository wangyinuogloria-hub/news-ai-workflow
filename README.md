# 📝 融媒体 AI 写稿工作流

<p align="center">
  <b>从选题到成稿，为记者打造的效率工具</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-Skill-blue?logo=claude" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Dify-Mobile-orange?logo=dify" alt="Dify">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/language-Python%203.10+-yellow?logo=python" alt="Python">
</p>

<p align="center">
  <b>选题 → 背景调查 → 同期声筛选 → 角度策划 → 事实核查 → 写稿修改</b><br>
  全仿真模拟记者写稿流程 · 为传统媒体记者打造
</p>

---

## 🤔 这是什么？

### 💡 创作理念

这个工作流是为各大媒体记者量身定制的。在各地市级广电、报纸和新媒体编辑部，记者们一直面临着"永远在路上"的困境。采访花掉大半天，回来还要搜资料、挑同期声、排结构、写初稿、改稿子。真正用来做内容的时间，被大量重复劳动挤压。

这个工作流通过观察记者的真实写稿模式，全仿真模拟了记者从选题到成稿的完整流程。记者可以在采访回来的路上把选题和采访素材输入进去，AI 自动完成背景调查、同期声筛选、角度策划和初稿写作。回到台里，稿子已经成型，直接进入剪辑环节。

工作流参考了各地市级官方媒体的写作调性，输出的稿件不会出现原则性失误。适用于**纸媒、电视播出端，以及较为正式的新媒体播出端**。

> 把时间还给采访，把重复劳动交给 AI。

---

输入选题和采访素材，AI 按照严格的新闻写作规范，自动完成：

- 🔍 **背景调查** — 自动联网搜索政策、数据、同类事件，附资料来源链接
- 🎙️ **同期声筛选** — 从大段采访转录中自动挑出最有价值的同期声（不编造、不改措辞、不张冠李戴）
- 🧭 **角度策划** — 分析素材后给 3 个不同的新闻角度供记者选择
- ✅ **事实核查** — 逐项核查稿件中数据、政策、人物的来源，标注置信度
- ✍️ **自动写稿** — 按新闻格式输出完整稿件，支持对话修改

---

## 🎯 三种使用方式

你不需要三种都装。根据你的场景选一个：

<table>
<tr>
<td width="33%" align="center">
  <h3>🏆 方案一</h3>
  <b>Claude Code Skill</b><br>
  质量最高，功能最完整
</td>
<td width="33%" align="center">
  <h3>💻 方案二</h3>
  <b>Streamlit 网页</b><br>
  浏览器打开就能用
</td>
<td width="33%" align="center">
  <h3>📱 方案三</h3>
  <b>Dify 移动端</b><br>
  手机就能写稿
</td>
</tr>
<tr>
<td>

- ✅ 满血 Claude 模型
- ✅ 多轮对话改稿
- ✅ 自动读记忆库
- ❌ 需要装终端应用
- ❌ 需要海外账号

</td>
<td>

- ✅ 浏览器打开即用
- ✅ 漂亮 UI 界面
- ✅ 联网搜索内置
- ⚠️ DeepSeek 模型
- ⚠️ 质量稍逊方案一

</td>
<td>

- ✅ 手机链接打开
- ✅ 零安装门槛
- ⚠️ 质量下降明显
- ⚠️ 知识库碎片化
- ❌ 无多轮交互

</td>
</tr>
<tr>
<td><b>适合：</b>对稿件质量有要求的记者，日常写稿</td>
<td><b>适合：</b>不想装任何东西，电脑前使用</td>
<td><b>适合：</b>在路上需要快速出初稿</td>
</tr>
</table>

---

## 🚀 方案一：Claude Code Skill（推荐）

### 你需要什么

- [Claude Code](https://claude.ai/code) 已安装
- Anthropic 账号

### 安装（1 分钟）

```bash
# 下载 Skill 文件
curl -O https://github.com/wangyinuogloria-hub/news-ai-workflow/raw/main/news-workflow.skill

# 安装
npx skills add ./news-workflow.skill -g -y
```

### 使用

在 Claude Code 终端中，直接说：

> "开始选题，今天有个关于XX的活动……"

AI 会按七步流程引导你完成写稿。每步由你触发，不自动推进。

---

## 💻 方案二：Streamlit 网页应用

### 你需要什么

- Python 3.10+
- [DeepSeek API Key](https://platform.deepseek.com)（注册 1 分钟，充 10 元够用很久）

### 安装 & 启动

```bash
# 克隆仓库
git clone https://github.com/wangyinuogloria-hub/news-ai-workflow.git
cd news-ai-workflow

# 安装依赖
pip3 install -r requirements.txt

# 启动
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`，默认密码 `shenshi2026`。

### 界面速览

```
┌────────────────────────────────────────────┐
│  📝 新闻 AI 写稿助手                        │
│  自动背景调查 · AI精选同期声 · 事实核查      │
│                                            │
│  ═══ 素材输入（按流程从上到下）══════       │
│  Step 1 · 选题录入     [_______________]    │
│  Step 2 · 背景调查     [🔍 AI自动搜索]      │
│  Step 3 · 采访见闻     [_______________]    │
│  Step 4 · 同期声转录   [📎上传文件]         │
│  Step 5 · 角度策划     [🤖 AI策划角度]      │
│                                            │
│  [✍️ 生成稿件]  [🔍 事实核查]               │
│                                            │
│  📄 稿件              ✏️ 可直接编辑          │
│  [___________________________________]     │
│                                            │
│  💬 修改意见           [🔄 重新生成]        │
│  [_______________________________]        │
└────────────────────────────────────────────┘
```

---

## 📋 七步工作流

| 步骤 | 触发方式 | AI 做什么 |
|------|---------|---------|
| **Step 1** · 选题录入 | 你提供选题信息 | 确认选题方向和时效要求 |
| **Step 2** · 背景调查 | 选题确认后 | 联网搜索政策、数据、事件，输出报告（附链接） |
| **Step 3** · 场景素材 | 你描述采访见闻 | 记录现场观察，用于稿件画面感 |
| **Step 4** · 同期声处理 | 你粘贴转录文本 | 筛选最佳同期声，删口头禅不改措辞 |
| **Step 5** · 角度策划 | Step 4 完成后 | 输出 3 个新闻角度，推荐最佳 |
| **Step 6** · 事实核查 | 角度确认后 | 逐项核查数据/政策/人物，标注置信度 |
| **Step 7** · 写稿 & 修改 | 核查确认后 | 输出完整稿件，支持小改（直接改字）和大改（AI 重写） |

---

## ⚠️ 同期声处理铁律

这是整个工作流最重要的规则。写稿质量的核心：

| 可以做 | 不可以做 |
|--------|---------|
| ✅ 拼接同一人的多段同期声 | ❌ 编造不存在的同期声 |
| ✅ 调换同期声先后顺序 | ❌ 修改原文措辞 |
| ✅ 删减口头禅、重复词 | ❌ 把不同人的话拼成一句 |
| | ❌ 断章取义歪曲原意 |

---

## 📂 仓库结构

```
news-ai-workflow/
├── README.md                          ← 你在这里
├── CLAUDE.md                          ← 项目说明（给 AI 看的）
├── news-workflow.skill                ← 方案一：Skill 安装文件
├── app.py                             ← 方案二：Streamlit 应用
├── requirements.txt                   ← Python 依赖
├── start.sh                           ← 一键启动脚本
└── skill/news-workflow/               ← Skill 源码
    ├── SKILL.md                       ← 核心规则和工作流
    └── references/                    ← 参考知识库
        ├── style-guide.md             ← 标题/导语/行文风格
        ├── quote-patterns.md          ← 同期声挑选规则
        ├── lessons.md                 ← 12 条实战写稿教训
        ├── terminology.md             ← 术语库 & 禁用词
        └── templates.md               ← 稿件结构模板
```

---

## 🙋 FAQ

<details>
<summary><b>我不会写代码，能用吗？</b></summary>

方案二和方案三不需要任何代码能力。方案一只需要终端里复制粘贴一行安装命令。如果你能打开终端，你就能用。

</details>

<details>
<summary><b>方案一和方案二的差距到底有多大？</b></summary>

差距来自两个地方：一是模型能力（Claude > DeepSeek），二是交互方式（多轮对话 > 单次生成）。方案一能跟你对话改稿，理解"这个太水了""第三个同期声换掉"这种模糊反馈。方案二不太行，需要你写得更具体。

</details>

<details>
<summary><b>为什么方案三质量最差？</b></summary>

Dify 的知识库是把写作规则切成碎片再检索，AI 脑子里永远只有"半本操作手册"，不像方案一方案二那样一次性读到全部规则。加上免费额度通常用较弱模型。

</details>

<details>
<summary><b>同期声格式为什么是「姓名 职位」而不是「姓名（职位）」？</b></summary>

电视新闻行业标准。括号在字幕和配音中不自然。空格是最干净的。

</details>

<details>
<summary><b>我想自己改规则，怎么做？</b></summary>

方案一：编辑 `skill/news-workflow/SKILL.md`，重新打包。方案二：编辑 `app.py` 里的 `SYSTEM_PROMPT` 变量。

</details>

---

## 🛠 技术栈

- **AI 模型**：Claude (Skill) / DeepSeek V3 (Streamlit)
- **框架**：Streamlit
- **联网搜索**：Tavily Search API + DuckDuckGo
- **Skill 打包**：Claude Code Skill Creator (Anthropic 官方)

---

<p align="center">
  <sub>大二传媒生 · 100+ 轮 AI 迭代 · 不是计算机专业 · 全靠自然语言</sub>
</p>
