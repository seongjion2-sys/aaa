import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="세대별 포켓몬 도감 & 인물 사전",
    page_icon="📖",
    layout="wide",
)

# 커스텀 CSS (어두운 테마, 카드형 레이아웃 스타일링)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .person-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .person-title {
        font-size: 20px;
        font-weight: bold;
        color: #58a6ff;
        margin-bottom: 10px;
    }
    .person-info {
        color: #c9d1d9;
        font-size: 15px;
        line-height: 1.6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 세대별 포켓몬 더미 데이터 (포켓몬 도감 탭용)
POKEMON_DATA = {
    "1세대 (관동)": [
        {"no": "No.0001", "name": "이상해씨", "type": "풀/독"},
        {"no": "No.0004", "name": "파이리", "type": "불꽃"},
        {"no": "No.0007", "name": "꼬부기", "type": "물"},
        {"no": "No.0025", "name": "피카츄", "type": "전기"},
        {"no": "No.0006", "name": "리자몽", "type": "불꽃/비행"},
    ]
}

# 세대별 주요 인물 데이터 (박사, 주인공, 라이벌, 관장, 사천왕 등)
CHARACTER_DATA = {
    "1세대 (관동)": [
        {
            "name": "오박사",
            "role": "포켓몬 연구소 박사",
            "desc": "포켓몬 연구의 권위자로, 태초마을에 연구소를 두고 있으며 신참 트레이너에게 포켓몬과 도감을 건네준다.",
            "pokemon": "없음 (연구원)",
            "location": "태초마을 오박사 연구소",
            "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
        },
        {
            "name": "레드",
            "role": "전설의 포켓몬 트레이너 (주인공)",
            "desc": "태초마을 출신으로, 관동 지방을 모험하며 포켓몬 리그를 제패한 전설적인 트레이너입니다.",
            "pokemon": "피카츄, 리자몽, 잠만보, 라프라스",
            "location": "은빛산 정상",
            "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png",
        },
        {
            "name": "그린",
            "role": "라이벌",
            "desc": "레드의 라이벌이자 오박사의 손자. 자존심이 강하고 언제나 한 발 앞서 주인공을 가로막습니다.",
            "pokemon": "피죤투, 나인테일, 파르셀, 괴력몬, 나시, 리자몽",
            "location": "상록시티 포켓몬 짐 (관장)",
            "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/9.png",
        },
        {
            "name": "웅",
            "role": "회색시티 체육관 관장",
            "desc": "단단한 정신력과 바위처럼 묵직한 포켓몬 전투를 구사하는 포켓몬 브리더입니다.",
            "pokemon": "꼬마돌, 롱스톤",
            "location": "회색시티 체육관",
            "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/74.png",
        },
        {
            "name": "이슬",
            "role": "블루시티 체육관 관장",
            "desc": "물 속의 요정이라 불리며, 활기차고 당찬 성격의 체육관 관장입니다.",
            "pokemon": "별가사리, 아쿠스타",
            "location": "블루시티 체육관",
            "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/121.png",
        },
        {
            "name": "목호",
            "role": "포켓몬리그 사천왕 / 챔피언",
            "desc": "드래곤 타입 포켓몬을 다루는 포켓몬리그의 최강자 중 한 명입니다.",
            "pokemon": "갸라도스, 망나뇽, 프테라",
            "location": "석영고원 포켓몬리그",
            "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/149.png",
        },
    ]
}

# 상단 타이틀
st.markdown("### 📖 세대별 포켓몬 도감 및 인물 사전")
st.markdown("---")

# 상단 메뉴 선택 (포켓몬 도감 vs 세대별 인물 도감)
menu = st.radio(
    "메뉴 선택", ["포켓몬 도감", "세대별 주요 인물 도감"], horizontal=True
)

if menu == "포켓몬 도감":
    st.markdown("#### ⚡ 세대별 포켓몬 도감")
    selected_gen_p = st.selectbox(
        "세대를 선택하세요 (포켓몬)", list(POKEMON_DATA.keys())
    )
    search_pokemon = st.text_input(
        f"{selected_gen_p} 범위 내 이름 또는 번호 입력..."
    )

    st.markdown(
        "<p style='color: #8b949e;'>포켓몬을 선택하거나 위 검색창에 이름을 입력하세요.</p>",
        unsafe_allow_html=True,
    )

    # 포켓몬 버튼 그리드 예시
    cols = st.columns(3)
    pokemons = POKEMON_DATA[selected_gen_p]
    if search_pokemon:
        pokemons = [
            p
            for p in pokemons
            if search_pokemon in p["name"] or search_pokemon in p["no"]
        ]

    for idx, pock in enumerate(pokemons):
        with cols[idx % 3]:
            if st.button(f"{pock['no']} {pock['name']}", use_container_width=True):
                st.info(
                    f"선택한 포켓몬: {pock['name']} (타입: {pock['type']})"
                )

else:
    # 세대별 인물 도감 영역
    st.markdown("#### 👥 세대별 주요 인물 도감 (박사, 주인공, 라이벌, 관장, 사천왕)")
    selected_gen_c = st.selectbox(
        "세대를 선택하세요 (인물)", list(CHARACTER_DATA.keys())
    )

    # 인물 검색창 (두 번째 사진 참고)
    search_query = st.text_input(
        f"{selected_gen_c} 인물 이름을 입력하세요...", key="char_search"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 데이터 필터링 (검색어 반영)
    characters = CHARACTER_DATA[selected_gen_c]
    if search_query:
        characters = [
            c
            for c in characters
            if search_query in c["name"] or search_query in c["role"]
        ]

    # 두 번째 사진 형태의 박스(카드) 레이아웃으로 인물 리스트 및 상세 정보 출력
    for person in characters:
        with st.container():
            st.markdown(
                f"""
                <div class="person-card">
                    <div class="person-title">{person['name']} <span style="font-size: 14px; color: #8b949e; font-weight: normal;">({person['role']})</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 내부 상세 내용 (이미지 + 설명, 포켓몬, 위치)
            col_img, col_detail = st.columns([1, 3])

            with col_img:
                st.image(
                    person["image"],
                    caption=person["name"],
                    use_container_width=True,
                )

            with col_detail:
                st.markdown(
                    f"""
                    <div class="person-info">
                        <b>설명:</b> {person['desc']}<br><br>
                        <b>사용하는 포켓몬:</b> {person['pokemon']}<br><br>
                        <b>위치:</b> {person['location']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)
