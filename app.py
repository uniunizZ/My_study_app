import streamlit as st
import google.generativeai as genai
import tempfile
import time

# 1. APIキーの設定
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# 【修正ポイント】モデルの指定方法を最もシンプルな形に変更
# 名前から 'models/' を消し、一番安定している名前を使います
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="iPad専用AI家庭教師", layout="wide")
st.title("📖 iPad専用AI家庭教師")

uploaded_files = st.file_uploader("教科書やプリント(PDF)を選択", accept_multiple_files=True, type=['pdf'])

if uploaded_files:
    gemini_files = []
    with st.spinner('ファイルを解析中...'):
        for uploaded_file in uploaded_files:
            # 既にアップロード済みのファイルを再利用しないよう処理
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                gen_file = genai.upload_file(path=tmp.name, display_name=uploaded_file.name)
                
                # ファイルが使えるようになるまで待機
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
            # プロンプトとファイルを組み合わせて送信
            # ここを一番シンプルなリスト形式にします
            content_to_send = []
            for f in gemini_files:
                content_to_send.append(f)
            content_to_send.append(f"あなたは教育のプロです。現在は「{mode}」モードです。")
            content_to_send.append("提供された教材に基づいてのみ回答してください。")
            content_to_send.append(user_input)
            
            with st.spinner('AIが回答を生成中...'):
                try:
                    response = model.generate_content(content_to_send)
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    st.info("APIキーが正しいか、Google AI Studioで再確認してみてください。")
