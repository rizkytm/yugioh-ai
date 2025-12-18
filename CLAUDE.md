# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered **Yu-Gi-Oh! card recommendation system** (v0.1) that uses Retrieval-Augmented Generation (RAG) with Large Language Models. The system analyzes user preferences about Yu-Gi-Oh! cards and strategies, providing personalized card recommendations using vector search and LLM reasoning. The system was originally built for anime recommendations and has been fully converted to handle Yu-Gi-Oh! cards.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
export GROQ_API_KEY="your_groq_api_key"
export HUGGINGFACEHUB_API_TOKEN="your_hf_token"
export TOKENIZERS_PARALLELISM="false"  # Prevents tokenizer warnings
```

### Build and Run
```bash
# Build the vector store from Yu-Gi-Oh! card data
python pipeline/build_pipeline.py

# Run the Streamlit web application
streamlit run app/app.py --server.port=8501
```

### ChromaDB Rebuild
```bash
# Clear and rebuild the vector store
rm -rf chroma_db
python pipeline/build_pipeline.py
```

## Architecture

### Core Components
- **YuGiOhRecommendationPipeline** (`pipeline/pipeline.py`): Main orchestrator for card recommendations
- **YuGiOhRecommender** (`src/recommender.py`): LLM-based recommendation engine using Groq's Llama 3.1 8B
- **VectorStoreBuilder** (`src/vector_store.py`): ChromaDB vector store management with `langchain-chroma`
- **YuGiOhDataLoader** (`src/data_loader.py`): Yu-Gi-Oh! card data processing with cleaning and formatting
- **Streamlit App** (`app/app.py`): Web interface with expanded help section

### Data Flow
1. **Raw Yu-Gi-Oh! card data** (`data/yugioh_cards.csv`) with 500+ cards including stats, effects, and metadata
2. **Data Processing**: Card data cleaned, formatted, and combined into searchable `combined_info` strings
3. **Text embeddings** generated using HuggingFace `all-MiniLM-L6-v2` model
4. **Vector storage** in ChromaDB (`chroma_db/`) for semantic card search
5. **User queries** processed through modern LangChain LCEL pattern with custom prompts
6. **LLM generates** 3 personalized card recommendations with ATK/DEF stats and strategic advice

### Key Configuration
- **LLM**: Llama 3.1 8B-instant via Groq API
- **Embeddings**: HuggingFace all-MiniLM-L6-v2
- **Vector Store**: ChromaDB with `langchain-chroma` (automatic persistence)
- **Web UI**: Streamlit on port 8501
- **Prompt Engineering**: Custom Yu-Gi-Oh! prompts with anti-duplication guidelines

### Data Requirements
- **Raw CSV**: `data/yugioh_cards.csv` must contain: `name`, `type`, `desc` (minimum)
- **Available Columns**: 17 total including `atk`, `def`, `level`, `rank`, `attribute`, `archetype`, prices
- **Processed Output**: `data/yugioh_processed.csv` with `combined_info` field for semantic search
- **Card Types**: Monsters, Spells, Traps with various subtypes and strategic attributes

## Environment Setup

Required environment variables:
- `GROQ_API_KEY`: Groq API access for LLM recommendations
- `HUGGINGFACEHUB_API_TOKEN`: HuggingFace token for embeddings
- `TOKENIZERS_PARALLELISM="false"`: Prevents tokenizer parallelism warnings

## Modern LangChain Integration

### Updated Dependencies
- `langchain-core`: Core LangChain components (prompts, messages)
- `langchain-text-splitters`: Text splitting (RecursiveCharacterTextSplitter)
- `langchain_chroma`: Modern ChromaDB integration (replaces deprecated langchain_community version)
- `langchain_groq`: Groq API integration

### Prompt Engineering
- **Custom Yu-Gi-Oh! prompts** in `src/prompt_template.py`
- **Anti-duplication guidelines** to prevent repeated recommendations
- **Monster card focus** including ATK/DEF stats in recommendations
- **Strategic context** for deck building and gameplay decisions

## Data Sources and Scraping

### Yu-Gi-Oh! Card Data
- **Source**: YGOProDeck API (`data/scraper.py`)
- **Coverage**: 500+ Yu-Gi-Oh! cards across all types (monsters, spells, traps)
- **Data Quality**: Cleaned CSV with proper escaping, no malformed records
- **Update Frequency**: Can be refreshed by re-running the scraper

### Scraping Features
- **Robust HTTP handling** with retry logic and rate limiting
- **Cloudflare bypass** techniques for API access
- **Data validation** and CSV formatting with proper quoting
- **Error handling** and progress tracking

## Logging and Error Handling
- Structured logging to `logs/log_YYYY-MM-DD.log`
- Custom exception handling with file/line tracking (`utils/custom_exception.py`)
- Comprehensive error context for debugging
- Graceful degradation for missing data or API failures

## Backward Compatibility
- Legacy class names maintained (`AnimeDataLoader`, `AnimeRecommender`, `AnimeRecommendationPipeline`)
- Migration path provided to new Yu-Gi-Oh! specific classes
- Warning messages guide developers to updated implementations

## Testing and Validation
- **Pipeline testing**: Verify vector store creation and loading
- **Data validation**: Ensure CSV format consistency and field completeness
- **Prompt testing**: Validate recommendation quality and anti-duplication
- **UI testing**: Streamlit interface functionality and user experience