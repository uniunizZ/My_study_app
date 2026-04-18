import streamlit as st
import google.generativeai as genai
import tempfile
import time

# 1. APIキーの設定
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("Secretsの設定でAPIキーが見つかりません。")
    st.stop()

st.set_page_config(page_title="iPad専用AI家庭教師", layout="wide")
st.title("📖 iPad専用AI家庭教師")

# 2. 【最重要】現在使えるモデルを強制的にリストアップして表示する
@st.cache_resource
def get_best_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # gemini-1.5-flash または gemini-1.5-pro を優先的に探す
        for target in ['flash', 'pro']:
            for m_name in models:
                if target in m_name:
                    return m_name
        return models[0] if models else "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

selected_model = get_best_model()
st.caption(f"システム稼働中（接続先: {selected_model}）")
model = genai.GenerativeModel(selected_model)

uploaded_files = st.file_uploader("教科書やプリント(PDF)を選択", accept_multiple_files=True, type=['pdf'])

if uploaded_files:
    gemini_files = []
    with st.spinner('ファイルを解析中...'):
        for uploaded_file in uploaded_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    gen_file = genai.upload_file(path=tmp.name, display_name=uploaded_file.name)
                    
                    while gen_file.state.name == "PROCESSING":
                        time.sleep(2)
                        gen_file = genai.get_file(gen_file.name)
                    
                    gemini_files.append(gen_file)
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")

    st.success("教材の読み込み完了！質問をどうぞ。")

    mode = st.radio("メニュー:", ["教科書の解説を聞く", "ランダム出題"])
    user_input = st.text_input("例：リボソームの役割を教えて")

    if st.button("実行"):
        if not user_input:
            st.warning("質問を入力してください。")
        else:
            with st.spinner('AIが回答を生成中...'):
                try:
                    # シンプルなメッセージ形式で送信
                    messages = []
                    for f in gemini_files:
                        messages.append(f)
                    messages.append(f"あなたは看護教育のプロです。現在は「{mode}」モードです。教材に基づいて日本語で詳しく答えてください。")
                    messages.append(user_input)
                    
                    response = model.generate_content(messages)
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    st.info("一度『Manage app』から『Reboot app』を試してみてください。")
