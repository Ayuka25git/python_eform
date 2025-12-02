"""
設定画面モジュール
入力項目を動的に設定できる画面
"""
import streamlit as st
import json
import os

CONFIG_FILE = "form_config.json"

def load_form_config():
    """フォーム設定を読み込む"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_form_config(config):
    """フォーム設定を保存する"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def render_config_page():
    """設定画面をレンダリング"""
    st.title("🔧 入力フォーム設定")
    st.markdown("---")

    # セッション状態の初期化
    if "form_fields" not in st.session_state:
        st.session_state.form_fields = load_form_config()

    st.subheader("項目一覧")

    # 既存項目の表示と編集
    if st.session_state.form_fields:
        for idx, field in enumerate(st.session_state.form_fields):
            with st.expander(f"項目 {idx + 1}: {field.get('label_name', '未設定')}", expanded=False):
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    field["label_name"] = st.text_input(
                        "項目名",
                        value=field.get("label_name", ""),
                        key=f"label_{idx}"
                    )

                with col2:
                    field["data_type"] = st.selectbox(
                        "データ型",
                        options=["文字列", "数値", "日付"],
                        index=["文字列", "数値", "日付"].index(field.get("data_type", "文字列")),
                        key=f"type_{idx}"
                    )

                with col3:
                    field["unit"] = st.text_input(
                        "単位",
                        value=field.get("unit", ""),
                        key=f"unit_{idx}",
                        placeholder="例: mm, kg"
                    )

                col4, col5, col6 = st.columns([2, 2, 1])

                with col4:
                    field["is_required"] = st.checkbox(
                        "必須項目",
                        value=field.get("is_required", False),
                        key=f"required_{idx}"
                    )

                with col5:
                    field["display_order"] = st.number_input(
                        "表示順",
                        min_value=1,
                        value=field.get("display_order", idx + 1),
                        key=f"order_{idx}"
                    )

                with col6:
                    if st.button("🗑️ 削除", key=f"delete_{idx}"):
                        st.session_state.form_fields.pop(idx)
                        st.rerun()
    else:
        st.info("項目が登録されていません。下の「新規項目追加」から追加してください。")

    st.markdown("---")

    # 新規項目追加エリア
    st.subheader("📝 新規項目追加")

    with st.form("add_field_form"):
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            new_label = st.text_input("項目名", placeholder="例: 電圧、外観、寸法")

        with col2:
            new_type = st.selectbox("データ型", options=["文字列", "数値", "日付"])

        with col3:
            new_unit = st.text_input("単位", placeholder="例: V, mm")

        col4, col5 = st.columns(2)

        with col4:
            new_required = st.checkbox("必須項目")

        with col5:
            new_order = st.number_input(
                "表示順",
                min_value=1,
                value=len(st.session_state.form_fields) + 1
            )

        submitted = st.form_submit_button("➕ 追加", use_container_width=True)

        if submitted:
            if new_label.strip():
                new_field = {
                    "label_name": new_label.strip(),
                    "data_type": new_type,
                    "unit": new_unit.strip(),
                    "is_required": new_required,
                    "display_order": new_order
                }
                st.session_state.form_fields.append(new_field)
                st.success(f"項目「{new_label}」を追加しました!")
                st.rerun()
            else:
                st.error("項目名を入力してください。")

    st.markdown("---")

    # 保存ボタン
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 設定を保存", use_container_width=True, type="primary"):
            # 表示順でソート
            sorted_fields = sorted(
                st.session_state.form_fields,
                key=lambda x: x.get("display_order", 0)
            )
            save_form_config(sorted_fields)
            st.success("設定を保存しました!")

    with col2:
        if st.button("🔄 設定をリセット", use_container_width=True):
            st.session_state.form_fields = []
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            st.success("設定をリセットしました!")
            st.rerun()

    # 現在の設定を表示(デバッグ用)
    with st.expander("📋 現在の設定内容(JSON)"):
        st.json(st.session_state.form_fields)
