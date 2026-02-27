"""
Zomato AI Restaurant Recommender - Streamlit App
Pixel-accurate match to React app. Deploy: working dir = ai-restaurant-recommender
"""

import streamlit as st
from src.phase3_api_service.service import get_all_localities, get_all_cuisines
from src.phase3_api_service.schemas import RecommendationRequest
from src.phase3_api_service.routes import recommend

st.set_page_config(page_title="Zomato AI Recommender", page_icon="🍽️", layout="centered")

# === CSS: Match React app exactly ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { box-sizing: border-box; }
    .stApp {
        background: #000000;
        background-image: radial-gradient(ellipse 80% 50% at 50% 0%, #5a1a1a 0%, transparent 50%),
            linear-gradient(180deg, #000000 0%, #3d0a0a 50%, #000000 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    [data-testid="stAppViewContainer"] > section > div {
        max-width: 960px;
        margin-left: auto;
        margin-right: auto;
        padding: 2.5rem 1.5rem;
    }
    
    /* Hero - match React app (localhost:5173): 4rem title, 1.35rem subtitle */
    .hero-section { text-align: center; margin-bottom: 2rem; }
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    .accent-red { color: #E23744 !important; text-shadow: 0 0 20px rgba(226,55,68,0.4); }
    .hero-subtitle {
        font-size: 1.35rem;
        color: rgba(255,255,255,0.85);
        margin: 0 0 1.5rem 0;
        font-weight: 400;
    }
    .hero-stats {
        display: inline-flex;
        align-items: center;
        gap: 1rem;
        padding: 0.5rem 1.5rem;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 999px;
        font-size: 1.15rem;
        color: rgba(255,255,255,0.85);
        font-weight: 500;
    }
    .stat-number {
        color: #E23744 !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    .stat-divider { color: #e91e63; opacity: 0.6; font-weight: 300; }
    
    .top-cuisines-label {
        font-size: 1.15rem;
        color: #ffffff;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        display: block;
        text-align: center;
    }
    
    /* Form card - React filter-section */
    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    /* Labels - React: 0.9rem, font-weight 600 */
    .stForm label { font-size: 0.9rem !important; font-weight: 600 !important; color: rgba(255,255,255,0.85) !important; }
    
    /* Submit - React: 1.15rem, padding 1.125rem, gradient 135deg */
    div[data-testid="stForm"] .stButton { width: 100%; margin-top: 1rem; }
    div[data-testid="stForm"] .stButton > button {
        width: 100% !important;
        padding: 1.125rem 1.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #e91e63, #c62828) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 20px rgba(233,30,99,0.4) !important;
    }
    
    /* Top cuisine buttons - match React: no text wrap, centered */
    .stButton > button:not(div[data-testid="stForm"] .stButton > button) {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1.25rem !important;
        white-space: nowrap !important;
    }
    .stButton > button:hover:not(div[data-testid="stForm"] .stButton > button:hover) {
        border-color: #e91e63 !important;
        background: rgba(233,30,99,0.1) !important;
    }
    
    /* Validation error - React validation-error */
    .validation-err {
        background: rgba(244,67,54,0.15);
        border: 1px solid rgba(244,67,54,0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #ff8a80;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Relaxed message - React relaxed-message */
    .relaxed-msg {
        background: rgba(233,30,99,0.12);
        border: 1px solid rgba(233,30,99,0.3);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        color: rgba(255,255,255,0.85);
        margin-bottom: 1.5rem;
    }
    
    /* No results - React no-results */
    .no-results {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 14px;
        padding: 2.5rem;
        text-align: center;
    }
    .no-results-title { font-size: 1.2rem; font-weight: 600; color: #ffffff; margin: 0 0 0.5rem 0; }
    .no-results-msg { font-size: 0.95rem; color: rgba(255,255,255,0.85); margin: 0; }
    
    /* Results header - React results-count: 2rem */
    .results-count { font-size: 2rem !important; font-weight: 700 !important; color: #ffffff !important; }
    
    /* Recommendation card - React recommendation-card */
    .rec-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .rec-card:hover { border-color: rgba(255,255,255,0.3); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
    .rec-title { font-size: 1.25rem; font-weight: 700; color: #ffffff; margin: 0; }
    .rec-rating-badge {
        background: rgba(34,197,94,0.25);
        border: 1px solid rgba(34,197,94,0.5);
        color: #22c55e;
        padding: 0.25rem 0.6rem;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 600;
    }
    .rec-line { margin: 0.4rem 0; font-size: 0.9rem; color: rgba(255,255,255,0.6); }
    .rec-why {
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        padding-left: 1rem;
        border-left: 4px solid #e91e63;
        background: rgba(233,30,99,0.06);
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
        color: rgba(255,255,255,0.85);
    }
    
    /* Footer - React footer-badge */
    .footer-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(90deg, #E62C2F 0%, #3C151B 100%);
        border-radius: 12px;
        color: #ffffff;
        font-size: 0.85rem;
    }
    .footer-line1 { font-weight: 700; text-transform: uppercase; }
    .footer-line2 { font-size: 0.8rem; color: rgba(255,255,255,0.9); }

    @media (max-width: 600px) {
        .hero-title { font-size: 3rem; }
        .hero-subtitle { font-size: 1.15rem; }
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "preselected_cuisines" not in st.session_state:
    st.session_state.preselected_cuisines = []
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "ratings-high-low"
if "last_results" not in st.session_state:
    st.session_state.last_results = None

# Load data with error handling
@st.cache_data(ttl=3600)
def _load_options():
    try:
        localities = get_all_localities()
        cuisines = get_all_cuisines()
        return localities, cuisines, None
    except Exception as e:
        return [], [], str(e)

localities, cuisines_list, load_error = _load_options()

# Hero
st.markdown(f'''
<div class="hero-section">
    <h1 class="hero-title"><span class="accent-red">Zomato</span> AI Recommender</h1>
    <p class="hero-subtitle">Helping you find the best places to eat in <span class="accent-red">Bangalore</span> city</p>
    <div class="hero-stats">
        <span>📍 <span class="stat-number">{len(localities) if localities else "—"}</span> Localities</span>
        <span class="stat-divider">|</span>
        <span>🍴 <span class="stat-number">{len(cuisines_list) if cuisines_list else "—"}</span> Cuisines</span>
    </div>
    <span class="top-cuisines-label">Top cuisines in Bangalore</span>
</div>
''', unsafe_allow_html=True)

# Top cuisines - 5 equal columns, centered, no text wrap (match React localhost:5173)
TOP_CUISINES = ["North Indian", "Chinese", "South Indian", "Fast Food", "Biryani"]
c1, c2, c3, c4, c5 = st.columns(5)
for i, cuisine in enumerate(TOP_CUISINES):
    with [c1, c2, c3, c4, c5][i]:
        if st.button(cuisine, key=f"top_{cuisine}", use_container_width=True, disabled=not cuisines_list):
            if cuisine not in st.session_state.preselected_cuisines:
                st.session_state.preselected_cuisines.append(cuisine)
            st.rerun()

default_cuisines = [c for c in st.session_state.preselected_cuisines if c in (cuisines_list or [])]

PRICE_RANGES = [(500, "Budget (₹ < 500)"), (1500, "Mid-range (₹500 - ₹1500)"), (5000, "Premium (₹ > 1500)")]

# Form
with st.form("recommend_form"):
    col1, col2 = st.columns(2)
    with col1:
        locality = st.selectbox(
            "📍 Select Locality *",
            options=[""] + (localities or []),
            format_func=lambda x: "Select locality..." if x == "" else x.replace("_", " ").title(),
        )
        selected_cuisines = st.multiselect(
            "🍴 Cuisines (Multi-select) *",
            options=cuisines_list or [],
            default=default_cuisines,
            help="Type to search or add. Click top cuisines above to quick-add.",
        )
    with col2:
        price_range = st.selectbox(
            "💰 Price Range *",
            options=[p[0] for p in PRICE_RANGES],
            format_func=lambda x: next(p[1] for p in PRICE_RANGES if p[0] == x),
        )
        min_rating = st.slider(
            "⭐ Ratings *",
            min_value=3.0,
            max_value=5.0,
            value=4.5,
            step=0.5,
            format="%.1f",
        )

    submitted = st.form_submit_button("Get Recommendations ✨")

if submitted:
    st.session_state.preselected_cuisines = []

validation_error = None
if submitted:
    if not locality or not str(locality).strip():
        validation_error = "Locality is required! Please select a locality to continue."
    elif not selected_cuisines:
        validation_error = "Please select at least one cuisine."
    elif min_rating is None or (isinstance(min_rating, float) and (min_rating < 0 or min_rating > 5)):
        validation_error = "Rating must be between 0 and 5."
    elif not price_range or price_range <= 0:
        validation_error = "Invalid price range selected."

if validation_error:
    st.session_state.last_results = None
    st.markdown(f'<div class="validation-err">{validation_error}</div>', unsafe_allow_html=True)
elif submitted and not validation_error:
    with st.spinner("Finding the best restaurants for you..."):
        try:
            req = RecommendationRequest(
                locality=str(locality).strip().lower(),
                price_range=int(price_range),
                min_rating=float(min_rating),
                cuisines=selected_cuisines,
            )
            response = recommend(req)
            st.session_state.last_results = response
        except Exception as e:
            st.session_state.last_results = None
            err_msg = str(e) if str(e) else "Failed to fetch recommendations. Please try again."
            st.markdown(f'<div class="validation-err">{err_msg}</div>', unsafe_allow_html=True)

# Show results (from session state so sort persists)
response = st.session_state.last_results
if response is not None:
    if response.total_results == 0:
        st.markdown('''
        <div class="no-results">
            <p class="no-results-title">No recommendations found</p>
            <p class="no-results-msg">Try adjusting your filters (lower rating, different cuisines, or higher price range) to see more results.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        if response.relaxed_message:
            st.markdown(f'<div class="relaxed-msg">ℹ️ {response.relaxed_message}</div>', unsafe_allow_html=True)

        sort_opts = [
            ("ratings-high-low", "Ratings (High-Low)"),
            ("ratings-low-high", "Ratings (Low-High)"),
            ("price-high-low", "Price (High-Low)"),
            ("price-low-high", "Price (Low-High)"),
        ]
        recs = list(response.recommendations)
        get_rating = lambda r: float(r.get("rating") or 0)
        get_price = lambda r: int(r.get("price_range") or 0)
        sort_key = st.session_state.sort_by
        if sort_key == "price-high-low":
            recs.sort(key=get_price, reverse=True)
        elif sort_key == "price-low-high":
            recs.sort(key=get_price)
        elif sort_key == "ratings-low-high":
            recs.sort(key=get_rating)
        else:
            recs.sort(key=get_rating, reverse=True)

        st.markdown(f'<p class="results-count">{response.total_results} result{"s" if response.total_results != 1 else ""} found</p>', unsafe_allow_html=True)
        new_sort = st.selectbox("Sort by", options=[s[0] for s in sort_opts], format_func=lambda x: next(s[1] for s in sort_opts if s[0] == x), key="sort_select")
        if new_sort != sort_key:
            st.session_state.sort_by = new_sort
            st.rerun()

        for i, rec in enumerate(recs, 1):
            rating = rec.get("rating", 0)
            price = rec.get("price_range", 0)
            cuisines_str = rec.get("cuisines", "")
            address = rec.get("address") or rec.get("locality", "")
            reason = rec.get("reason", "")
            reason_block = f'<div class="rec-why"><strong>Why you\'ll like it:</strong> {reason}</div>' if reason else ''
            card = f'''
            <div class="rec-card">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.5rem;">
                    <span class="rec-title">{i}. {rec.get("restaurant_name", "Unknown")}</span>
                    <span class="rec-rating-badge">{float(rating):.1f} ★</span>
                </div>
                {f'<p class="rec-line">🍴 {cuisines_str}</p>' if cuisines_str else ''}
                {f'<p class="rec-line">💰 Avg. ₹{price} for two</p>' if price else ''}
                {f'<p class="rec-line">📍 {address}</p>' if address else ''}
                {reason_block}
            </div>
            '''
            st.markdown(card, unsafe_allow_html=True)

# Load error
if load_error and (not localities or not cuisines_list):
    st.warning(f"Could not load localities/cuisines. Error: {load_error}. Refresh the page to retry.")

# Footer
st.markdown("---")
st.markdown('''
<div class="footer-badge">
    <div>
        <span class="footer-line1">POWERED BY GROQ AI</span>
        <span class="footer-line2">Made by <strong>Dhaval Patel</strong> with</span>
    </div>
    <span style="font-size:2rem;">❤️</span>
</div>
''', unsafe_allow_html=True)
