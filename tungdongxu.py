import streamlit as st
import random
import pandas as pd
import time

# 1. Cấu hình giao diện 16:9 và phong cách
st.set_page_config(layout="wide", page_title="Mô phỏng Tung đồng xu - Toán THCS")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #2e7d32; color: white; }
    .author-info { position: fixed; left: 20px; bottom: 20px; font-size: 15px; color: #2c3e50; font-weight: bold; line-height: 1.2; z-index: 100; background: rgba(255,255,255,0.7); padding: 5px; border-radius: 5px; }
    .coin-circle { width: 100px; height: 100px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 40px; font-weight: bold; margin: 10px; border: 4px solid #f1c40f; background: #f39c12; color: white; box-shadow: 2px 2px 10px rgba(0,0,0,0.2); }
    .stat-table { width: 100%; border-collapse: collapse; }
    </style>
    """, unsafe_allow_html=True)

# --- PHẦN GÓC TRÁI (1/4 màn hình) ---
with st.sidebar:
    st.header("⚙️ Cài đặt thực nghiệm")
    
    num_coins = st.radio("Số lượng đồng xu:", [1, 2, 3], horizontal=True)
    
    # Định nghĩa biến cố tùy theo số đồng xu
    if num_coins == 1:
        event_options = {
            "Mặt xuất hiện là Sấp (S)": lambda x: x.count('S') == 1,
            "Mặt xuất hiện là Ngửa (N)": lambda x: x.count('N') == 1
        }
    elif num_coins == 2:
        event_options = {
            "Cả hai mặt đều Sấp (SS)": lambda x: x.count('S') == 2,
            "Cả hai mặt đều Ngửa (NN)": lambda x: x.count('N') == 2,
            "Có ít nhất một mặt Sấp": lambda x: x.count('S') >= 1,
            "Có ít nhất một mặt Ngửa": lambda x: x.count('N') >= 1,
            "Hai mặt xuất hiện khác nhau": lambda x: x[0] != x[1]
        }
    else: # 3 đồng xu
        event_options = {
            "Cả ba mặt đều Sấp (SSS)": lambda x: x.count('S') == 3,
            "Có đúng hai mặt Sấp": lambda x: x.count('S') == 2,
            "Có ít nhất một mặt Ngửa": lambda x: x.count('N') >= 1,
            "Số mặt Sấp nhiều hơn số mặt Ngửa": lambda x: x.count('S') > x.count('N'),
            "Ba mặt đều giống nhau": lambda x: x.count('S') == 3 or x.count('N') == 3,
            "Không có mặt Sấp nào": lambda x: x.count('S') == 0
        }
    
    selected_event = st.selectbox("Lựa chọn biến cố:", list(event_options.keys()))
    trials = st.number_input("Số lần thực nghiệm (tối đa 10.000):", min_value=1, max_value=10000, value=10)
    
    run_btn = st.button("🚀 BẮT ĐẦU TUNG")

# --- CHIA LAYOUT CHÍNH (Trung tâm và Phải) ---
# Tỉ lệ: Sidebar(1/4), Center(3/8), Right(3/8) -> (Tổng phần còn lại là 3/4)
col_center, col_right = st.columns([1, 1])

# Khởi tạo dữ liệu
if 'coin_history' not in st.session_state:
    st.session_state.coin_history = []
    st.session_state.current_result = []

# Xử lý khi bấm nút Tung
if run_btn:
    # Hiệu ứng âm thanh (Tiếng đồng xu rơi)
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/misc/sounds/coin-flip-01.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    
    new_results = []
    for _ in range(trials):
        flip = tuple(random.choice(['S', 'N']) for _ in range(num_coins))
        new_results.append(flip)
    
    st.session_state.coin_history = new_results
    st.session_state.current_result = new_results[-1] # Lấy kết quả cuối cùng để hiển thị hoạt cảnh

# --- PHẦN TRUNG TÂM ---
with col_center:
    st.subheader("🪙 Mô phỏng thực tế")
    
    if st.session_state.current_result:
        # Hiển thị đồng xu
        cols = st.columns(len(st.session_state.current_result))
        for i, res in enumerate(st.session_state.current_result):
            with cols[i]:
                color = "#f39c12" if res == 'S' else "#7f8c8d"
                st.markdown(f'<div class="coin-circle" style="background:{color}">{res}</div>', unsafe_allow_html=True)
        
        st.write(f"**Kết quả lần tung cuối:** {' - '.join(st.session_state.current_result)}")
        
        # Bảng kết quả thực nghiệm
        st.write("### Bảng dữ liệu thực nghiệm")
        df = pd.DataFrame(st.session_state.coin_history, columns=[f"Đồng xu {i+1}" for i in range(num_coins)])
        st.dataframe(df, height=300, use_container_width=True)

# --- PHẦN MÀN HÌNH PHẢI ---
with col_right:
    st.subheader("📊 Phân tích xác suất")
    
    show_sample_space = st.checkbox("Hiện không gian mẫu (Ω)")
    show_prob = st.checkbox("Hiện xác suất biến cố")
    
    if show_sample_space:
        import itertools
        space = list(itertools.product(['S', 'N'], repeat=num_coins))
        space_str = " ; ".join(["".join(item) for item in space])
        st.info(f"**Không gian mẫu ({len(space)} kết quả):**\n\n{space_str}")
    
    if st.session_state.coin_history:
        # Tính toán xác suất thực nghiệm
        logic_func = event_options[selected_event]
        success_count = sum(1 for res in st.session_state.coin_history if logic_func(res))
        exp_prob = success_count / len(st.session_state.coin_history)
        
        if show_prob:
            st.success(f"**Biến cố đang xét:** {selected_event}")
            st.metric("Số lần xảy ra", f"{success_count} / {len(st.session_state.coin_history)}")
            
            # Tính phần trăm cho progress bar
            st.write(f"**Xác suất thực nghiệm: {exp_prob:.2%}**")
            st.progress(exp_prob)
            
            # Giải thích thêm
            st.write(f"Trong {len(st.session_state.coin_history)} lần thực nghiệm, biến cố xảy ra {success_count} lần.")

# --- THÔNG TIN TÁC GIẢ (Góc dưới trái) ---
st.markdown(f"""
    <div class="author-info">
        Giáo viên: Trịnh Thị Như Quỳnh<br>
        Trường THCS Trần Hưng Đạo
    </div>
    """, unsafe_allow_html=True)