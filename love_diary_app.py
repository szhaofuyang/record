# love_diary_app.py - 精简优化版
import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
from PIL import Image
import io
import base64

# ================= 配置 =================
DATA_FILE = "data.json"
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# 初始化数据文件
def init_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "entries": [],
            "memorials": [],
            "todos": [],
            "quotes": ["你是我的一切。", "每天爱你多一点。", "喜欢你的笑容。", "你是我最美的风景。"]
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

def add_entry(entry):
    data = load_data()
    entry["id"] = len(data["entries"]) + 1
    data["entries"].append(entry)
    save_data(data)

def delete_entry(eid):
    data = load_data()
    data["entries"] = [e for e in data["entries"] if e.get("id") != eid]
    save_data(data)

def get_memorials():
    return load_data().get("memorials", [])

def add_memorial(name, date_str, repeat):
    data = load_data()
    data["memorials"].append({"name": name, "date": date_str, "repeat": repeat})
    save_data(data)

def delete_memorial(mid):
    data = load_data()
    data["memorials"] = [m for m in data["memorials"] if m.get("id") != mid]
    save_data(data)

def get_todos():
    return load_data().get("todos", [])

def add_todo(title, category):
    data = load_data()
    data["todos"].append({"title": title, "done": False, "category": category})
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

def get_random_quote():
    data = load_data()
    quotes = data.get("quotes", ["你是我的一切。"])
    import random
    return random.choice(quotes)

# ================= 主题配置 =================
st.set_page_config(page_title="恋爱日记", layout="wide", initial_sidebar_state="expanded")

# 简单CSS美化
st.markdown("""
<style>
    .main { background-color: #fef6f8; }
    .stButton>button { background-color: #FF6B8A; color: white; border-radius: 30px; }
    .stButton>button:hover { background-color: #ff4d7a; }
    .card { background: white; padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ================= 页面函数 =================
def home_page():
    st.header("💗 恋爱日记")
    # 在一起天数
    start_date = date(2022, 7, 4)  # 修改为你们的纪念日
    days = (date.today() - start_date).days
    st.markdown(f"<h2 style='text-align:center;'>在一起 <span style='color:#FF6B8A;'>{days}</span> 天</h2>", unsafe_allow_html=True)
    # 今日情话
    st.markdown(f"<div style='text-align:center;padding:1rem;background:#fef0f3;border-radius:16px;'>{get_random_quote()}</div>", unsafe_allow_html=True)
    # 最近3条日记
    entries = get_entries()[-3:][::-1]
    if entries:
        st.subheader("📖 最近记录")
        for e in entries:
            with st.expander(f"{e.get('date', '')} {e.get('title', '无标题')}"):
                st.write(e.get('content', '')[:200] + ("..." if len(e.get('content',''))>200 else ""))
    else:
        st.info("还没有日记，写一篇吧！")

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
                if e.get('tags'): st.caption(f"标签: {e['tags']}")
                if e.get('mood'): st.caption(f"心情: {e['mood']}")
                if e.get('location'): st.caption(f"地点: {e['location']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("删除", key=f"del_{e['id']}"):
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
                })
                st.success("已保存")
                st.rerun()

def memorial_page():
    st.header("🎉 纪念日")
    with st.form("add_memorial"):
        name = st.text_input("名称")
        date_str = st.date_input("日期", value=date.today())
        repeat = st.checkbox("每年重复")
        if st.form_submit_button("添加"):
            if name:
                data = load_data()
                data["memorials"].append({"name": name, "date": date_str.isoformat(), "repeat": repeat})
                save_data(data)
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
                        <span><b>{m['name']}</b></span>
                        <span style='color:#FF6B8A;'>{delta}天</span>
                    </div>
                    <div style='font-size:0.9rem;opacity:0.7;'>{m['date']} {'🔄' if m['repeat'] else ''}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("删除", key=f"del_mem_{m['id']}"):
                data = load_data()
                data["memorials"] = [mm for mm in data["memorials"] if mm.get("id") != m.get("id")]
                save_data(data)
                st.rerun()

def todo_page():
    st.header("✅ 待办清单")
    with st.form("add_todo"):
        title = st.text_input("任务")
        category = st.selectbox("分类", ["一起做的事", "惊喜", "日常", "其他"])
        if st.form_submit_button("添加"):
            if title:
                data = load_data()
                data["todos"].append({"title": title, "done": False, "category": category})
                save_data(data)
                st.rerun()
    todos = get_todos()
    if not todos:
        st.info("还没有待办")
    else:
        for idx, t in enumerate(todos):
            col1, col2, col3 = st.columns([4,1,1])
            with col1:
                if t["done"]:
                    st.markdown(f"~~{t['title']}~~ ({t['category']})")
                else:
                    st.write(f"{t['title']} ({t['category']})")
            with col2:
                if st.button("✅" if not t["done"] else "↩️", key=f"todo_{idx}"):
                    data = load_data()
                    data["todos"][idx]["done"] = not data["todos"][idx]["done"]
                    save_data(data)
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_todo_{idx}"):
                    data = load_data()
                    data["todos"].pop(idx)
                    save_data(data)
                    st.rerun()

def gallery_page():
    st.header("🖼️ 照片墙")
    st.info("照片上传功能已简化，请上传图片到 images 文件夹或通过日记上传（此版本暂不支持直接上传）")

def stats_page():
    st.header("📊 统计")
    entries = get_entries()
    if not entries:
        st.info("暂无数据")
        return
    df = pd.DataFrame(entries)
    st.subheader("心情分布")
    if 'mood' in df.columns:
        st.bar_chart(df['mood'].value_counts())
    st.subheader("每月记录数")
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    st.line_chart(df.groupby('month').size())
    if 'intimacy' in df.columns:
        st.subheader("亲密度趋势")
        df['date'] = pd.to_datetime(df['date'])
        st.line_chart(df.sort_values('date').set_index('date')['intimacy'])

# ================= 侧边栏 =================
st.sidebar.title("💗 恋爱日记")
menu = st.sidebar.radio("导航", ["🏠 首页", "📝 日记", "🎉 纪念日", "✅ 待办", "🖼️ 照片墙", "📊 统计"])

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
elif menu == "📊 统计":
    stats_page()