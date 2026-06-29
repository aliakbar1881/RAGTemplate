# RAGTemplate

> A simple yet extensible RAG (Retrieval-Augmented Generation) template for building advanced AI-powered systems.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview

**RAGTemplate** is a modular starter kit for developing Retrieval-Augmented Generation applications. It provides a clean, component-based architecture that separates concerns across data handling, retrieval, generation, and presentation layers. Whether you're building a document Q&A bot, a research assistant, or a custom knowledge-retrieval system, this template gives you a solid foundation to build upon.

## ✨ Core Features

- **🔍 Retrieval Module**: Pluggable retriever components for fetching relevant context from your data sources.
- **🧠 Generation Module**: Integrates with LLMs to produce accurate, context-aware responses.
- **📂 Data Layer**: Dedicated module for data ingestion, preprocessing, and management.
- **🌐 Web Interface**: Built-in view layer with HTML, CSS, and JavaScript for quick prototyping and demos.
- **⚙️ Service Layer**: API-ready service components for exposing RAG functionality.
- **🧩 Extensible Core**: Base classes (`rag_base.py`, `generator_base.py`, `retriever_base.py`) make it easy to swap or customize components.

## 📁 Project Structure
```
RAGTemplate/
├── src/
│ ├── core/ # Base classes and abstractions
│ │ ├── generator_base.py # Base generator interface
│ │ ├── rag_base.py # Base RAG pipeline interface
│ │ └── retriver_base.py # Base retriever interface
│ ├── data/ # Data ingestion and preprocessing
│ ├── model/ # Model definitions and configurations
│ ├── rag/ # RAG pipeline implementation
│ │ ├── generator.py # Generator implementation
│ │ ├── rag.py # Main RAG orchestration
│ │ └── retriever.py # Retriever implementation
│ ├── service/ # API / service layer
│ ├── utils/ # Utility functions and helpers
│ ├── view/ # Web interface (HTML, CSS, JS)
│ └── main.py # Application entry point
├── .gitignore
├── README.md
├── TODO.md
└── environment.yaml # Conda environment specification
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or `pip`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aliakbar1881/RAGTemplate.git
   cd RAGTemplate
```
Set up the environment using Conda:
```bash

conda env create -f environment.yaml
conda activate rag-template
```
        If you prefer pip, create a virtual environment and install dependencies manually from environment.yaml or requirements.txt (if available).

Running the Application

Start the application:
```bash

python src/main.py
```
The web interface should be available at http://localhost:5000 (or the port specified in your configuration).
