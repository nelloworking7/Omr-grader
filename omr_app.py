import streamlit as st
import numpy as np
import cv2

# 예시 정답 (1번부터 10번까지, 각 문제에 대한 정답은 A~D 중 하나)
ANSWER_KEY = ['B', 'C', 'A', 'D', 'B', 'A', 'C', 'D', 'A', 'B']

CHOICE_LABELS = ['A', 'B', 'C', 'D']

st.title("📷 OMR 자동 채점기")
st.markdown("iPad로 사진을 찍어서 업로드하면 자동으로 채점해줄게요!")

uploaded_file = st.file_uploader("🖼️ OMR 사진 업로드", type=["jpg", "jpeg", "png"])

def preprocess_image(image):
    # 이미지 흑백 변환 및 이진화
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    return thresh

def detect_answers(image, num_questions=10, num_choices=4):
    """
    아주 간단한 그리드 기반 OMR 감지 함수 (완전한 건 아님. 예시용)
    각 번호 영역이 이미지에 고르게 분포되어 있다고 가정
    """
    height, width = image.shape
    box_height = height // num_questions
    box_width = width // num_choices

    selected_choices = []

    for q in range(num_questions):
        row_top = q * box_height
        row_bottom = (q + 1) * box_height
        row_choices = []

        max_black = 0
        selected_idx = -1

        for c in range(num_choices):
            col_left = c * box_width
            col_right = (c + 1) * box_width
            cell = image[row_top:row_bottom, col_left:col_right]

            black_pixels = cv2.countNonZero(cell)
            row_choices.append(black_pixels)

            if black_pixels > max_black:
                max_black = black_pixels
                selected_idx = c

        selected_choices.append(CHOICE_LABELS[selected_idx])

    return selected_choices

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    st.image(image, caption="업로드한 OMR", use_column_width=True)

    # 전처리 및 선택지 감지
    processed = preprocess_image(image)
    detected = detect_answers(processed)

    # 채점
    score = 0
    for user, answer in zip(detected, ANSWER_KEY):
        if user == answer:
            score += 1

    st.subheader("📊 채점 결과")
    st.write(f"총 점수: **{score} / {len(ANSWER_KEY)}**")
    st.write("답안 비교:")

    for idx, (u, a) in enumerate(zip(detected, ANSWER_KEY), 1):
        result = "✅" if u == a else "❌"
        st.write(f"{idx}. 너의 답: **{u}** / 정답: **{a}** {result}")