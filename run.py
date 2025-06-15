#!/usr/bin/env python3
"""
Crawl4AI Web Application Startup Script
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import settings


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Crawl4AI Web Application")
    
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to bind to (default: {settings.port})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.reload,
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=settings.debug,
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--log-level",
        default=settings.log_level.lower(),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help=f"Log level (default: {settings.log_level.lower()})"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Print startup information
    print("=" * 60)
    print(f"🚀 Starting {settings.app_name}")
    print(f"📝 Version: {settings.app_version}")
    print(f"🌐 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Reload: {args.reload}")
    print(f"🐛 Debug: {args.debug}")
    print(f"📊 Log Level: {args.log_level.upper()}")
    print("=" * 60)
    print()
    print(f"📱 Web Interface: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🎮 API Playground: http://{args.host}:{args.port}/playground")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Check if required directories exist
    static_dir = current_dir / "static"
    templates_dir = current_dir / "templates"
    
    if not static_dir.exists():
        print(f"⚠️  Warning: Static directory not found: {static_dir}")
    
    if not templates_dir.exists():
        print(f"⚠️  Warning: Templates directory not found: {templates_dir}")
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if not args.reload else 1,
            access_log=True,
            use_colors=True,
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
