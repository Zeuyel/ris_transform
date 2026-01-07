# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RIS文件处理器 (RIS File Processor) is a PyQt5-based desktop application for processing and classifying academic literature RIS files. It supports multiple journal classification standards (CCF, FMS, AJG, ZUFE) and includes automatic translation capabilities for titles and abstracts.

## Development Commands

### Running the Application
```bash
python app.py
```

### Building Executable
```bash
# Recommended: Use the build script
python build.py

# Alternative: Direct PyInstaller command
pyinstaller --clean --name "RIS文件处理器" --icon "resources/filter.ico" --add-data "data/*;data" --add-data "resources/*;resources" --noconsole app.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Core Architecture

### Data Flow
1. **Input**: RIS files (UTF-8 encoded) containing academic paper metadata
2. **Processing Pipeline**:
   - `core/paper_processor.py`: Parses RIS format, applies classification criteria, handles deduplication
   - `core/data_manager.py`: Manages rating data loading/caching and configuration persistence
   - `utils/translator.py`: Provides translation services for titles/abstracts via external APIs
3. **Output**: Filtered RIS files organized by journal classification criteria

### Key Components

- **GUI Layer** (`gui/main_window.py`): PyQt5-based interface with drag-and-drop support, progress tracking, and configuration management
- **Core Processing** (`core/`):
  - `paper_processor.py`: RIS parsing, journal rating lookup, classification logic
  - `data_manager.py`: Centralized data access, configuration management, caching
  - `data_types.py`: Type definitions (RatingSystem enum, JournalRating, DataConfig dataclasses)
- **Data Files** (`data/`):
  - `ratings/`: Journal rating data (JSON format)
  - `criteria/`: Pre-defined classification criteria
  - `profiles/`: Institution-specific configurations
  - `config.json`: User preferences and API tokens

### Rating System Integration

The application uses a flexible rating system defined in `core/data_types.py`:
- Each rating system (CCF, FMS, AJG, ZUFE) maps journals to classification levels
- JSON files in `data/ratings/` contain journal-level pairs
- Classification criteria in `selection_criteria` dict combine multiple rating systems

### Adding New Classification Standards

1. Add rating data JSON to `data/ratings/`
2. Update `data/config.json`:
   - Add to `rating_systems` with display name and field mappings
   - Add file path to `rating_file_paths`
   - Add attribute mapping to `json_attribute_mapping`
3. Define selection criteria in `core/paper_processor.py` `selection_criteria` dict

## Important Implementation Details

- **Encoding**: All files must use UTF-8 encoding
- **Deduplication**: Papers are deduplicated by title (case-insensitive)
- **Translation**: Requires network connection and valid API tokens in config
- **Resource Bundling**: When building executables, `build.py` automatically collects all data files and resources
- **Configuration Persistence**: User settings (output directory, translation options) are saved to `config.json`