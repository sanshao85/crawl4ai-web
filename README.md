# Crawl4AI Web Application

A modern web application built on top of Crawl4AI, providing an intuitive user interface for powerful web crawling capabilities.

## ✨ Features

- 🚀 **Real-time Web Crawling** - High-performance crawling engine powered by Crawl4AI
- 🎯 **Multiple Extraction Strategies** - Support for Default, LLM, CSS Selector, and more
- 📱 **Responsive Interface** - Modern Bootstrap 5 UI design
- ⚡ **Real-time Progress** - WebSocket-based live progress updates
- 📊 **Multi-format Results** - View results in Markdown, HTML, and JSON formats
- 💾 **One-click Download** - Download results in multiple formats
- 🔧 **Flexible Configuration** - Rich crawling parameter options
- 🖼️ **Screenshot Support** - Capture page screenshots during crawling
- 🔗 **Link Extraction** - Extract and organize internal/external links

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Bootstrap 5 + JavaScript
- **Crawling Engine**: Crawl4AI + Playwright
- **Real-time Communication**: WebSocket
- **Data Validation**: Pydantic

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/crawl4ai-web.git
cd crawl4ai-web
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**
```bash
playwright install chromium
playwright install-deps  # Required on Linux
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env file as needed
```

6. **Start the application**
```bash
python run.py
```

7. **Access the application**
Open your browser and visit: http://localhost:8080

## 📖 Usage Guide

### Basic Crawling

1. Enter the target URL in the input field
2. Select extraction strategy (recommend "Default" for most cases)
3. Adjust configuration parameters (optional)
4. Click "Start Crawling"
5. Monitor real-time progress and view results

### Advanced Configuration

- **Word Count Threshold**: Filter content blocks with fewer words than specified
- **CSS Selector**: Use CSS selectors for targeted content extraction
- **Screenshot**: Capture page screenshots
- **Link Extraction**: Extract all links from the page

### API Usage

The application provides a comprehensive RESTful API for programmatic access:

#### Quick Start
```bash
# Simple synchronous crawl
curl -X POST "http://localhost:8080/api/v1/crawl/quick" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "config": {"extraction_strategy": "default"}}'

# Asynchronous crawl with task tracking
curl -X POST "http://localhost:8080/api/v1/crawl/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "config": {"extraction_strategy": "default"}}'
```

#### Key API Endpoints
- `POST /api/v1/crawl/` - Create crawling task
- `POST /api/v1/crawl/quick` - Synchronous crawl with timeout
- `POST /api/v1/crawl/batch` - Batch crawl multiple URLs
- `GET /api/v1/crawl/{task_id}` - Get task status and results
- `GET /api/v1/crawl/{task_id}/download` - Download results as file
- `GET /api/v1/crawl/stats` - Get crawling statistics
- `POST /api/v1/auth/generate-key` - Generate API key
- `GET /api/v1/health/` - Health check

#### Documentation
- **Interactive API Docs**: http://localhost:8080/docs
- **API Guide**: [docs/API.md](docs/API.md)
- **Quick Start**: [docs/QUICK_START_API.md](docs/QUICK_START_API.md)
- **Examples**: [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)
- **Postman Collection**: [docs/Crawl4AI_API.postman_collection.json](docs/Crawl4AI_API.postman_collection.json)

## 📁 Project Structure

```
crawl4ai-web/
├── app/                    # Main application directory
│   ├── api/               # API routes
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Image assets
├── templates/             # HTML templates
├── requirements.txt       # Python dependencies
├── run.py                # Application entry point
└── README.md             # Project documentation
```

## 🔧 Development

### Local Development

1. Install development dependencies
```bash
pip install -r requirements.txt
```

2. Start development server with auto-reload
```bash
python run.py --reload
```

### Code Standards

- Use Black for code formatting
- Use Flake8 for linting
- Follow PEP 8 coding standards
- Write comprehensive docstrings

## 🚢 Deployment

### Docker Deployment

```bash
# Build image
docker build -t crawl4ai-web .

# Run container
docker run -p 8080:8080 crawl4ai-web
```

### Production Deployment

For production, use Gunicorn + Nginx:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

## ❓ FAQ

### Q: What if crawling fails?
A: Check if the target website is accessible, verify network connectivity. Some websites may have anti-crawling mechanisms.

### Q: How to improve crawling speed?
A: You can adjust concurrency settings, but be mindful not to overwhelm target websites.

### Q: Which websites are supported?
A: Theoretically supports all publicly accessible websites, though some with strict anti-crawling measures may be challenging.

### Q: Can I use custom extraction strategies?
A: Yes, the application supports multiple extraction strategies including custom CSS selectors and LLM-based extraction.

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Update documentation as needed
- Follow the existing code style
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - The powerful crawling engine that powers this application
- [FastAPI](https://fastapi.tiangolo.com/) - The modern web framework for building APIs
- [Playwright](https://playwright.dev/) - Browser automation library
- [Bootstrap](https://getbootstrap.com/) - Frontend framework

## 📞 Support

If you encounter any issues or have questions:

- 📝 [Create an Issue](https://github.com/your-username/crawl4ai-web/issues)
- 💬 [Start a Discussion](https://github.com/your-username/crawl4ai-web/discussions)
- 📧 Contact the maintainers

---

**Star ⭐ this repository if you find it helpful!**
