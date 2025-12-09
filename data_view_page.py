#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登録済みデータ閲覧タブ
"""
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QLabel
)

DATA_FILE = "input_data.json"


class DataViewPage(QWidget):
    """登録済みデータ表示用ウィジェット"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_registered_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("登録済みデータ")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            "日付", "品種", "ロット番号", "登録日時", "詳細"
        ])

        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.data_table)
        self.setLayout(layout)

    def load_registered_data(self):
        """登録済みデータを読み込んでテーブルに表示"""
        self.data_table.setRowCount(0)

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data_list = json.load(f)

        for idx, data in enumerate(reversed(data_list)):
            self.data_table.insertRow(idx)
            self.data_table.setItem(idx, 0, QTableWidgetItem(data.get("entry_date", "")))
            self.data_table.setItem(idx, 1, QTableWidgetItem(data.get("product_name", "")))
            self.data_table.setItem(idx, 2, QTableWidgetItem(data.get("lot_no", "")))

            registered_at = data.get("registered_at", "")
            if registered_at:
                try:
                    dt = datetime.fromisoformat(registered_at)
                    registered_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            self.data_table.setItem(idx, 3, QTableWidgetItem(registered_at))

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
