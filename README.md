# Line Counter GUI - Code Analysis Tool

A simple GUI application for counting lines of code in projects with folder selection, file exclusion capabilities, and export functionality.

## Features

- **Folder Selection**: Browse and select any folder to analyze
- **File Type Filtering**: Include only specific file extensions (e.g., .py, .js, .html)
- **File Exclusion**: Exclude files by patterns (e.g., *.pyc, *.exe)
- **Folder Exclusion**: Exclude entire folders (e.g., .git, node_modules, __pycache__)
- **Line Counting Options**: Choose between counting all lines, non-empty lines, or code lines only
- **Detailed Results**: View results grouped by file extension with individual file details
- **Progress Indication**: Progress bar shows when analysis is running
- **Summary Statistics**: Total files, lines of code, and file sizes
- **Export Functionality**: Export results as CSV or JSON with preview and save/copy options

## How to Use

1. **Run the Application**:
   ```bash
   python line_counter_gui.py
   ```

2. **Select a Folder**:
   - Click the "Browse" button to select the folder you want to analyze

3. **Configure Filters** (optional):
   - **Include Extensions**: Specify which file types to include (default includes common programming languages)
     - Use specific extensions: `.py,.js,.html`
     - Use `.**` to include all extensions except excluded ones
     - Use `.*` to include everything (ignores exclude patterns)
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

6. **Export Results** (NEW):
   - After analysis completes, "Export as CSV" and "Export as JSON" buttons appear
   - Click either button to see a preview of the export data
   - In the preview window, you can:
     - **Copy to Clipboard**: Copy the formatted data to your clipboard
     - **Save to File**: Save the data to a file on your computer
     - **Close**: Close the preview without saving

## Export Formats

### CSV Export
- Includes all individual files with their paths, extensions, line counts, and file sizes
- Contains summary statistics (total files, lines, size)
- Provides breakdown by file extension
- Compatible with Excel and other spreadsheet applications

### JSON Export
- Structured data format perfect for programmatic processing
- Contains analysis summary with metadata
- Individual file details in organized arrays
- Extension summary statistics
- Includes analysis settings (count method, analyzed folder)

## Default Settings

- **Included Extensions**: `.py,.js,.html,.css,.java,.cpp,.c,.h,.cs,.php,.rb,.go,.rs,.ts,.jsx,.tsx,.vue,.swift,.kt,.scala,.r,.m,.mm,.sh,.bat,.ps1,.sql`
- **Excluded Patterns**: `*.pyc,*.exe,*.dll,*.so,*.o,*.obj`
- **Excluded Folders**: `.git,.svn,__pycache__,node_modules,.vscode`

## Special Extension Patterns

The tool supports special patterns for more flexible file inclusion:

### `.**` - All Extensions Except Excluded
- **Use case**: Analyze all code files in a project while excluding common non-source files
- **Example**: Set Include Extensions to `.**` and Exclude Patterns to `*.pyc,*.exe,*.dll,*.log,*.tmp`
- **Result**: Includes all file types (.py, .js, .html, .md, etc.) but excludes compiled/temporary files

### `.*` - Everything Including Excluded
- **Use case**: Complete project analysis including all files (documentation, configs, etc.)
- **Example**: Set Include Extensions to `.*`
- **Result**: Includes ALL files regardless of exclude patterns - useful for comprehensive project analysis

### Combining Patterns
- You can combine special patterns with specific extensions: `.*,.py,.js` (though `.* ` alone would include everything)
- Multiple special patterns: `.**, .py` means "all extensions except excluded ones, plus specifically .py files"

## Requirements

- Python 3.x (tkinter is included with most Python installations)
- No additional packages required - uses only Python standard library

## Notes

- **Line Counting Methods**:
  - **All lines**: Counts every line in the file including empty ones (gives you the total line count you see in editors)
  - **Non-empty lines**: Counts only lines with content (excludes blank lines and whitespace-only lines)
  - **Code lines only**: Attempts to exclude comments and blank lines (basic heuristic based on file extension)
- **Export Features**:
  - Preview shows formatted data before saving
  - Copy to clipboard for quick sharing or pasting into other applications
  - Save to file with automatic file extension and proper encoding
  - All export data is sorted by line count (highest first) for easy analysis
- **Window Behavior**:
  - Fullscreen mode is disabled to maintain consistent user experience
  - Window can be resized normally but cannot enter fullscreen
  - Maximum window size is limited to 95% of screen width and 90% of screen height
- Handles encoding issues gracefully (tries UTF-8 first, then Latin-1)
- Results are organized hierarchically by file extension for easy analysis
- Thread-safe operation prevents UI freezing during large directory scans 