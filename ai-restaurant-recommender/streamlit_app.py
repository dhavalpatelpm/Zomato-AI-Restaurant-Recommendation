"""
Zomato AI Restaurant Recommender - Streamlit App
Deploy on Streamlit Cloud: set working directory to ai-restaurant-recommender
"""

import streamlit as st
from src.phase3_api_service.service import (
    get_all_localities,
    get_all_cuisines,
    filter_restaurants_with_fallback,
    _row_to_dict,
)
from src.phase3_api_service.schemas import RecommendationRequest
from src.phase3_api_service.routes import recommend

st.set_page_config(
    page_title="Zomato AI Recommender",
    page_icon="🍽️",
    layout="centered",
)

# Custom styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .accent-red { color: #E23744; }
    .subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.85);
        margin-bottom: 1.5rem;
    }
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        font-weight: 600 !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="main-header"><span class="accent-red">Zomato</span> AI Recommender</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">Helping you find the best places to eat in <span class="accent-red">Bangalore</span> city</p>',
    unsafe_allow_html=True,
)

# Load localities and cuisines (cached)
@st.cache_data(ttl=3600)
def load_options():
    try:
        localities = get_all_localities()
        cuisines = get_all_cuisines()
        return localities, cuisines
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return [], []

localities, cuisines_list = load_options()

# Price range options
PRICE_RANGES = [
    (500, "Budget (₹ < 500)"),
    (1500, "Mid-range (₹500 - ₹1500)"),
    (5000, "Premium (₹ > 1500)"),
]

# Form
with st.form("recommend_form"):
    col1, col2 = st.columns(2)

    with col1:
        locality = st.selectbox(
            "📍 Select Locality *",
            options=[""] + localities,
            format_func=lambda x: "Select locality..." if x == "" else x.title(),
        )
        price_range = st.selectbox(
            "💰 Price Range *",
            options=[p[0] for p in PRICE_RANGES],
            format_func=lambda x: next(p[1] for p in PRICE_RANGES if p[0] == x),
        )

    with col2:
        selected_cuisines = st.multiselect(
            "🍴 Cuisines (Multi-select) *",
            options=cuisines_list,
            default=[],
            help="Select one or more cuisines",
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
                    st.warning("No recommendations found. Try adjusting your filters (lower rating, different cuisines, or higher price range).")
                else:
                    if response.relaxed_message:
                        st.info(response.relaxed_message)

                    st.success(f"**{response.total_results}** result(s) found")

                    for i, rec in enumerate(response.recommendations, 1):
                        with st.container():
                            st.markdown(f"### {i}. {rec.get('restaurant_name', 'Unknown')}")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Rating", f"{rec.get('rating', 0):.1f} ★")
                            with col_b:
                                st.metric("Avg. for two", f"₹{rec.get('price_range', 0)}")
                            if rec.get("cuisines"):
                                st.caption(f"🍴 {rec['cuisines']}")
                            if rec.get("address") or rec.get("locality"):
                                st.caption(f"📍 {rec.get('address') or rec.get('locality', '')}")
                            if rec.get("reason"):
                                st.markdown(f"**Why you'll like it:** {rec['reason']}")
                            st.divider()

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.exception(e)

# Top cuisines
st.markdown("---")
st.markdown("**Top cuisines in Bangalore**")
top_cuisines = ["North Indian", "Chinese", "South Indian", "Fast Food", "Biryani"]
st.markdown(
    "  •  ".join([f"**{c}**" for c in top_cuisines])
)

# Footer
st.markdown("---")
st.caption("Powered by GROQ AI • Data from Zomato Bangalore")
