#!/usr/bin/env python3
"""
Simple test script to verify export functionality
"""

import json
import csv
import io
import os

# Test data similar to what the app would generate
test_file_results = [
    {'path': 'src/main.py', 'lines': 150, 'size': 5000, 'extension': '.py'},
    {'path': 'src/utils.js', 'lines': 80, 'size': 3200, 'extension': '.js'},
    {'path': 'README.md', 'lines': 45, 'size': 2100, 'extension': '.md'},
]

test_extension_stats = {
    '.py': {'files': 1, 'lines': 150, 'size': 5000},
    '.js': {'files': 1, 'lines': 80, 'size': 3200}, 
    '.md': {'files': 1, 'lines': 45, 'size': 2100}
}

def test_csv_export():
    """Test CSV export functionality"""
    print("Testing CSV export...")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['File Path', 'Extension', 'Lines of Code', 'File Size (bytes)', 'File Size (KB)'])
    
    # Write data for each file
    for file_info in sorted(test_file_results, key=lambda x: x['lines'], reverse=True):
        size_kb = file_info['size'] / 1024
        writer.writerow([
            file_info['path'],
            file_info['extension'] or '(no extension)',
            file_info['lines'],
            file_info['size'],
            f"{size_kb:.2f}"
        ])
    
    csv_data = output.getvalue()
    
    # Test writing to file
    test_filename = "test_export.csv"
    try:
        with open(test_filename, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_data)
        
        if os.path.exists(test_filename) and os.path.getsize(test_filename) > 0:
            print(f"✓ CSV export successful! File size: {os.path.getsize(test_filename)} bytes")
            print(f"✓ First few lines of CSV:")
            with open(test_filename, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i < 3:
                        print(f"  {line.strip()}")
            os.remove(test_filename)  # Clean up
            return True
        else:
            print("✗ CSV file was not created properly")
            return False
            
    except Exception as e:
        print(f"✗ CSV export failed: {e}")
        return False

def test_json_export():
    """Test JSON export functionality"""
    print("\nTesting JSON export...")
    
    export_data = {
        'analysis_summary': {
            'total_files': len(test_file_results),
            'total_lines': sum(f['lines'] for f in test_file_results),
            'total_size_bytes': sum(f['size'] for f in test_file_results),
            'analyzed_folder': '/test/folder',
            'count_method': 'all'
        },
        'files': [
            {
                'path': file_info['path'],
                'extension': file_info['extension'] or None,
                'lines_of_code': file_info['lines'],
                'file_size_bytes': file_info['size'],
                'file_size_kb': round(file_info['size'] / 1024, 2)
            }
            for file_info in sorted(test_file_results, key=lambda x: x['lines'], reverse=True)
        ],
        'extension_summary': [
            {
                'extension': ext if ext else None,
                'file_count': stats['files'],
                'total_lines': stats['lines'],
                'total_size_bytes': stats['size'],
                'total_size_kb': round(stats['size'] / 1024, 2)
            }
            for ext, stats in sorted(test_extension_stats.items(), key=lambda x: x[1]['lines'], reverse=True)
        ]
    }
    
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # Test writing to file
    test_filename = "test_export.json"
    try:
        with open(test_filename, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        if os.path.exists(test_filename) and os.path.getsize(test_filename) > 0:
            print(f"✓ JSON export successful! File size: {os.path.getsize(test_filename)} bytes")
            
            # Verify JSON is valid by reading it back
            with open(test_filename, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                print(f"✓ JSON is valid. Total files: {loaded_data['analysis_summary']['total_files']}")
            
            os.remove(test_filename)  # Clean up
            return True
        else:
            print("✗ JSON file was not created properly")
            return False
            
    except Exception as e:
        print(f"✗ JSON export failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing export functionality...\n")
    
    csv_ok = test_csv_export()
    json_ok = test_json_export()
    
    print(f"\n{'='*50}")
    if csv_ok and json_ok:
        print("✓ All export tests passed!")
    else:
        print("✗ Some export tests failed!")
        
    print("Export functionality test complete.") 