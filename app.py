import streamlit as st
import google.generativeai as genai
import tempfile
import time

# 1. APIキーの設定
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# 【解決策】使えるモデルを自動で検索してセットする関数
def get_available_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # flashがあれば優先、なければ最初に見つかったものを使う
            if 'gemini-1.5-flash' in m.name:
                return m.name
    return 'models/gemini-1.5-flash' # 万が一見つからない場合の予備

selected_model_name = get_available_model()
model = genai.GenerativeModel(selected_model_name)

st.set_page_config(page_title="iPad専用AI家庭教師", layout="wide")
st.title("📖 iPad専用AI家庭教師")
st.info(f"使用中のモデル: {selected_model_name}") # 確認用

uploaded_files = st.file_uploader("教科書やプリント(PDF)を選択", accept_multiple_files=True, type=['pdf'])

if uploaded_files:
    gemini_files = []
    with st.spinner('ファイルを解析中...'):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                gen_file = genai.upload_file(path=tmp.name, display_name=uploaded_file.name)
                
                while gen_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gen_file = genai.get_file(gen_file.name)
                
                gemini_files.append(gen_file)

    st.success(f"教材の読み込みが完了しました。")

    mode = st.radio("学習メニュー:", ["教科書の解説を聞く", "プリントからランダム出題"])
    user_input = st.text_input("質問や指示を入力してください:")

    if st.button("実行"):
        if not user_input:
            st.warning("質問を入力してください。")
        else:
            content_to_send = gemini_files + [
                f"あなたは教育のプロです。現在は「{mode}」モードです。",
                "提供された教材に基づいてのみ回答してください。",
                user_input
            ]
            
            with st.spinner('AIが回答を生成中...'):
                try:
                    response = model.generate_content(content_to_send)
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
