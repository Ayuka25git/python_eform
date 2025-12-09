#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アカウント/権限設定タブ
"""
import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit,
    QCheckBox, QPushButton, QMessageBox, QHBoxLayout
)

ACCOUNT_CONFIG_FILE = "account_settings.json"


class AccountSettingsPage(QWidget):
    """簡易的な権限管理設定ウィジェット"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("アカウント設定 / 権限管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # アカウント基本情報
        account_group = QGroupBox("アカウント情報")
        account_form = QFormLayout()
        self.account_name_input = QLineEdit()
        self.account_name_input.setPlaceholderText("例: 山田太郎")
        account_form.addRow("表示名:", self.account_name_input)

        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("例: 管理者 / 現場リーダー")
        account_form.addRow("ロール名:", self.role_input)
        account_group.setLayout(account_form)
        layout.addWidget(account_group)

        # 権限チェックボックス
        permission_group = QGroupBox("付与する権限")
        permission_layout = QVBoxLayout()
        self.permission_checks = {
            "create": QCheckBox("データ登録"),
            "update": QCheckBox("データ編集"),
            "delete": QCheckBox("データ削除"),
            "export": QCheckBox("データ出力/エクスポート"),
            "manage_users": QCheckBox("ユーザー管理"),
            "manage_forms": QCheckBox("フォーム設定の変更")
        }
        for checkbox in self.permission_checks.values():
            permission_layout.addWidget(checkbox)
        permission_group.setLayout(permission_layout)
        layout.addWidget(permission_group)

        # ボタン
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 権限を保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("🔄 リセット")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        if not os.path.exists(ACCOUNT_CONFIG_FILE):
            return

        with open(ACCOUNT_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.account_name_input.setText(data.get("display_name", ""))
        self.role_input.setText(data.get("role", ""))
        permissions = data.get("permissions", {})
        for key, checkbox in self.permission_checks.items():
            checkbox.setChecked(permissions.get(key, False))

    def save_settings(self):
        data = {
            "display_name": self.account_name_input.text().strip(),
            "role": self.role_input.text().strip(),
            "permissions": {key: cb.isChecked() for key, cb in self.permission_checks.items()}
        }

        with open(ACCOUNT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "成功", "アカウント設定を保存しました。")

    def reset_settings(self):
        if os.path.exists(ACCOUNT_CONFIG_FILE):
            os.remove(ACCOUNT_CONFIG_FILE)
        self.account_name_input.clear()
        self.role_input.clear()
        for checkbox in self.permission_checks.values():
            checkbox.setChecked(False)
        QMessageBox.information(self, "完了", "設定をリセットしました。")
