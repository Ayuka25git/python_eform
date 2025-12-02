"""
入力画面モジュール
設定された項目に基づいて動的にフォームを生成する
"""
import streamlit as st
from datetime import datetime
import json
import os

CONFIG_FILE = "form_config.json"
DATA_FILE = "input_data.json"

def load_form_config():
    """フォーム設定を読み込む"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_input_data():
    """入力データを読み込む"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_input_data(data_list):
    """入力データを保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

def render_input_page():
    """入力画面をレンダリング"""
    st.title("📝 データ入力画面")
    st.markdown("---")

    # フォーム設定を読み込み
    form_config = load_form_config()

    if not form_config:
        st.warning("⚠️ 入力項目が設定されていません。")
        st.info("「設定画面」から入力項目を追加してください。")
        return

    # ヘッダー情報入力
    st.subheader("📋 基本情報")

    col1, col2, col3 = st.columns(3)

    with col1:
        entry_date = st.date_input(
            "日付",
            value=datetime.now(),
            key="entry_date"
        )

    with col2:
        product_name = st.text_input(
            "品種",
            key="product_name",
            placeholder="例: 製品A"
        )

    with col3:
        lot_no = st.text_input(
            "製造ロット番号",
            key="lot_no",
            placeholder="例: LOT-20250101-001"
        )

    st.markdown("---")

    # 詳細入力エリア(動的生成)
    st.subheader("🔢 詳細データ入力")

    if not product_name or not lot_no:
        st.info("基本情報を入力すると、詳細データ入力フォームが表示されます。")
        return

    # 表示順でソート
    sorted_fields = sorted(form_config, key=lambda x: x.get("display_order", 0))

    # 入力値を保持する辞書
    if "detail_values" not in st.session_state:
        st.session_state.detail_values = {}

    # 動的にフォームを生成
    st.write(f"**{len(sorted_fields)}個の入力項目があります**")

    for idx, field in enumerate(sorted_fields):
        label_name = field.get("label_name", "")
        data_type = field.get("data_type", "文字列")
        unit = field.get("unit", "")
        is_required = field.get("is_required", False)

        # ラベル作成
        label = label_name
        if unit:
            label += f" ({unit})"
        if is_required:
            label += " *"

        # データ型に応じた入力フィールドを生成
        field_key = f"field_{idx}_{label_name}"

        if data_type == "数値":
            value = st.number_input(
                label,
                key=field_key,
                format="%.2f",
                help="数値を入力してください"
            )
            st.session_state.detail_values[label_name] = value

        elif data_type == "日付":
            value = st.date_input(
                label,
                key=field_key,
                help="日付を選択してください"
            )
            st.session_state.detail_values[label_name] = str(value)

        else:  # 文字列
            value = st.text_input(
                label,
                key=field_key,
                help="文字列を入力してください"
            )
            st.session_state.detail_values[label_name] = value

    st.markdown("---")

    # 登録ボタン
    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("✅ データを登録", use_container_width=True, type="primary"):
            # 必須チェック
            errors = []
            for field in sorted_fields:
                if field.get("is_required"):
                    label_name = field.get("label_name")
                    value = st.session_state.detail_values.get(label_name)
                    if not value or (isinstance(value, str) and not value.strip()):
                        errors.append(f"「{label_name}」は必須項目です。")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # データを保存
                new_data = {
                    "entry_date": str(entry_date),
                    "product_name": product_name,
                    "lot_no": lot_no,
                    "details": st.session_state.detail_values.copy(),
                    "registered_at": datetime.now().isoformat()
                }

                existing_data = load_input_data()
                existing_data.append(new_data)
                save_input_data(existing_data)

                st.success("✅ データを登録しました!")

                # 詳細値をクリア
                st.session_state.detail_values = {}
                st.rerun()

    with col2:
        if st.button("🔄 クリア", use_container_width=True):
            st.session_state.detail_values = {}
            st.rerun()

    st.markdown("---")

    # 登録済みデータの表示
    st.subheader("📊 登録済みデータ")

    existing_data = load_input_data()

    if existing_data:
        st.write(f"**{len(existing_data)}件のデータが登録されています**")

        for idx, data in enumerate(reversed(existing_data)):
            with st.expander(
                f"No.{len(existing_data) - idx} | {data['entry_date']} | {data['product_name']} | {data['lot_no']}",
                expanded=False
            ):
                st.write("**基本情報:**")
                st.write(f"- 日付: {data['entry_date']}")
                st.write(f"- 品種: {data['product_name']}")
                st.write(f"- ロット番号: {data['lot_no']}")
                st.write(f"- 登録日時: {data['registered_at']}")

                st.write("**詳細データ:**")
                for key, value in data['details'].items():
                    st.write(f"- {key}: {value}")
    else:
        st.info("まだデータが登録されていません。")
