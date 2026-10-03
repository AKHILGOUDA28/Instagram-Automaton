@echo off
echo Starting Current Affairs Agent...
cd "C:\Users\akhil\OneDrive\Desktop\Current Affairs Insta"

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Run the ingestion to update ChromaDB facts
echo Updating RAG Knowledge Base...
python src\rag\ingest.py

:: Run the main posting pipeline
echo Generating and Publishing...
python src\main.py

echo Done!
