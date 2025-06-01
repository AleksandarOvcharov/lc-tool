#!/usr/bin/env python3
"""
Test the special extension patterns .** and .*
"""

def test_pattern_logic():
    """Test the logic for special patterns"""
    print("Testing special extension pattern logic...")
    
    # Test data
    test_files = [
        "main.py", "script.js", "README.md", "config.json",
        "compiled.pyc", "binary.exe", "library.dll", "data.log"
    ]
    
    # Test different pattern combinations
    test_cases = [
        {
            "name": "Normal extensions (.py,.js)",
            "include_exts": [".py", ".js"],
            "exclude_patterns": ["*.pyc", "*.exe", "*.dll"],
            "expected_included": ["main.py", "script.js"]
        },
        {
            "name": "All except excluded (.** pattern)",
            "include_exts": [".**"],
            "exclude_patterns": ["*.pyc", "*.exe", "*.dll"],
            "expected_included": ["main.py", "script.js", "README.md", "config.json", "data.log"]
        },
        {
            "name": "Everything including excluded (.* pattern)",
            "include_exts": [".*"],
            "exclude_patterns": ["*.pyc", "*.exe", "*.dll"],
            "expected_included": ["main.py", "script.js", "README.md", "config.json", "compiled.pyc", "binary.exe", "library.dll", "data.log"]
        },
        {
            "name": "Mixed patterns (.**, .py)",
            "include_exts": [".**", ".py"],
            "exclude_patterns": ["*.pyc", "*.exe", "*.dll"],
            "expected_included": ["main.py", "script.js", "README.md", "config.json", "data.log"]
        }
    ]
    
    import fnmatch
    from pathlib import Path
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        include_exts = test_case["include_exts"]
        exclude_patterns = test_case["exclude_patterns"]
        
        # Simulate the logic from the main code
        include_all_except_excluded = ".**" in include_exts
        include_everything = ".*" in include_exts
        
        # Remove special patterns from the list
        if include_all_except_excluded:
            include_exts = [ext for ext in include_exts if ext != ".**"]
        if include_everything:
            include_exts = [ext for ext in include_exts if ext != ".*"]
        
        included_files = []
        
        for file in test_files:
            file_path = Path(file)
            
            # Check exclude patterns (unless .* is used)
            if not include_everything and any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                continue
            
            # Check extension inclusion
            file_ext = file_path.suffix.lower()
            
            should_include = False
            
            if include_everything:
                should_include = True
            elif include_all_except_excluded:
                should_include = True  # Already filtered by exclude patterns
            elif include_exts:
                should_include = any(file_ext == ext for ext in include_exts)
            else:
                should_include = True  # No extensions specified
            
            if should_include:
                included_files.append(file)
        
        print(f"Include extensions: {test_case['include_exts']}")
        print(f"Exclude patterns: {exclude_patterns}")
        print(f"Expected: {test_case['expected_included']}")
        print(f"Actual:   {included_files}")
        
        # Check if results match
        if set(included_files) == set(test_case['expected_included']):
            print("✓ PASS")
        else:
            print("✗ FAIL")
            missing = set(test_case['expected_included']) - set(included_files)
            extra = set(included_files) - set(test_case['expected_included'])
            if missing:
                print(f"  Missing: {missing}")
            if extra:
                print(f"  Extra: {extra}")

if __name__ == "__main__":
    print("Testing Special Extension Patterns")
    print("=" * 40)
    test_pattern_logic()
    print("\nTest complete!") 