import streamlit as st
import random
import copy
import time

st.set_page_config(page_title="ナンプレ", layout="centered")
st.title("🧩 ナンプレ（数独）")

SIZE = 9

# -----------------------
# CSS（ダークモード + 枠線）
# -----------------------
st.markdown("""
<style>
html, body, .block-container {
    background-color: #121212 !important;
    color: #ffffff !important;
}

input[type="number"] {
    background-color: #1e1e1e !important;
    color: #ffffff !important;
    text-align: center;
    font-size: 22px;
    height: 45px;
}

.fixed-cell {
    border: 1px solid #666;
    background-color: #2a2a2a;
    color: #ffffff;
    height: 45px;
    line-height: 45px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}

.hr {
    border: 3px solid #ffffff;
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 数独ロジック
# -----------------------
def is_valid(board, r, c, num):
    if num in board[r]:
        return False

    for i in range(SIZE):
        if board[i][c] == num:
            return False

    br = (r // 3) * 3
    bc = (c // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[br + i][bc + j] == num:
                return False

    return True


def solve(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True


def generate_puzzle():
    board = [[0]*SIZE for _ in range(SIZE)]
    solve(board)

    puzzle = copy.deepcopy(board)

    remove = 45
    while remove > 0:
        r = random.randint(0, 8)
        c = random.randint(0, 8)
        if puzzle[r][c] != 0:
            puzzle[r][c] = 0
            remove -= 1

    return puzzle, board


# -----------------------
# 初期化
# -----------------------
if "puzzle" not in st.session_state:
    st.session_state.puzzle, st.session_state.answer = generate_puzzle()
    st.session_state.user = copy.deepcopy(st.session_state.puzzle)
    st.session_state.start_time = time.time()

# ⭐ ベストタイム初期化
if "best_time" not in st.session_state:
    st.session_state.best_time = None


# -----------------------
# リセット
# -----------------------
if st.button("🔄 新しい問題"):
    for k in ["puzzle", "answer", "user", "start_time"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


# -----------------------
# タイマー表示
# -----------------------
elapsed = int(time.time() - st.session_state.start_time)
st.info(f"⏱ 経過時間：{elapsed} 秒")

# ⭐ ベストタイム表示
if st.session_state.best_time is None:
    st.info("🏆 ベストタイム：未記録")
else:
    st.success(f"🏆 ベストタイム：{st.session_state.best_time} 秒")

st.write("空欄に数字（1〜9）を入力してください")

# -----------------------
# 盤面表示（レイアウト変更なし）
# -----------------------
for r in range(SIZE):

    if r % 3 == 0 and r != 0:
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    row_cols = st.columns([1,1,1,0.15,1,1,1,0.15,1,1,1])
    col_index = 0

    for c in range(SIZE):
        col = row_cols[col_index]
        value = st.session_state.user[r][c]

        if st.session_state.puzzle[r][c] != 0:
            col.markdown(
                f"<div class='fixed-cell'>{value}</div>",
                unsafe_allow_html=True
            )
        else:
            new = col.number_input(
                "",
                min_value=0,
                max_value=9,
                value=value,
                key=f"{r}-{c}",
                step=1,
                label_visibility="collapsed"
            )

            # 🔒 1〜9以外は反映しない
            if new == 0:
                st.session_state.user[r][c] = value
            else:
                st.session_state.user[r][c] = new

        col_index += 1

        # 縦の太線
        if (c + 1) % 3 == 0 and c != SIZE - 1:
            divider = row_cols[col_index]
            divider.markdown(
                "<div style='border-left:3px solid white;height:45px'></div>",
                unsafe_allow_html=True
            )
            col_index += 1


# -----------------------
# 正解チェック
# -----------------------
if st.button("✅ 答え合わせ"):
    correct = True
    for r in range(SIZE):
        for c in range(SIZE):
            if st.session_state.user[r][c] != st.session_state.answer[r][c]:
                correct = False

    if correct:
        clear_time = int(time.time() - st.session_state.start_time)

        # 🏆 ベストタイム更新
        if (
            st.session_state.best_time is None
            or clear_time < st.session_state.best_time
        ):
            st.session_state.best_time = clear_time
            st.success(f"🎉 新記録！ クリアタイム：{clear_time} 秒")
        else:
            st.success(f"🎉 クリア！ タイム：{clear_time} 秒")

        st.balloons()
    else:
        st.error("❌ 間違いがあります")
