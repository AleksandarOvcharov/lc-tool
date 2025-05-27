LineCounter - Code Analysis Tool
================================

This is a standalone executable for counting lines of code in projects.

WHAT IT DOES:
- Counts lines of code in selected folders
- Allows filtering by file types and exclusion patterns
- Provides three counting methods:
  * All lines (including empty lines)
  * Non-empty lines only
  * Code lines only (excludes comments)
- Shows results organized by file extension
- Displays file sizes and totals

HOW TO USE:
1. Double-click LineCounter.exe to run
2. Click "Browse" to select a folder to analyze
3. Optionally adjust the filters:
   - Include Extensions: file types to include (e.g., .py,.js,.html)
   - Exclude Patterns: files to skip (e.g., *.exe,*.dll)
   - Exclude Folders: folders to skip (e.g., .git,node_modules)
   - Count Method: how to count lines
4. Click "Count Lines" to start analysis
5. View results in the tree below

SYSTEM REQUIREMENTS:
- Windows 10/11
- No additional software required (Python not needed)

FILE SIZE: ~11MB
This executable contains everything needed to run the application.

For technical support or source code, visit:
https://github.com/[your-repo] (if applicable)

Developed with Python and tkinter
Packaged with PyInstaller 