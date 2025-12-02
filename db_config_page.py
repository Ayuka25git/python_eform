#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース接続設定画面モジュール (PySide6版)
PostgreSQLとSQL Serverの接続設定を管理
"""
import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QGroupBox, QSpinBox
)
from PySide6.QtCore import Signal

DB_CONFIG_FILE = "db_config.json"


class DBConfigPage(QWidget):
    """データベース接続設定画面ウィジェット"""

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
        title = QLabel("データベース接続設定")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # 接続設定グループ
        config_group = QGroupBox("接続情報")
        config_layout = QVBoxLayout()

        # DB種別選択
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("DB種別:"))
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["PostgreSQL", "Microsoft SQL Server"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        row1.addWidget(self.db_type_combo)
        row1.addStretch()
        config_layout.addLayout(row1)

        # ホスト名・IPアドレス
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("ホスト名/IPアドレス:"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("例: localhost, 192.168.1.100")
        row2.addWidget(self.host_input)
        config_layout.addLayout(row2)

        # ポート番号
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("ポート番号:"))
        self.port_spin = QSpinBox()
        self.port_spin.setMinimum(1)
        self.port_spin.setMaximum(65535)
        self.port_spin.setValue(5432)  # PostgreSQLのデフォルト
        row3.addWidget(self.port_spin)
        row3.addStretch()
        config_layout.addLayout(row3)

        # データベース名
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("データベース名:"))
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("例: production_db")
        row4.addWidget(self.database_input)
        config_layout.addLayout(row4)

        # ユーザー名
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("ユーザー名:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("例: admin")
        row5.addWidget(self.username_input)
        config_layout.addLayout(row5)

        # パスワード
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("パスワード:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # パスワード表示を隠す
        self.password_input.setPlaceholderText("パスワードを入力")
        row6.addWidget(self.password_input)

        # パスワード表示切り替えボタン
        self.show_password_btn = QPushButton("👁 表示")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        row6.addWidget(self.show_password_btn)
        config_layout.addLayout(row6)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # 接続テスト・保存ボタン
        button_layout = QHBoxLayout()

        test_btn = QPushButton("🔌 接続テスト")
        test_btn.setStyleSheet("background-color: #FFC107; color: white; padding: 10px; font-size: 14px;")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)

        save_btn = QPushButton("💾 設定を保存")
        save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-size: 14px;")
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("🔄 設定をクリア")
        reset_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-size: 14px;")
        reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

        # 説明エリア
        info_group = QGroupBox("注意事項")
        info_layout = QVBoxLayout()
        info_label = QLabel(
            "• パスワードはファイルに平文で保存されます。本番環境では暗号化の実装を推奨します。\n"
            "• 接続テスト機能は現在実装されていません（将来の実装予定）。\n"
            "• 設定を保存後、データ入力機能でDBへの保存が有効になります。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        info_layout.addWidget(info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        self.setLayout(layout)

    def on_db_type_changed(self, db_type):
        """DB種別が変更されたときにデフォルトポートを設定"""
        if db_type == "PostgreSQL":
            self.port_spin.setValue(5432)
        elif db_type == "Microsoft SQL Server":
            self.port_spin.setValue(1433)

    def toggle_password_visibility(self):
        """パスワードの表示/非表示を切り替え"""
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈 隠す")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁 表示")

    def load_config(self):
        """設定ファイルを読み込む"""
        if os.path.exists(DB_CONFIG_FILE):
            with open(DB_CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)

                # 各フィールドに値を設定
                db_type = config.get("db_type", "PostgreSQL")
                index = self.db_type_combo.findText(db_type)
                if index >= 0:
                    self.db_type_combo.setCurrentIndex(index)

                self.host_input.setText(config.get("host", ""))
                self.port_spin.setValue(config.get("port", 5432))
                self.database_input.setText(config.get("database", ""))
                self.username_input.setText(config.get("username", ""))
                self.password_input.setText(config.get("password", ""))

    def save_config(self):
        """設定を保存"""
        config = {
            "db_type": self.db_type_combo.currentText(),
            "host": self.host_input.text().strip(),
            "port": self.port_spin.value(),
            "database": self.database_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text()  # 注意: 平文保存
        }

        with open(DB_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "成功", "データベース接続設定を保存しました。")
        self.config_saved.emit()

    def reset_config(self):
        """設定をクリア"""
        reply = QMessageBox.question(
            self, "確認",
            "データベース接続設定をクリアしますか?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.host_input.clear()
            self.database_input.clear()
            self.username_input.clear()
            self.password_input.clear()
            self.db_type_combo.setCurrentIndex(0)
            self.port_spin.setValue(5432)

            if os.path.exists(DB_CONFIG_FILE):
                os.remove(DB_CONFIG_FILE)

            QMessageBox.information(self, "成功", "設定をクリアしました。")

    def test_connection(self):
        """接続テスト（将来の実装予定）"""
        QMessageBox.information(
            self, "接続テスト",
            "接続テスト機能は将来の実装予定です。\n\n"
            "現在の設定:\n"
            f"DB種別: {self.db_type_combo.currentText()}\n"
            f"ホスト: {self.host_input.text()}\n"
            f"ポート: {self.port_spin.value()}\n"
            f"データベース: {self.database_input.text()}\n"
            f"ユーザー名: {self.username_input.text()}"
        )
