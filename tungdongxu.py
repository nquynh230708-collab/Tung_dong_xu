import numpy as np
import streamlit as st
import random
import pandas as pd
import itertools

# 1. Thiết lập tỉ lệ 16:9 và tiêu đề trang
st.set_page_config(layout="wide", page_title="Mô phỏng Tung đồng xu - GV Trịnh Thị Như Quỳnh")

# 2. CSS Đặc biệt cho Chrome: Cố định thông tin tác giả
st.markdown("""
    <style>
    /* Thanh thông tin tác giả phía trên cùng */
    .author-header {
        background-color: #1e4620;
        color: #ffffff;
        padding: 10px 25px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 8px solid #d4a017;
    }
    /* Thanh thông tin tác giả phía dưới cùng cố định */
    .author-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f1f3f4;
        color: #202124;
        text-align: left;
        padding: 10px 30px;
        font-size: 16px;
        border-top: 2px solid #2e7d32;
        z-index: 100;
        font-weight: bold;
    }
    /* Tăng kích thước emoji đồng xu */
    .coin-display {
        font-size: 80px;
        text-align: center;
    }
    </style>
    
    <div class="author-header">
        <h3 style='margin:0;'>MÔ PHỎNG XÁC SUẤT TUNG ĐỒNG XU</h3>
        <p style='margin:0;'>Giáo viên: Trịnh Thị Như Quỳnh — Trường THCS Trần Hưng Đạo</p>
    </div>
    
    <div class="author-footer">
        Tác giả: GV. Trịnh Thị Như Quỳnh - Trường THCS Trần Hưng Đạo
    </div>
    """, unsafe_allow_html=True)

# --- PHẦN GÓC TRÁI (1/4 Màn hình) ---
with st.sidebar:
    st.header("⚙️ Cài đặt")
    num_coins = st.radio("Số lượng đồng xu:", [1, 2, 3], horizontal=True)
    
    # Danh sách ít nhất 5-10 biến cố tùy chọn
    if num_coins == 1:
        events = {
            "Mặt xuất hiện là mặt sấp (S)": lambda x: x.count('S') == 1,
            "Mặt xuất hiện là mặt ngửa (N)": lambda x: x.count('N') == 1
        }
    elif num_coins == 2:
        events = {
            "Có ít nhất một mặt sấp (S)": lambda x: x.count('S') >= 1,
            "Mặt xuất hiện có hai mặt giống nhau": lambda x: x[0] == x[1],
            "Cả hai mặt đều là ngửa (N)": lambda x: x.count('N') == 2,
            "Có đúng một mặt sấp (S)": lambda x: x.count('S') == 1,
            "Hai mặt xuất hiện khác nhau": lambda x: x[0] != x[1]
        }
    else:
        events = {
            "Cả ba mặt đều sấp (S)": lambda x: x.count('S') == 3,
            "Có ít nhất một mặt sấp (S)": lambda x: x.count('S') >= 1,
            "Số mặt sấp nhiều hơn mặt ngửa": lambda x: x.count('S') > x.count('N'),
            "Ba mặt xuất hiện giống hệt nhau": lambda x: x.count('S') == 3 or x.count('N') == 3,
            "Không có mặt sấp nào xuất hiện": lambda x: x.count('S') == 0
        }

    selected_event_name = st.selectbox("Lựa chọn biến cố:", list(events.keys()))
    trials = st.number_input("Số lần thực nghiệm (n):", min_value=1, max_value=10000, value=100)
    run_btn = st.button("🚀 BẮT ĐẦU THỰC NGHIỆM")

# --- LAYOUT CHÍNH ---
col_center, col_right = st.columns([1, 1])

if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.last_res = []

if run_btn:
    # Âm thanh đồng xu cho Chrome
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/misc/sounds/coin-flip-01.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    
    # Thực hiện mô phỏng
    results = [tuple(random.choice(['S', 'N']) for _ in range(num_coins)) for _ in range(trials)]
    st.session_state.history = results
    st.session_state.last_res = results[-1]

# --- MÀN HÌNH TRUNG TÂM (3/8) ---
with col_center:
    st.subheader("📺 Mô phỏng hoạt động")
    if st.session_state.last_res:
        # Hiển thị kết quả cuối bằng hình ảnh/emoji lớn
        coin_html = "".join([f"<span style='margin:10px;'>🪙 {r}</span>" for r in st.session_state.last_res])
        st.markdown(f"<div class='coin-display'>{coin_html}</div>", unsafe_allow_html=True)
        
        st.write("### 📊 Bảng dữ liệu thực nghiệm")
        df = pd.DataFrame(st.session_state.history, columns=[f"Đồng xu {i+1}" for i in range(num_coins)])
        st.dataframe(df, use_container_width=True, height=350)

# --- MÀN HÌNH BÊN PHẢI (3/8) ---
with col_right:
    st.subheader("📝 Kết quả & Phân tích")
    show_omega = st.checkbox("Hiện không gian mẫu (Ω)")
    show_prob = st.checkbox("Hiện xác suất lí thuyết & thực nghiệm")
    
    if show_omega:
        omega = list(itertools.product(['S', 'N'], repeat=num_coins))
        st.info(f"**Không gian mẫu Ω:** {set([''.join(i) for i in omega])}")

    if st.session_state.history and show_prob:
        # Tính toán xác suất
        success_count = sum(1 for r in st.session_state.history if events[selected_event_name](r))
        p_thuc_nghiem = success_count / trials
        
        omega = list(itertools.product(['S', 'N'], repeat=num_coins))
        success_lt = sum(1 for r in omega if events[selected_event_name](r))
        p_ly_thuyet = success_lt / len(omega)
        
        st.metric("Xác suất thực nghiệm (P_tn)", f"{p_thuc_nghiem:.4f}")
        st.metric("Xác suất lý thuyết (P_lt)", f"{p_ly_thuyet:.4f}")
        
        # Câu kết luận sư phạm
        st.markdown("---")
        st.success(f"**Kết luận:** Qua {trials} lần thử, ta thấy xác suất thực nghiệm ({p_thuc_nghiem:.4f}) xấp xỉ bằng xác suất lý thuyết ({p_ly_thuyet:.4f}). "
                   "Khi số lần thực nghiệm càng lớn, sự sai khác này càng nhỏ.")
                         
       
    
