# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **dynamic form input system for production facilities** that allows no-code configuration of data entry forms. The system enables managers to configure form fields (text, numbers, dates, passwords, etc.) without programming, and operators to input production data using these dynamically generated forms.

**Current Status**: Prototype phase with JSON-based storage. Database integration (PostgreSQL/SQL Server) is planned but not yet implemented.

## Running the Application

```bash
# Install dependencies
pip install PySide6

# Run the application
python main.py
```

The application will launch a Qt desktop GUI with three tabs.

## Architecture

### Core Design Pattern: Dynamic Form Generation

The system uses a **metadata-driven architecture** where form definitions stored in JSON files control the UI generation at runtime. This is the central architectural concept.

**Flow**:
1. Admin defines form fields in `config_page_qt.py` → saves to `form_config.json`
2. `input_page_qt.py` reads `form_config.json` → dynamically generates Qt widgets
3. User inputs data → saved to `input_data.json` (future: database)

### File Structure

**Active PySide6 Implementation** (current):
- `main.py` - Entry point, 3-tab Qt application
- `config_page_qt.py` - Form field configuration UI with detailed settings dialog
- `input_page_qt.py` - Dynamic form generator and data entry UI
- `db_config_page.py` - Database connection settings (UI only, not connected)

**Legacy Streamlit Files** (deprecated, ignore):
- `config_page.py`, `input_page.py` - Old Streamlit implementation

**Data Files** (auto-generated):
- `form_config.json` - Field definitions (metadata)
- `db_config.json` - DB connection settings
- `input_data.json` - Input records

### Key Architectural Concepts

#### 1. Field Configuration Schema

Each field in `form_config.json` contains:
```json
{
  "label_name": "電圧",
  "data_type": "数値",  // 文字列|パスワード|数値|日付|日付時刻
  "unit": "V",
  "is_required": true,
  "display_order": 1,
  "column_position": 1,  // Grid layout column
  "new_row": false,      // Force new row before this field
  "min_value": 0.0,      // Validation (numeric only)
  "max_value": 500.0,
  "regex_pattern": "",   // Validation (text/password only)
  "max_length": 255,
  "placeholder": "",
  "help_text": ""
}
```

#### 2. Dynamic Widget Mapping

`input_page_qt.py` maps data types to Qt widgets:
- `文字列` → `QLineEdit`
- `パスワード` → `QLineEdit` (with `setEchoMode(Password)`)
- `数値` → `QDoubleSpinBox` (with min/max validation)
- `日付` → `QDateEdit` (calendar popup)
- `日付時刻` → `QDateTimeEdit` (calendar + time picker)

#### 3. Grid Layout Algorithm

Forms use `QGridLayout` with automatic row/column calculation:
- Max 3 columns per row by default
- `new_row=true` forces a new row
- `column_position` is stored but currently not used (future enhancement)

#### 4. Signal-Based UI Updates

When configuration is saved:
```python
# config_page_qt.py
self.config_saved.emit()  # Signal emitted

# main.py
self.config_page.config_saved.connect(self.input_page.reload_config)
```

This triggers `input_page_qt.py` to reload and regenerate all form widgets.

## Important Implementation Details

### Character Encoding

All Python files use UTF-8 encoding with BOM header:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

This is **critical** for Japanese text. Always include this header in new files.

### Validation Logic

Validation occurs in `input_page_qt.py` → `register_data()`:
1. Required field check (empty strings, None values)
2. Numeric range validation (min_value ≤ value ≤ max_value)
3. Regex pattern matching (for text/password fields)
4. All validation errors collected before showing single error dialog

### Password Storage Warning

DB passwords in `db_config.json` are stored in **plaintext**. This is acknowledged in the UI with a warning. Production deployment requires encryption implementation.

### Deleted Fields Behavior

When a field is deleted from `config_page_qt.py`:
- It's removed from `form_config.json`
- `input_page_qt.py` reads the file on reload → deleted fields automatically disappear
- No explicit "soft delete" or "is_active" flag needed

## Future Database Integration

The system is designed for **EAV (Entity-Attribute-Value) pattern**:

**Planned Tables**:
- `m_form_def` - Field definitions (replaces `form_config.json`)
- `t_production_header` - Header data (date, product, lot)
- `t_production_detail` - Detail data (EAV rows referencing field definitions)

**Migration Path**:
When implementing DB integration:
1. Create SQLAlchemy models matching the schema in `README.md`
2. Add database operations in new `db_manager.py` module
3. Replace JSON file I/O in `config_page_qt.py` and `input_page_qt.py`
4. Keep JSON as fallback/offline mode

## Common Pitfalls

1. **Qt Import Issues**: Always import `Qt` from `PySide6.QtCore` for alignment constants (e.g., `Qt.AlignCenter`)

2. **Lambda Closures in Loops**: When creating buttons in loops, use default arguments:
   ```python
   # Correct
   btn.clicked.connect(lambda checked, row=idx: self.edit_field(row))

   # Wrong - all buttons will reference final idx value
   btn.clicked.connect(lambda: self.edit_field(idx))
   ```

3. **Layout Cleanup**: Always clear layouts properly before regenerating:
   ```python
   while layout.count():
       item = layout.takeAt(0)
       if item.widget():
           item.widget().deleteLater()
   ```

4. **Data Type Consistency**: Field data types are stored as Japanese strings (`文字列`, `数値`, etc.). Don't mix English equivalents.

## Testing

No automated tests exist yet. Manual testing workflow:

1. Run `python main.py`
2. Go to "⚙️ フォーム設定" tab
3. Click "➕ 新規項目追加"
4. Configure field with various data types and validations
5. Save configuration
6. Switch to "📝 データ入力" tab
7. Verify field appears with correct widget type
8. Test validation rules
9. Register data and verify in table

## Configuration Files

- `form_config.json` - **Critical**: Contains all form field definitions. Backup before major changes.
- `db_config.json` - DB connection settings (not currently used)
- `input_data.json` - Saved input records (will be migrated to DB)

All JSON files are auto-generated and should not be manually edited unless debugging.
