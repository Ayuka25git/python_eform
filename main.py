#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生産現場向け・可変型入力システム
メインアプリケーション (PySide6版)

DB接続なし版: 設定画面で項目を増やすと、入力画面のフォームが動的に増える仕組みを実装
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from config_page_qt import ConfigPage
from input_page_qt import InputPage
from data_view_page import DataViewPage
from db_config_page import DBConfigPage
from account_settings_page import AccountSettingsPage


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("生産現場向け・可変型入力システム")
        self.setGeometry(100, 100, 1400, 900)

        # タブウィジェットの作成
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 入力画面タブ
        self.input_page = InputPage()
        self.tabs.addTab(self.input_page, "📝 データ入力")

        # データ閲覧タブ
        self.data_view_page = DataViewPage()
        self.tabs.addTab(self.data_view_page, "📊 登録データ")

        # 設定画面タブ
        self.config_page = ConfigPage()
        self.tabs.addTab(self.config_page, "⚙️ フォーム設定")

        # DB接続設定画面タブ
        self.db_config_page = DBConfigPage()
        self.tabs.addTab(self.db_config_page, "🔌 DB接続設定")

        # アカウント設定タブ
        self.account_settings_page = AccountSettingsPage()
        self.tabs.addTab(self.account_settings_page, "👤 アカウント設定")

        # 設定画面で保存されたときに入力画面を更新
        self.config_page.config_saved.connect(self.input_page.reload_config)
        # 入力画面でデータ登録が完了したらデータ閲覧タブを更新
        self.input_page.data_saved.connect(self.data_view_page.load_registered_data)


def main():
    """メインアプリケーション"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # モダンなスタイルを適用

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
