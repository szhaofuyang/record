# love_diary_app.py - 新增地图点亮功能
import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
import random
from pyecharts.charts import Map
from pyecharts import options as opts
from pyecharts.globals import ThemeType

# ================= 数据存储（JSON） =================
DATA_FILE = "data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "entries": [],
            "memorials": [],
            "todos": [],
            "quotes": [],
            "visited_places": []  # 新增：去过的地方
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
init_data()

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================= 工具函数 =================
def get_entries():
    return load_data().get("entries", [])

def add_entry(entry, image_files=None):
    data = load_data()
    entry["id"] = len(data["entries"]) + 1
    entry["images"] = []
    if image_files:
        os.makedirs("data/images", exist_ok=True)
        for img in image_files:
            if img is not None:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"img_{timestamp}_{img.name}"
                filepath = os.path.join("data/images", filename)
                with open(filepath, "wb") as f:
                    f.write(img.getbuffer())
                entry["images"].append(filename)
    data["entries"].append(entry)
    save_data(data)

def delete_entry(eid):
    data = load_data()
    for e in data["entries"]:
        if e.get("id") == eid:
            for img in e.get("images", []):
                try:
                    os.remove(os.path.join("data/images", img))
                except:
                    pass
            break
    data["entries"] = [e for e in data["entries"] if e.get("id") != eid]
    save_data(data)

def get_memorials():
    return load_data().get("memorials", [])

def add_memorial(name, date_str, repeat):
    data = load_data()
    data["memorials"].append({"id": len(data["memorials"])+1, "name": name, "date": date_str, "repeat": repeat})
    save_data(data)

def delete_memorial(mid):
    data = load_data()
    data["memorials"] = [m for m in data["memorials"] if m.get("id") != mid]
    save_data(data)

def get_todos():
    return load_data().get("todos", [])

def add_todo(title, category):
    data = load_data()
    data["todos"].append({"id": len(data["todos"])+1, "title": title, "done": False, "category": category})
    save_data(data)

def toggle_todo(tid):
    data = load_data()
    for t in data["todos"]:
        if t.get("id") == tid:
            t["done"] = not t["done"]
            break
    save_data(data)

def delete_todo(tid):
    data = load_data()
    data["todos"] = [t for t in data["todos"] if t.get("id") != tid]
    save_data(data)

# ================= 地图相关 =================
# 中国省份列表（34个省级行政区）
PROVINCES = [
    "北京市", "天津市", "上海市", "重庆市",
    "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省",
    "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省",
    "河南省", "湖北省", "湖南省", "广东省", "海南省",
    "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省",
    "台湾省", "内蒙古自治区", "广西壮族自治区", "西藏自治区",
    "宁夏回族自治区", "新疆维吾尔自治区",
    "香港特别行政区", "澳门特别行政区"
]

def get_visited_places():
    return load_data().get("visited_places", [])

def add_visited_place(province, note, image_files):
    data = load_data()
    # 检查是否已存在
    for p in data["visited_places"]:
        if p["province"] == province:
            return False  # 已存在
    place = {
        "id": len(data["visited_places"]) + 1,
        "province": province,
        "note": note,
        "images": [],
        "date": date.today().isoformat()
    }
    if image_files:
        os.makedirs("data/images/visited", exist_ok=True)
        for img in image_files:
            if img is not None:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"visited_{timestamp}_{img.name}"
                filepath = os.path.join("data/images/visited", filename)
                with open(filepath, "wb") as f:
                    f.write(img.getbuffer())
                place["images"].append(filename)
    data["visited_places"].append(place)
    save_data(data)
    return True

def delete_visited_place(pid):
    data = load_data()
    for p in data["visited_places"]:
        if p.get("id") == pid:
            for img in p.get("images", []):
                try:
                    os.remove(os.path.join("data/images/visited", img))
                except:
                    pass
            break
    data["visited_places"] = [p for p in data["visited_places"] if p.get("id") != pid]
    save_data(data)

def get_map_html():
    """生成中国地图 HTML"""
    visited = get_visited_places()
    visited_provinces = [p["province"] for p in visited]
    
    # 构建数据：去过为1，未去为0（但只显示去过的高亮）
    data_pair = [(province, 1 if province in visited_provinces else 0) for province in PROVINCES]
    
    c = (
        Map(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="600px"))
        .add("去过的地方", data_pair, "china", is_map_symbol_show=False)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="", subtitle=""),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,  # 不显示颜色条
                min_=0,
                max_=1,
                range_color=["#e0e0e0", "#FF6B8A"],  # 未去为浅灰，去过为粉色
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}<br/>状态: {c}",
            ),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True, color="#333", font_size=10)
        )
    )
    return c.render_embed()  # 返回 HTML 字符串

