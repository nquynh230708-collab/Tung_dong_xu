import numpy as np
import streamlit as st
import random
import pandas as pd
import time
import itertools

# 1. Cấu hình tỉ lệ màn hình 16:9
st.set_page_config(layout="wide", page_title="Mô phỏng Tung đồng xu - GV Trịnh Thị Như Quỳnh")

# 2. CSS để tạo giao diện chuyên nghiệp và ghim tên tác giả
st.markdown("""
    <style>
    /* Ghim thông tin tác giả ở góc dưới bên trái */
    .author-footer {
        position: fixed;
        left: 20px;
        bottom: 20px;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-left: 5px solid #2e7d32;
        border-radius: 5px;
        z-index: 1000;
        font-family: 'Helvetica', sans-serif;
    }
    .coin-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 150px;
    }
    .stButton>button {
        background-color: #d4a017;
        color: white;
        height: 3em;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Link hình ảnh đồng xu 3D (Quỳnh thay bằng link raw trên GitHub của mình nhé)
# Ví dụ: url_s = "https://raw.githubusercontent.com/user/repo/main/sap.png"
url_s = "https://img.icons8.com/papercut/200/gold-pot.png" # Link minh họa mặt Sấp
url_n = "https://img.icons8.com/papercut/200/silver-medal.png" # Link minh họa mặt Ngửa

# --- PHẦN GÓC TRÁI (1/4) ---
with st.sidebar:
    st.header("⚙️ THIẾT LẬP")
    num_coins = st.radio("Số lượng đồng xu:", [1, 2, 3], horizontal=True)
    
    # Danh sách biến cố
    if num_coins == 1:
        events = {"Mặt xuất hiện là mặt sấp (S)": lambda x: x.count('S') == 1,
                  "Mặt xuất hiện là mặt ngửa (N)": lambda x: x.count('N') == 1}
    elif num_coins == 2:
        events = {"Có ít nhất một mặt sấp (S)": lambda x: x.count('S') >= 1,
                  "Cả hai mặt đều ngửa (N)": lambda x: x.count('N') == 2,
                  "Hai mặt giống nhau": lambda x: x[0] == x[1],
                  "Hai mặt khác nhau": lambda x: x[0] != x[1],
                  "Có đúng một mặt sấp (S)": lambda x: x.count('S') == 1}
    else:
        events = {"Cả ba mặt đều sấp (S)": lambda x: x.count('S') == 3,
                  "Có ít nhất một mặt sấp (S)": lambda x: x.count('S') >= 1,
                  "Số mặt sấp nhiều hơn mặt ngửa": lambda x: x.count('S') > x.count('N'),
                  "Có đúng hai mặt ngửa (N)": lambda x: x.count('N') == 2,
                  "Ba mặt như nhau": lambda x: x.count('S') == 3 or x.count('N') == 3}

    selected_event_name = st.selectbox("Lựa chọn biến cố:", list(events.keys()))
    trials = st.number_input("Số lần thực nghiệm:", min_value=1, max_value=10000, value=100)
    
    run_btn = st.button("🎲 TUNG ĐỒNG XU")

# --- CHIA LAYOUT CHÍNH ---
col_center, col_right = st.columns([1, 1])

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.last_result = []

if run_btn:
    # Hiệu ứng âm thanh
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/misc/sounds/coin-flip-01.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    
    current_batch = []
    for _ in range(trials):
        res = tuple(random.choice(['S', 'N']) for _ in range(num_coins))
        current_batch.append(res)
    
    st.session_state.history = current_batch
    st.session_state.last_result = current_batch[-1]

# --- PHẦN TRUNG TÂM (3/8) ---
with col_center:
    st.subheader("📺 Mô phỏng 3D")
    if st.session_state.last_result:
        cols = st.columns(num_coins)
        for i, r in enumerate(st.session_state.last_result):
            with cols[i]:
                img = url_s if r == 'S' else url_n
                st.image(img, caption=f"Đồng xu {i+1}: {r}")
        
        st.write("### 📋 Bảng kết quả chi tiết")
        df = pd.DataFrame(st.session_state.history, columns=[f"Đồng xu {i+1}" for i in range(num_coins)])
        st.dataframe(df, use_container_width=True, height=300)

# --- PHẦN BÊN PHẢI (3/8) ---
with col_right:
    st.subheader("📊 Kết quả Xác suất")
    show_omega = st.checkbox("Hiện không gian mẫu (Ω)")
    show_logic = st.checkbox("Hiện so sánh xác suất")
    
    if show_omega:
        omega = list(itertools.product(['S', 'N'], repeat=num_coins))
        st.code(f"Ω = {set([''.join(i) for i in omega])}")

    if st.session_state.history and show_logic:
        # Tính toán
        success = sum(1 for r in st.session_state.history if events[selected_event_name](r))
        p_thuc_nghiem = success / trials
        
        omega = list(itertools.product(['S', 'N'], repeat=num_coins))
        success_lt = sum(1 for r in omega if events[selected_event_name](r))
        p_ly_thuyet = success_lt / len(omega)
        
        st.metric("Xác suất thực nghiệm", f"{p_thuc_nghiem:.4f}")
        st.metric("Xác suất lý thuyết", f"{p_ly_thuyet:.4f}")
        
        st.info(f"**Kết luận:** Khi số lần thực nghiệm càng lớn (n={trials}), xác suất thực nghiệm ({p_thuc_nghiem:.4f}) sẽ càng tiến gần đến xác suất lý thuyết ({p_ly_thuyet:.4f}).")

# --- HIỂN THỊ TÊN TÁC GIẢ (Góc dưới cùng bên trái) ---
st.markdown(f"""
    <div class="author-footer">
        <b>Giáo viên:</b> Trịnh Thị Như Quỳnh<br>
        <b>Trường:</b> THCS Trần Hưng Đạo
    </div>
    """, unsafe_allow_html=True)
