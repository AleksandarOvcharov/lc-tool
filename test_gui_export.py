#!/usr/bin/env python3
"""
Test GUI export functionality without needing the full app
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
import io
import os

# Test data
test_data_csv = """File Path,Extension,Lines of Code,File Size (bytes),File Size (KB)
src/main.py,.py,150,5000,4.88
src/utils.js,.js,80,3200,3.12"""

test_data_json = """{"analysis_summary": {"total_files": 2, "total_lines": 230}}"""

def test_file_dialog_and_save():
    """Test the file dialog and save functionality"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    print("Testing file dialog and save functionality...")
    print("1. Testing CSV save dialog...")
    
    # Test CSV save
    filename_csv = filedialog.asksaveasfilename(
        title="Test CSV Save",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="test_results.csv"
    )
    
    if filename_csv:
        print(f"   Selected file: {filename_csv}")
        try:
            with open(filename_csv, 'w', encoding='utf-8', newline='') as f:
                f.write(test_data_csv)
            
            if os.path.exists(filename_csv) and os.path.getsize(filename_csv) > 0:
                print(f"   ✓ CSV file saved successfully! Size: {os.path.getsize(filename_csv)} bytes")
                
                # Clean up
                try:
                    os.remove(filename_csv)
                    print("   ✓ Test file cleaned up")
                except:
                    print(f"   ! Could not remove test file: {filename_csv}")
            else:
                print("   ✗ CSV file was not created properly")
                
        except Exception as e:
            print(f"   ✗ CSV save failed: {e}")
    else:
        print("   - CSV save cancelled by user")
    
    print("\n2. Testing JSON save dialog...")
    
    # Test JSON save
    filename_json = filedialog.asksaveasfilename(
        title="Test JSON Save",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialfile="test_results.json"
    )
    
    if filename_json:
        print(f"   Selected file: {filename_json}")
        try:
            with open(filename_json, 'w', encoding='utf-8') as f:
                f.write(test_data_json)
            
            if os.path.exists(filename_json) and os.path.getsize(filename_json) > 0:
                print(f"   ✓ JSON file saved successfully! Size: {os.path.getsize(filename_json)} bytes")
                
                # Clean up
                try:
                    os.remove(filename_json)
                    print("   ✓ Test file cleaned up")
                except:
                    print(f"   ! Could not remove test file: {filename_json}")
            else:
                print("   ✗ JSON file was not created properly")
                
        except Exception as e:
            print(f"   ✗ JSON save failed: {e}")
    else:
        print("   - JSON save cancelled by user")
    
    root.destroy()

def test_preview_window():
    """Test the preview window functionality"""
    print("\n3. Testing preview window...")
    
    root = tk.Tk()
    root.title("Export Test")
    root.geometry("400x300")
    
    def show_csv_preview():
        show_preview("CSV Export Test", test_data_csv, "csv")
    
    def show_json_preview():
        show_preview("JSON Export Test", test_data_json, "json")
    
    def show_preview(title, data, file_type):
        """Simplified preview window"""
        preview_window = tk.Toplevel(root)
        preview_window.title(title)
        preview_window.geometry("600x400")
        
        # Text area
        text_widget = tk.Text(preview_window, wrap=tk.NONE, font=("Consolas", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, data)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def copy_to_clipboard():
            preview_window.clipboard_clear()
            preview_window.clipboard_append(data)
            messagebox.showinfo("Success", "Data copied to clipboard!")
        
        def save_to_file():
            file_extension = "csv" if file_type == "csv" else "json"
            default_filename = f"test_results.{file_extension}"
            
            filename = filedialog.asksaveasfilename(
                title=f"Save {file_type.upper()} file",
                defaultextension=f".{file_extension}",
                filetypes=[(f"{file_type.upper()} files", f"*.{file_extension}"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if filename:
                try:
                    newline_setting = '' if file_type == "csv" else None
                    with open(filename, 'w', encoding='utf-8', newline=newline_setting) as f:
                        f.write(data)
                    
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        messagebox.showinfo("Success", f"Data saved successfully!\n\nFile: {filename}\nSize: {os.path.getsize(filename)} bytes")
                        preview_window.destroy()
                    else:
                        messagebox.showerror("Error", "File was created but appears to be empty or inaccessible.")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save to File", command=save_to_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=preview_window.destroy).pack(side=tk.RIGHT)
    
    # Main window buttons
    ttk.Label(root, text="Export Functionality Test", font=("Arial", 14, "bold")).pack(pady=20)
    ttk.Button(root, text="Test CSV Export", command=show_csv_preview).pack(pady=10)
    ttk.Button(root, text="Test JSON Export", command=show_json_preview).pack(pady=10)
    ttk.Button(root, text="Quit", command=root.quit).pack(pady=20)
    
    print("   ✓ Preview window test ready - interact with the GUI to test")
    root.mainloop()

if __name__ == "__main__":
    print("GUI Export Functionality Test")
    print("=" * 40)
    
    # Test file dialogs first
    test_file_dialog_and_save()
    
    # Then test preview window
    test_preview_window()
    
    print("\nGUI export test complete!") 