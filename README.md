# Yu-Gi-Oh! Card Recommender 🃏

An AI-powered Yu-Gi-Oh! card recommendation system that uses Retrieval-Augmented Generation (RAG) with Large Language Models to help players discover the perfect cards for their decks based on strategy preferences.

## 🎯 Features

- **Smart Card Discovery**: AI-powered recommendations based on your strategy preferences
- **Comprehensive Database**: 500+ Yu-Gi-Oh! cards with detailed information
- **Stat-Aware**: Includes ATK/DEF points for monster cards in recommendations
- **Strategic Advice**: Get explanations of why cards fit your playstyle
- **Modern Tech Stack**: Built with LangChain, ChromaDB, and Groq's Llama 3.1
- **Clean Interface**: User-friendly Streamlit web application

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Groq API key (get free at [console.groq.com](https://console.groq.com))
- HuggingFace token (get free at [huggingface.co](https://huggingface.co))

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd yugioh-ai

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_actual_api_key_here
HUGGINGFACEHUB_API_TOKEN=hf_your_actual_token_here
```

Or export them directly:
```bash
export GROQ_API_KEY="gsk_your_actual_api_key_here"
export HUGGINGFACEHUB_API_TOKEN="hf_your_actual_token_here"
export TOKENIZERS_PARALLELISM="false"
```

### Step 3: Scrape Yu-Gi-Oh! Card Data

Scrape the Yu-Gi-Oh! card database from the official API:

**Option A: Scrape ALL Cards (Recommended)**
```bash
python data/scraper.py --all
```
This will collect all 12,000+ Yu-Gi-Oh! cards available in the database.

**Option B: Scrape Specific Number of Pages**
```bash
python data/scraper.py --pages 10
```
This will scrape 10 pages (1,000 cards).

**Option C: Default (5 pages)**
```bash
python data/scraper.py
```

### Step 4: Build Vector Store

Build the search index from Yu-Gi-Oh! card data:
```bash
python pipeline/build_pipeline.py
```

Expected output (for full dataset):
```
Processed 12,847 Yu-Gi-Oh! cards
Yu-Gi-Oh! vector store built successfully...
```

### Step 5: Launch Application

```bash
streamlit run app/app.py --server.port=8501
```

Open your browser and navigate to `http://localhost:8501` to start discovering cards!

### Optional: Verify Installation

Test that all components work:
```bash
python -c "from src.vector_store import VectorStoreBuilder; print('✅ Vector store import successful')"
python -c "from pipeline.pipeline import YuGiOhRecommendationPipeline; print('✅ Pipeline import successful')"
```

## 💡 How to Use

1. **Describe your strategy**: Enter what type of cards or strategy you're looking for
2. **Be specific**: Mention card types (Monster, Spell, Trap), attributes, or playstyles
3. **Get recommendations**: The AI will suggest 3 cards that match your criteria

**Example searches:**
- "Powerful dragon monsters with high attack points"
- "Light attribute fairy monsters for healing"
- "Quick-play spells for battle phase"
- "Trap cards that destroy opponent's cards"
- "Cards that work in a Blue-Eyes deck"
- "Fusion summoning support cards"

## 🏗️ Project Structure

```
yugioh-ai/
├── app/
│   └── app.py                    # Streamlit web interface
├── src/
│   ├── data_loader.py            # Yu-Gi-Oh! card data processing
│   ├── vector_store.py           # ChromaDB vector store management
│   ├── recommender.py            # LLM recommendation engine
│   └── prompt_template.py        # Custom Yu-Gi-Oh! prompts
├── pipeline/
│   ├── build_pipeline.py         # Main pipeline runner
│   └── pipeline.py               # Orchestration logic
├── data/
│   ├── yugioh_cards.csv          # Raw Yu-Gi-Oh! card data (500+ cards)
│   ├── yugioh_processed.csv      # Processed search data
│   └── scraper.py                # Card data scraper
├── chroma_db/                    # Vector database storage
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
├── CLAUDE.md                    # Development documentation
└── README.md                     # This file
```

## 🔧 Technology Stack

- **Backend**: Python 3.10+
- **LLM**: Groq's Llama 3.1 8B model
- **Vector Database**: ChromaDB with semantic search
- **Embeddings**: HuggingFace `all-MiniLM-L6-v2`
- **Framework**: LangChain (modern v2.0+)
- **Frontend**: Streamlit web interface
- **Data Processing**: Pandas for CSV handling

## 🛠️ Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'src'**
```bash
# Run from project root directory
cd yugioh-ai
python pipeline/build_pipeline.py
```

**ChromaDB persist() error**
- This is fixed in the latest version. The database automatically persists.

**Tokenizer parallelism warnings**
```bash
export TOKENIZERS_PARALLELISM="false"
```

**API connection errors**
- Verify your Groq API key is valid
- Check your internet connection
- Ensure you have API credits available

**Vector store not found**
```bash
# Rebuild the vector store
rm -rf chroma_db
python pipeline/build_pipeline.py
```

### Debug Mode

Enable detailed logging:
```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from pipeline.pipeline import YuGiOhRecommendationPipeline
pipeline = YuGiOhRecommendationPipeline()
"
```

## 📊 Data Source

The Yu-Gi-Oh! card data is sourced from:
- **API**: YGOProDeck API (ygoprodeck.com)
- **Coverage**: 500+ cards across all types
- **Data includes**: Names, types, effects, stats, attributes, archetypes
- **Update frequency**: Can be refreshed by re-running the scraper

To update the card database:
```bash
python data/scraper.py
python pipeline/build_pipeline.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes. Yu-Gi-Oh! card data is used under fair use for analysis and recommendation purposes.

## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [CLAUDE.md](CLAUDE.md) for technical details
3. Create an issue with:
   - Python version
   - Error messages
   - Steps to reproduce

## 🎮 Happy Dueling!

Discover your next favorite Yu-Gi-Oh! cards and build the ultimate deck with AI-powered recommendations!