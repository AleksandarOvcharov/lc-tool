import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import fnmatch
from pathlib import Path
import threading
import json
import csv
import io

class LineCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Counter - Code Analysis Tool")
        self.root.geometry("800x700")
        root.resizable(False, False)
        
        # Disable fullscreen mode with more robust approach
        self.setup_fullscreen_prevention()
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.exclude_patterns = tk.StringVar(value="*.pyc,*.exe,*.dll,*.so,*.o,*.obj, *.md, *.txt")
        self.exclude_folders = tk.StringVar(value=".git,.svn,__pycache__,node_modules,.vscode")
        self.include_extensions = tk.StringVar(value=".py,.js,.html,.css,.java,.cpp,.c,.h,.cs,.php,.rb,.go,.rs,.ts,.jsx,.tsx,.vue,.swift,.kt,.scala,.r,.m,.mm,.sh,.bat,.ps1,.sql")
        self.line_count_method = tk.StringVar(value="all")
        
        # Results storage
        self.results = {}
        self.total_lines = 0
        self.total_files = 0
        
        # Storage for export functionality
        self.file_results = []
        self.extension_stats = {}
        
        self.setup_ui()
        
        # Ensure fullscreen is disabled after UI setup
        self.disable_fullscreen()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Folder selection
        ttk.Label(main_frame, text="Select Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(folder_frame, textvariable=self.selected_folder, state="readonly").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        
        # Include extensions
        ttk.Label(main_frame, text="Include Extensions:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.include_extensions).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, text="(comma-separated, e.g., .py,.js,.html | .** = all except excluded | .* = everything)", font=("Arial", 8)).grid(row=2, column=1, columnspan=2, sticky=tk.W)
        
        # Exclude patterns
        ttk.Label(main_frame, text="Exclude File Patterns:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.exclude_patterns).grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, text="(comma-separated patterns, e.g., *.pyc,*.exe)", font=("Arial", 8)).grid(row=4, column=1, columnspan=2, sticky=tk.W)
        
        # Exclude folders
        ttk.Label(main_frame, text="Exclude Folders:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.exclude_folders).grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Line counting method
        ttk.Label(main_frame, text="Count Method:").grid(row=6, column=0, sticky=tk.W, pady=5)
        count_frame = ttk.Frame(main_frame)
        count_frame.grid(row=6, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(count_frame, text="All lines", variable=self.line_count_method, value="all").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(count_frame, text="Non-empty lines", variable=self.line_count_method, value="non_empty").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(count_frame, text="Code lines only", variable=self.line_count_method, value="code_only").pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        self.count_button = ttk.Button(button_frame, text="Count Lines", command=self.start_counting)
        self.count_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=(0, 10))
        
        # Export buttons (initially hidden)
        self.export_csv_button = ttk.Button(button_frame, text="Export as CSV", command=self.export_csv)
        self.export_json_button = ttk.Button(button_frame, text="Export as JSON", command=self.export_json)
        
        # Initially hide export buttons
        self.show_export_buttons(False)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Summary
        self.summary_label = ttk.Label(results_frame, text="No analysis performed yet", font=("Arial", 10, "bold"))
        self.summary_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Results tree
        tree_frame = ttk.Frame(results_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=("Lines", "Size"), show="tree headings")
        self.tree.heading("#0", text="File/Extension")
        self.tree.heading("Lines", text="Lines of Code")
        self.tree.heading("Size", text="File Size")
        
        self.tree.column("#0", width=400)
        self.tree.column("Lines", width=100)
        self.tree.column("Size", width=100)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select folder to analyze")
        if folder:
            self.selected_folder.set(folder)
            
    def start_counting(self):
        if not self.selected_folder.get():
            messagebox.showerror("Error", "Please select a folder first!")
            return
            
        if not os.path.exists(self.selected_folder.get()):
            messagebox.showerror("Error", "Selected folder does not exist!")
            return
            
        # Disable button and start progress
        self.count_button.config(state="disabled")
        self.progress.start()
        
        # Run counting in separate thread
        thread = threading.Thread(target=self.count_lines)
        thread.daemon = True
        thread.start()
        
    def count_lines(self):
        try:
            folder_path = Path(self.selected_folder.get())
            
            # Parse patterns
            include_exts = [ext.strip() for ext in self.include_extensions.get().split(",") if ext.strip()]
            exclude_patterns = [pattern.strip() for pattern in self.exclude_patterns.get().split(",") if pattern.strip()]
            exclude_folders = [folder.strip() for folder in self.exclude_folders.get().split(",") if folder.strip()]
            
            # Check for special extension patterns
            include_all_except_excluded = ".**" in include_exts
            include_everything = ".*" in include_exts
            
            # Remove special patterns from the list for normal processing
            if include_all_except_excluded:
                include_exts = [ext for ext in include_exts if ext != ".**"]
            if include_everything:
                include_exts = [ext for ext in include_exts if ext != ".*"]
            
            # Results storage
            file_results = []
            extension_stats = {}
            
            # Walk through directory
            for root, dirs, files in os.walk(folder_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_folders)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if file should be excluded by pattern (unless .* is used)
                    if not include_everything and any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                        continue
                        
                    # Check if file extension is included
                    file_ext = file_path.suffix.lower()
                    
                    # Determine if file should be included based on extension rules
                    should_include = False
                    
                    if include_everything:
                        # .* pattern: include everything
                        should_include = True
                    elif include_all_except_excluded:
                        # .** pattern: include all extensions except those matching exclude patterns
                        should_include = True  # Already filtered by exclude patterns above
                    elif include_exts:
                        # Normal extension filtering: include only specified extensions
                        should_include = any(file_ext == ext for ext in include_exts)
                    else:
                        # No extensions specified: include everything (backward compatibility)
                        should_include = True
                    
                    if not should_include:
                        continue
                        
                    # Count lines
                    try:
                        lines = self.count_file_lines(file_path, self.line_count_method.get())
                        file_size = file_path.stat().st_size
                        rel_path = file_path.relative_to(folder_path)
                        
                        # Always add file to results, even if binary or 0 lines
                        file_results.append({
                            'path': str(rel_path),
                            'lines': lines,
                            'size': file_size,
                            'extension': file_ext
                        })
                        
                        # Update extension stats
                        if file_ext not in extension_stats:
                            extension_stats[file_ext] = {'files': 0, 'lines': 0, 'size': 0}
                        extension_stats[file_ext]['files'] += 1
                        
                        # Only add to line and size count if not binary
                        if lines != "binary" and lines > 0:
                            extension_stats[file_ext]['lines'] += lines
                        extension_stats[file_ext]['size'] += file_size
                            
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
            
            # Update UI in main thread
            self.root.after(0, self.update_results, file_results, extension_stats)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, self.counting_finished)
            
    def is_binary_file(self, file_path):
        """Check if a file is binary by examining the first 8192 bytes"""
        try:
            # First check if the file extension is known to be text
            file_ext = Path(file_path).suffix.lower()
            
            # Known text file extensions - these should never be considered binary
            text_extensions = {
                '.txt', '.md', '.rst', '.log', '.ini', '.cfg', '.conf', '.config',
                '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.html', '.htm', '.xhtml',
                '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml',
                '.java', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs', '.php',
                '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.mm',
                '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1', '.sql',
                '.pl', '.pm', '.lua', '.tcl', '.vb', '.vbs', '.asm', '.s',
                '.dockerfile', '.makefile', '.cmake', '.gradle', '.maven',
                '.gitignore', '.gitattributes', '.htaccess', '.env',
                '.vue', '.svelte', '.elm', '.dart', '.groovy', '.clj', '.cljs',
                '.lisp', '.scm', '.rkt', '.hs', '.fs', '.fsx', '.ml', '.mli',
                '.tex', '.bib', '.sty', '.cls', '.dtx', '.ins'
            }
            
            # If it's a known text extension, don't consider it binary
            if file_ext in text_extensions:
                return False
                
            # For files without extension or unknown extensions, check content
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                
            # Empty files are not binary
            if len(chunk) == 0:
                return False
                
            # Check for null bytes which strongly indicate binary files
            if b'\x00' in chunk:
                return True
                
            # Expanded definition of text characters including more Unicode ranges
            # ASCII printable (32-126) + common control chars (9=tab, 10=LF, 13=CR) + extended ASCII (128-255)
            text_chars = sum(1 for byte in chunk if 
                           (32 <= byte <= 126) or  # ASCII printable
                           byte in (9, 10, 13) or  # Tab, LF, CR
                           (128 <= byte <= 255))   # Extended ASCII/UTF-8 continuation bytes
            
            # Much more lenient threshold - only consider binary if less than 50% are text-like
            if len(chunk) > 0 and text_chars / len(chunk) < 0.50:
                return True
                
            return False
        except:
            # If we can't read the file, assume it's binary to be safe
            return True

    def count_file_lines(self, file_path, method):
        """Count lines in a file based on the selected method"""
        # First check if file is binary
        if self.is_binary_file(file_path):
            return "binary"
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                    lines = f.readlines()
            except:
                return 0
        
        if method == "all":
            # Count all lines including empty ones
            return len(lines)
        elif method == "non_empty":
            # Count only non-empty lines (original behavior)
            return sum(1 for line in lines if line.strip())
        elif method == "code_only":
            # Count lines that are not empty and not comments (basic heuristic)
            count = 0
            for line in lines:
                stripped = line.strip()
                if stripped and not self.is_comment_line(stripped, file_path.suffix):
                    count += 1
            return count
        else:
            return len(lines)  # Default to all lines
    
    def is_comment_line(self, line, file_extension):
        """Basic heuristic to detect comment lines based on file extension"""
        ext = file_extension.lower()
        
        # Python, Shell, R, etc.
        if ext in ['.py', '.sh', '.r', '.rb', '.pl', '.ps1']:
            return line.startswith('#')
        
        # JavaScript, TypeScript, Java, C/C++, C#, etc.
        elif ext in ['.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.go', '.rs', '.swift', '.kt', '.scala']:
            return line.startswith('//') or line.startswith('/*') or line.startswith('*')
        
        # HTML, XML
        elif ext in ['.html', '.htm', '.xml', '.vue']:
            return line.startswith('<!--') or line.startswith('*')
        
        # CSS
        elif ext in ['.css']:
            return line.startswith('/*') or line.startswith('*')
        
        # SQL
        elif ext in ['.sql']:
            return line.startswith('--') or line.startswith('/*')
        
        # Default: no comment detection
        return False
                
    def update_results(self, file_results, extension_stats):
        # Store results for export functionality
        self.file_results = file_results
        self.extension_stats = extension_stats
        
        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        
        # Calculate totals (excluding binary files from line count)
        self.total_files = len(file_results)
        self.total_lines = sum(result['lines'] for result in file_results if result['lines'] != "binary" and isinstance(result['lines'], int))
        total_size = sum(result['size'] for result in file_results)
        
        # Update summary
        size_mb = total_size / (1024 * 1024)
        self.summary_label.config(text=f"Total: {self.total_files} files, {self.total_lines:,} lines of code, {size_mb:.2f} MB")
        
        # Show export buttons when results are available
        self.show_export_buttons(True)
        
        # Add extension summaries
        for ext, stats in sorted(extension_stats.items(), key=lambda x: x[1]['lines'], reverse=True):
            ext_name = ext if ext else "(no extension)"
            size_kb = stats['size'] / 1024
            parent = self.tree.insert("", "end", text=f"{ext_name} files ({stats['files']} files)", 
                                    values=(f"{stats['lines']:,}", f"{size_kb:.1f} KB"))
            
            # Add individual files for this extension
            ext_files = [f for f in file_results if f['extension'] == ext]
            # Sort with binary files at the end
            ext_files.sort(key=lambda x: (-1, x['path']) if x['lines'] == "binary" else (x['lines'], x['path']), reverse=True)
            
            for file_info in ext_files:
                size_kb = file_info['size'] / 1024
                # Handle binary files display
                if file_info['lines'] == "binary":
                    lines_display = "binary"
                else:
                    lines_display = f"{file_info['lines']:,}"
                    
                self.tree.insert(parent, "end", text=file_info['path'], 
                               values=(lines_display, f"{size_kb:.1f} KB"))
        
    def counting_finished(self):
        self.progress.stop()
        self.count_button.config(state="normal")
        
    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.summary_label.config(text="No analysis performed yet")
        self.results = {}
        self.total_lines = 0
        self.total_files = 0
        
        # Clear export data and hide export buttons
        self.file_results = []
        self.extension_stats = {}
        self.show_export_buttons(False)

    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def show_export_buttons(self, show):
        """Show or hide export buttons based on whether results are available"""
        if show:
            self.export_csv_button.pack(side=tk.LEFT, padx=(0, 10))
            self.export_json_button.pack(side=tk.LEFT, padx=(0, 10))
        else:
            self.export_csv_button.pack_forget()
            self.export_json_button.pack_forget()

    def export_csv(self):
        """Export results as CSV with preview and save/copy options"""
        if not self.file_results:
            messagebox.showwarning("Warning", "No results to export!")
            return
            
        # Generate CSV data
        csv_data = self.generate_csv_data()
        
        # Show preview dialog
        self.show_export_preview("CSV Export", csv_data, "csv")

    def export_json(self):
        """Export results as JSON with preview and save/copy options"""
        if not self.file_results:
            messagebox.showwarning("Warning", "No results to export!")
            return
            
        # Generate JSON data
        json_data = self.generate_json_data()
        
        # Show preview dialog
        self.show_export_preview("JSON Export", json_data, "json")

    def generate_csv_data(self):
        """Generate CSV formatted data from results"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['File Path', 'Extension', 'Lines of Code', 'File Size (bytes)', 'File Size (KB)'])
        
        # Write data for each file (sort with binary files at the end)
        def sort_key(x):
            if x['lines'] == "binary":
                return (-1, x['path'])  # Binary files at end
            return (x['lines'], x['path'])
        
        for file_info in sorted(self.file_results, key=sort_key, reverse=True):
            size_kb = file_info['size'] / 1024
            writer.writerow([
                file_info['path'],
                file_info['extension'] or '(no extension)',
                file_info['lines'],
                file_info['size'],
                f"{size_kb:.2f}"
            ])
        
        # Add summary section
        writer.writerow([])  # Empty row
        writer.writerow(['=== SUMMARY ==='])
        writer.writerow(['Total Files', '', self.total_files, '', ''])
        writer.writerow(['Total Lines', '', self.total_lines, '', ''])
        writer.writerow(['Total Size (MB)', '', '', '', f"{sum(f['size'] for f in self.file_results) / (1024*1024):.2f}"])
        
        # Add extension summary
        writer.writerow([])
        writer.writerow(['=== BY EXTENSION ==='])
        writer.writerow(['Extension', 'Files', 'Lines', 'Size (KB)', ''])
        
        for ext, stats in sorted(self.extension_stats.items(), key=lambda x: x[1]['lines'], reverse=True):
            ext_name = ext if ext else '(no extension)'
            size_kb = stats['size'] / 1024
            writer.writerow([ext_name, stats['files'], stats['lines'], f"{size_kb:.2f}", ''])
        
        return output.getvalue()

    def generate_json_data(self):
        """Generate JSON formatted data from results"""
        export_data = {
            'analysis_summary': {
                'total_files': self.total_files,
                'total_lines': self.total_lines,
                'total_size_bytes': sum(f['size'] for f in self.file_results),
                'analyzed_folder': self.selected_folder.get(),
                'count_method': self.line_count_method.get()
            },
            'files': [
                {
                    'path': file_info['path'],
                    'extension': file_info['extension'] or None,
                    'lines_of_code': file_info['lines'],
                    'file_size_bytes': file_info['size'],
                    'file_size_kb': round(file_info['size'] / 1024, 2)
                }
                for file_info in sorted(self.file_results, key=lambda x: (-1, x['path']) if x['lines'] == "binary" else (x['lines'], x['path']), reverse=True)
            ],
            'extension_summary': [
                {
                    'extension': ext if ext else None,
                    'file_count': stats['files'],
                    'total_lines': stats['lines'],
                    'total_size_bytes': stats['size'],
                    'total_size_kb': round(stats['size'] / 1024, 2)
                }
                for ext, stats in sorted(self.extension_stats.items(), key=lambda x: x[1]['lines'], reverse=True)
            ]
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def show_export_preview(self, title, data, file_type):
        """Show preview dialog with export data and save/copy options"""
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(title)
        preview_window.geometry("800x600")
        preview_window.resizable(True, True)
        
        # Configure grid weights
        preview_window.columnconfigure(0, weight=1)
        preview_window.rowconfigure(1, weight=1)
        
        # Title and info
        info_frame = ttk.Frame(preview_window, padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text=f"{title} Preview", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        ttk.Label(info_frame, text=f"Files: {self.total_files}, Lines: {self.total_lines:,}").grid(row=1, column=0, sticky=tk.W)
        
        # Text area with scrollbars
        text_frame = ttk.Frame(preview_window, padding="10")
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbars
        text_widget = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 9))
        v_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Insert data
        text_widget.insert(tk.END, data)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Buttons
        button_frame = ttk.Frame(preview_window, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        def copy_to_clipboard():
            preview_window.clipboard_clear()
            preview_window.clipboard_append(data)
            messagebox.showinfo("Success", "Data copied to clipboard!")
        
        def save_to_file():
            try:
                file_extension = "csv" if file_type == "csv" else "json"
                default_filename = f"line_count_results.{file_extension}"
                filetypes = [
                    (f"{file_type.upper()} files", f"*.{file_extension}"),
                    ("All files", "*.*")
                ]
                
                filename = filedialog.asksaveasfilename(
                    title=f"Save {file_type.upper()} file",
                    defaultextension=f".{file_extension}",
                    filetypes=filetypes,
                    initialfile=default_filename
                )
                
                if filename:
                    # Ensure the file has the correct extension
                    if not filename.lower().endswith(f'.{file_extension}'):
                        filename += f'.{file_extension}'
                    
                    # Use different newline settings for CSV vs JSON
                    newline_setting = '' if file_type == "csv" else None
                    
                    try:
                        with open(filename, 'w', encoding='utf-8', newline=newline_setting) as f:
                            f.write(data)
                        
                        # Verify the file was actually written
                        if os.path.exists(filename) and os.path.getsize(filename) > 0:
                            messagebox.showinfo("Success", f"Data saved successfully!\n\nFile: {filename}\nSize: {os.path.getsize(filename)} bytes")
                            preview_window.destroy()
                        else:
                            messagebox.showerror("Error", "File was created but appears to be empty or inaccessible.")
                            
                    except PermissionError:
                        messagebox.showerror("Permission Error", f"Cannot write to the selected location.\nPlease choose a different location or run as administrator.\n\nFile: {filename}")
                    except OSError as e:
                        messagebox.showerror("File System Error", f"Cannot write to file:\n{str(e)}\n\nPlease try a different location or filename.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save file:\n{str(e)}\n\nFile: {filename}")
                else:
                    # User cancelled the dialog - this is normal, no error message needed
                    pass
                    
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while trying to save:\n{str(e)}")
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save to File", command=save_to_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=preview_window.destroy).pack(side=tk.RIGHT)

    def disable_fullscreen(self):
        """Comprehensive fullscreen prevention system"""
        try:
            # Force fullscreen to be disabled
            self.root.attributes('-fullscreen', False)
            
            # Bind all possible fullscreen key combinations
            fullscreen_keys = [
                '<F11>', '<Control-F11>', '<Shift-F11>', '<Alt-F11>',
                '<Alt-Return>', '<Alt-Enter>', '<Control-Alt-Return>',
                '<Super-F11>', '<Meta-F11>'
            ]
            
            for key in fullscreen_keys:
                try:
                    self.root.bind(key, lambda e: self.force_windowed_mode())
                except tk.TclError:
                    pass  # Some key combinations might not be supported
            
            # Monitor window state changes
            self.root.bind('<Configure>', self.check_fullscreen_state)
            self.root.bind('<FocusIn>', self.check_fullscreen_state)
            self.root.bind('<Map>', self.check_fullscreen_state)
            
            # Start periodic fullscreen checking
            self.monitor_fullscreen()
            
        except tk.TclError:
            # Some window managers might not support these attributes
            pass
    
    def force_windowed_mode(self):
        """Force the window back to windowed mode"""
        try:
            self.root.attributes('-fullscreen', False)
            # Ensure window is visible and properly sized
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except tk.TclError:
            pass
    
    def check_fullscreen_state(self, event=None):
        """Check and prevent fullscreen state"""
        try:
            # Check if window is in fullscreen mode
            if self.root.attributes('-fullscreen'):
                self.force_windowed_mode()
                
            # Also check window size and prevent if it's screen-sized
            if hasattr(self.root, 'winfo_width') and hasattr(self.root, 'winfo_height'):
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                win_width = self.root.winfo_width()
                win_height = self.root.winfo_height()
                
                # If window takes up entire screen, resize it smaller
                if win_width >= screen_width and win_height >= screen_height:
                    new_width = int(screen_width * 0.9)
                    new_height = int(screen_height * 0.8)
                    self.root.geometry(f"{new_width}x{new_height}")
                    self.root.update()
                    
        except tk.TclError:
            pass
    
    def monitor_fullscreen(self):
        """Continuously monitor and prevent fullscreen mode"""
        self.check_fullscreen_state()
        # Schedule next check in 100ms
        self.root.after(100, self.monitor_fullscreen)

    def setup_fullscreen_prevention(self):
        """Set up initial fullscreen prevention"""
        # Disable fullscreen mode
        self.root.attributes('-fullscreen', False)
        
        # Prevent fullscreen with F11 key and other fullscreen methods
        self.root.bind('<F11>', lambda e: self.force_windowed_mode())
        self.root.bind('<Alt-Return>', lambda e: self.force_windowed_mode())
        self.root.bind('<Alt-F4>', lambda e: self.root.quit())  # Keep Alt+F4 for quit
        
        # Set maximum window size to screen size (prevents true fullscreen)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        max_width = int(screen_width * 0.95)  # 95% of screen width
        max_height = int(screen_height * 0.90)  # 90% of screen height
        self.root.maxsize(max_width, max_height)

def main():
    root = tk.Tk()
    app = LineCounterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 