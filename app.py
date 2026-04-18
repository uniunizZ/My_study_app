import streamlit as st
import google.generativeai as genai
import tempfile
import time

# APIキーの設定
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

st.set_page_config(page_title="iPad専用AI家庭教師", layout="wide")
st.title("📖 iPad専用AI家庭教師")

uploaded_files = st.file_uploader("教科書やプリント(PDF)を選択", accept_multiple_files=True, type=['pdf'])

if uploaded_files:
    gemini_files = []
    with st.spinner('ファイルを解析中...'):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                gen_file = genai.upload_file(path=tmp.name, display_name=uploaded_file.name)
                
                # 重要：ファイルが「有効」になるまで待機する処理を追加
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
            prompt = [
                f"あなたは教育のプロです。現在は「{mode}」モードです。",
                "提供された教材の内容に基づいてのみ回答してください。",
                "解説は教科書に沿って分かりやすく、問題作成は提供された問題データからランダムに行ってください。",
                user_input
            ]
            
            with st.spinner('AIが回答を生成中...'):
                try:
                    # ファイルとプロンプトを送信
                    response = model.generate_content(gemini_files + prompt)
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
