"""
Zomato AI Restaurant Recommender - Streamlit App
Matches the React app UI/UX. Deploy on Streamlit Cloud: working dir = ai-restaurant-recommender
"""

import streamlit as st
from src.phase3_api_service.service import (
    get_all_localities,
    get_all_cuisines,
)
from src.phase3_api_service.schemas import RecommendationRequest
from src.phase3_api_service.routes import recommend

st.set_page_config(
    page_title="Zomato AI Recommender",
    page_icon="🍽️",
    layout="centered",
)

# Match React app styling
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: #000000;
        background-image: radial-gradient(ellipse 80% 50% at 50% 0%, #5a1a1a 0%, transparent 50%),
            linear-gradient(180deg, #000000 0%, #3d0a0a 50%, #000000 100%);
    }
    
    /* Center main content - match React max-width 960px */
    [data-testid="stAppViewContainer"] > section > div {
        max-width: 960px;
        margin-left: auto;
        margin-right: auto;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    /* Hero section - CENTERED */
    .hero-section {
        text-align: center;
        margin-bottom: 2rem;
        max-width: 960px;
        margin-left: auto;
        margin-right: auto;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        text-align: center;
    }
    .accent-red {
        color: #E23744 !important;
        text-shadow: 0 0 20px rgba(226, 55, 68, 0.4);
    }
    .hero-subtitle {
        font-size: 1.35rem;
        color: rgba(255,255,255,0.85);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Hero stats pill - centered */
    .hero-stats {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 0.5rem 1.5rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 999px;
        font-size: 1.15rem;
        color: rgba(255,255,255,0.85);
        font-weight: 500;
        margin-bottom: 2rem;
    }
    .stat-number {
        color: #E23744 !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    .stat-divider {
        color: #e91e63;
        opacity: 0.6;
    }
    
    /* Top cuisines section - centered */
    .top-cuisines-wrap {
        text-align: center;
        margin-bottom: 2rem;
    }
    .top-cuisines-label {
        font-size: 1.15rem;
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 1rem;
        display: block;
        text-align: center;
    }
    .top-cuisines-boxes {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.75rem;
        margin-bottom: 2rem;
    }
    .top-cuisine-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.6rem 1.25rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .top-cuisine-box:hover {
        border-color: #e91e63;
        background: rgba(233, 30, 99, 0.1);
        box-shadow: 0 0 16px rgba(233, 30, 99, 0.2);
    }
    
    /* Form card - centered, match original */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    /* Form submit row - full width button */
    div[data-testid="stForm"] > div:last-child {
        width: 100%;
    }
    
    /* Result cards */
    .rec-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .rec-card:hover {
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .rec-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .rec-rating {
        color: #E23744;
        font-weight: 700;
    }
    .rec-line { margin: 0.25rem 0; color: rgba(255,255,255,0.85); font-size: 0.95rem; }
    .rec-why { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.9); }
    
    /* Top cuisine buttons - style buttons outside forms */
    .stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.25rem !important;
    }
    .stButton > button:hover {
        border-color: #e91e63 !important;
        background: rgba(233, 30, 99, 0.1) !important;
    }
    
    /* Submit button - match Image 3: full-width, red-pink gradient */
    div[data-testid="stForm"] .stButton {
        width: 100%;
    }
    div[data-testid="stForm"] .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #e91e63 0%, #c62828 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.875rem 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for quick-add cuisines
if "preselected_cuisines" not in st.session_state:
    st.session_state.preselected_cuisines = []

# Load options (cached)
@st.cache_data(ttl=3600)
def load_options():
    try:
        localities = get_all_localities()
        cuisines = get_all_cuisines()
        return localities, cuisines
    except Exception as e:
        return [], []

localities, cuisines_list = load_options()
locality_count = len(localities)
cuisine_count = len(cuisines_list)

# Hero section - all centered
hero_html = f'''
<div class="hero-section">
    <p class="hero-title"><span class="accent-red">Zomato</span> AI Recommender</p>
    <p class="hero-subtitle">Helping you find the best places to eat in <span class="accent-red">Bangalore</span> city</p>
    <div class="hero-stats">
        <span>📍 <span class="stat-number">{locality_count}</span> Localities</span>
        <span class="stat-divider">|</span>
        <span>🍴 <span class="stat-number">{cuisine_count}</span> Cuisines</span>
    </div>
    <div class="top-cuisines-wrap">
        <span class="top-cuisines-label">Top cuisines in Bangalore</span>
    </div>
</div>
'''
st.markdown(hero_html, unsafe_allow_html=True)

# Top cuisines - centered row of clickable boxes
TOP_CUISINES = ["North Indian", "Chinese", "South Indian", "Fast Food", "Biryani"]
# Use side columns to center the 5 cuisine buttons
_, c1, c2, c3, c4, c5, _ = st.columns([1, 1, 1, 1, 1, 1, 1])
cuisine_cols = [c1, c2, c3, c4, c5]
for i, cuisine in enumerate(TOP_CUISINES):
    with cuisine_cols[i]:
        if st.button(cuisine, key=f"top_{cuisine}", use_container_width=True):
            if cuisine not in st.session_state.preselected_cuisines:
                st.session_state.preselected_cuisines.append(cuisine)
            st.rerun()

# Build default cuisines from preselected
default_cuisines = [
    c for c in st.session_state.preselected_cuisines
    if c in cuisines_list
]

PRICE_RANGES = [
    (500, "Budget (₹ < 500)"),
    (1500, "Mid-range (₹500 - ₹1500)"),
    (5000, "Premium (₹ > 1500)"),
]

# Form - layout matches original: Left: Locality, Cuisines | Right: Price Range, Rating
with st.form("recommend_form"):
    col1, col2 = st.columns(2)
    with col1:
        locality = st.selectbox(
            "📍 Select Locality *",
            options=[""] + localities,
            format_func=lambda x: "Select locality..." if x == "" else x.title(),
        )
        selected_cuisines = st.multiselect(
            "🍴 Cuisines (Multi-select) *",
            options=cuisines_list,
            default=default_cuisines,
            help="Select one or more cuisines. Click top cuisines above to quick-add.",
        )
    with col2:
        price_range = st.selectbox(
            "💰 Price Range *",
            options=[p[0] for p in PRICE_RANGES],
            format_func=lambda x: next(p[1] for p in PRICE_RANGES if p[0] == x),
        )
        min_rating = st.slider(
            "⭐ Min Rating *",
            min_value=3.0,
            max_value=5.0,
            value=4.0,
            step=0.5,
            format="%.1f",
        )

    submitted = st.form_submit_button("Get Recommendations ✨")

# Clear preselected after form submit
if submitted:
    st.session_state.preselected_cuisines = []

if submitted:
    if not locality or not locality.strip():
        st.error("Please select a locality.")
    elif not selected_cuisines:
        st.error("Please select at least one cuisine.")
    else:
        with st.spinner("Finding the best restaurants for you..."):
            try:
                req = RecommendationRequest(
                    locality=locality.strip().lower(),
                    price_range=price_range,
                    min_rating=float(min_rating),
                    cuisines=selected_cuisines,
                )
                response = recommend(req)

                if response.total_results == 0:
                    st.warning(
                        "No recommendations found. Try adjusting your filters "
                        "(lower rating, different cuisines, or higher price range)."
                    )
                else:
                    if response.relaxed_message:
                        st.info(response.relaxed_message)
                    st.markdown(f"### **{response.total_results}** result(s) found")

                    for i, rec in enumerate(response.recommendations, 1):
                        rating = rec.get("rating", 0)
                        price = rec.get("price_range", 0)
                        cuisines_str = rec.get("cuisines", "")
                        address = rec.get("address") or rec.get("locality", "")
                        reason = rec.get("reason", "")

                        card_html = f"""
                        <div class="rec-card">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                                <span class="rec-title">{i}. {rec.get('restaurant_name', 'Unknown')}</span>
                                <span class="rec-rating">{rating:.1f} ★</span>
                            </div>
                            {f'<p class="rec-line">🍴 {cuisines_str}</p>' if cuisines_str else ''}
                            {f'<p class="rec-line">💰 Avg. ₹{price} for two</p>' if price else ''}
                            {f'<p class="rec-line">📍 {address}</p>' if address else ''}
                            {f'<div class="rec-why"><strong>Why you\'ll like it:</strong> {reason}</div>' if reason else ''}
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.exception(e)

# Footer
st.markdown("---")
st.caption("Powered by GROQ AI • Made by Dhaval Patel • Data from Zomato Bangalore")
