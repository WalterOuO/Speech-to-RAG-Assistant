import streamlit as st
import requests
import time
import os

# 設定頁面配置
st.set_page_config(
    page_title="Speech-to-RAG Assistant",
    page_icon="🎙️",
    layout="wide"
)

# 後端 URL 設定：優先使用環境變數，預設 localhost:8002
BACKEND_URL = os.getenv("STREAMLIT_BACKEND_URL", "http://localhost:8002")

def wait_for_backend():
    """輪詢後端狀態，直到系統就緒"""
    holder = st.empty()
    seen_messages = set()

    while True:
        try:
            response = requests.get(f"{BACKEND_URL}/status", timeout=2)
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                ready = data.get("ready", False)

                with holder.container():
                    for msg in messages:
                        if msg not in seen_messages:
                            st.markdown(msg)
                            seen_messages.add(msg)

                if ready:
                    # 稍微延遲讓使用者看到最後一條訊息
                    time.sleep(0.5)
                    holder.empty()
                    return True
            else:
                with holder.container():
                    st.info("等待後端服務回應...")
        except Exception:
            with holder.container():
                st.info("等待後端服務啟動中...")

        time.sleep(1)

def resolve_filename(raw_input):
    """
    檔名匹配邏輯：
    1. 若輸入含副檔名 (.wav, .mp3, .m4a) -> 直接精確比對
    2. 若不含副檔名 -> 依優先序 [wav, mp3, m4a] 嘗試匹配
    """
    raw = raw_input.strip()
    if not raw:
        return []

    ext = os.path.splitext(raw)[1].lower()
    if ext in (".wav", ".mp3", ".m4a"):
        return [raw]

    # 優先順位: wav -> mp3 -> m4a
    return [raw + ".wav", raw + ".mp3", raw + ".m4a"]

def main():
    # 初始化 Session State
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
        st.session_state.last_query = None
        st.session_state.last_answer = None
        st.session_state.last_sources = None

    # 1. 啟動等待流程
    if not st.session_state.initialized:
        if wait_for_backend():
            st.session_state.initialized = True
            st.rerun()
        return

    # --- 正式功能頁面 ---
    st.title("🎙️ Speech-to-RAG Assistant")
    st.markdown("---")

    # 使用兩欄佈局
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("📁 檔案管理")

        # A. 上傳音檔區塊
        with st.container(border=True):
            st.markdown("**上傳音檔**")
            uploaded_file = st.file_uploader(
                "選擇音訊檔 (.wav, .mp3, .m4a)",
                type=["wav", "mp3", "m4a"],
                key="file_uploader"
            )
            if st.button("開始上傳", use_container_width=True):
                if uploaded_file:
                    try:
                        # 準備檔案傳送
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        res = requests.post(f"{BACKEND_URL}/speech/upload", files=files)
                        if res.status_code == 201:
                            st.success(f"上傳成功！檔名: {res.json()['filename']}")
                        else:
                            st.error(f"上傳失敗: {res.text}")
                    except Exception as e:
                        st.error(f"連線錯誤: {e}")
                else:
                    st.warning("請先選擇檔案")

        st.markdown("<br>", unsafe_allow_html=True)

        # B. 調閱音檔狀態區塊
        with st.container(border=True):
            st.markdown("**調閱上傳狀態**")
            # 使用 key 以便內容在 Enter 後保留
            status_query = st.text_input("輸入檔名 (可不含副檔名)", key="status_input")

            if status_query:
                # 當使用者按下 Enter 時，這裡會觸發 (Streamlit 機制)
                candidates = resolve_filename(status_query)
                found = False
                for cand in candidates:
                    try:
                        res = requests.get(f"{BACKEND_URL}/speech/status/{cand}")
                        if res.status_code == 200:
                            data = res.json()
                            st.success(f"檔案: `{data['filename']}`\n狀態: **{data['status']}**")
                            found = True
                            break
                    except Exception:
                        continue
                if not found:
                    st.error(f"找不到檔名為 `{status_query}` 的相關紀錄")

    with col2:
        st.subheader("💬 RAG 語意問答")

        # C. 問 RAG 系統問題區塊
        with st.container(border=True):
            # 輸入框：按 Enter 送出，內容保留
            question = st.text_input("請輸入您想詢問的問題", key="question_input")

            # 偵測是否為新問題送出 (避免 rerun 時重複呼叫 API)
            if question and question != st.session_state.get("last_query"):
                with st.spinner("思考中..."):
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/rag/ask",
                            json={"question": question}
                        )
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.last_query = question
                            st.session_state.last_answer = data.get("answer")
                            st.session_state.last_sources = data.get("sources", [])
                        else:
                            st.error(f"後端錯誤: {res.text}")
                    except Exception as e:
                        st.error(f"連線失敗: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # D. 回答生成區域
        if st.session_state.last_answer:
            with st.container(border=True):
                st.markdown("**Answer**")
                st.markdown(st.session_state.last_answer)

                if st.session_state.last_sources:
                    st.markdown("---")
                    with st.expander("🔍 查看資料來源"):
                        for src in st.session_state.last_sources:
                            st.markdown(f"- 檔案: `{src['filename']}` (Chunk {src['chunk']})")

if __name__ == "__main__":
    main()
