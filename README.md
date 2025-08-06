# Instagram Script-Writer

![CI](https://github.com/yourusername/instagram-script-writer/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)

> A full-stack Python pipeline that learns your Instagram video‐script style and generates fresh, platform-optimized content on demand.

## 🌟 Features

- **Style Learning**: Analyzes your existing Instagram scripts to understand your unique voice
- **Retrieval-Augmented Generation**: Combines your past content with AI to maintain consistent style
- **Two-Stage Polish**: Draft generation followed by high-quality refinement
- **Quality Control**: Automatic checks for caption length, hashtag count, and more
- **User-Friendly UI**: Simple Streamlit interface for script generation
- **Efficient Embeddings**: Uses `llama-text-embed-v2` from HuggingFace for high-quality embeddings
- **Telugu Reels Scraper**: Automatically scrapes and processes trending Telugu reels

## 📋 Requirements

1. Python 3.10+
2. OpenAI API key
3. Pinecone API key and serverless index
4. Your existing Instagram scripts (as text files)
5. HuggingFace's `llama-text-embed-v2` model (automatically downloaded)

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/instagram-script-writer.git
cd instagram-script-writer

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to add your API keys
```

The environment file should contain:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key

# Pinecone Vector Database (required)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST=https://scriptwriter-jltat6g.svc.aped-4627-b74a.pinecone.io
PINECONE_INDEX=scriptwriter
PINECONE_REGION=us-east-1

# Embedding Model Configuration
EMBEDDING_MODEL=llama-text-embed-v2

# Optional Instagram Credentials (for authenticated scraping)
INSTA_USERNAME=your_instagram_username
INSTA_PASSWORD=your_instagram_password
```

> **Note**: The application uses HuggingFace's `llama-text-embed-v2` embedding model for optimal vector representation of your scripts. This provides better semantic understanding of your content than the default OpenAI embeddings.

### Setup Your Scripts

1. Create text files of your past Instagram scripts in the `scripts/` directory
2. Each script should be a separate `.txt` file

## 📝 Usage

### 1. Ingest Your Scripts

Process and index your existing scripts into the vector database:

```bash
python src/ingest.py
```

Example output:

```
Initializing Pinecone...
Loading scripts from scripts directory...
Found 12 scripts to process
Embedding documents...
[✓] Successfully ingested 12 scripts into index 'ig-scripts'
```

### 2. Generate a Script (CLI)

Generate an Instagram script from the command line:

```bash
python src/generator.py
```

You'll be prompted to enter a topic:

```
Topic: sustainable fashion tips
Generating script...
Polishing...

HOOK: Want to look stylish AND save the planet? 🌎

BODY:
Let's talk sustainable fashion that doesn't sacrifice your style.

I used to think eco-friendly meant boring basics, but that myth needs busting! Here are three game-changers I've discovered:

1️⃣ Thrift with intention - Go with a list, not aimlessly. You'll find designer gems at fraction of the cost.

2️⃣ Learn the "30 wears test" - Before buying, ask: "Will I wear this at least 30 times?" If not, leave it.

3️⃣ Care techniques matter - Washing in cold water and air-drying can double your clothes' lifespan!

The fashion industry creates 10% of global carbon emissions, but your choices can help change that.

CTA: Which sustainable fashion tip are you trying first? Comment below and let's inspire each other!

CAPTION: Small closet changes = big planet impact. These sustainable fashion hacks will transform your style AND carbon footprint! 🌿👗

VISUAL DIRECTIONS:
- Start with split screen showing fast fashion pile vs. curated sustainable wardrobe
- Show yourself modeling thrifted outfits with price comparisons
- Use text overlay for the 30 wears calculation
- Demonstrate washing techniques
- End with a slow-motion twirl in your favorite sustainable outfit

HASHTAGS:
#SustainableFashion #EcoFriendlyStyle #SlowFashion #ThriftFinds #ConsciousCloset #GreenWardrobe #FashionRevolution
```

### 3. Telugu Reels Scraper

Fetch trending Telugu reels and generate script templates from them:

```bash
# Run the complete pipeline with a single command
python src/run_all.py --mode full --topic "your topic"

# Or run individual components:
python src/run_all.py --mode scraper       # Fetch and process Telugu reels only
python src/run_all.py --mode ingest        # Index scripts including Telugu templates
python src/run_all.py --mode generate --topic "your topic"  # Generate from indexed scripts
```

Example output from scraper:

```
Starting scraper phase...
Fetching up to 100 reels for #Telugu
Saved 50 reels so far...
Completed scraping. Saved 87 reels out of 100 posts examined.
Loading reel data from data/raw_reels/Telugu/*.json
Loaded 87 reels
Saved top 20 reels to data/top_reels.csv
Created 20 script templates in scripts/auto_telugu
Scraper phase complete: 20 top reels processed, 20 script templates generated
```

### 4. Web Interface

Launch the Streamlit web app for an interactive experience:

```bash
streamlit run src/app.py
```

The web interface includes a "Refresh Telugu Examples" button in the sidebar that will:

1. Fetch trending Telugu reels from Instagram
2. Process them into script templates
3. Index them for use in script generation

This opens a browser window where you can:

- Enter topics for script generation
- Review generated scripts
- See quality control metrics
- Save and export your favorite scripts

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_generator.py

# Run with coverage report
pytest --cov=src
```

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t instagram-script-writer .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  -e PINECONE_HOST=your_pinecone_host \
  -e PINECONE_INDEX=scriptwriter \
  -e PINECONE_REGION=us-east-1 \
  -e EMBEDDING_MODEL=llama-text-embed-v2 \
  -v ./scripts:/app/scripts \
  instagram-script-writer
```

Or use docker-compose:

```bash
docker-compose up
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on the development process and how to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
