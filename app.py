import streamlit as st
import google.generativeai as genai
import tempfile
import time

# 1. APIキーの設定
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("APIキーの設定を確認してください。")
    st.stop()

st.set_page_config(page_title="iPad専用AI家庭教師", layout="wide")
st.title("📖 iPad専用AI家庭教師")

# 現在使えるモデルを自動選択
@st.cache_resource
def get_best_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['flash', 'pro']:
            for m_name in models:
                if target in m_name: return m_name
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

selected_model = get_best_model()
st.caption(f"システム稼働中（接続先: {selected_model}）")
model = genai.GenerativeModel(selected_model)

uploaded_files = st.file_uploader("教科書やプリント(PDF)を選択", accept_multiple_files=True, type=['pdf'])

# セッション状態でファイルを保持
if 'gemini_files' not in st.session_state:
    st.session_state.gemini_files = []

if uploaded_files and not st.session_state.gemini_files:
    with st.spinner('ファイルを解析中...'):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                gen_file = genai.upload_file(path=tmp.name, display_name=uploaded_file.name)
                while gen_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gen_file = genai.get_file(gen_file.name)
                st.session_state.gemini_files.append(gen_file)
    st.success("教材の読み込み完了！")

mode = st.radio("メニュー:", ["教科書の解説を聞く", "ランダム出題"])
user_input = st.text_input("質問を入力:", value="リボソームについて教えて")

if st.button("実行"):
    if not user_input:
        st.warning("質問を入力してください。")
    elif not st.session_state.gemini_files:
        st.error("先にファイルをアップロードしてください。")
    else:
        with st.spinner('AIが回答を生成中...'):
            try:
                # 【修正の肝】最新のSDKに合わせた最も安全なリスト形式
                prompt = f"あなたは看護教育のプロです。現在は「{mode}」モードです。提供された教材に基づいて日本語で詳しく答えてください。\n質問: {user_input}"
                
                # ファイルとテキストを一つのリストにまとめる
                request_content = []
                for f in st.session_state.gemini_files:
                    request_content.append(f)
                request_content.append(prompt)
                
                response = model.generate_content(request_content)
                st.markdown("---")
                st.write(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
