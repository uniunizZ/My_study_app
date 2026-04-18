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

# モデルの準備
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. ファイルアップロード（1つに限定して負荷を下げます）
uploaded_file = st.file_uploader("教科書やプリント(PDF)を選択", type=['pdf'])

# セッションで管理
if 'gemini_file' not in st.session_state:
    st.session_state.gemini_file = None

if uploaded_file and st.session_state.gemini_file is None:
    with st.spinner('重いファイルを解析中...数分かかる場合があります'):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            gen_file = genai.upload_file(path=tmp.name)
            # 完了まで待機
            while gen_file.state.name == "PROCESSING":
                time.sleep(5)
                gen_file = genai.get_file(gen_file.name)
            st.session_state.gemini_file = gen_file
    st.success("教材の読み込み完了！")

mode = st.radio("メニュー:", ["教科書の解説を聞く", "ランダム出題"])
user_input = st.text_input("質問を入力:", value="リボソームについて教えて")

if st.button("実行"):
    if not user_input:
        st.warning("質問を入力してください。")
    elif not st.session_state.gemini_file:
        st.error("先にファイルをアップロードしてください。")
    else:
        with st.spinner('AIが回答を生成中...'):
            try:
                # 【重要】chat形式にすることで、巨大なファイルを何度も送る負荷を避けます
                chat = model.start_chat(history=[
                    {"role": "user", "parts": [st.session_state.gemini_file]},
                    {"role": "model", "parts": ["教材を確認しました。看護のプロとして解説します。"]}
                ])
                
                prompt = f"現在は「{mode}」モードです。教材に基づいて日本語で答えてください：{user_input}"
                response = chat.send_message(prompt)
                
                st.markdown("---")
                st.write(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.info("ファイルが大きすぎる場合は、必要な数ページだけをPDFにして試してみてください。")
