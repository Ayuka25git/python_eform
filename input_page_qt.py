#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
入力画面モジュール (PySide6版) - 拡張版
設定された項目に基づいて動的にフォームを生成する
パスワード、日付時刻、配置、入力規則に対応
"""
import json
import os
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QScrollArea, QDateEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QDoubleSpinBox, QHeaderView,
    QDateTimeEdit, QGridLayout
)
from PySide6.QtCore import Qt, QDate, QDateTime

CONFIG_FILE = "form_config.json"
DATA_FILE = "input_data.json"


class InputPage(QWidget):
    """入力画面ウィジェット"""

    def __init__(self):
        super().__init__()
        self.detail_widgets = {}  # 詳細入力ウィジェットを保持
        self.init_ui()
        self.reload_config()

    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # タイトル
        title = QLabel("データ入力画面")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # ヘッダー情報入力エリア
        header_group = QGroupBox("基本情報")
        header_layout = QHBoxLayout()

        # 日付
        header_layout.addWidget(QLabel("日付:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        header_layout.addWidget(self.date_edit)

        # 品種
        header_layout.addWidget(QLabel("品種:"))
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("例: 製品A")
        header_layout.addWidget(self.product_input)

        # ロット番号
        header_layout.addWidget(QLabel("製造ロット番号:"))
        self.lot_input = QLineEdit()
        self.lot_input.setPlaceholderText("例: LOT-20250101-001")
        header_layout.addWidget(self.lot_input)

        header_group.setLayout(header_layout)
        layout.addWidget(header_group)

        # 詳細データ入力エリア(動的生成)
        self.detail_group = QGroupBox("詳細データ入力")
        self.detail_main_layout = QVBoxLayout()

        # スクロール可能なエリア
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content_layout = QGridLayout()  # グリッドレイアウトに変更
        self.scroll_content.setLayout(self.scroll_content_layout)
        self.scroll_area.setWidget(self.scroll_content)

        self.detail_main_layout.addWidget(self.scroll_area)
        self.detail_group.setLayout(self.detail_main_layout)
        layout.addWidget(self.detail_group)

        # 登録・クリアボタン
        button_layout = QHBoxLayout()

        register_btn = QPushButton("✅ データを登録")
        register_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        register_btn.clicked.connect(self.register_data)
        button_layout.addWidget(register_btn)

        clear_btn = QPushButton("🔄 クリア")
        clear_btn.setStyleSheet("background-color: #FFC107; color: white; padding: 10px; font-size: 14px;")
        clear_btn.clicked.connect(self.clear_inputs)
        button_layout.addWidget(clear_btn)

        layout.addLayout(button_layout)

        # 登録済みデータ表示エリア
        data_group = QGroupBox("登録済みデータ")
        data_layout = QVBoxLayout()

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            "日付", "品種", "ロット番号", "登録日時", "詳細"
        ])

        # テーブルのヘッダーを調整
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        data_layout.addWidget(self.data_table)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        self.setLayout(layout)

        # 登録済みデータを読み込み
        self.load_registered_data()

    def reload_config(self):
        """設定を再読み込みして詳細入力フォームを再生成"""
        # 既存のウィジェットをクリア
        while self.scroll_content_layout.count():
            item = self.scroll_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.detail_widgets.clear()

        # 設定ファイルを読み込み
        if not os.path.exists(CONFIG_FILE):
            label = QLabel("⚠️ 入力項目が設定されていません。\n「設定画面」から入力項目を追加してください。")
            label.setStyleSheet("color: orange; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.scroll_content_layout.addWidget(label, 0, 0)
            return

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        if not config:
            label = QLabel("⚠️ 入力項目が設定されていません。\n「設定画面」から入力項目を追加してください。")
            label.setStyleSheet("color: orange; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            self.scroll_content_layout.addWidget(label, 0, 0)
            return

        # 表示順でソート
        config.sort(key=lambda x: x.get("display_order", 0))

        # グリッドレイアウトでフォームを生成
        current_row = 0
        current_col = 0

        for field in config:
            # 改行フラグがある場合は次の行へ
            if field.get("new_row", False) and current_col > 0:
                current_row += 1
                current_col = 0

            # 列位置を取得
            col_pos = field.get("column_position", 1)

            # 入力フィールドを作成
            label_widget, input_widget = self.create_input_field(field)

            # グリッドに配置
            self.scroll_content_layout.addWidget(label_widget, current_row, current_col * 2)
            self.scroll_content_layout.addWidget(input_widget, current_row, current_col * 2 + 1)

            current_col += 1

            # 3列を超えたら次の行へ
            if current_col >= 3:
                current_row += 1
                current_col = 0

    def create_input_field(self, field):
        """データ型に応じた入力フィールドを生成"""
        label_name = field.get("label_name", "")
        data_type = field.get("data_type", "文字列")
        unit = field.get("unit", "")
        is_required = field.get("is_required", False)
        placeholder = field.get("placeholder", "")
        help_text = field.get("help_text", "")

        # ラベル作成
        label_text = label_name
        if unit:
            label_text += f" ({unit})"
        if is_required:
            label_text += " *"

        label = QLabel(label_text)
        label.setMinimumWidth(150)

        # ヘルプテキストがあればツールチップに設定
        if help_text:
            label.setToolTip(help_text)

        # データ型に応じたウィジェットを生成
        if data_type == "数値":
            widget = QDoubleSpinBox()
            min_val = field.get("min_value", -999999.99)
            max_val = field.get("max_value", 999999.99)
            widget.setMinimum(min_val)
            widget.setMaximum(max_val)
            widget.setDecimals(2)
            widget.setSingleStep(0.1)
            if placeholder:
                widget.setSpecialValueText(placeholder)

        elif data_type == "日付":
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
            widget.setCalendarPopup(True)

        elif data_type == "日付時刻":
            widget = QDateTimeEdit()
            widget.setDateTime(QDateTime.currentDateTime())
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        elif data_type == "パスワード":
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.Password)
            if placeholder:
                widget.setPlaceholderText(placeholder)
            else:
                widget.setPlaceholderText(f"{label_name}を入力してください")

            # 最大文字数設定
            max_length = field.get("max_length", 255)
            widget.setMaxLength(max_length)

        else:  # 文字列
            widget = QLineEdit()
            if placeholder:
                widget.setPlaceholderText(placeholder)
            else:
                widget.setPlaceholderText(f"{label_name}を入力してください")

            # 最大文字数設定
            max_length = field.get("max_length", 255)
            widget.setMaxLength(max_length)

        # ウィジェットを保存
        self.detail_widgets[label_name] = {
            "widget": widget,
            "data_type": data_type,
            "is_required": is_required,
            "field_config": field
        }

        return label, widget

    def register_data(self):
        """データを登録"""
        # ヘッダー情報の検証
        product_name = self.product_input.text().strip()
        lot_no = self.lot_input.text().strip()

        if not product_name or not lot_no:
            QMessageBox.warning(self, "入力エラー", "品種と製造ロット番号を入力してください。")
            return

        # 詳細データの検証と取得
        detail_values = {}
        errors = []

        for label_name, info in self.detail_widgets.items():
            widget = info["widget"]
            data_type = info["data_type"]
            is_required = info["is_required"]
            field_config = info["field_config"]

            # 値を取得
            if data_type == "数値":
                value = widget.value()

                # 数値の範囲チェック
                min_val = field_config.get("min_value")
                max_val = field_config.get("max_value")
                if min_val is not None and value < min_val:
                    errors.append(f"「{label_name}」は{min_val}以上で入力してください。")
                if max_val is not None and value > max_val:
                    errors.append(f"「{label_name}」は{max_val}以下で入力してください。")

            elif data_type == "日付":
                value = widget.date().toString("yyyy-MM-dd")

            elif data_type == "日付時刻":
                value = widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")

            else:  # 文字列またはパスワード
                value = widget.text().strip()

                # 正規表現チェック
                regex_pattern = field_config.get("regex_pattern", "")
                if regex_pattern and value:
                    try:
                        if not re.match(regex_pattern, value):
                            errors.append(f"「{label_name}」の形式が正しくありません。")
                    except re.error:
                        pass  # 正規表現のエラーは無視

            # 必須チェック
            if is_required:
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"「{label_name}」は必須項目です。")
                elif data_type == "数値" and value == 0:
                    # 数値の場合、0も有効な値として扱う
                    pass

            detail_values[label_name] = value

        if errors:
            QMessageBox.warning(self, "入力エラー", "\n".join(errors))
            return

        # データを保存
        new_data = {
            "entry_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "product_name": product_name,
            "lot_no": lot_no,
            "details": detail_values,
            "registered_at": datetime.now().isoformat()
        }

        # 既存データを読み込み
        existing_data = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

        existing_data.append(new_data)

        # 保存
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "成功", "データを登録しました。")

        # 入力フィールドをクリア
        self.clear_inputs()

        # 登録済みデータを再読み込み
        self.load_registered_data()

    def clear_inputs(self):
        """入力フィールドをクリア"""
        for info in self.detail_widgets.values():
            widget = info["widget"]
            data_type = info["data_type"]

            if data_type == "数値":
                widget.setValue(0.0)
            elif data_type == "日付":
                widget.setDate(QDate.currentDate())
            elif data_type == "日付時刻":
                widget.setDateTime(QDateTime.currentDateTime())
            else:  # 文字列またはパスワード
                widget.clear()

    def load_registered_data(self):
        """登録済みデータを読み込んでテーブルに表示"""
        self.data_table.setRowCount(0)

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data_list = json.load(f)

        # 新しい順に表示
        for idx, data in enumerate(reversed(data_list)):
            self.data_table.insertRow(idx)

            # 日付
            self.data_table.setItem(idx, 0, QTableWidgetItem(data.get("entry_date", "")))

            # 品種
            self.data_table.setItem(idx, 1, QTableWidgetItem(data.get("product_name", "")))

            # ロット番号
            self.data_table.setItem(idx, 2, QTableWidgetItem(data.get("lot_no", "")))

            # 登録日時
            registered_at = data.get("registered_at", "")
            if registered_at:
                # ISO形式を読みやすく変換
                try:
                    dt = datetime.fromisoformat(registered_at)
                    registered_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            self.data_table.setItem(idx, 3, QTableWidgetItem(registered_at))

            # 詳細データをボタンで表示
            details_btn = QPushButton("詳細")
            details_btn.clicked.connect(lambda checked, d=data: self.show_details(d))
            self.data_table.setCellWidget(idx, 4, details_btn)

    def show_details(self, data):
        """詳細データをメッセージボックスで表示"""
        details = data.get("details", {})

        message = "【基本情報】\n"
        message += f"日付: {data.get('entry_date', '')}\n"
        message += f"品種: {data.get('product_name', '')}\n"
        message += f"ロット番号: {data.get('lot_no', '')}\n"
        message += f"登録日時: {data.get('registered_at', '')}\n\n"
        message += "【詳細データ】\n"

        for key, value in details.items():
            message += f"{key}: {value}\n"

        QMessageBox.information(self, "詳細データ", message)