# ================= 页面配置与样式 =================
st.set_page_config(page_title="恋爱日记", layout="wide", initial_sidebar_state="expanded")

# iOS 风格 CSS（与之前保持一致）
st.markdown("""
<style>
    /* ===== 全局 ===== */
    .main {
        background-color: #f9f9f9;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    }

    /* ===== 侧边栏（毛玻璃导航） ===== */
    .css-1d391kg, .stSidebar {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: saturate(180%) blur(24px);
        -webkit-backdrop-filter: saturate(180%) blur(24px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 30px rgba(0,0,0,0.05);
    }
    .css-1d391kg .sidebar-content {
        padding: 2rem 0.8rem;
    }
    .css-1d391kg .stMarkdown h1, .css-1d391kg .stMarkdown h2, .css-1d391kg .stMarkdown h3 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1c1c1e;
        padding-left: 0.5rem;
        font-size: 1.5rem;
    }

    /* ===== 导航列表 ===== */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.15rem !important;
        padding: 0 0.5rem;
    }
    .stRadio > div > label {
        display: flex !important;
        align-items: center !important;
        padding: 0.7rem 1.2rem !important;
        border-radius: 14px !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
        font-weight: 450 !important;
        font-size: 1rem !important;
        color: #1c1c1e !important;
        cursor: pointer !important;
        margin: 0 !important;
        line-height: 1.2;
        min-height: 44px;
        border: none !important;
    }
    .stRadio > div > label:hover {
        background: rgba(255, 107, 138, 0.08) !important;
    }
    .stRadio > div > label[data-checked="true"] {
        background: rgba(255, 107, 138, 0.12) !important;
        color: #FF6B8A !important;
        font-weight: 600 !important;
        border-radius: 14px !important;
    }
    .stRadio > div > label > div:first-child {
        display: none !important;
    }

    /* ===== 椭圆按钮 ===== */
    .stButton > button,
    .stDownloadButton > button,
    .stFileUploader button {
        background: rgba(255, 107, 138, 0.12) !important;
        color: #FF6B8A !important;
        border: 1px solid rgba(255, 107, 138, 0.25) !important;
        border-radius: 9999px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.25s ease !important;
        box-shadow: none !important;
        min-height: 44px;
        width: auto !important;
        cursor: pointer;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        letter-spacing: 0.3px;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
        line-height: 1.2;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFileUploader button:hover {
        background: rgba(255, 107, 138, 0.22) !important;
        transform: scale(1.02);
        box-shadow: 0 4px 16px rgba(255, 107, 138, 0.15) !important;
    }
    .stButton > button:active,
    .stDownloadButton > button:active,
    .stFileUploader button:active {
        transform: scale(0.94);
        background: rgba(255, 107, 138, 0.30) !important;
    }
    .stButton > button[kind="primary"] {
        background: #FF6B8A !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(255, 107, 138, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 24px rgba(255, 107, 138, 0.45) !important;
        transform: scale(1.02);
    }
    .stButton > button[kind="primary"]:active {
        transform: scale(0.94);
    }

    /* ===== 输入框、文本域 ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stDateInput > div > div {
        border-radius: 16px !important;
        border: 1.5px solid rgba(0,0,0,0.06) !important;
        background: #ffffff !important;
        padding: 0.7rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        min-height: 44px;
        box-shadow: none !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #FF6B8A !important;
        box-shadow: 0 0 0 4px rgba(255, 107, 138, 0.15) !important;
        outline: none !important;
    }

    /* ===== 滑块 ===== */
    .stSlider > div > div > div {
        background: rgba(255, 107, 138, 0.2) !important;
        height: 4px !important;
        border-radius: 4px !important;
    }
    .stSlider > div > div > div > div {
        background: #FF6B8A !important;
        border-radius: 4px !important;
    }
    .stSlider > div > div > div > div > div {
        background: #FF6B8A !important;
        border-radius: 50% !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: 0 2px 8px rgba(255, 107, 138, 0.3) !important;
    }

    /* ===== 卡片 ===== */
    .card, .stExpander {
        background: #ffffff;
        border-radius: 20px !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03) !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.2s;
    }

    /* ===== 大数字 ===== */
    .big-number {
        font-size: 3.6rem;
        font-weight: 700;
        color: #FF6B8A;
        text-align: center;
        letter-spacing: -0.02em;
    }

    /* ===== 移动端适配 ===== */
    @media (max-width: 768px) {
        .css-1d391kg {
            width: 280px !important;
        }
        .stRadio > div > label {
            font-size: 0.95rem !important;
            padding: 0.7rem 1rem !important;
            min-height: 48px;
        }
        .stButton > button,
        .stDownloadButton > button,
        .stFileUploader button {
            width: 100% !important;
            padding: 0.6rem 1rem !important;
            min-height: 48px;
            font-size: 1rem !important;
        }
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .card {
            padding: 1rem !important;
        }
        .big-number {
            font-size: 2.8rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ================= 页面函数 =================
def home_page():
    st.header("💗 恋爱日记")
    start_date = date(2022, 7, 4)  # ⚠️ 修改为你的纪念日
    days = (date.today() - start_date).days
    st.markdown(f"<div class='big-number'>{days}</div><div style='text-align:center;color:#8e8e93;'>在一起的天数</div>", unsafe_allow_html=True)
    
    entries = get_entries()[-3:][::-1]
    if entries:
        st.subheader("📖 最近记录")
        for e in entries:
            with st.expander(f"{e.get('date', '')} {e.get('title', '无标题')}"):
                st.write(e.get('content', '')[:200] + ("..." if len(e.get('content',''))>200 else ""))
    else:
        st.info("📝 还没有日记，写一篇吧！")

def diary_page():
    st.header("📝 日记")
    tab1, tab2 = st.tabs(["📋 列表", "✏️ 新建"])
    with tab1:
        entries = get_entries()
        if not entries:
            st.info("暂无记录")
        for e in entries[::-1]:
            with st.expander(f"{e.get('date', '')} {e.get('title', '无标题')}"):
                st.write(e.get('content', ''))
                if e.get('tags'): st.caption(f"🏷️ {e['tags']}")
                if e.get('mood'): st.caption(f"😊 {e['mood']}")
                if e.get('location'): st.caption(f"📍 {e['location']}")
                if e.get('images'):
                    cols = st.columns(min(len(e['images']), 4))
                    for idx, img in enumerate(e['images']):
                        with cols[idx % 4]:
                            try:
                                st.image(os.path.join("data/images", img), use_column_width=True)
                            except:
                                pass
                if st.button("🗑️ 删除", key=f"del_{e['id']}"):
                    delete_entry(e['id'])
                    st.rerun()
    with tab2:
        with st.form("new_entry"):
            date_input = st.date_input("日期", value=date.today())
            title = st.text_input("标题")
            content = st.text_area("内容", height=150)
            mood = st.selectbox("心情", ["😊 开心","😍 热恋","😌 平静","🤔 忧虑","😢 难过"])
            tags = st.text_input("标签（逗号分隔）")
            location = st.text_input("地点")
            intimacy = st.slider("亲密度", 1, 10, 7)
            privacy = st.checkbox("私密")
            images_input = st.file_uploader("上传图片（可多选）", type=["png","jpg","jpeg","gif"], accept_multiple_files=True)
            if st.form_submit_button("💾 保存"):
                add_entry({
                    "date": date_input.isoformat(),
                    "title": title,
                    "content": content,
                    "mood": mood,
                    "tags": tags,
                    "location": location,
                    "intimacy": intimacy,
                    "privacy": privacy,
                    "created_at": datetime.utcnow().isoformat()
                }, images_input)
                st.success("✅ 已保存")
                st.rerun()

def memorial_page():
    st.header("🎉 纪念日")
    with st.form("add_memorial"):
        name = st.text_input("名称")
        date_str = st.date_input("日期", value=date.today())
        repeat = st.checkbox("每年重复")
        if st.form_submit_button("➕ 添加"):
            if name:
                add_memorial(name, date_str.isoformat(), repeat)
                st.rerun()
    memorials = get_memorials()
    if not memorials:
        st.info("暂无纪念日")
    else:
        today = date.today()
        for m in memorials:
            m_date = datetime.strptime(m["date"], "%Y-%m-%d").date()
            if m["repeat"]:
                this_year = date(today.year, m_date.month, m_date.day)
                if this_year < today:
                    this_year = date(today.year+1, m_date.month, m_date.day)
            else:
                this_year = m_date
            delta = (this_year - today).days
            st.markdown(f"""
                <div class='card'>
                    <div style='display:flex;justify-content:space-between;'>
                        <b>{m['name']}</b>
                        <span style='color:#FF6B8A;'>{delta}天</span>
                    </div>
                    <div style='opacity:0.7;'>{m['date']} {'🔄' if m['repeat'] else ''}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ 删除", key=f"del_mem_{m['id']}"):
                delete_memorial(m['id'])
                st.rerun()

def todo_page():
    st.header("✅ 待办清单")
    with st.form("add_todo"):
        title = st.text_input("任务")
        category = st.selectbox("分类", ["一起做的事", "惊喜", "日常", "其他"])
        if st.form_submit_button("➕ 添加"):
            if title:
                add_todo(title, category)
                st.rerun()
    todos = get_todos()
    if not todos:
        st.info("还没有待办")
    else:
        for t in todos:
            col1, col2, col3 = st.columns([4,1,1])
            with col1:
                if t["done"]:
                    st.markdown(f"~~{t['title']}~~ ({t['category']})")
                else:
                    st.write(f"{t['title']} ({t['category']})")
            with col2:
                if st.button("✅" if not t["done"] else "↩️", key=f"todo_{t['id']}"):
                    toggle_todo(t['id'])
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_todo_{t['id']}"):
                    delete_todo(t['id'])
                    st.rerun()

def gallery_page():
    st.header("🖼️ 照片墙")
    entries = get_entries()
    all_images = []
    for e in entries:
        for img in e.get("images", []):
            all_images.append(img)
    if not all_images:
        st.info("📭 还没有图片，写日记时上传吧")
        return
    cols = st.columns(4)
    for idx, img_name in enumerate(all_images[::-1]):
        path = os.path.join("data/images", img_name)
        if os.path.exists(path):
            with cols[idx % 4]:
                try:
                    st.image(path, use_column_width=True)
                except:
                    pass

def stats_page():
    st.header("📊 统计")
    entries = get_entries()
    if not entries:
        st.info("暂无数据")
        return
    df = pd.DataFrame(entries)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("😊 心情分布")
        if 'mood' in df.columns:
            st.bar_chart(df['mood'].value_counts())
    with col2:
        st.subheader("📈 每月记录数")
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
        st.line_chart(df.groupby('month').size())
    if 'intimacy' in df.columns:
        st.subheader("💕 亲密度趋势")
        df['date'] = pd.to_datetime(df['date'])
        st.line_chart(df.sort_values('date').set_index('date')['intimacy'])

# ================= 地图页面 =================
def map_page():
    st.header("🗺️ 点亮中国")
    
    # 显示地图
    st.subheader("📌 足迹地图")
    map_html = get_map_html()
    st.components.v1.html(map_html, height=650, width=None)
    
    # 添加地点表单
    st.subheader("➕ 添加新地点")
    with st.form("add_place"):
        col1, col2 = st.columns(2)
        with col1:
            province = st.selectbox("选择省份", PROVINCES)
        with col2:
            note = st.text_input("备注（例如：城市、景点）")
        images = st.file_uploader("上传照片（可多选）", type=["png","jpg","jpeg","gif"], accept_multiple_files=True)
        if st.form_submit_button("保存地点"):
            if add_visited_place(province, note, images):
                st.success(f"✅ 已添加 {province}")
                st.rerun()
            else:
                st.error(f"❌ {province} 已存在，请勿重复添加")
    
    # 显示已去地点列表
    st.subheader("📍 已点亮的地点")
    places = get_visited_places()
    if not places:
        st.info("还没有去过的地方，添加一个吧！")
    else:
        for p in places:
            with st.expander(f"📍 {p['province']} - {p.get('date', '')}"):
                if p.get('note'):
                    st.write(f"📝 {p['note']}")
                if p.get('images'):
                    cols = st.columns(min(len(p['images']), 4))
                    for idx, img in enumerate(p['images']):
                        with cols[idx % 4]:
                            try:
                                st.image(os.path.join("data/images/visited", img), use_column_width=True)
                            except:
                                pass
                if st.button("🗑️ 删除", key=f"del_place_{p['id']}"):
                    delete_visited_place(p['id'])
                    st.rerun()

# ================= 侧边栏导航 =================
st.sidebar.title("💗 恋爱日记")
menu = st.sidebar.radio("导航", [
    "🏠 首页",
    "📝 日记",
    "🎉 纪念日",
    "✅ 待办",
    "🖼️ 照片墙",
    "🗺️ 地图",
    "📊 统计"
])

if menu == "🏠 首页":
    home_page()
elif menu == "📝 日记":
    diary_page()
elif menu == "🎉 纪念日":
    memorial_page()
elif menu == "✅ 待办":
    todo_page()
elif menu == "🖼️ 照片墙":
    gallery_page()
elif menu == "🗺️ 地图":
    map_page()
elif menu == "📊 统计":
    stats_page()