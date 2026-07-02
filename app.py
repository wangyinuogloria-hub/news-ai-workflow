"""
电视新闻 AI 写稿助手 v2.7
"""

import streamlit as st
import requests
import datetime
import io

# ============================================================
DEFAULT_PASSWORD = "shenshi2026"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"
TAVILY_KEY = "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"

try:
    from tavily import TavilyClient; HAS_TAVILY = True
except ImportError: HAS_TAVILY = False
try:
    from duckduckgo_search import DDGS; HAS_DDG = True
except ImportError: HAS_DDG = False

# ============================================================
SYSTEM_PROMPT = """你是一个地方电视台新闻栏目的 AI 写稿助手。你熟悉电视新闻的写作规范，擅长从采访素材中提炼最有价值的同期声，用具体、有画面感的语言撰写稿件。

## ⚠️ 同期声铁律（最高优先级，违反即为错误稿件）
1. **禁止编造**：同期声必须逐字来自转录文本。不可自己写、不可改措辞、不可凭空创造。
2. **禁止张冠李戴**：A 说的话只能署 A 的名。采访对象名单和转录文本必须一一对应。
3. **禁止拼接不同人**：不可把两个人的话拼成一个人的同期声。
4. **可选操作**：可删口头禅（"就是说""那个"）、可调换顺序、可拼接同一人的多段话。
5. 同期声格式：【同期声】姓名 职位：原话内容（姓名后空格接职位，无括号）
6. 挑选标准：只选"正文写不出来的"——有画面感、有情感、有数字对比。正文能交代的信息交给正文，不要让同期声重复正文。
7. 长度：群众类 1-3 句；官员/企业类 2-4 句。
8. 口语处理：删"好爽啊""你看这个""我跟你说啊"；保留"应该""大概""你会发现"。

## 格式规范
- 稿件结构：【标题】【导语】【正文】【同期声】，各自独立成段。
- 正文直接过渡到同期声，不用"XXX表示""XXX认为"。
- 不用破折号和感叹号。段落简短，每段 2-4 句。

## 写作风格
- 场景描写有具体地点+具体动作。导语：时间+主体+事件，不加修饰。
- 正文第三人称，不出现"记者注意到""记者了解到"。
- 核心数据放结尾。"场景→细节→数据"漏斗。
- 机构/企业全称做主语。所在城市高频做主语。
- 不写"推动发展""北冰南展""重要引擎""黄金通道"等空话。

## 其他
- 标题：动词叙事式/数据前置式/城市冒号式。具体。
- 背景调查：从政策、数据、机构、同类事件、趋势等维度整理。有搜索结果的附URL。
- 角度策划：给出 3 个不同角度，推荐最佳。
- 事实核查：逐项标注来源URL和置信度。
- 链接格式：[文字](URL)。不使用 ** * # 等 Markdown 符号。
- 输出纯文本。"""

# ============================================================
st.set_page_config(page_title="新闻 AI 写稿助手", page_icon="📝", layout="wide")

st.markdown("""<style>
    .stApp { background: #f5f5f7; }
    h1 { font-weight: 700 !important; font-size: 1.8rem !important; }
    h2, h3 { font-weight: 600 !important; }
    .stCaption { color: #86868b !important; }
    .stTextArea textarea, .stTextInput input, .stSelectbox [data-baseweb="select"] > div {
        background: white !important; border: 1px solid rgba(0,0,0,0.1) !important; border-radius: 10px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #0071e3 !important; box-shadow: 0 0 0 3px rgba(0,113,227,0.12) !important; outline: none !important;
    }
    .stButton > button {
        border-radius: 10px !important; font-weight: 500 !important; font-size: 0.88rem !important;
        padding: 0.4rem 1.1rem !important; transition: all 0.15s !important;
        background: #f0f4fa !important; border: 1px solid rgba(0,113,227,0.2) !important; color: #0071e3 !important;
    }
    .stButton > button:hover { background: #e4edf8 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important; }
    .stButton > button[kind="primary"] { background: #0071e3 !important; border: none !important; color: white !important; font-weight: 600 !important; }
    .stButton > button[kind="primary"]:hover { background: #0077ed !important; box-shadow: 0 4px 14px rgba(0,113,227,0.3) !important; }
    .stExpander, .stAlert { background: white !important; border-radius: 10px !important; border: 1px solid rgba(0,0,0,0.08) !important; }
    hr { border-color: rgba(0,0,0,0.06) !important; }
    #MainMenu, footer, header { visibility: hidden; }
</style>""", unsafe_allow_html=True)

