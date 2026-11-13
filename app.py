import streamlit as st
from google import genai

# 1. ページ基本設定（ブラウザのタブ名とアイコン）
st.set_page_config(page_title="游海亭 みやじま クチコミ返信ツール", page_icon="🌊")

# ------------------------------------------------------------------
# 洗練されたデザインにするためのカスタムCSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #F8F9FA;
        font-family: 'Yu Gothic', '游ゴシック', YuGothic, '游ゴシック体', sans-serif;
    }
    h1 {
        color: #2C3E50;
        font-weight: 600;
        font-size: 26px !important;
        padding-bottom: 10px;
        border-bottom: 2px solid #E0E0E0;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[role="radiogroup"] {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #2C3E50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1A252F;
        color: white;
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------------

# 画面のタイトルと説明文
st.title("🌊 游海亭 みやじま 専用クチコミ返信ツール")
st.caption("楽天トラベルなどのクチコミを貼り付けると、当館の情報に基づいた返信文を自動生成します。")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 3. 入力フォーム
review_text = st.text_area(
    "お客様からのクチコミ本文：", 
    height=150, 
    placeholder="例：部屋からの夕日がとても綺麗でした。夕食の海鮮も新鮮で美味しかったです。"
)

tone = st.radio(
    "返信の方向性：", 
    ["標準（丁寧・誠実）", "感謝強調（高評価向け）", "お詫び・改善強調（低評価向け）"], 
    horizontal=True
)

# 4. 生成ボタン押下時の処理
if st.button("返信文を生成する", type="primary"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif not review_text:
        st.warning("クチコミ本文を入力してください。")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # クチコミの文字数を判定して指示を切り替える
            review_length = len(review_text)
            if review_length <= 700:
                length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字です。返信文はクチコミと同程度のボリューム（約{review_length}文字程度）になるよう、当館の魅力や感謝の言葉を織り交ぜて作成してください。"
            else:
                length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字と長文のため、簡潔かつ丁寧に要点をまとめた返信文を作成してください（無理に同じ長さに伸ばす必要はありません）。"

            # ★【重要】施設情報は一般的な内容を入れています。必要に応じて修正してください。
            system_prompt = f"""
あなたは「游海亭 みやじま」の優秀なWeb担当者です。
入力されたお客様からのクチコミに対し、以下の【游海亭 みやじまの基本情報】を踏まえて適切な返信文を作成してください。

【游海亭 みやじまの基本情報】
立地： 山形県・湯野浜温泉。目の前に広がる日本海の雄大な景色と、「日本の夕陽百選」にも選ばれた絶景の夕日が最大の強みです。
お風呂： 日本海を見渡す展望大浴場や露天風呂を完備。波の音をBGMに、心身ともにリフレッシュできる湯野浜の湯を提供しています。
食事： 庄内浜で水揚げされた新鮮な海の幸や、地元の旬の食材をふんだんに使用したこだわりの会席料理を提供します。
客室： 海の景色を存分に楽しめる寛ぎの和空間を提供し、非日常のゆったりとした時間を演出します。
接客方針： 美しい景色と美味しいお食事を心ゆくまで楽しんでいただけるよう、付かず離れずの心地よく温かいおもてなしを心がけます。
クレーム対応方針：
【施設・設備の古さ等】歴史をご理解いただきつつ、日々の清掃とメンテナンスの徹底をお約束する。
【食事やサービスの不備】誠心誠意お詫びし、スタッフ間での共有と具体的な改善姿勢を示す。

【返信作成ルール】
1. 選択されたトーン設定: {tone}
2. クチコミ内容を分析し、お褒めの言葉には感謝を、ご指摘やクレームには言い訳をせず誠実な謝罪と改善姿勢を示してください。
3. 宿泊予約サイトにふさわしい丁寧でプロフェッショナルな「です・ます調」で作成してください。
4. 前置きや解説は含めず、そのまま管理画面にコピペできる返信文章のみを出力してください。{length_rule}
5. 返信の最後には必ず、改行して「湯野浜温泉 游海亭 みやじま」という署名（記名）を入れてください。
"""

            with st.spinner("当館のナレッジを参照して返信文を作成中..."):
                response_stream = client.models.generate_content_stream(
                    model='gemini-3.5-flash',
                    contents=[system_prompt, f"クチコミ本文:\n{review_text}"]
                )
                
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.empty()

            st.success("作成が完了しました！")
            st.text_area("生成された返信文（枠内をクリックし、すべて選択してコピーしてください）", full_response, height=300)

        except Exception as e:
            error_msg = str(e).lower()
            if "503" in error_msg or "high demand" in error_msg:
                st.error("⚠️ 現在、AIのサーバーが混み合っています。数秒〜1分ほど待ってから、もう一度ボタンを押してください。")
            elif "429" in error_msg or "quota" in error_msg:
                st.error("⚠️ 短時間の利用制限にかかりました。1分ほど待ってから再度お試しください。")
            else:
                st.error(f"⚠️ エラーが発生しました。少し時間をおいてやり直してください。（詳細: {e}）")
