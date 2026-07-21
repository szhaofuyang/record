# love_diary_app.py - 含设置功能（背景主题、字号、照片背景）
import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
from pyecharts.charts import Map
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import base64
import tempfile

# ================= 数据存储 =================
DATA_FILE = "data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        default = {
            "entries": [],
            "visited_places": [],
            "photos": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
init_data()

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================= 日记功能 =================
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
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                fname = f"img_{ts}_{img.name}"
                path = os.path.join("data/images", fname)
                with open(path, "wb") as f:
                    f.write(img.getbuffer())
                entry["images"].append(fname)
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

# ================= 照片墙功能 =================
def get_photos():
    return load_data().get("photos", [])

def add_photo(image_file, caption=""):
    data = load_data()
    os.makedirs("data/photos", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    fname = f"photo_{ts}_{image_file.name}"
    path = os.path.join("data/photos", fname)
    with open(path, "wb") as f:
        f.write(image_file.getbuffer())
    photo = {
        "id": len(data["photos"]) + 1,
        "filepath": path,
        "filename": fname,
        "caption": caption,
        "date": date.today().isoformat()
    }
    data["photos"].append(photo)
    save_data(data)
    return True

def delete_photo(pid):
    data = load_data()
    for p in data["photos"]:
        if p.get("id") == pid:
            try:
                os.remove(p["filepath"])
            except:
                pass
            break
    data["photos"] = [p for p in data["photos"] if p.get("id") != pid]
    save_data(data)

# ================= 地图功能 =================
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
    for p in data["visited_places"]:
        if p["province"] == province:
            return False
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
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                fname = f"visited_{ts}_{img.name}"
                path = os.path.join("data/images/visited", fname)
                with open(path, "wb") as f:
                    f.write(img.getbuffer())
                place["images"].append(fname)
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
    visited = get_visited_places()
    visited_provinces = [p["province"] for p in visited]
    data_pair = [(province, 1 if province in visited_provinces else 0) for province in PROVINCES]
    c = (
        Map(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="600px"))
        .add("", data_pair, "china", is_map_symbol_show=False)
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                min_=0,
                max_=1,
                range_color=["#e8e8e8", "#FF6B8A"],
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
    return c.render_embed()

# ================= 设置模块 =================
def init_settings():
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "theme": "light",       # light, dark, system
            "bg_image": None,       # base64 string
            "font_scale": 1.0,
        }
init_settings()

