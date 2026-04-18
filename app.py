import streamlit as st
import google.generativeai as genai
import tempfile

# 1. APIキーの設定（StreamlitのSecrets機能を使います）
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

st.set_page_config(page_title="iPad専用AI家庭教師", layout="wide")
st.title("📖 iPad専用AI家庭教師")

# 2. 教科書・プリントのアップロード
uploaded_files = st.file_uploader("教科書やプリント(PDF)を選択", accept_multiple_files=True, type=['pdf'])

if uploaded_files:
    # PDFをGeminiに認識させる
    gemini_files = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            gen_file = genai.upload_file(path=tmp.name, display_name=uploaded_file.name)
            gemini_files.append(gen_file)

    st.success(f"教材の読み込みが完了しました。")

    # 3. モード選択と実行
    mode = st.radio("学習メニュー:", ["教科書の解説を聞く", "プリントからランダム出題"])
    user_input = st.text_input("質問や指示を入力してください:")

    if st.button("実行"):
        # 教育に特化した指示（プロンプト）
        prompt = [
            f"あなたは教育のプロです。現在は「{mode}」モードです。",
            "常に提供された教材に基づいて回答してください。",
            "解説は分かりやすく、問題作成はランダムに行ってください。",
            user_input
        ]
        
        with st.spinner('AIが回答を生成中...'):
            response = model.generate_content(gemini_files + prompt)
            st.markdown("---")
            st.markdown(response.text)