# ============================================================
# 会话状态
# ============================================================
defaults = {
    "authenticated": False, "chat_history": [], "current_draft": "",
    "custom_password": "", "api_key": "", "angle_result": "", "bg_result": "",
    "interviewees": [{"name":"","title":""},{"name":"","title":""}],
    "use_abc_names": False, "factcheck_result": "",
    "topic_text": "", "scene_text": "", "transcript_text": "",
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ============================================================
# 密码
# ============================================================
if not st.session_state.authenticated:
    st.title("🔒 新闻 AI 写稿助手")
    pwd = st.text_input("密码", type="password")
    if st.button("验证"):
        if pwd == (st.session_state.custom_password or DEFAULT_PASSWORD):
            st.session_state.authenticated = True; st.rerun()
        else: st.error("密码错误")
    st.stop()

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.header("⚙️ 设置")
    ak = st.text_input("DeepSeek API Key", value=st.session_state.api_key, type="password", placeholder="sk-...")
    if ak: st.session_state.api_key = ak
    if not st.session_state.api_key:
        with st.expander("💡 获取 API Key", expanded=True):
            st.markdown("1. [platform.deepseek.com](https://platform.deepseek.com) 注册\n2. API Keys → 创建\n3. 充值 10 元\n4. 粘贴到上方")
    st.divider()
    st.caption("✅ 联网搜索已内置 · 🔒 稿件仅本地保存")
    st.divider()
    st.caption("修改密码")
    np = st.text_input("新密码", type="password", key="pwd", placeholder="留空不修改")
    if np: st.session_state.custom_password = np; st.success("已更新")
    st.caption(f"当前：{st.session_state.custom_password or DEFAULT_PASSWORD}")
    st.divider()
    if st.button("🗑️ 清空全部", use_container_width=True):
        for k in ["chat_history","current_draft","angle_result","bg_result","factcheck_result","topic_text","scene_text","transcript_text"]:
            st.session_state[k] = [] if k=="chat_history" else ""
        st.session_state.interviewees = [{"name":"","title":""},{"name":"","title":""}]
        st.rerun()

# ============================================================
st.title("📝 新闻 AI 写稿助手")
st.caption("自动背景调查 · AI精选同期声 · 一键角度策划 · 事实核查")

with st.expander("📖 使用说明（点击展开）"):
    st.markdown("""
### 工作流（从上到下）
| 步骤 | 类型 | 你做什么 | AI 做什么 |
|------|------|---------|----------|
| Step 1 · 选题 | ✏️ 你输入 | 填写选题信息 | — |
| Step 2 · 背景调查 | 🤖 AI生成 | 点按钮 | 联网搜索+生成报告，填入下方框 |
| Step 3 · 采访见闻 | ✏️ 你输入 | 写现场观察 | — |
| Step 4 · 同期声 | ✏️ 你输入 | 填姓名+粘贴转录 | 写稿时自动筛选同期声 |
| Step 5 · 角度 | 🤖 AI生成 | 点按钮 | 输出 3 个角度+推荐 |
### 改稿：小改=直接在稿件框里改字，大改=下方意见框写方向→点重新生成
""")

# ============================================================
# 工具函数
# ============================================================
def web_search(query, max_results=5):
    results = []
    if HAS_TAVILY:
        try:
            client = TavilyClient(api_key=TAVILY_KEY)
            for r in client.search(query, max_results=max_results, search_depth="basic").get("results",[]):
                results.append(f"- [{r.get('title','')}]({r.get('url','')})：{r.get('content','')}")
            if results: return "\n".join(results)
        except: pass
    if HAS_DDG:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(f"- [{r.get('title','')}]({r.get('href','')})：{r.get('body','')}")
        except: pass
    return "\n".join(results) if results else "(未搜索到结果)"

def call_ds(msg, hist):
    msgs = [{"role":"system","content":SYSTEM_PROMPT}]
    for m in hist[-20:]: msgs.append(m)
    msgs.append({"role":"user","content":msg})
    try:
        r = requests.post(DEEPSEEK_API_URL,
            headers={"Content-Type":"application/json","Authorization":f"Bearer {st.session_state.api_key}"},
            json={"model":MODEL,"messages":msgs,"temperature":0.7,"max_tokens":4096}, timeout=120)
        if r.status_code==401: return "❌ API Key 无效"
        if r.status_code==402: return "❌ 余额不足"
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"❌ 网络错误：{str(e)[:200]}"

def build_name_list():
    if st.session_state.use_abc_names:
        return "（姓名未知，请用「市民A」「参赛选手B」「企业负责人C」等代称，后期替换。）"
    ns = []
    for p in st.session_state.interviewees:
        n,t = p["name"].strip(), p["title"].strip()
        if n or t: ns.append(f"- {n or '(待填)'} {t or '(待填)'}")
    return "\n".join(ns) if ns else "（未填写，请根据转录推断。）"

def build_material():
    p = []
    p.append(f"【Step 1 · 选题】\n{topic.strip() or '(待补充)'}")
    p.append(f"【Step 2 · 背景调查】\n{bg_text or '(待补充)'}")
    p.append(f"【Step 3 · 采访见闻】\n{scene.strip() or '(无)'}")
    nl = build_name_list()
    p.append(f"【Step 4 · 同期声】\n采访对象（同期声署名必须与名单一一对应）：\n{nl}\n\n转录：\n{transcript.strip() or '(无)'}")
    at = angle_pref.strip()
    if st.session_state.angle_result and not at:
        at = "AI建议：\n"+st.session_state.angle_result
    elif st.session_state.angle_result:
        at = at+"\nAI参考：\n"+st.session_state.angle_result
    p.append(f"【Step 5 · 角度】\n{at or '(由AI自动判断)'}")
    return "\n\n".join(p)

# ============================================================
# Step 1 · 选题（✏️ 用户输入）
# ============================================================
st.subheader("Step 1 · 选题录入")
st.caption("把选题相关信息粘贴到这里。活动文件、领导通知、选题背景……越长越详细越好。")
topic = st.text_area("Step1", value=st.session_state.topic_text, height=120, label_visibility="collapsed",
    placeholder="例如：本周末一场省级青少年科技赛事在本市举办……附：活动通知原文、主办方介绍……")
if topic != st.session_state.topic_text:
    st.session_state.topic_text = topic

# ============================================================
# Step 2 · 背景调查
# ============================================================
st.subheader("Step 2 · 背景调查")
st.caption("点按钮，AI 自动搜索并生成背景报告。也可手动粘贴补充。")

c2a, c2b = st.columns([4,1])
with c2b:
    bg_btn = st.button("🔍 AI 背景调查", use_container_width=True)

# --- 按钮处理 ---
if bg_btn:
    if not st.session_state.api_key: st.error("请先设置 API Key")
    elif not topic.strip(): st.error("请先填写 Step 1（选题）")
    else:
        with st.status("正在进行背景调查……", expanded=True) as status:
            st.write("🔍 正在搜索互联网相关信息……")
            sr = web_search(f"{topic.strip()}", max_results=8)
            st.write("🤖 正在整合搜索结果为背景调查报告……")
            prompt = f"""为以下选题做背景调查。

【选题】{topic.strip()}

【搜索结果】{sr}

综合搜索结果和已有知识，从政策背景、产业/行业数据、关键机构/人物、同类事件、趋势等维度整理。有搜索结果优先用搜索并附URL。搜索不到的用已有知识标注"基于公开信息，具体请核实"。——这是给记者的背景参考资料，不是稿件正文，请用清晰的分类和条目呈现。"""
            result = call_ds(prompt, st.session_state.chat_history)
            if not result.startswith("❌"):
                st.write("✅ 背景调查完成")
                status.update(label="背景调查完成", state="complete")
                st.session_state.bg_result = result
                st.session_state.chat_history.append({"role":"user","content":prompt})
                st.session_state.chat_history.append({"role":"assistant","content":result})
                st.rerun()
            else:
                status.update(label="背景调查失败", state="error")
                st.error(result)

# --- 背景调查结果：预览优先（链接可点击），编辑框其次 ---
if st.session_state.bg_result:
    st.markdown("##### 📋 背景调查报告")
    st.markdown(st.session_state.bg_result)  # 渲染后可点击链接

    # 细化调查
    st.caption("如需调整方向或补充内容，输入后点「重新调查」")
    refine_col, refine_btn_col = st.columns([4, 1])
    with refine_col:
        bg_refine = st.text_input("细化方向（可选）", label_visibility="collapsed",
            placeholder="如：重点查一下广东省的政策支持、补充近三年的数据……",
            key="bg_refine")
    with refine_btn_col:
        bg_re_btn = st.button("🔄 重新调查", use_container_width=True)

    if bg_re_btn:
        if not st.session_state.api_key: st.error("请先设置 API Key")
        else:
            with st.status("正在重新调查……", expanded=True) as status:
                refine_query = f"{topic.strip()} {bg_refine.strip()}" if bg_refine.strip() else topic.strip()
                st.write(f"🔍 正在搜索：{refine_query[:80]}……")
                sr = web_search(refine_query, max_results=8)
                st.write("🤖 正在整合……")
                prompt = f"""为以下选题做背景调查。

【选题】{topic.strip()}
【细化方向】{bg_refine.strip() if bg_refine.strip() else '补充更多维度的信息'}
【上一次背景调查】{st.session_state.bg_result[:500]}
【新搜索结果】{sr}

请生成一份更新后的完整背景调查报告。综合上次报告、新搜索结果和已有知识。"""
                result = call_ds(prompt, st.session_state.chat_history)
                if not result.startswith("❌"):
                    st.write("✅ 重新调查完成")
                    status.update(label="重新调查完成", state="complete")
                    st.session_state.bg_result = result
                    st.session_state.chat_history.append({"role":"user","content":prompt})
                    st.session_state.chat_history.append({"role":"assistant","content":result})
                    st.rerun()
                else:
                    status.update(label="重新调查失败", state="error")
                    st.error(result)

    # 编辑原始文本（折叠）
    with st.expander("✏️ 编辑原始文本（高级）", expanded=False):
        bg_edited = st.text_area(
            "Step2_edit",
            value=st.session_state.bg_result,
            height=300,
            label_visibility="collapsed"
        )
        if bg_edited != st.session_state.bg_result:
            st.session_state.bg_result = bg_edited
        bg_text = st.session_state.bg_result  # 供 build_material 使用
else:
    # 还没有结果时的占位
    bg_text = st.text_area(
        "Step2_empty",
        value="",
        height=120,
        label_visibility="collapsed",
        placeholder="👆 点击上方「AI 背景调查」自动生成。如需手动粘贴通稿或政策文件，直接输入。"
    )
    if bg_text != st.session_state.bg_result:
        st.session_state.bg_result = bg_text

# ============================================================
# Step 3 · 采访见闻（✏️ 用户输入）
# ============================================================
st.subheader("Step 3 · 采访见闻")
st.caption("你在现场看到、感受到的。画面感的来源。")
scene = st.text_area("Step3", value=st.session_state.scene_text, height=80, label_visibility="collapsed",
    placeholder="例如：现场约200人，分三个展区。某展台围满观众。场地开阔，采光好。")
if scene != st.session_state.scene_text:
    st.session_state.scene_text = scene

# ============================================================
# Step 4 · 同期声（✏️ 用户输入）
# ============================================================
st.subheader("Step 4 · 同期声转录")

st.caption("采访对象 — AI 写稿时严格按此署名，确保人名言一致")
st.session_state.use_abc_names = st.checkbox(
    "暂不知道姓名（自动用「市民A」「参赛选手B」等代称，后期替换）",
    value=st.session_state.use_abc_names, key="abc_check"
)
if not st.session_state.use_abc_names:
    for i, p in enumerate(st.session_state.interviewees):
        n1, n2, n3 = st.columns([2,2,1])
        with n1:
            st.session_state.interviewees[i]["name"] = st.text_input(
                f"姓名 {i+1}", value=p["name"], placeholder="如：张某某",
                key=f"iv_n_{i}", label_visibility="collapsed")
        with n2:
            st.session_state.interviewees[i]["title"] = st.text_input(
                f"职位 {i+1}", value=p["title"], placeholder="如：参赛选手 / 企业负责人",
                key=f"iv_t_{i}", label_visibility="collapsed")
        with n3:
            if len(st.session_state.interviewees) > 1:
                if st.button("✕", key=f"iv_d_{i}"):
                    st.session_state.interviewees.pop(i); st.rerun()
    if len(st.session_state.interviewees) < 6:
        if st.button("+ 添加采访对象"):
            st.session_state.interviewees.append({"name":"","title":""}); st.rerun()

st.caption("转录文本 — 上传 .txt 自动识别姓名职位，也可直接粘贴。")

c4a, c4b = st.columns([3,1])
with c4a:
    tfiles = st.file_uploader("上传 .txt（可多选）", type=["txt"], key="tf", label_visibility="collapsed", accept_multiple_files=True)
with c4b:
    if tfiles: st.caption(f"✅ {len(tfiles)} 个文件")

# 文件上传：读取内容 → 存入 session_state
if tfiles:
    fc = ""
    for f in tfiles:
        fc += f"\n--- {f.name} ---\n"
        fc += f.read().decode("utf-8", errors="ignore")
        fc += "\n"
    st.session_state.transcript_text = fc.strip()

    # 自动识别文件名中的姓名职位
    # 如 "参赛选手 何乙龙 深圳市民 王凯旋-文稿-转写结果.txt" → 何乙龙 参赛选手, 王凯旋 深圳市民
    import re
    if not st.session_state.use_abc_names:
        auto_names = []
        for f in tfiles:
            basename = f.name.rsplit(".", 1)[0]
            parts = re.split(r'[-_—]', basename)
            name_part = parts[0] if parts else basename
            words = name_part.split()
            i = 0
            while i + 1 < len(words):
                auto_names.append({"name": words[i+1], "title": words[i]})
                i += 2
            if i < len(words):
                auto_names.append({"name": words[i], "title": ""})
        if auto_names:
            st.session_state.interviewees = auto_names[:6]
            while len(st.session_state.interviewees) < 2:
                st.session_state.interviewees.append({"name": "", "title": ""})
            st.caption(f"🤖 已从文件名识别 {len(auto_names)} 个采访对象，请核对")

transcript = st.text_area("Step4", value=st.session_state.transcript_text, height=180, label_visibility="collapsed",
    placeholder="上传 .txt 文件自动识别，或直接粘贴转录文本……\n\n说话人1: 张某某 参赛选手\n说话人2: 我今年12岁，准备了三个月……")
if transcript != st.session_state.transcript_text:
    st.session_state.transcript_text = transcript

# 自动检测转录中有几个不同的说话人
if st.session_state.transcript_text.strip():
    import re as re_speaker
    speaker_nums = set(re_speaker.findall(r'说话人(\d+)', st.session_state.transcript_text))
    detected_count = len(speaker_nums) if speaker_nums else 0

    if detected_count > 0:
        # 统计实际填了几个采访对象（姓名或职位至少有一个）
        filled_count = sum(1 for p in st.session_state.interviewees if p["name"].strip() or p["title"].strip())

        if not st.session_state.use_abc_names:
            if filled_count < detected_count:
                st.warning(f"⚠️ 转录中检测到 {detected_count} 个不同的说话人，但只填写了 {filled_count} 个采访对象。请核对上方名单是否漏了人，或点「+ 添加采访对象」。")
            elif filled_count > detected_count and detected_count > 0:
                st.info(f"💡 转录中检测到 {detected_count} 个说话人，但填写了 {filled_count} 个采访对象。如有多余的可点 ✕ 删除。")

# ============================================================
# Step 5 · 角度策划
# ============================================================
st.subheader("Step 5 · 角度策划")
st.caption("AI 分析素材后给出 3 个角度。不满意可换一组。")

c5a, c5b, c5c = st.columns([2, 1, 1])
with c5a:
    angle_pref = st.text_input("角度偏好（可选）", label_visibility="collapsed",
        placeholder="留空由 AI 自动策划；也可指定偏好方向",
        key="step5_input")
with c5b:
    angle_btn = st.button("🤖 AI 策划角度", use_container_width=True)
with c5c:
    angle_reroll = st.button("🔄 换一组", use_container_width=True)

# --- AI 策划角度 ---
if angle_btn:
    if not st.session_state.api_key: st.error("请先设置 API Key")
    elif not topic.strip(): st.error("请先填写 Step 1")
    else:
        with st.status("正在策划角度……", expanded=True) as status:
            st.write("🤖 正在分析素材……")
            pref_note = f"\n用户偏好方向：{angle_pref.strip()}" if angle_pref.strip() else ""
            prompt = f"根据以下素材策划 3 个不同新闻角度。各附新闻价值和稿件类型。推荐最佳。{pref_note}\n\n{build_material()}"
            result = call_ds(prompt, st.session_state.chat_history)
            if not result.startswith("❌"):
                st.write("✅ 角度策划完成")
                status.update(label="角度策划完成", state="complete")
                st.session_state.angle_result = result
                st.session_state.chat_history.append({"role":"user","content":prompt})
                st.session_state.chat_history.append({"role":"assistant","content":result})
                st.rerun()
            else:
                status.update(label="角度策划失败", state="error")
                st.error(result)

# --- 换一组角度 ---
if angle_reroll:
    if not st.session_state.api_key: st.error("请先设置 API Key")
    elif not topic.strip(): st.error("请先填写 Step 1")
    else:
        with st.status("正在重新策划角度……", expanded=True) as status:
            st.write("🤖 正在从不同角度分析……")
            pref_note = f"\n用户偏好方向：{angle_pref.strip()}" if angle_pref.strip() else ""
            prev = st.session_state.angle_result
            prev_note = f"\n上一次角度（请避免重复，给出全新的角度）：\n{prev[:300]}" if prev else ""
            prompt = f"根据以下素材策划 3 个全新的、与之前不同的新闻角度。各附新闻价值和稿件类型。推荐最佳。{pref_note}{prev_note}\n\n{build_material()}"
            result = call_ds(prompt, st.session_state.chat_history)
            if not result.startswith("❌"):
                st.write("✅ 新角度策划完成")
                status.update(label="新角度策划完成", state="complete")
                st.session_state.angle_result = result
                st.session_state.chat_history.append({"role":"user","content":prompt})
                st.session_state.chat_history.append({"role":"assistant","content":result})
                st.rerun()
            else:
                status.update(label="角度策划失败", state="error")
                st.error(result)

# 角度结果：纯输出，有内容才显示
if st.session_state.angle_result:
    st.info(st.session_state.angle_result)

# ============================================================
# 选项 + 生成 / 核查按钮
# ============================================================
o1, o2, o3 = st.columns([1, 1, 1])
with o1:
    draft_type = st.selectbox("稿件类型", ["动态新闻（1'30\" ~ 2'）","主题报道（2' ~ 3'）","多主题拼接稿"])
with o2:
    angle_choice = st.selectbox("使用角度", ["（未选择）","角度一","角度二","角度三","自定义角度"])
with o3:
    extra_cmd = st.text_input("额外指令（可选）", placeholder="如：不要气温描述、结尾用数据收...")

custom_angle = ""
if angle_choice == "自定义角度":
    custom_angle = st.text_input("自定义角度内容", placeholder="如：从青少年参与和产业落地的双线叙事切入……")

c1, c2, c3 = st.columns([2,2,5])
with c1:
    generate_btn = st.button("✍️ 生成稿件", type="primary", use_container_width=True)
with c2:
    factcheck_btn = st.button("🔍 事实核查", use_container_width=True)

# --- 生成稿件（按钮处理紧跟按钮）---
if generate_btn:
    if not st.session_state.api_key: st.error("请先设置 API Key")
    elif not topic.strip() and not transcript.strip(): st.error("请至少填写 Step 1 或 Step 4")
    else:
        with st.status("正在生成稿件……", expanded=True) as status:
            st.write("🤖 正在分析素材、筛选同期声、撰写稿件……")
            ins = f"根据以下素材写一篇电视新闻稿。\n\n{build_material()}\n\n【稿件类型】{draft_type}"
            if angle_choice != "（未选择）":
                if angle_choice == "自定义角度" and custom_angle.strip():
                    ins += f"\n【指定角度】{custom_angle.strip()}"
                elif angle_choice != "自定义角度":
                    ins += f"\n【指定角度】请使用{angle_choice}"
            if extra_cmd.strip():
                ins += f"\n【额外指令】{extra_cmd.strip()}"
            ins += """

【同期声检查清单 — 输出前逐条确认】
1. 每段同期声是否来自 Step 4 转录原文？（不是 = 重写）
2. 说话人姓名是否与采访对象名单完全一致？（不一致 = 重写）
3. A 说的话是否署了 A 的名？（署错 = 重写）
4. 是否有编造或改写措辞？（有 = 重写）
5. 每段同期声是否提供了正文写不出的信息？（不必要 = 删掉）

严格按格式输出：【标题】【导语】【正文】【同期声】。末尾附 3-4 个备选标题。"""
            result = call_ds(ins, st.session_state.chat_history)
            if not result.startswith("❌"):
                st.write("✅ 稿件生成完成 —— 已显示在下方")
                status.update(label="稿件生成完成", state="complete")
                st.session_state.current_draft = result
                st.session_state.chat_history.append({"role":"user","content":ins})
                st.session_state.chat_history.append({"role":"assistant","content":result})
                st.rerun()
            else:
                status.update(label="稿件生成失败", state="error")
                st.error(result)

# --- 事实核查（按钮处理紧跟按钮）---
if factcheck_btn:
    if not st.session_state.api_key: st.error("请先设置 API Key")
    else:
        d = draft_area_val.strip() if draft_area_val else st.session_state.current_draft.strip()
        if not d: st.error("请先生成稿件")
        else:
            with st.status("正在进行事实核查……", expanded=True) as status:
                st.write("🔍 正在搜索关键数据……")
                sr = web_search(f"{topic.strip()}", max_results=5)
                st.write("🤖 正在逐项核查……")
                prompt = f"""对以下稿件进行事实核查。

【稿件】{d}

【素材】{build_material()}

【搜索结果】{sr}

逐项列出：数据、政策/机构名称、人物姓名职位。每项标注原始出处、搜索验证结果、置信度。如有URL用 Markdown 链接格式：[标题](URL)，确保记者可点击验证。总结需确认的项目。"""
                result = call_ds(prompt, st.session_state.chat_history)
                if not result.startswith("❌"):
                    st.write("✅ 核查完成 —— 结果显示在稿件下方")
                    status.update(label="事实核查完成", state="complete")
                    st.session_state.factcheck_result = result
                    st.session_state.chat_history.append({"role":"user","content":prompt})
                    st.session_state.chat_history.append({"role":"assistant","content":result})
                    st.rerun()
                else:
                    status.update(label="核查失败", state="error")
                    st.error(result)

st.divider()

# ============================================================
# 稿件（AI 生成 / 可编辑 — 不设固定key）
# ============================================================
st.subheader("📄 稿件")
st.caption("✏️ 可直接编辑文字（小改）。下方「修改意见」用于大幅调整（大改）。")

draft_area_val = st.text_area(
    "draft_display",
    value=st.session_state.current_draft,
    height=350,
    placeholder="👆 点击上方「生成稿件」后，稿件将显示在此……",
    label_visibility="collapsed"
)
if draft_area_val != st.session_state.current_draft:
    st.session_state.current_draft = draft_area_val

# ============================================================
# 修改意见
# ============================================================
fc_col, bc_col = st.columns([4,1])
with fc_col:
    feedback = st.text_area("feedback", height=70, label_visibility="collapsed",
        placeholder="例如：第三段精简一下、第二个同期声换信息量更大的、结尾加具体数据……",
        key="feedback_input")
with bc_col:
    st.write("")
    revise_btn = st.button("🔄 重新生成", use_container_width=True)

# --- 修改稿件（按钮处理紧跟按钮）---
if revise_btn:
    if not st.session_state.api_key: st.error("请先设置 API Key")
    elif not feedback.strip(): st.error("请先输入修改意见")
    elif not draft_area_val.strip(): st.error("请先生成稿件")
    else:
        with st.status("正在修改稿件……", expanded=True) as status:
            st.write("🤖 正在根据意见调整……")
            ri = f"根据修改意见调整。\n\n【当前稿件】\n{draft_area_val.strip()}\n\n【修改意见】\n{feedback.strip()}\n\n重新输出完整稿件。格式不变。"
            result = call_ds(ri, st.session_state.chat_history)
            if not result.startswith("❌"):
                st.write("✅ 修改完成 —— 已更新上方稿件")
                status.update(label="修改完成", state="complete")
                st.session_state.current_draft = result
                st.session_state.chat_history.append({"role":"user","content":ri})
                st.session_state.chat_history.append({"role":"assistant","content":result})
                st.rerun()
            else:
                status.update(label="修改失败", state="error")
                st.error(result)

# ============================================================
# 事实核查结果（纯输出，有内容才显示）
# ============================================================
if st.session_state.factcheck_result:
    st.divider()
    st.subheader("🔍 事实核查结果")
    st.caption("以下链接可直接点击打开验证。")
    st.markdown(st.session_state.factcheck_result)
    if st.button("✕ 关闭核查结果"):
        st.session_state.factcheck_result = ""; st.rerun()

# ============================================================
# 导出
# ============================================================
if st.session_state.current_draft:
    st.divider()
    d1,d2,_ = st.columns([1,1,5])
    with d1:
        st.download_button("⬇️ TXT", data=st.session_state.current_draft,
            file_name=f"新闻稿件_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain", use_container_width=True)
    with d2:
        try:
            from docx import Document
            doc = Document()
            for ln in st.session_state.current_draft.split("\n"):
                if ln.strip(): doc.add_paragraph(ln)
            buf = io.BytesIO(); doc.save(buf); buf.seek(0)
            st.download_button("⬇️ DOCX", data=buf,
                file_name=f"新闻稿件_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True)
        except ImportError:
            st.caption("💡 pip3 install python-docx")

st.divider()
st.caption(f"电视新闻 AI 写稿助手 v2.7 · {MODEL} · {datetime.datetime.now().year}")
