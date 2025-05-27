import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import fnmatch
from pathlib import Path
import threading

class LineCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Counter - Code Analysis Tool")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
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
        
        self.setup_ui()
        
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
        ttk.Label(main_frame, text="(comma-separated, e.g., .py,.js,.html)", font=("Arial", 8)).grid(row=2, column=1, columnspan=2, sticky=tk.W)
        
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
        
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT)
        
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
            
            # Results storage
            file_results = []
            extension_stats = {}
            
            # Walk through directory
            for root, dirs, files in os.walk(folder_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_folders)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if file should be excluded by pattern
                    if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                        continue
                        
                    # Check if file extension is included
                    file_ext = file_path.suffix.lower()
                    if include_exts and not any(file_ext == ext for ext in include_exts):
                        continue
                        
                    # Count lines
                    try:
                        lines = self.count_file_lines(file_path, self.line_count_method.get())
                        if lines > 0:
                            file_size = file_path.stat().st_size
                            rel_path = file_path.relative_to(folder_path)
                            
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
            
    def count_file_lines(self, file_path, method):
        """Count lines in a file based on the selected method"""
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
        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        
        # Calculate totals
        self.total_files = len(file_results)
        self.total_lines = sum(result['lines'] for result in file_results)
        total_size = sum(result['size'] for result in file_results)
        
        # Update summary
        size_mb = total_size / (1024 * 1024)
        self.summary_label.config(text=f"Total: {self.total_files} files, {self.total_lines:,} lines of code, {size_mb:.2f} MB")
        
        # Add extension summaries
        for ext, stats in sorted(extension_stats.items(), key=lambda x: x[1]['lines'], reverse=True):
            ext_name = ext if ext else "(no extension)"
            size_kb = stats['size'] / 1024
            parent = self.tree.insert("", "end", text=f"{ext_name} files ({stats['files']} files)", 
                                    values=(f"{stats['lines']:,}", f"{size_kb:.1f} KB"))
            
            # Add individual files for this extension
            ext_files = [f for f in file_results if f['extension'] == ext]
            ext_files.sort(key=lambda x: x['lines'], reverse=True)
            
            for file_info in ext_files:
                size_kb = file_info['size'] / 1024
                self.tree.insert(parent, "end", text=file_info['path'], 
                               values=(f"{file_info['lines']:,}", f"{size_kb:.1f} KB"))
        
    def counting_finished(self):
        self.progress.stop()
        self.count_button.config(state="normal")
        
    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.summary_label.config(text="No analysis performed yet")
        self.results = {}
        self.total_lines = 0
        self.total_files = 0
        
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

def main():
    root = tk.Tk()
    app = LineCounterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 