def apply_css():
    settings = st.session_state.settings
    theme = settings["theme"]
    font_scale = settings["font_scale"]
    bg_image = settings.get("bg_image")

    # 定义颜色
    if theme == "dark":
        bg_color = "#1c1c1e"
        card_bg = "#2c2c2e"
        text_color = "#f5f5f7"
        border_color = "rgba(255,255,255,0.06)"
    else:
        bg_color = "#f8f8fc"
        card_bg = "#ffffff"
        text_color = "#1c1c1e"
        border_color = "rgba(0,0,0,0.03)"

    # 背景图片 CSS
    bg_css = ""
    if bg_image:
        bg_css = f"""
            .stApp {{
                background-image: url('data:image/png;base64,{bg_image}');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .stApp::before {{
                content: '';
                position: fixed;
                top:0;left:0;right:0;bottom:0;
                background: rgba(0,0,0,0.4);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                z-index: -1;
            }}
            .main .block-container {{
                background: rgba(255,255,255,0.85);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }}
        """
    else:
        bg_css = f"""
            .stApp {{ background-color: {bg_color}; }}
            .main .block-container {{
                background: {card_bg};
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            }}
        """

    css = f"""
        .main {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
            color: {text_color};
        }}
        .css-1d391kg, .stSidebar {{
            background: rgba(255,255,255,0.8) !important;
            backdrop-filter: saturate(180%) blur(24px);
            -webkit-backdrop-filter: saturate(180%) blur(24px);
            border-right: 1px solid rgba(255,255,255,0.3);
        }}
        .stRadio > div > label {{
            color: {text_color} !important;
        }}
        .stRadio > div > label[data-checked="true"] {{
            background: rgba(255,107,138,0.12) !important;
            color: #FF6B8A !important;
        }}
        .card, .stExpander {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }}
        .stat-card {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 1.2rem;
            text-align: center;
        }}
        .stat-number {{
            color: #FF6B8A;
        }}
        .big-number {{
            color: #FF6B8A;
        }}
        .stTextInput > div > div > input, .stTextArea > div > div > textarea,
        .stSelectbox > div > div, .stDateInput > div > div {{
            background: {card_bg} !important;
            color: {text_color} !important;
            border: 1.5px solid {border_color} !important;
        }}
        /* 字号缩放 */
        html, body, .stApp {{
            font-size: {16 * font_scale}px;
        }}
        h1 {{ font-size: {28 * font_scale}px; }}
        h2 {{ font-size: {22 * font_scale}px; }}
        h3 {{ font-size: {18 * font_scale}px; }}
        .big-number {{ font-size: {48 * font_scale}px; }}
        .stat-number {{ font-size: {24 * font_scale}px; }}
        .stButton > button, .stDownloadButton > button, .stFileUploader button {{
            font-size: {16 * font_scale}px;
            padding: 0.6rem 1.8rem;
        }}
        {bg_css}
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ================= 页面配置 =================
st.set_page_config(page_title="恋爱日记", layout="wide", initial_sidebar_state="expanded")
apply_css()

# ================= 设置页面 =================
def settings_page():
    st.header("设置")
    settings = st.session_state.settings

    st.subheader("主题")
    theme = st.radio(
        "选择主题",
        ["浅色", "深色", "跟随系统"],
        index=["浅色", "深色", "跟随系统"].index(
            "浅色" if settings["theme"] == "light" else
            "深色" if settings["theme"] == "dark" else
            "跟随系统"
        ),
        horizontal=True
    )
    new_theme = {"浅色": "light", "深色": "dark", "跟随系统": "system"}[theme]
    if new_theme != settings["theme"]:
        settings["theme"] = new_theme
        st.rerun()

    st.subheader("背景图片")
    bg_file = st.file_uploader("从手机相册选择照片", type=["png","jpg","jpeg"])
    if bg_file:
        img = bg_file.read()
        b64 = base64.b64encode(img).decode()
        settings["bg_image"] = b64
        st.success("背景已更新")
        st.rerun()
    if settings.get("bg_image"):
        if st.button("移除背景图片"):
            settings["bg_image"] = None
            st.rerun()

    st.subheader("字号")
    font_scale = st.slider("文字大小", 0.8, 1.4, settings["font_scale"], 0.05)
    if font_scale != settings["font_scale"]:
        settings["font_scale"] = font_scale
        st.rerun()

    st.subheader("数据管理")
    if st.button("导出数据 (JSON)"):
        data = load_data()
        st.download_button(
            "下载 data.json",
            json.dumps(data, ensure_ascii=False, indent=2),
            file_name="love_diary_backup.json",
            mime="application/json"
        )
    uploaded_file = st.file_uploader("导入数据 (JSON)", type=["json"])
    if uploaded_file:
        try:
            imported = json.load(uploaded_file)
            save_data(imported)
            st.success("数据导入成功，请刷新页面")
            st.rerun()
        except Exception as e:
            st.error(f"导入失败: {e}")

# ================= 其他页面 =================
def home_page():
    st.header("恋爱日记")
    start_date = date(2022, 7, 4)
    days = (date.today() - start_date).days
    st.markdown(f"<div class='big-number'>{days}</div><div style='text-align:center;color:#8e8e93;'>在一起的天数</div>", unsafe_allow_html=True)

    entries = get_entries()
    total = len(entries)
    mood_counts = {}
    for e in entries:
        mood = e.get('mood', '未标注')
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    top_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else "无"
    visited = len(get_visited_places())
    photos = len(get_photos())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{total}</div><div class='stat-label'>日记</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{visited}</div><div class='stat-label'>省份</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{photos}</div><div class='stat-label'>照片</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{top_mood}</div><div class='stat-label'>心情</div></div>", unsafe_allow_html=True)

    if entries:
        st.subheader("最近日记")
        for e in entries[-5:][::-1]:
            with st.expander(f"{e.get('date', '')} {e.get('title', '无标题')}"):
                st.write(e.get('content', '')[:300] + ("..." if len(e.get('content',''))>300 else ""))

def diary_page():
    st.header("日记")
    tab1, tab2 = st.tabs(["浏览", "写日记"])
    with tab1:
        entries = get_entries()
        if not entries:
            st.info("还没有日记")
        else:
            search = st.text_input("搜索标题或内容")
            tag_filter = st.text_input("标签筛选（逗号分隔）")
            filtered = []
            for e in entries:
                match = True
                if search:
                    if search.lower() not in e.get('title','').lower() and search.lower() not in e.get('content','').lower():
                        match = False
                if tag_filter:
                    tags = e.get('tags', '').split(',')
                    if not any(t.strip() in tag_filter for t in tags):
                        match = False
                if match:
                    filtered.append(e)
            if not filtered:
                st.info("没有匹配的记录")
            for e in filtered[::-1]:
                with st.expander(f"{e.get('date', '')} {e.get('title', '无标题')}"):
                    st.write(e.get('content', ''))
                    if e.get('tags'): st.caption(f"标签: {e['tags']}")
                    if e.get('mood'): st.caption(f"心情: {e['mood']}")
                    if e.get('location'): st.caption(f"地点: {e['location']}")
                    if e.get('images'):
                        cols = st.columns(min(len(e['images']), 4))
                        for idx, img in enumerate(e['images']):
                            with cols[idx % 4]:
                                try:
                                    st.image(os.path.join("data/images", img), use_column_width=True)
                                except:
                                    pass
                    if st.button("删除", key=f"del_{e['id']}"):
                        delete_entry(e['id'])
                        st.rerun()
    with tab2:
        with st.form("new_entry"):
            date_input = st.date_input("日期", value=date.today())
            title = st.text_input("标题")
            content = st.text_area("内容", height=150)
            mood = st.selectbox("心情", ["开心", "热恋", "平静", "忧虑", "难过"])
            tags = st.text_input("标签（逗号分隔）")
            location = st.text_input("地点")
            intimacy = st.slider("亲密度", 1, 10, 7)
            privacy = st.checkbox("私密")
            images_input = st.file_uploader("上传图片", type=["png","jpg","jpeg","gif"], accept_multiple_files=True)
            if st.form_submit_button("保存"):
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
                st.success("保存成功")
                st.rerun()

def gallery_page():
    st.header("照片墙")
    with st.expander("上传新照片"):
        with st.form("upload_photo"):
            photo_file = st.file_uploader("选择照片", type=["png","jpg","jpeg","gif"])
            caption = st.text_input("备注（可选）")
            if st.form_submit_button("上传"):
                if photo_file:
                    add_photo(photo_file, caption)
                    st.success("上传成功")
                    st.rerun()
                else:
                    st.error("请选择照片")

    photos = get_photos()
    if not photos:
        st.info("还没有照片，上传一张吧")
    else:
        cols = st.columns(4)
        for idx, p in enumerate(photos[::-1]):
            with cols[idx % 4]:
                try:
                    st.image(p["filepath"], use_column_width=True)
                    if p.get('caption'):
                        st.caption(p['caption'])
                    if st.button("删除", key=f"del_photo_{p['id']}"):
                        delete_photo(p['id'])
                        st.rerun()
                except:
                    pass

def map_page():
    st.header("点亮中国")
    st.subheader("足迹地图")
    map_html = get_map_html()
    st.components.v1.html(map_html, height=650, width=None)

    st.subheader("添加新地点")
    with st.form("add_place"):
        col1, col2 = st.columns(2)
        with col1:
            province = st.selectbox("选择省份", PROVINCES)
        with col2:
            note = st.text_input("备注（城市/景点）")
        images = st.file_uploader("上传照片", type=["png","jpg","jpeg","gif"], accept_multiple_files=True)
        if st.form_submit_button("保存"):
            if add_visited_place(province, note, images):
                st.success(f"已添加 {province}")
                st.rerun()
            else:
                st.error(f"{province} 已存在")

    places = get_visited_places()
    if not places:
        st.info("还没有去过的地方")
    else:
        for p in places:
            with st.expander(f"{p['province']} - {p.get('date', '')}"):
                if p.get('note'):
                    st.write(f"备注: {p['note']}")
                if p.get('images'):
                    cols = st.columns(min(len(p['images']), 4))
                    for idx, img in enumerate(p['images']):
                        with cols[idx % 4]:
                            try:
                                st.image(os.path.join("data/images/visited", img), use_column_width=True)
                            except:
                                pass
                if st.button("删除", key=f"del_place_{p['id']}"):
                    delete_visited_place(p['id'])
                    st.rerun()

def stats_page():
    st.header("统计")
    entries = get_entries()
    if not entries:
        st.info("暂无数据")
        return
    df = pd.DataFrame(entries)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("心情分布")
        st.bar_chart(df['mood'].value_counts())
    with col2:
        st.subheader("每月日记数")
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
        st.line_chart(df.groupby('month').size())
    if 'intimacy' in df.columns:
        st.subheader("亲密度趋势")
        df['date'] = pd.to_datetime(df['date'])
        st.line_chart(df.sort_values('date').set_index('date')['intimacy'])
    all_tags = []
    for e in entries:
        if e.get('tags'):
            all_tags.extend([t.strip() for t in e['tags'].split(',') if t.strip()])
    if all_tags:
        tag_counts = pd.Series(all_tags).value_counts()
        st.subheader("常用标签")
        st.bar_chart(tag_counts)

# ================= 导航栏 =================
st.sidebar.title("恋爱日记")
menu = st.sidebar.radio("", [
    "首页",
    "日记",
    "照片墙",
    "地图",
    "统计",
    "设置"
])

if menu == "首页":
    home_page()
elif menu == "日记":
    diary_page()
elif menu == "照片墙":
    gallery_page()
elif menu == "地图":
    map_page()
elif menu == "统计":
    stats_page()
elif menu == "设置":
    settings_page()