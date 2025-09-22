import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime

class MultiFormatManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Multi-Format File Manager")
        self.window.geometry("1000x700")
        self.window.configure(bg="lightgray")

        # Data storage
        self.current_file = None
        self.current_format = None
        self.data = None

        # Supported formats
        self.supported_formats = {
            '.csv': 'CSV',
            '.json': 'JSON',
            '.xml': 'XML',
            '.txt': 'Text'
        }

        self.buat_interface()

    def buat_interface(self):
        # Header
        header_frame = tk.Frame(self.window, bg="darkblue", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="MULTI-FORMAT FILE MANAGER",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="darkblue"
        ).pack(pady=15)

        # Toolbar
        toolbar = tk.Frame(self.window, bg="lightgray", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)

        # Load file button
        btn_load = tk.Button(
            toolbar,
            text="📁 Load File",
            command=self.load_file,
            bg="lightblue",
            font=("Arial", 10),
            width=12
        )
        btn_load.pack(side=tk.LEFT, padx=2, pady=2)

        # Save file button
        btn_save = tk.Button(
            toolbar,
            text="💾 Save File",
            command=self.save_file,
            bg="lightgreen",
            font=("Arial", 10),
            width=12
        )
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)

        # Convert format button
        btn_convert = tk.Button(
            toolbar,
            text="🔄 Convert",
            command=self.show_convert_dialog,
            bg="lightyellow",
            font=("Arial", 10),
            width=12
        )
        btn_convert.pack(side=tk.LEFT, padx=2, pady=2)

        # Validate button
        btn_validate = tk.Button(
            toolbar,
            text="✓ Validate",
            command=self.validate_file,
            bg="lightcoral",
            font=("Arial", 10),
            width=12
        )
        btn_validate.pack(side=tk.LEFT, padx=2, pady=2)

        # File info label
        self.file_info_label = tk.Label(
            toolbar,
            text="No file loaded",
            font=("Arial", 10),
            bg="lightgray"
        )
        self.file_info_label.pack(side=tk.RIGHT, padx=10)

                # Main content dengan notebook
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Raw Data View
        self.raw_frame = tk.Frame(self.notebook)
        self.notebook.add(self.raw_frame, text="Raw Data")

        # Text widget untuk raw data
        self.raw_text = tk.Text(
            self.raw_frame,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        raw_scrollbar = tk.Scrollbar(self.raw_frame, orient=tk.VERTICAL, command=self.raw_text.yview)
        self.raw_text.configure(yscrollcommand=raw_scrollbar.set)

        self.raw_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        raw_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Tab 2: Structured View
        self.structured_frame = tk.Frame(self.notebook)
        self.notebook.add(self.structured_frame, text="Structured View")

        # Treeview untuk structured data
        self.tree = ttk.Treeview(self.structured_frame)
        tree_scrollbar_v = ttk.Scrollbar(self.structured_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar_h = ttk.Scrollbar(self.structured_frame, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=tree_scrollbar_v.set, xscrollcommand=tree_scrollbar_h.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        tree_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X, padx=5)

        # Tab 3: Statistics
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")

        # Text widget untuk statistics
        self.stats_text = tk.Text(
            self.stats_frame,
            font=("Courier", 11),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        stats_scrollbar = tk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)

        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def load_file(self):
        """Method untuk load file dengan format detection"""
        file_types = [
            ("CSV files", "*.csv"),
            ("JSON files", "*.json"),
            ("XML files", "*.xml"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select file to load",
            filetypes=file_types
        )

        if filename:
            try:
                self.current_file = filename
                self.detect_format(filename)
                self.load_file_content(filename)
                self.update_file_info()

                messagebox.showinfo("Success", f"File loaded: {os.path.basename(filename)}")

            except Exception as e:
                messagebox.showerror("Error", f"Cannot load file: {str(e)}")

    def detect_format(self, filename):
        """Method untuk detect format file berdasarkan ekstensi"""
        _, ext = os.path.splitext(filename.lower())
        self.current_format = self.supported_formats.get(ext, 'Unknown')

    def load_file_content(self, filename):
        """Method untuk load content berdasarkan format"""
        if self.current_format == 'CSV':
            self.load_csv_file(filename)
        elif self.current_format == 'JSON':
            self.load_json_file(filename)
        elif self.current_format == 'XML':
            self.load_xml_file(filename)
        else:
            self.load_text_file(filename)

        # Update all views
        self.update_raw_view()
        self.update_structured_view()
        self.update_statistics()

    def load_csv_file(self, filename):
        """Method untuk load CSV file"""
        self.data = {
            'type': 'csv',
            'headers': [],
            'rows': [],
            'raw_content': ''
        }

        with open(filename, 'r', encoding='utf-8') as file:
            # Baca raw content
            file.seek(0)
            self.data['raw_content'] = file.read()

            # Parse CSV
            file.seek(0)
            csv_reader = csv.reader(file)

            # Baca header
            try:
                self.data['headers'] = next(csv_reader)
            except StopIteration:
                self.data['headers'] = []

            # Baca rows
            for row in csv_reader:
                self.data['rows'].append(row)

    def load_json_file(self, filename):
        """Method untuk load JSON file"""
        with open(filename, 'r', encoding='utf-8') as file:
            raw_content = file.read()

        self.data = {
            'type': 'json',
            'content': json.loads(raw_content),
            'raw_content': raw_content
        }

    def load_xml_file(self, filename):
        """Method untuk load XML file"""
        with open(filename, 'r', encoding='utf-8') as file:
            raw_content = file.read()

        tree = ET.parse(filename)
        root = tree.getroot()

        self.data = {
            'type': 'xml',
            'tree': tree,
            'root': root,
            'raw_content': raw_content
        }

    def load_text_file(self, filename):
        """Method untuk load text file"""
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        self.data = {
            'type': 'text',
            'content': content,
            'raw_content': content
        }

    def update_raw_view(self):
        """Method untuk update raw data view"""
        if self.data:
            self.raw_text.delete(1.0, tk.END)
            self.raw_text.insert(1.0, self.data['raw_content'])

    def update_structured_view(self):
        """Method untuk update structured view"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.data:
            return

        if self.data['type'] == 'csv':
            self.update_csv_tree_view()
        elif self.data['type'] == 'json':
            self.update_json_tree_view()
        elif self.data['type'] == 'xml':
            self.update_xml_tree_view()
        else:
            self.update_text_tree_view()

    def update_csv_tree_view(self):
        """Method untuk update CSV tree view"""
        # Setup columns
        if self.data['headers']:
            self.tree["columns"] = self.data['headers']
            self.tree["show"] = "headings"

            # Configure column headers
            for header in self.data['headers']:
                self.tree.heading(header, text=header)
                self.tree.column(header, width=100)

            # Insert data rows
            for i, row in enumerate(self.data['rows']):
                # Pad row if it has fewer columns than headers
                padded_row = row + [''] * (len(self.data['headers']) - len(row))
                self.tree.insert("", tk.END, values=padded_row[:len(self.data['headers'])])
        else:
            # No headers, show as simple list
            self.tree["columns"] = ("Data",)
            self.tree["show"] = "headings"
            self.tree.heading("Data", text="Data")

            for i, row in enumerate(self.data['rows']):
                self.tree.insert("", tk.END, values=(str(row),))

    def update_json_tree_view(self):
        """Method untuk update JSON tree view"""
        self.tree["show"] = "tree"
        self.tree["columns"] = ("Value",)
        self.tree.heading("#0", text="Key")
        self.tree.heading("Value", text="Value")

        def add_json_node(parent, key, value, path=""):
            if isinstance(value, dict):
                node = self.tree.insert(parent, tk.END, text=key, values=("Object",))
                for k, v in value.items():
                    add_json_node(node, k, v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                node = self.tree.insert(parent, tk.END, text=key, values=(f"Array ({len(value)} items)",))
                for i, item in enumerate(value):
                    add_json_node(node, f"[{i}]", item, f"{path}[{i}]" if path else f"[{i}]")
            else:
                self.tree.insert(parent, tk.END, text=key, values=(str(value),))

        if isinstance(self.data['content'], dict):
            for key, value in self.data['content'].items():
                add_json_node("", key, value)
        elif isinstance(self.data['content'], list):
            for i, item in enumerate(self.data['content']):
                add_json_node("", f"[{i}]", item)
        else:
            self.tree.insert("", tk.END, text="Root", values=(str(self.data['content']),))

    def update_xml_tree_view(self):
        """Method untuk update XML tree view"""
        self.tree["show"] = "tree"
        self.tree["columns"] = ("Attributes", "Text")
        self.tree.heading("#0", text="Element")
        self.tree.heading("Attributes", text="Attributes")
        self.tree.heading("Text", text="Text Content")

        def add_xml_node(parent, element):
            # Format attributes
            attrs = ", ".join([f"{k}={v}" for k, v in element.attrib.items()]) if element.attrib else ""

            # Get text content (only direct text, not from children)
            text_content = (element.text or "").strip()

            node = self.tree.insert(
                parent, 
                tk.END, 
                text=element.tag, 
                values=(attrs, text_content)
            )

            # Add child elements
            for child in element:
                add_xml_node(node, child)

        add_xml_node("", self.data['root'])

    def update_text_tree_view(self):
        """Method untuk update text tree view"""
        self.tree["show"] = "tree"
        self.tree["columns"] = ("Content",)
        self.tree.heading("#0", text="Line")
        self.tree.heading("Content", text="Content")

        lines = self.data['content'].split('\n')
        for i, line in enumerate(lines, 1):
            self.tree.insert("", tk.END, text=f"Line {i}", values=(line,))

    def update_statistics(self):
        """Method untuk update statistics view"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)

        if not self.data:
            self.stats_text.insert(1.0, "No data loaded")
            self.stats_text.config(state=tk.DISABLED)
            return

        stats = self.generate_statistics()
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state=tk.DISABLED)

    def generate_statistics(self):
        """Method untuk generate statistics berdasarkan format"""
        if self.data['type'] == 'csv':
            return self.generate_csv_statistics()
        elif self.data['type'] == 'json':
            return self.generate_json_statistics()
        elif self.data['type'] == 'xml':
            return self.generate_xml_statistics()
        else:
            return self.generate_text_statistics()

    def generate_csv_statistics(self):
        """Method untuk generate CSV statistics"""
        stats = f"""CSV FILE STATISTICS
{'='*50}

File: {os.path.basename(self.current_file) if self.current_file else 'Unknown'}
Format: CSV (Comma Separated Values)

STRUCTURE:
- Headers: {len(self.data['headers'])}
- Data Rows: {len(self.data['rows'])}
- Total Rows: {len(self.data['rows']) + (1 if self.data['headers'] else 0)}

HEADERS:
"""

        for i, header in enumerate(self.data['headers'], 1):
            stats += f"{i:2d}. {header}\n"

        if self.data['rows']:
            stats += f"\nDATA ANALYSIS:\n"

            # Analyze each column
            for i, header in enumerate(self.data['headers']):
                column_data = []
                for row in self.data['rows']:
                    if i < len(row) and row[i].strip():
                        column_data.append(row[i].strip())

                stats += f"\nColumn '{header}':\n"
                stats += f"  - Non-empty values: {len(column_data)}\n"
                stats += f"  - Empty values: {len(self.data['rows']) - len(column_data)}\n"

                if column_data:
                    # Check if numeric
                    numeric_values = []
                    for value in column_data:
                        try:
                            numeric_values.append(float(value))
                        except ValueError:
                            pass

                    if numeric_values:
                        stats += f"  - Numeric values: {len(numeric_values)}\n"
                        stats += f"  - Min: {min(numeric_values)}\n"
                        stats += f"  - Max: {max(numeric_values)}\n"
                        stats += f"  - Average: {sum(numeric_values)/len(numeric_values):.2f}\n"
                    else:
                        # Text analysis
                        unique_values = set(column_data)
                        stats += f"  - Unique values: {len(unique_values)}\n"
                        if len(unique_values) <= 10:
                            stats += f"  - Values: {', '.join(sorted(unique_values))}\n"

        return stats

    def generate_json_statistics(self):
        """Method untuk generate JSON statistics"""
        stats = f"""JSON FILE STATISTICS
{'='*50}

File: {os.path.basename(self.current_file) if self.current_file else 'Unknown'}
Format: JSON (JavaScript Object Notation)

"""

        def analyze_json_structure(obj, path="root", depth=0):
            result = ""
            indent = "  " * depth

            if isinstance(obj, dict):
                result += f"{indent}{path}: Object ({len(obj)} keys)\n"
                for key, value in obj.items():
                    result += analyze_json_structure(value, key, depth + 1)
            elif isinstance(obj, list):
                result += f"{indent}{path}: Array ({len(obj)} items)\n"
                if obj:
                    # Analyze first few items
                    for i, item in enumerate(obj[:3]):
                        result += analyze_json_structure(item, f"[{i}]", depth + 1)
                    if len(obj) > 3:
                        result += f"{indent}  ... and {len(obj) - 3} more items\n"
            else:
                value_type = type(obj).__name__
                value_str = str(obj)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                result += f"{indent}{path}: {value_type} = {value_str}\n"

            return result

        stats += "STRUCTURE:\n"
        stats += analyze_json_structure(self.data['content'])

        # Count different types
        def count_types(obj, counts=None):
            if counts is None:
                counts = {}

            obj_type = type(obj).__name__
            counts[obj_type] = counts.get(obj_type, 0) + 1

            if isinstance(obj, dict):
                for value in obj.values():
                    count_types(value, counts)
            elif isinstance(obj, list):
                for item in obj:
                    count_types(item, counts)

            return counts

        type_counts = count_types(self.data['content'])

        stats += f"\nTYPE DISTRIBUTION:\n"
        for obj_type, count in sorted(type_counts.items()):
            stats += f"- {obj_type}: {count}\n"

        return stats

    def generate_xml_statistics(self):
        """Method untuk generate XML statistics"""
        stats = f"""XML FILE STATISTICS
{'='*50}

File: {os.path.basename(self.current_file) if self.current_file else 'Unknown'}
Format: XML (eXtensible Markup Language)

ROOT ELEMENT: {self.data['root'].tag}

"""

        # Count elements
        element_counts = {}
        attribute_counts = {}
        total_elements = 0
        elements_with_text = 0

        def analyze_element(element):
            nonlocal total_elements, elements_with_text

            total_elements += 1

            # Count element types
            tag = element.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1

            # Count attributes
            if element.attrib:
                for attr in element.attrib:
                    attribute_counts[attr] = attribute_counts.get(attr, 0) + 1

            # Check for text content
            if element.text and element.text.strip():
                elements_with_text += 1

            # Recurse through children
            for child in element:
                analyze_element(child)

        analyze_element(self.data['root'])

        stats += f"STRUCTURE ANALYSIS:\n"
        stats += f"- Total elements: {total_elements}\n"
        stats += f"- Elements with text: {elements_with_text}\n"
        stats += f"- Unique element types: {len(element_counts)}\n"
        stats += f"- Unique attributes: {len(attribute_counts)}\n"

        stats += f"\nELEMENT DISTRIBUTION:\n"
        for element, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True):
            stats += f"- {element}: {count}\n"

        if attribute_counts:
            stats += f"\nATTRIBUTE DISTRIBUTION:\n"
            for attr, count in sorted(attribute_counts.items(), key=lambda x: x[1], reverse=True):
                stats += f"- {attr}: {count}\n"

        return stats

    def generate_text_statistics(self):
        """Method untuk generate text statistics"""
        content = self.data['content']

        stats = f"""TEXT FILE STATISTICS
{'='*50}

File: {os.path.basename(self.current_file) if self.current_file else 'Unknown'}
Format: Plain Text

BASIC COUNTS:
- Characters: {len(content)}
- Characters (no spaces): {len(content.replace(' ', '').replace('\n', '').replace('\t', ''))}
- Words: {len(content.split())}
- Lines: {content.count(chr(10)) + 1}
- Paragraphs: {len([p for p in content.split('\n\n') if p.strip()])}

CHARACTER ANALYSIS:
- Spaces: {content.count(' ')}
- Tabs: {content.count('\t')}
- Newlines: {content.count('\n')}
- Digits: {sum(1 for c in content if c.isdigit())}
- Letters: {sum(1 for c in content if c.isalpha())}
- Uppercase: {sum(1 for c in content if c.isupper())}
- Lowercase: {sum(1 for c in content if c.islower())}

"""

        # Word frequency (top 10)
        words = content.lower().split()
        word_freq = {}
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

        if word_freq:
            stats += "MOST FREQUENT WORDS:\n"
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            for word, count in sorted_words[:10]:
                stats += f"- {word}: {count}\n"

        return stats
    
    def validate_file(self):
        """Method untuk validasi file"""
        if not self.data:
            messagebox.showwarning("Warning", "No file loaded!")
            return

        try:
            validation_result = self.perform_validation()
            messagebox.showinfo("Validation Result", validation_result)
        except Exception as e:
            messagebox.showerror("Validation Error", f"Validation failed: {str(e)}")

    def perform_validation(self):
        """Method untuk perform validation berdasarkan format"""
        if self.data['type'] == 'csv':
            return self.validate_csv()
        elif self.data['type'] == 'json':
            return self.validate_json()
        elif self.data['type'] == 'xml':
            return self.validate_xml()
        else:
            return self.validate_text()

    def validate_csv(self):
        """Method untuk validasi CSV"""
        issues = []

        # Check for consistent column count
        if self.data['headers']:
            expected_cols = len(self.data['headers'])
            for i, row in enumerate(self.data['rows'], 2):  # Start from row 2 (after header)
                if len(row) != expected_cols:
                    issues.append(f"Row {i}: Expected {expected_cols} columns, found {len(row)}")

        # Check for empty cells
        empty_cells = 0
        for i, row in enumerate(self.data['rows'], 2):
            for j, cell in enumerate(row):
                if not cell.strip():
                    empty_cells += 1

        result = f"CSV Validation Results:\n\n"
        result += f"✓ File structure: Valid CSV format\n"
        result += f"✓ Headers: {len(self.data['headers'])} columns\n"
        result += f"✓ Data rows: {len(self.data['rows'])}\n"

        if issues:
            result += f"\n⚠ Issues found:\n"
            for issue in issues[:10]:  # Show max 10 issues
                result += f"  - {issue}\n"
            if len(issues) > 10:
                result += f"  ... and {len(issues) - 10} more issues\n"
        else:
            result += f"✓ Column consistency: All rows have correct number of columns\n"

        if empty_cells > 0:
            result += f"⚠ Empty cells: {empty_cells} found\n"
        else:
            result += f"✓ Data completeness: No empty cells\n"

        return result

    def validate_json(self):
        """Method untuk validasi JSON"""
        result = f"JSON Validation Results:\n\n"
        result += f"✓ Syntax: Valid JSON format\n"

        # Check structure
        if isinstance(self.data['content'], dict):
            result += f"✓ Root type: Object with {len(self.data['content'])} keys\n"
        elif isinstance(self.data['content'], list):
            result += f"✓ Root type: Array with {len(self.data['content'])} items\n"
        else:
            result += f"✓ Root type: {type(self.data['content']).__name__}\n"

        # Check for common issues
        def check_json_issues(obj, path=""):
            issues = []

            if isinstance(obj, dict):
                # Check for empty keys
                if "" in obj:
                    issues.append(f"Empty key found at {path}")

                # Check for null values
                for key, value in obj.items():
                    if value is None:
                        issues.append(f"Null value at {path}.{key}")
                    else:
                        issues.extend(check_json_issues(value, f"{path}.{key}" if path else key))

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    issues.extend(check_json_issues(item, f"{path}[{i}]" if path else f"[{i}]"))

            return issues

        issues = check_json_issues(self.data['content'])

        if issues:
            result += f"\n⚠ Potential issues:\n"
            for issue in issues[:10]:
                result += f"  - {issue}\n"
            if len(issues) > 10:
                result += f"  ... and {len(issues) - 10} more issues\n"
        else:
            result += f"✓ Structure: No issues detected\n"

        return result

    def validate_xml(self):
        """Method untuk validasi XML"""
        result = f"XML Validation Results:\n\n"
        result += f"✓ Syntax: Well-formed XML\n"
        result += f"✓ Root element: {self.data['root'].tag}\n"

        # Count elements and check for issues
        total_elements = 0
        empty_elements = 0
        elements_with_attrs = 0

        def check_element(element):
            nonlocal total_elements, empty_elements, elements_with_attrs

            total_elements += 1

            if not element.text or not element.text.strip():
                if len(element) == 0:  # No children either
                    empty_elements += 1

            if element.attrib:
                elements_with_attrs += 1

            for child in element:
                check_element(child)

        check_element(self.data['root'])

        result += f"✓ Total elements: {total_elements}\n"
        result += f"✓ Elements with attributes: {elements_with_attrs}\n"

        if empty_elements > 0:
            result += f"⚠ Empty elements: {empty_elements} found\n"
        else:
            result += f"✓ Content: All elements have content or children\n"

        return result

    def validate_text(self):
        """Method untuk validasi text"""
        content = self.data['content']

        result = f"Text File Validation Results:\n\n"
        result += f"✓ File readable as text\n"
        result += f"✓ Character count: {len(content)}\n"
        result += f"✓ Line count: {content.count(chr(10)) + 1}\n"

        # Check encoding issues
        try:
            content.encode('utf-8')
            result += f"✓ Encoding: UTF-8 compatible\n"
        except UnicodeEncodeError:
            result += f"⚠ Encoding: Contains non-UTF-8 characters\n"

        # Check for very long lines
        lines = content.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 200]

        if long_lines:
            result += f"⚠ Long lines: {len(long_lines)} lines exceed 200 characters\n"
        else:
            result += f"✓ Line length: All lines under 200 characters\n"

        return result

    def show_convert_dialog(self):
        """Method untuk menampilkan dialog konversi"""
        if not self.data:
            messagebox.showwarning("Warning", "No file loaded!")
            return

        # Create conversion dialog
        convert_dialog = tk.Toplevel(self.window)
        convert_dialog.title("Convert File Format")
        convert_dialog.geometry("400x300")
        convert_dialog.transient(self.window)
        convert_dialog.grab_set()

        tk.Label(
            convert_dialog,
            text=f"Convert from {self.current_format}",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            convert_dialog,
            text="Select target format:",
            font=("Arial", 12)
        ).pack(pady=5)

        # Format selection
        format_var = tk.StringVar(value="JSON")
        formats = ["CSV", "JSON", "XML", "Text"]

        for fmt in formats:
            if fmt != self.current_format:
                tk.Radiobutton(
                    convert_dialog,
                    text=fmt,
                    variable=format_var,
                    value=fmt,
                    font=("Arial", 11)
                ).pack(anchor="w", padx=50)

        # Buttons
        button_frame = tk.Frame(convert_dialog)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Convert",
            command=lambda: self.perform_conversion(format_var.get(), convert_dialog),
            bg="green",
            fg="white",
            width=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=convert_dialog.destroy,
            bg="red",
            fg="white",
            width=10
        ).pack(side=tk.LEFT, padx=5)

    def perform_conversion(self, target_format, dialog):
        """Method untuk perform file conversion"""
        try:
            if target_format == "CSV":
                converted_data = self.convert_to_csv()
                extension = ".csv"
            elif target_format == "JSON":
                converted_data = self.convert_to_json()
                extension = ".json"
            elif target_format == "XML":
                converted_data = self.convert_to_xml()
                extension = ".xml"
            else:  # Text
                converted_data = self.convert_to_text()
                extension = ".txt"

            # Save converted file
            filename = filedialog.asksaveasfilename(
                title=f"Save as {target_format}",
                defaultextension=extension,
                filetypes=[(f"{target_format} files", f"*{extension}"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(converted_data)

                dialog.destroy()
                messagebox.showinfo("Success", f"File converted and saved as {target_format}")

        except Exception as e:
            messagebox.showerror("Conversion Error", f"Cannot convert file: {str(e)}")

    def convert_to_csv(self):
        """Method untuk convert ke CSV"""
        if self.data['type'] == 'csv':
            return self.data['raw_content']
        elif self.data['type'] == 'json':
            # Convert JSON to CSV (flatten if possible)
            if isinstance(self.data['content'], list) and self.data['content']:
                if isinstance(self.data['content'][0], dict):
                    # List of objects - can convert to CSV
                    import io
                    output = io.StringIO()

                    # Get all possible keys
                    all_keys = set()
                    for item in self.data['content']:
                        if isinstance(item, dict):
                            all_keys.update(item.keys())

                    fieldnames = sorted(all_keys)
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()

                    for item in self.data['content']:
                        if isinstance(item, dict):
                            writer.writerow(item)

                    return output.getvalue()

            # Fallback: convert to simple key-value CSV
            output = "Key,Value\n"
            def flatten_json(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, (dict, list)):
                            flatten_json(value, new_key)
                        else:
                            output += f'"{new_key}","{value}"\n'
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
                        if isinstance(item, (dict, list)):
                            flatten_json(item, new_key)
                        else:
                            output += f'"{new_key}","{item}"\n'

            flatten_json(self.data['content'])
            return output

        else:
            # Convert other formats to simple CSV
            return f"Data,Value\n\"{self.current_format}\",\"{self.data.get('raw_content', '')[:100]}...\""

    def convert_to_json(self):
        """Method untuk convert ke JSON"""
        if self.data['type'] == 'json':
            return self.data['raw_content']
        elif self.data['type'] == 'csv':
            # Convert CSV to JSON
            result = []
            for row in self.data['rows']:
                row_dict = {}
                for i, header in enumerate(self.data['headers']):
                    row_dict[header] = row[i] if i < len(row) else ""
                result.append(row_dict)
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # Convert other formats to JSON
            return json.dumps({
                "format": self.current_format,
                "content": self.data.get('raw_content', ''),
                "converted_at": datetime.now().isoformat()
            }, indent=2)

    def convert_to_xml(self):
        """Method untuk convert ke XML"""
        if self.data['type'] == 'xml':
            return self.data['raw_content']
        elif self.data['type'] == 'csv':
            # Convert CSV to XML
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<data>\n'
            for i, row in enumerate(self.data['rows']):
                xml_content += f'  <row id="{i+1}">\n'
                for j, header in enumerate(self.data['headers']):
                    value = row[j] if j < len(row) else ""
                    xml_content += f'    <{header}>{value}</{header}>\n'
                xml_content += '  </row>\n'
            xml_content += '</data>'
            return xml_content
        elif self.data['type'] == 'json':
            # Convert JSON to XML
            def json_to_xml(obj, tag="item"):
                if isinstance(obj, dict):
                    xml = f"<{tag}>\n"
                    for key, value in obj.items():
                        xml += json_to_xml(value, key)
                    xml += f"</{tag}>\n"
                    return xml
                elif isinstance(obj, list):
                    xml = f"<{tag}>\n"
                    for i, item in enumerate(obj):
                        xml += json_to_xml(item, f"item_{i}")
                    xml += f"</{tag}>\n"
                    return xml
                else:
                    return f"<{tag}>{obj}</{tag}>\n"

            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += json_to_xml(self.data['content'], "root")
            return xml_content
        else:
            # Convert other formats to XML
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<document>
  <format>{self.current_format}</format>
  <content>{self.data.get('raw_content', '')}</content>
</document>'''

    def convert_to_text(self):
        """Method untuk convert ke text"""
        if self.data['type'] == 'text':
            return self.data['raw_content']
        else:
            return self.data.get('raw_content', '')

    def save_file(self):
        """Method untuk save file"""
        if not self.data:
            messagebox.showwarning("Warning", "No file loaded!")
            return

        # Get current content from raw view (in case user edited it)
        current_content = self.raw_text.get(1.0, tk.END).rstrip('\n')

        if self.current_file:
            # Save to current file
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(current_content)
                messagebox.showinfo("Success", f"File saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {str(e)}")
        else:
            # Save as new file
            self.save_as_file(current_content)

    def save_as_file(self, content=None):
        """Method untuk save as new file"""
        if content is None:
            if not self.data:
                messagebox.showwarning("Warning", "No file loaded!")
                return
            content = self.raw_text.get(1.0, tk.END).rstrip('\n')

        # Determine file types based on current format
        if self.current_format == 'CSV':
            file_types = [("CSV files", "*.csv"), ("All files", "*.*")]
            default_ext = ".csv"
        elif self.current_format == 'JSON':
            file_types = [("JSON files", "*.json"), ("All files", "*.*")]
            default_ext = ".json"
        elif self.current_format == 'XML':
            file_types = [("XML files", "*.xml"), ("All files", "*.*")]
            default_ext = ".xml"
        else:
            file_types = [("Text files", "*.txt"), ("All files", "*.*")]
            default_ext = ".txt"

        filename = filedialog.asksaveasfilename(
            title="Save File As",
            filetypes=file_types,
            defaultextension=default_ext
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)

                self.current_file = filename
                self.update_file_info()
                messagebox.showinfo("Success", f"File saved as: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {str(e)}")

    def update_file_info(self):
        """Method untuk update file info label"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_info_label.config(text=f"{filename} ({self.current_format})")
        else:
            self.file_info_label.config(text="No file loaded")

    def jalankan(self):
        """Method untuk menjalankan aplikasi"""
        self.window.mainloop()

# Untuk menjalankan aplikasi
if __name__ == "__main__":
    app = MultiFormatManager()
    app.jalankan()