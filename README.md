# Line Counter GUI - Code Analysis Tool

A simple GUI application for counting lines of code in projects with folder selection and file exclusion capabilities.

## Features

- **Folder Selection**: Browse and select any folder to analyze
- **File Type Filtering**: Include only specific file extensions (e.g., .py, .js, .html)
- **File Exclusion**: Exclude files by patterns (e.g., *.pyc, *.exe)
- **Folder Exclusion**: Exclude entire folders (e.g., .git, node_modules, __pycache__)
- **Line Counting Options**: Choose between counting all lines, non-empty lines, or code lines only
- **Detailed Results**: View results grouped by file extension with individual file details
- **Progress Indication**: Progress bar shows when analysis is running
- **Summary Statistics**: Total files, lines of code, and file sizes

## How to Use

1. **Run the Application**:
   ```bash
   python line_counter_gui.py
   ```

2. **Select a Folder**:
   - Click the "Browse" button to select the folder you want to analyze

3. **Configure Filters** (optional):
   - **Include Extensions**: Specify which file types to include (default includes common programming languages)
   - **Exclude File Patterns**: Specify patterns for files to exclude (default excludes compiled files)
   - **Exclude Folders**: Specify folder names to exclude (default excludes common non-source folders)
   - **Count Method**: Choose how to count lines:
     - **All lines**: Count every line including empty lines (total line count)
     - **Non-empty lines**: Count only lines with content (excludes blank lines)
     - **Code lines only**: Count only code lines (excludes blank lines and comments)

4. **Run Analysis**:
   - Click "Count Lines" to start the analysis
   - The progress bar will show while the analysis is running
   - Results will appear in the tree view below

5. **View Results**:
   - Summary shows total files, lines, and size
   - Results are grouped by file extension
   - Expand each extension group to see individual files
   - Files are sorted by line count (highest first)

## Default Settings

- **Included Extensions**: `.py,.js,.html,.css,.java,.cpp,.c,.h,.cs,.php,.rb,.go,.rs,.ts,.jsx,.tsx,.vue,.swift,.kt,.scala,.r,.m,.mm,.sh,.bat,.ps1,.sql`
- **Excluded Patterns**: `*.pyc,*.exe,*.dll,*.so,*.o,*.obj`
- **Excluded Folders**: `.git,.svn,__pycache__,node_modules,.vscode`

## Requirements

- Python 3.x (tkinter is included with most Python installations)
- No additional packages required - uses only Python standard library

## Notes

- **Line Counting Methods**:
  - **All lines**: Counts every line in the file including empty ones (gives you the total line count you see in editors)
  - **Non-empty lines**: Counts only lines with content (excludes blank lines and whitespace-only lines)
  - **Code lines only**: Attempts to exclude comments and blank lines (basic heuristic based on file extension)
- Handles encoding issues gracefully (tries UTF-8 first, then Latin-1)
- Results are organized hierarchically by file extension for easy analysis
- Thread-safe operation prevents UI freezing during large directory scans 