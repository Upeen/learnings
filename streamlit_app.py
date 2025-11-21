import streamlit as st
import json
import os

# ==========================================
# Load Data (cached)
# ==========================================
@st.cache_data
def load_roadmaps():
    with open("roadmaps.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["roadmaps"]

roadmaps = load_roadmaps()

# ==========================================
# Page Setup
# ==========================================
st.set_page_config(page_title="Learning Roadmap Explorer", layout="wide")

# ==========================================
# Custom CSS (UI, Animations, Sticky Sidebar)
# ==========================================
st.markdown("""
<style>

body {
    background-color: #0a0a0a !important;
}

/* --- Sticky Sidebar --- */
[data-testid="stSidebar"] {
    position: sticky !important;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    z-index: 999;
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(8px);
}

/* --- Grid for cards --- */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
    grid-gap: 20px;
}

/* --- Card Styling + Animation --- */
.card {
    background-color: #1a1a1a;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(0,150,255,0.3);
    box-shadow: 0 4px 20px rgba(0,150,255,0.15);
    opacity: 0;
    transform: translateY(25px);
    animation: fadeUp 0.7s ease-out forwards;
    transition: all 0.25s ease;
}

.card:hover {
    transform: scale(1.02) translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,150,255,0.45);
}

@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
}

.card:nth-child(1) { animation-delay: 0.0s; }
.card:nth-child(2) { animation-delay: 0.1s; }
.card:nth-child(3) { animation-delay: 0.2s; }

.topic-box {
    padding: 10px;
    margin: 10px 0;
    background: #111;
    border-radius: 8px;
    border-left: 4px solid #0099ff;
    animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.tag {
    display: inline-block;
    padding: 5px 12px;
    background: rgba(0,150,255,0.25);
    border-radius: 8px;
    color: #66d0ff;
    font-size: 12px;
    margin: 4px 6px 0 0;
    transition: 0.2s ease-in-out;
}

.tag:hover {
    background: #0099ff;
    color: white;
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# Header
# ==========================================
st.title("📘 Roadmap Explorer")
st.write("A modern, animated roadmap viewer.")

# ==========================================
# Sidebar Filters
# ==========================================
st.sidebar.header("🔍 Filters & Viewer Options")

difficulty_filter = st.sidebar.selectbox(
    "Difficulty Level",
    ["all", "beginner", "intermediate", "advanced", "expert"],
)

search_text = st.sidebar.text_input("Search keyword")

roadmap_titles = ["All Roadmaps"] + [r["title"] for r in roadmaps]
selected_title = st.sidebar.selectbox("Choose Roadmap", roadmap_titles)

show_tools = st.sidebar.checkbox("Show Tools", True)
collapse_levels = st.sidebar.checkbox("Collapse Skill Levels", False)

# ==========================================
# Filtering Logic
# ==========================================
filtered = roadmaps

if difficulty_filter != "all":
    filtered = [r for r in filtered if r["difficulty"] == difficulty_filter]

if selected_title != "All Roadmaps":
    filtered = [r for r in filtered if r["title"] == selected_title]

if search_text:
    q = search_text.lower()
    filtered = [
        r for r in filtered if
        q in r["title"].lower()
        or q in r["description"].lower()
        or any(q in tool.lower() for tool in r["tools"])
        or any(q in topic["topic"].lower()
               for lvl in r["levels"].values()
               for topic in lvl)
        or any(q in res.lower() for res in r.get("resources", []))
    ]

# ==========================================
# Cached Renderer
# ==========================================
@st.cache_data
def render_card(roadmap):
    return f"""
    <div class="card">
        <h2 style="color:#4db8ff;">🔷 {roadmap['title']}</h2>
        <img src="{roadmap['image']}" width="60">
        <p style="color:#bbb;">{roadmap['description']}</p>
    </div>
    """

# ==========================================
# Render Cards in Grid
# ==========================================
st.markdown("<div class='card-grid'>", unsafe_allow_html=True)

if not filtered:
    st.warning("No roadmaps match your filters.")
else:
    for roadmap in filtered:

        st.markdown(render_card(roadmap), unsafe_allow_html=True)

        # Levels
        for level in ["beginner", "intermediate", "advanced", "expert"]:
            items = roadmap["levels"].get(level, [])
            if not items:
                continue

            level_title = f"📌 {level.capitalize()} Level"

            if collapse_levels:
                container = st.expander(level_title)
            else:
                st.markdown(f"### {level_title}")
                container = st.container()

            with container:
                for item in items:
                    st.markdown(f"#### {item['topic']}")
                    st.markdown(
                        f"<div class='topic-box'><b>Concepts:</b> {', '.join(item['concepts'])}</div>",
                        unsafe_allow_html=True
                    )

        # Tools
        if show_tools:
            st.markdown("### 🛠 Tools")
            for tool in roadmap["tools"]:
                st.markdown(f"<span class='tag'>{tool}</span>", unsafe_allow_html=True)

        # Resources
        if "resources" in roadmap and roadmap["resources"]:
            st.markdown("### 📚 Resources")
            for res in roadmap["resources"]:
                st.markdown(f"- [{res}]({res})")

        st.markdown("---")

st.markdown("</div>", unsafe_allow_html=True)
