import streamlit as st
import sys
import os

# Set environment variables to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.pipeline import YuGiOhRecommendationPipeline
from dotenv import load_dotenv

st.set_page_config(page_title="Yu-Gi-Oh! Card Recommender", layout="wide")

load_dotenv()

@st.cache_resource
def init_pipeline():
    try:
        return YuGiOhRecommendationPipeline()
    except Exception as e:
        st.error(f"Failed to initialize Yu-Gi-Oh! pipeline: {str(e)}")
        st.info("💡 Make sure you've built the vector store first by running: `python pipeline/build_pipeline.py`")
        return None

pipeline = init_pipeline()

if pipeline is None:
    st.error("❌ Failed to initialize the Yu-Gi-Oh! recommendation system.")
    st.stop()

st.title("🃏 Yu-Gi-Oh! Card Recommender System")
st.markdown("Discover the perfect Yu-Gi-Oh! cards for your deck based on your strategy preferences!")

# Add info section
with st.expander("ℹ️ How to use this recommender", expanded=True):
    st.markdown("""
    1. **Describe your strategy**: Enter what type of cards or strategy you're looking for
    2. **Be specific**: Mention card types (Monster, Spell, Trap), attributes, or playstyles
    3. **Use examples**: Try common searches like "Powerful dragon monsters" or "Trap cards for defense"
    4. **Get recommendations**: The AI will suggest cards that match your criteria

    **Example searches:**
    - "Light attribute fairy monsters for healing"
    - "Quick-play spells for battle phase"
    - "Link summoning support cards"
    - "Cards that work in a Blue-Eyes deck"
    - "High ATK monsters for aggressive decks"
    - "Fusion summoning support cards"
    """)

# Example queries in a dropdown
query_examples = [
    "Powerful dragon monsters with high attack points",
    "Spell cards for summoning multiple monsters",
    "Trap cards that destroy opponent's cards",
    "Light attribute warriors for a deck",
    "Cards that work well in a Dark Magician deck",
    "Fusion summoning support cards"
]

query = st.text_input(
    "Enter your card preferences:",
    placeholder="e.g., Powerful dragon monsters with high attack points"
)

if query:
    with st.spinner("🔍 Finding the perfect cards for your deck..."):
        try:
            response = pipeline.recommend(query)
            st.markdown("### 🎴 Recommended Cards")
            st.write(response)
        except Exception as e:
            st.error(f"❌ Error getting recommendations: {str(e)}")
            st.info("💡 Make sure you've built the vector store first by running: `python pipeline/build_pipeline.py`")


