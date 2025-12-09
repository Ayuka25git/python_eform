#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定画面モジュール (PySide6版)
入力項目を動的に設定できる画面（拡張版）
"""
import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QCheckBox, QSpinBox, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QGroupBox, QHeaderView, QDoubleSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QScrollArea
)
from PySide6.QtCore import Signal, Qt

CONFIG_FILE = "form_config.json"


class FieldDetailDialog(QDialog):
    """項目詳細設定ダイアログ"""

    def __init__(self, field_data=None, parent=None):
        super().__init__(parent)
        self.field_data = field_data or {}
        self.init_ui()

    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("項目詳細設定")
        self.setModal(True)
        self.resize(600, 700)

        layout = QVBoxLayout()

        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout()

        # 基本設定
        basic_group = QGroupBox("基本設定")
        basic_layout = QFormLayout()

        self.label_input = QLineEdit(self.field_data.get("label_name", ""))
        self.label_input.setPlaceholderText("例: 電圧、外観、寸法")
        basic_layout.addRow("項目名 *:", self.label_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["文字列", "パスワード", "数値", "日付", "日付時刻", "時刻", "表形式"])
        current_type = self.field_data.get("data_type", "文字列")
        index = self.type_combo.findText(current_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        basic_layout.addRow("データ型 *:", self.type_combo)

        self.unit_input = QLineEdit(self.field_data.get("unit", ""))
        self.unit_input.setPlaceholderText("例: V, mm, kg")
        basic_layout.addRow("単位:", self.unit_input)

        self.required_check = QCheckBox()
        self.required_check.setChecked(self.field_data.get("is_required", False))
        basic_layout.addRow("必須項目:", self.required_check)

        self.order_spin = QSpinBox()
        self.order_spin.setMinimum(1)
        self.order_spin.setMaximum(999)
        self.order_spin.setValue(self.field_data.get("display_order", 1))
        basic_layout.addRow("表示順:", self.order_spin)

        basic_group.setLayout(basic_layout)
        form_layout.addRow(basic_group)

        # レイアウト設定
        layout_group = QGroupBox("レイアウト設定")
        layout_layout = QFormLayout()

        self.column_pos_spin = QSpinBox()
        self.column_pos_spin.setMinimum(1)
        self.column_pos_spin.setMaximum(10)
        self.column_pos_spin.setValue(self.field_data.get("column_position", 1))
        layout_layout.addRow("列位置（1-10）:", self.column_pos_spin)

        self.new_row_check = QCheckBox()
        self.new_row_check.setChecked(self.field_data.get("new_row", False))
        layout_layout.addRow("この項目の前で改行:", self.new_row_check)

        layout_group.setLayout(layout_layout)
        form_layout.addRow(layout_group)

        # 入力規則設定
        validation_group = QGroupBox("入力規則設定（数値型のみ）")
        validation_layout = QFormLayout()

        self.min_value_spin = QDoubleSpinBox()
        self.min_value_spin.setMinimum(-999999.99)
        self.min_value_spin.setMaximum(999999.99)
        self.min_value_spin.setValue(self.field_data.get("min_value", 0.0))
        validation_layout.addRow("最小値:", self.min_value_spin)

        self.max_value_spin = QDoubleSpinBox()
        self.max_value_spin.setMinimum(-999999.99)
        self.max_value_spin.setMaximum(999999.99)
        self.max_value_spin.setValue(self.field_data.get("max_value", 100.0))
        validation_layout.addRow("最大値:", self.max_value_spin)

        validation_group.setLayout(validation_layout)
        self.validation_group = validation_group
        form_layout.addRow(validation_group)

        # 入力規則設定（文字列型のみ）
        text_validation_group = QGroupBox("入力規則設定（文字列型のみ）")
        text_validation_layout = QFormLayout()

        self.regex_input = QLineEdit(self.field_data.get("regex_pattern", ""))
        self.regex_input.setPlaceholderText("例: ^[0-9]{3}-[0-9]{4}$ （郵便番号）")
        text_validation_layout.addRow("正規表現パターン:", self.regex_input)

        self.max_length_spin = QSpinBox()
        self.max_length_spin.setMinimum(0)
        self.max_length_spin.setMaximum(10000)
        self.max_length_spin.setValue(self.field_data.get("max_length", 255))
        text_validation_layout.addRow("最大文字数:", self.max_length_spin)

        text_validation_group.setLayout(text_validation_layout)
        self.text_validation_group = text_validation_group
        form_layout.addRow(text_validation_group)

        # その他設定
        other_group = QGroupBox("その他設定")
        other_layout = QFormLayout()

        self.placeholder_input = QLineEdit(self.field_data.get("placeholder", ""))
        self.placeholder_input.setPlaceholderText("例: ここに入力してください")
        other_layout.addRow("プレースホルダー:", self.placeholder_input)

        self.help_text_input = QLineEdit(self.field_data.get("help_text", ""))
        self.help_text_input.setPlaceholderText("例: 小数点第2位まで入力")
        other_layout.addRow("ヘルプテキスト:", self.help_text_input)

        other_group.setLayout(other_layout)
        form_layout.addRow(other_group)

        # 表形式設定
        table_group = QGroupBox("表形式設定")
        table_layout = QFormLayout()
        self.table_columns_input = QLineEdit(",".join(self.field_data.get("table_columns", [])))
        self.table_columns_input.setPlaceholderText("例: 項目A, 項目B, 項目C")
        table_layout.addRow("カラム名（カンマ区切り）:", self.table_columns_input)

        self.table_rows_spin = QSpinBox()
        self.table_rows_spin.setMinimum(1)
        self.table_rows_spin.setMaximum(200)
        self.table_rows_spin.setValue(self.field_data.get("table_rows", 20))
        table_layout.addRow("表示行数:", self.table_rows_spin)

        table_group.setLayout(table_layout)
        self.table_group = table_group
        form_layout.addRow(table_group)

        scroll_widget.setLayout(form_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # ボタン
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # 初期状態で表示/非表示を設定
        self.on_type_changed(self.type_combo.currentText())

    def on_type_changed(self, data_type):
        """データ型が変更されたときに入力規則の表示を切り替え"""
        # 数値型の場合のみ数値入力規則を表示
        self.validation_group.setVisible(data_type == "数値")
        # 文字列/パスワード型の場合のみ文字列入力規則を表示
        self.text_validation_group.setVisible(data_type in ["文字列", "パスワード"])
        # 表形式のみ表設定を表示
        self.table_group.setVisible(data_type == "表形式")

    def get_field_data(self):
        """入力された項目データを取得"""
        data = {
            "label_name": self.label_input.text().strip(),
            "data_type": self.type_combo.currentText(),
            "unit": self.unit_input.text().strip(),
            "is_required": self.required_check.isChecked(),
            "display_order": self.order_spin.value(),
            "column_position": self.column_pos_spin.value(),
            "new_row": self.new_row_check.isChecked(),
            "placeholder": self.placeholder_input.text().strip(),
            "help_text": self.help_text_input.text().strip(),
        }

        # 数値型の場合の入力規則
        if self.type_combo.currentText() == "数値":
            data["min_value"] = self.min_value_spin.value()
            data["max_value"] = self.max_value_spin.value()

        # 文字列/パスワード型の場合の入力規則
        if self.type_combo.currentText() in ["文字列", "パスワード"]:
            data["regex_pattern"] = self.regex_input.text().strip()
            data["max_length"] = self.max_length_spin.value()

        if self.type_combo.currentText() == "表形式":
            columns = [c.strip() for c in self.table_columns_input.text().split(",") if c.strip()]
            data["table_columns"] = columns
            data["table_rows"] = self.table_rows_spin.value()

        return data


class ConfigPage(QWidget):
    """設定画面ウィジェット"""

    # 設定が保存されたときのシグナル
    config_saved = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # タイトル
        title = QLabel("入力フォーム設定")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # 項目一覧テーブル
        table_group = QGroupBox("登録済み項目一覧")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "項目名", "データ型", "単位", "必須", "表示順", "編集", "削除"
        ])

        # テーブルのヘッダーを調整
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # ボタンエリア
        button_layout = QHBoxLayout()

        add_btn = QPushButton("➕ 新規項目追加")
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        add_btn.clicked.connect(self.add_field)
        button_layout.addWidget(add_btn)

        save_btn = QPushButton("💾 設定を保存")
        save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-size: 14px;")
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("🔄 設定をリセット")
        reset_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-size: 14px;")
        reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_config(self):
        """設定ファイルを読み込んでテーブルに表示"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.update_table(config)

    def update_table(self, config):
        """テーブルを更新"""
        self.table.setRowCount(0)

        for idx, field in enumerate(config):
            self.table.insertRow(idx)

            # 項目名
            self.table.setItem(idx, 0, QTableWidgetItem(field.get("label_name", "")))

            # データ型
            self.table.setItem(idx, 1, QTableWidgetItem(field.get("data_type", "")))

            # 単位
            self.table.setItem(idx, 2, QTableWidgetItem(field.get("unit", "")))

            # 必須
            required = "✓" if field.get("is_required", False) else ""
            item = QTableWidgetItem(required)
            item.setTextAlignment(int(Qt.AlignCenter))
            self.table.setItem(idx, 3, item)

            # 表示順
            order_item = QTableWidgetItem(str(field.get("display_order", 0)))
            order_item.setTextAlignment(int(Qt.AlignCenter))
            self.table.setItem(idx, 4, order_item)

            # 編集ボタン
            edit_btn = QPushButton("✏️ 編集")
            edit_btn.setStyleSheet("background-color: #2196F3; color: white;")
            edit_btn.clicked.connect(lambda checked, row=idx: self.edit_field(row))
            self.table.setCellWidget(idx, 5, edit_btn)

            # 削除ボタン
            delete_btn = QPushButton("🗑️ 削除")
            delete_btn.setStyleSheet("background-color: #f44336; color: white;")
            delete_btn.clicked.connect(lambda checked, row=idx: self.delete_field(row))
            self.table.setCellWidget(idx, 6, delete_btn)

    def add_field(self):
        """新規項目を追加"""
        # 現在の設定を読み込んで次の表示順を計算
        config = []
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

        next_order = max([f.get("display_order", 0) for f in config], default=0) + 1

        # デフォルト値で詳細ダイアログを開く
        default_data = {"display_order": next_order}
        dialog = FieldDetailDialog(default_data, self)

        if dialog.exec():
            field_data = dialog.get_field_data()

            if not field_data["label_name"]:
                QMessageBox.warning(self, "入力エラー", "項目名を入力してください。")
                return

            config.append(field_data)

            # 一時保存
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            # テーブルを更新
            self.update_table(config)

            QMessageBox.information(self, "成功", f"項目「{field_data['label_name']}」を追加しました。")

    def edit_field(self, row):
        """項目を編集"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

            if 0 <= row < len(config):
                # 編集ダイアログを開く
                dialog = FieldDetailDialog(config[row], self)

                if dialog.exec():
                    field_data = dialog.get_field_data()

                    if not field_data["label_name"]:
                        QMessageBox.warning(self, "入力エラー", "項目名を入力してください。")
                        return

                    config[row] = field_data

                    # 保存
                    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)

                    # テーブルを更新
                    self.update_table(config)

                    QMessageBox.information(self, "成功", f"項目「{field_data['label_name']}」を更新しました。")

    def delete_field(self, row):
        """項目を削除"""
        reply = QMessageBox.question(
            self, "確認",
            f"項目「{self.table.item(row, 0).text()}」を削除しますか?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 現在の設定を読み込み
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # 項目を削除
                if 0 <= row < len(config):
                    config.pop(row)

                    # 保存
                    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)

                    # テーブルを更新
                    self.update_table(config)

                    QMessageBox.information(self, "成功", "項目を削除しました。")

                    # シグナルを発行して入力画面に通知
                    self.config_saved.emit()

    def save_config(self):
        """設定を保存"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 表示順でソート
            config.sort(key=lambda x: x.get("display_order", 0))

            # 保存
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "成功", "設定を保存しました。")

            # シグナルを発行して入力画面に通知
            self.config_saved.emit()
        else:
            QMessageBox.warning(self, "警告", "保存する設定がありません。")

    def reset_config(self):
        """設定をリセット"""
        reply = QMessageBox.question(
            self, "確認",
            "すべての設定をリセットしますか?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)

            self.table.setRowCount(0)

            QMessageBox.information(self, "成功", "設定をリセットしました。")

            # シグナルを発行して入力画面に通知
            self.config_saved.emit()
