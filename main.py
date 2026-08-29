import math
import urllib.parse
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="포켓몬 위키", page_icon="⚡", layout="wide")

# Session State 초기화
if "search_query" not in st.session_state:
  st.session_state.search_query = ""

if "current_page" not in st.session_state:
  st.session_state.current_page = "Main"

if "selected_gen" not in st.session_state:
  st.session_state.selected_gen = None

if "search_history" not in st.session_state:
  st.session_state.search_history = []

if "character_search_query" not in st.session_state:
  st.session_state.character_search_query = ""

if "selected_char_gen" not in st.session_state:
  st.session_state.selected_char_gen = None

if "character_search_history" not in st.session_state:
  st.session_state.character_search_history = []

if "selected_character" not in st.session_state:
  st.session_state.selected_character = None


# 세대별 범위 정의 (포켓몬)
GENERATIONS = {
    "1세대 (관동)": {"range": (1, 151), "color": "#FF5959"},
    "2세대 (성도)": {"range": (152, 251), "color": "#FF8C42"},
    "3세대 (호연)": {"range": (252, 386), "color": "#F3C623"},
    "4세대 (신오)": {"range": (387, 493), "color": "#1089FF"},
    "5세대 (하나)": {"range": (494, 649), "color": "#628E90"},
    "6세대 (칼로스)": {"range": (650, 721), "color": "#7B1FA2"},
    "7세대 (알로라)": {"range": (722, 809), "color": "#FF7043"},
    "8세대 (가라르)": {"range": (810, 905), "color": "#00838F"},
    "9세대 (팔데아)": {"range": (906, 1025), "color": "#C2185B"},
}

# 세대별 주요 인물 데이터 (1세대 대폭 강화 및 나무위키 구조 적용)
CHARACTER_GENERATIONS = {
    "1세대 (관동)": {
        "color": "#FF5959",
        "characters": [
            {
                "name": "레드",
                "category": "주인공",
                "title": "태초마을의 소년 / 전설의 트레이너",
                "location": "태초마을 / 은빛산 정상",
                "desc": (
                    "포켓몬 본가 초대 작품(적·녹·P·LG)의 남성 주인공. 말수가"
                    " 적고 묵묵히 실천하는 타입으로, 포켓몬 리그를 제패하고"
                    " 관동과 조토 지방을 구원한 전설의 트레이너입니다."
                ),
                "pokemon": ["피카츄", "리자몽", "잠만보", "라프라스", "잠만보"],
                "image": (
                    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/red.png"
                ),
            },
            {
                "name": "리프",
                "category": "주인공",
                "title": "파이어레드·잎녹색 여성 주인공",
                "location": "태초마을",
                "desc": (
                    "3세대 리메이크작인 파이어레드·잎녹색의 공식 여성"
                    " 주인공입니다. 밝고 활기찬 성격으로 모험을 이끌어"
                    " 나갑니다."
                ),
                "pokemon": ["이상해꽃", "피카츄", "라프라스"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/leaf.png",
            },
            {
                "name": "태주 / 보연",
                "category": "주인공",
                "title": "Let's Go! 피카츄·이브이 주인공",
                "location": "태초마을",
                "desc": (
                    "Let's Go! 피카츄·이브이의 주인공으로, 파트너 포켓몬과"
                    " 함께 관동 지방을 여행하는 친근한 트레이너입니다."
                ),
                "pokemon": ["파트너 피카츄", "파트너 이브이"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/chase.png",
            },
            {
                "name": "그린",
                "category": "라이벌",
                "title": "오박사의 손자 / 전 챔피언",
                "location": "태초마을 / 상록시티 체육관",
                "desc": (
                    "주인공의 영원한 라이벌이자 오박사의 손자. 오만하고"
                    " 실력도 뛰어난 천재 트레이너로, 주인공보다 한 발 앞서"
                    " 체육관을 제패하고 챔피언에 올랐던 인물입니다."
                ),
                "pokemon": ["괴력몬", "나인테일", "윈디", "나목환", "거북왕"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/blue.png",
            },
            {
                "name": "오박사 (오키드)",
                "category": "포켓몬 박사",
                "title": "포켓몬 연구의 권위자",
                "location": "태초마을 연구소",
                "desc": (
                    "본명은 오키드 유키오. 포켓몬과 인간의 공존을 연구하는"
                    " 세계적인 권위자로, 10살이 된 소년소녀들에게 첫"
                    " 포켓몬과 도감을 건네주는 스승 같은 존재입니다."
                ),
                "pokemon": ["이상해씨", "파이리", "꼬부기"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/oak.png",
            },
            {
                "name": "웅",
                "category": "체육관 관장",
                "title": "회색시티 체육관 관장",
                "location": "회색시티 체육관",
                "desc": (
                    "바위 타입 포켓몬을 다루는 바위 사나이. 단단한 정신력과"
                    " 묵직한 배틀을 구사하며, 포켓몬 브리더를 지망합니다."
                ),
                "pokemon": ["꼬마돌", "롱스톤"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/brock.png",
            },
            {
                "name": "이슬",
                "category": "체육관 관장",
                "title": "블루시티 체육관 관장",
                "location": "블루시티 체육관",
                "desc": (
                    "물 속의 요정이라 불리는 활기차고 당찬 성격의 소녀"
                    " 관장입니다. 물 타입 포켓몬을 전문적으로 다룹니다."
                ),
                "pokemon": ["별가람", "아쿠스타"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/misty.png",
            },
            {
                "name": "마티스",
                "category": "체육관 관장",
                "title": "갈색시티 체육관 관장",
                "location": "갈색시티 체육관",
                "desc": (
                    "전기 파도를 타는 미국의 군인 출신 관장. '번개의"
                    " 미국인'이라는 별명을 가졌으며, 전쟁터에서 전기"
                    " 포켓몬 덕분에 살아남았다고 합니다."
                ),
                "pokemon": ["찌리리공", "피카츄", "라이츄"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/ltsurge.png",
            },
            {
                "name": "민화",
                "category": "체육관 관장",
                "title": "무지개시티 체육관 관장",
                "location": "무지개시티 체육관",
                "desc": (
                    "관동의 아가씨. 기모노를 차려입고 온화한 인상을 주지만,"
                    " 풀 타입 포켓몬을 다루는 실력은 매우 강력합니다."
                ),
                "pokemon": ["우츠동", "덩쿠리", "라플레시아"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/erika.png",
            },
            {
                "name": "독주",
                "category": "체육관 관장",
                "title": "연분홍시티 체육관 관장",
                "location": "연분홍시티 체육관",
                "desc": (
                    "닌자 가문의 후예로 맹독과 트랩을 주로 사용하는 포커페이스"
                    " 관장입니다. 독 타입 포켓몬을 전문으로 합니다."
                ),
                "pokemon": ["도나리", "베를로몬", "아보크", "도나리"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/koga.png",
            },
            {
                "name": "초은",
                "category": "체육관 관장",
                "title": "노랑시티 체육관 관장",
                "location": "노랑시티 체육관",
                "desc": (
                    "초능력을 사용하는 신비로운 소녀 관장. 강력한 에스퍼"
                    " 타입 포켓몬으로 상대를 압박하며 예지 능력이 있습니다."
                ),
                "pokemon": ["윤겔라", "최면술사", "후딘"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/sabrina.png",
            },
            {
                "name": "강연",
                "category": "체육관 관장",
                "title": "홍련섬 체육관 관장",
                "location": "홍련섬 체육관",
                "desc": (
                    "홍련섬의 뜨거운 화염 같은 수수께끼의 노인 관장. 불꽃"
                    " 타입 포켓몬과 퀴즈를 사랑하는 괴짜입니다."
                ),
                "pokemon": ["가디", "포니타", "윈디", "부스터"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/blaine.png",
            },
            {
                "name": "칸나",
                "category": "사천왕",
                "title": "얼음 포켓몬의 마스터",
                "location": "석영고원 사천왕의 방",
                "desc": (
                    "오렌지諸島 출신의 사천왕. 차갑고 도도한 인상이며, 얼음과"
                    " 물 타입 포켓몬을 조합하여 상대를 꽁꽁 얼려버립니다."
                ),
                "pokemon": ["쥬레곤", "파르셀", "야도란", "루주라", "라프라스"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/lorelei.png",
            },
            {
                "name": "시바",
                "category": "사천왕",
                "title": "격투 포켓몬의 마스터",
                "location": "석영고원 사천왕의 방",
                "desc": (
                    "산 속에서 포켓몬과 함께 육체를 단련하는 열혈 격투가"
                    " 사천왕입니다."
                ),
                "pokemon": ["롱스톤", "시라소몬", "홍수몬", "괴력몬"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/bruno.png",
            },
            {
                "name": "국화",
                "category": "사천왕",
                "title": "고스트 포켓몬의 마스터",
                "location": "석영고원 사천왕의 방",
                "desc": (
                    "오박사의 옛 라이벌이자 노련한 사천왕. 고스트 타입의"
                    " 음산하고 교란하는 배틀을 구사합니다."
                ),
                "pokemon": ["고오스", "골뱃", "고우스트", "팬텀"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/agatha.png",
            },
            {
                "name": "목호",
                "category": "사천왕",
                "title": "드래곤 포켓몬의 마스터",
                "location": "석영고원 사천왕의 방",
                "desc": (
                    "망토를 두른 카리스마 넘치는 드래곤 사천왕. 이후 2세대에서"
                    " 챔피언으로 등극하는 강력한 트레이너입니다."
                ),
                "pokemon": ["갸라도스", "신뇽", "망나뇽"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/lance.png",
            },
            {
                "name": "비주기",
                "category": "로켓단",
                "title": "로켓단 보스 / 상록시티 체육관 관장",
                "location": "상록시티 체육관 / 로켓단 아지트",
                "desc": (
                    "악의 조직 '로켓단'의 냉혹한 수장이자, 마지막 관동"
                    " 체육관의 관장. 땅 타입 포켓몬을 전문으로 다룹니다."
                ),
                "pokemon": ["코뿌리", "니드퀸", "니드킹", "코뿌리"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/giovanni.png",
            },
            {
                "name": "로이 & 로사",
                "category": "로켓단",
                "title": "로켓단 간부 / 트러블메이커",
                "location": "관동 전역 (지우를 쫓아다님)",
                "desc": (
                    "포켓몬 애니메이션에서 유래하여 게임에도 영향을 준"
                    " 악당이지만 밉지 않은 로켓단의 명콤비. 말하는"
                    " 나옹이와 함께 항상 주인공의 피카츄를 노립니다."
                ),
                "pokemon": ["아보크", "또도가스", "나옹"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/jessie-james.png",
            },
        ],
    },
    "2세대 (성도)": {
        "color": "#FF8C42",
        "characters": [
            {
                "name": "심향 / 크리스 / 코트",
                "category": "주인공",
                "title": "성도 지방의 주인공",
                "location": "연두마을",
                "desc": (
                    "포켓몬 금·은·크리스탈 및 하트골드·소울실버의"
                    " 주인공들입니다."
                ),
                "pokemon": ["메가니움", "블레이범", "장크로다일"],
                "image": "https://play.pokemonshowdown.com/sprites/trainers/ethan.png",
            }
        ],
    },
}

FEATURED_POKEMON_MAP = {
    "켄타로스": "tauros",
    "식스테일": "vulpix",
    "가디": "growlithe",
    "슬리프": "drowzee",
    "나무지기": "treecko",
    "루브도": "smeargle",
}


def go_to_page(page_name):
  st.session_state.current_page = page_name
  if page_name == "포켓몬 도감":
    st.session_state.selected_gen = None
  elif page_name == "인물 도감":
    st.session_state.selected_char_gen = None
    st.session_state.selected_character = None


def add_search_history(query):
  query = query.strip()
  if query:
    if query in st.session_state.search_history:
      st.session_state.search_history.remove(query)
    st.session_state.search_history.insert(0, query)
    if len(st.session_state.search_history) > 10:
      st.session_state.search_history.pop()


def update_search():
  query = st.session_state.user_input
  st.session_state.search_query = query
  st.session_state.current_page = "포켓몬 도감"
  if query.strip():
    add_search_history(query)


def update_national_search():
  query = st.session_state.national_user_input
  st.session_state.search_query = query
  st.session_state.current_page = "전국 도감"
  if query.strip():
    add_search_history(query)


# CSS 스타일 적용 (나무위키풍 카드 및 인물 카드 레이아웃 포함)
st.markdown(
    """
    <style>
    :root {
        --wiki-main: #008275;
    }
    .stTextInput input {
        font-size: 1.2rem !important;
        padding: 14px 18px !important;
        border-radius: 10px !important;
        border: 2px solid var(--wiki-main) !important;
    }
    .main-title {
        color: var(--wiki-main);
        font-weight: bold;
        border-bottom: 2px solid var(--wiki-main);
        padding-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .section-title {
        color: var(--wiki-main);
        border-bottom: 1px solid #ccc;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .menu-card {
        background-color: #ffffff;
        color: #222222;
        border: 2px solid #e0e0e0;
        border-radius: 14px 14px 0 0;
        padding: 25px 15px;
        height: 180px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .gen-banner, .char-banner {
        border-radius: 12px;
        padding: 25px 15px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    .char-card-box {
        border: 1px solid #d0d0d0;
        border-radius: 8px;
        padding: 15px;
        background-color: #fcfcfc;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .char-card-box img {
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin-bottom: 10px;
    }
    .wiki-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }
    .wiki-table th {
        background-color: #008275;
        color: white;
        padding: 8px;
        border: 1px solid #00665c;
        text-align: center;
    }
    .wiki-table td {
        background-color: #ffffff;
        color: #333;
        padding: 8px;
        border: 1px solid #ddd;
    }
    </style>
""",
    unsafe_allow_html=True,
)

TYPE_NAME_MAP = {
    "normal": "노멀",
    "fire": "불꽃",
    "water": "물",
    "grass": "풀",
    "electric": "전기",
    "ice": "얼음",
    "fighting": "격투",
    "poison": "독",
    "ground": "땅",
    "flying": "비행",
    "psychic": "에스퍼",
    "bug": "벌레",
    "rock": "바위",
    "ghost": "고스트",
    "dragon": "드래곤",
    "dark": "악",
    "steel": "강철",
    "fairy": "페어리",
}


@st.cache_data(ttl=86400)
def get_pokemon_name_by_id(pokemon_id):
  try:
    res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}", timeout=2
    )
    if res.status_code == 200:
      data = res.json()
      return next(
          (n["name"] for n in data["names"] if n["language"]["name"] == "ko"),
          f"No.{pokemon_id}",
      )
  except Exception:
    pass
  return f"No.{pokemon_id}"


@st.cache_data(ttl=86400)
def search_national_pokemon_id(query_name, max_id=1025):
  query_name = query_name.strip().lower()
  if query_name.isdigit():
    num = int(query_name)
    if 1 <= num <= max_id:
      return num
    return None
  try:
    for p_id in range(1, max_id + 1):
      ko_name = get_pokemon_name_by_id(p_id)
      if ko_name and query_name in ko_name.lower():
        return p_id
  except Exception:
    pass
  return None


@st.cache_data(ttl=86400)
def get_pokemon_data(target_id):
  try:
    pokemon_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{target_id}", timeout=2
    )
    if pokemon_res.status_code != 200:
      return None
    pokemon_data = pokemon_res.json()
    species_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{target_id}", timeout=2
    )
    species_data = species_res.json()
    ko_name = next(
        (
            n["name"]
            for n in species_data["names"]
            if n["language"]["name"] == "ko"
        ),
        pokemon_data["name"],
    )
    img_url = (
        pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
        or pokemon_data["sprites"]["front_default"]
    )
    return {
        "id": pokemon_data["id"],
        "formatted_id": f"No.{str(pokemon_data['id']).zfill(4)}",
        "name": ko_name,
        "image": img_url,
    }
  except Exception:
    return None


# 사이드바 네비게이션
st.sidebar.title("⚡ 포켓몬 위키 네비게이션")
if st.sidebar.button("🏠 메인 메뉴", use_container_width=True):
  go_to_page("Main")

if st.sidebar.button("📖 세대별 도감", use_container_width=True):
  go_to_page("포켓몬 도감")

if st.sidebar.button("👤 인물 도감", use_container_width=True):
  go_to_page("인물 도감")

# ==================== 페이지 라우팅 ====================

if st.session_state.current_page == "Main":
  st.title("⚡ 포켓몬 나무위키 통합 메인")
  st.write("원하시는 도감을 선택하여 상세 정보를 확인해 보세요!")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        """
        <div class="menu-card">
            <div style="font-size: 2.0rem; margin-bottom: 6px;">📖</div>
            <div style="font-weight: bold; font-size: 1.1rem; color: #008275; margin-bottom: 4px;">포켓몬 도감</div>
            <div style="font-size: 0.8rem; color: #666;">세대별 포켓몬 목록 및 정보 확인</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("세대별 도감", key="btn_pokedex", use_container_width=True):
      go_to_page("포켓몬 도감")
      st.rerun()

  with col2:
    st.markdown(
        """
        <div class="menu-card">
            <div style="font-size: 2.0rem; margin-bottom: 6px;">👤</div>
            <div style="font-weight: bold; font-size: 1.1rem; color: #008275; margin-bottom: 4px;">인물 도감</div>
            <div style="font-size: 0.8rem; color: #666;">트레이너, 관장, 사천왕 및 로켓단 정보</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("인물 도감", key="btn_character", use_container_width=True):
      go_to_page("인물 도감")
      st.rerun()

  with col3:
    st.markdown(
        """
        <div class="menu-card">
            <div style="font-size: 2.0rem; margin-bottom: 6px;">🗺️</div>
            <div style="font-weight: bold; font-size: 1.1rem; color: #008275; margin-bottom: 4px;">맵 도감</div>
            <div style="font-size: 0.8rem; color: #666;">지방별 필드 및 서식지 정보</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("맵 도감", key="btn_map", use_container_width=True):
      go_to_page("맵 도감")
      st.rerun()

elif st.session_state.current_page == "포켓몬 도감":
  st.title("📖 세대별 포켓몬 도감")
  if not st.session_state.selected_gen:
    st.write(
        "**원하시는 세대 도감을 선택하여 해당 세대 포켓몬만 탐색 및 검색하세요.**"
    )
    all_menu_items = list(GENERATIONS.keys()) + ["전국 도감"]
    for r in range(4):
      cols = st.columns(3)
      for c in range(3):
        idx = r * 3 + c
        if idx < len(all_menu_items):
          item_name = all_menu_items[idx]
          with cols[c]:
            if item_name == "전국 도감":
              st.markdown(
                  """
                  <div class="gen-banner" style="background-color: #2F3640;">
                      전국 도감<br>
                      <span style="font-size: 0.85rem; font-weight: normal;">No.001 ~ No.1025</span>
                  </div>
                  """,
                  unsafe_allow_html=True,
              )
              if st.button(
                  "전국 도감 입장",
                  key="btn_national_card",
                  use_container_width=True,
              ):
                go_to_page("전국 도감")
                st.rerun()
            else:
              g_info = GENERATIONS[item_name]
              start, end = g_info["range"]
              st.markdown(
                  f"""
                  <div class="gen-banner" style="background-color: {g_info['color']};">
                      {item_name}<br>
                      <span style="font-size: 0.85rem; font-weight: normal;">No.{str(start).zfill(3)} ~ No.{str(end).zfill(3)}</span>
                  </div>
                  """,
                  unsafe_allow_html=True,
              )
              if st.button(
                  f"{item_name} 도감 입장",
                  key=f"gen_btn_{idx}",
                  use_container_width=True,
              ):
                st.session_state.selected_gen = item_name
                st.rerun()
  else:
    # 세대별 포켓몬 리스트 표시 영역
    g_name = st.session_state.selected_gen
    start_id, end_id = GENERATIONS[g_name]["range"]
    if st.button("◀ 세대 목록으로"):
      st.session_state.selected_gen = None
      st.rerun()
    st.markdown(f"### ⚡ {g_name} 포켓몬 목록")
    poke_cols = st.columns(3)
    for p_id in range(start_id, end_id + 1):
      p_name = get_pokemon_name_by_id(p_id)
      col_idx = (p_id - start_id) % 3
      with poke_cols[col_idx]:
        if st.button(
            f"No.{str(p_id).zfill(4)} {p_name}",
            key=f"p_list_{p_id}",
            use_container_width=True,
        ):
          st.session_state.search_query = str(p_id)
          go_to_page("전국 도감")
          st.rerun()

elif st.session_state.current_page == "전국 도감":
  st.title("🌐 전국 포켓몬 도감 통합 검색")
  st.text_input(
      "포켓몬 이름 또는 번호 입력",
      value=st.session_state.search_query,
      key="national_user_input",
      on_change=update_national_search,
  )
  q = search_national_pokemon_id(str(st.session_state.search_query))
  if q:
    p_data = get_pokemon_data(q)
    if p_data:
      st.markdown(
          f"<h2>{p_data['name']} ({p_data['formatted_id']})</h2>",
          unsafe_allow_html=True,
      )
      st.image(p_data["image"], width=250)

elif st.session_state.current_page == "인물 도감":
  st.title("👤 세대별 인물 도감")

  if not st.session_state.selected_char_gen:
    st.write(
        "**원하시는 세대를 선택하여 해당 세대에 등장하는 주인공, 라이벌, 관장,"
        " 사천왕 등의 상세 정보를 확인하세요.**"
    )
    row1 = ["1세대 (관동)", "2세대 (성도)"]
    cols = st.columns(2)
    for c_idx, g_name in enumerate(row1):
      if g_name in CHARACTER_GENERATIONS:
        g_info = CHARACTER_GENERATIONS[g_name]
        with cols[c_idx]:
          st.markdown(
              f"""
              <div class="char-banner" style="background-color: {g_info['color']};">
                  {g_name}<br>
                  <span style="font-size: 0.85rem; font-weight: normal;">주인공, 라이벌, 관장 및 사천왕</span>
              </div>
              """,
              unsafe_allow_html=True,
          )
          if st.button(
              f"{g_name} 인물 도감 입장",
              key=f"char_gen_btn_{c_idx}",
              use_container_width=True,
          ):
            st.session_state.selected_char_gen = g_name
            st.session_state.selected_character = None
            st.rerun()

  elif st.session_state.selected_character is None:
    # 1세대 인물 목록 그리드 출력 (사진과 나무위키 스타일 버튼 카드 형태)
    g_name = st.session_state.selected_char_gen
    g_data = CHARACTER_GENERATIONS[g_name]

    if st.button("◀ 세대 목록으로"):
      st.session_state.selected_char_gen = None
      st.rerun()

    st.markdown(f"### 👤 {g_name} 인물 도감 목록")
    st.write(
        "아래 인물을 클릭하면 나무위키 스타일의 상세 설명과 보유 포켓몬 정보를"
        " 확인할 수 있습니다."
    )

    characters = g_data["characters"]
    cols = st.columns(3)
    for idx, char in enumerate(characters):
      col_idx = idx % 3
      with cols[col_idx]:
        st.markdown(
            f"""
            <div class="char-card-box">
                <img src="{char['image']}">
                <div style="font-weight: bold; font-size: 1.1px; color: #008275;">{char['name']}</div>
                <div style="font-size: 0.85rem; color: #666; margin-bottom: 8px;">[{char['category']}] {char['title']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"📖 {char['name']} 정보 보기",
            key=f"char_click_{idx}",
            use_container_width=True,
        ):
          st.session_state.selected_character = char
          st.rerun()

  else:
    # 선택된 개별 인물의 상세 나무위키 스타일 화면 출력
    char = st.session_state.selected_character
    if st.button("◀ 인물 목록으로"):
      st.session_state.selected_character = None
      st.rerun()

    col1, col2 = st.columns([1.5, 2.5])
    with col1:
      st.markdown(
          f"""
          <div style="border: 2px solid #008275; border-radius: 8px; padding: 15px; text-align: center; background-color: #f8f9fa;">
              <h3 style="background-color: #008275; color: white; padding: 6px; border-radius: 4px; margin-top:0;">{char['name']}</h3>
              <img src="{char['image']}" style="width: 150px; height: 150px; object-fit: contain; margin: 10px 0;">
          </div>
          """,
          unsafe_allow_html=True,
      )

      st.markdown(
          f"""
          <table class="wiki-table">
              <tr><th>구분</th><td>{char['category']}</td></tr>
              <tr><th>칭호</th><td>{char['title']}</td></tr>
              <tr><th>주요 출현 위치</th><td>{char['location']}</td></tr>
              <tr><th>주력 포켓몬</th><td>{', '.join(char['pokemon'])}</td></tr>
          </table>
          """,
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          f"<h1 class='main-title'>{char['name']} <small style='font-size:1rem; color:#666;'>| {char['title']}</small></h1>",
          unsafe_allow_html=True,
      )

      st.markdown(
          "<h3 class='section-title'>1. 개요</h3>", unsafe_allow_html=True
      )
      st.write(char["desc"])

      st.markdown(
          "<h3 class='section-title'>2. 사용 포켓몬</h3>", unsafe_allow_html=True
      )
      st.write(
          "배틀이나 스토리 진행 시 이 인물이 다루는 대표적인 포켓몬 목록입니다:"
      )
      for p in char["pokemon"]:
        st.markdown(f"- **{p}**")

      st.markdown(
          "<h3 class='section-title'>3. 관련 설정 및 특징</h3>",
          unsafe_allow_html=True,
      )
      st.write(
          f"'{char['name']}'은(는) 관동 지방 모험에서 플레이어에게 깊은"
          " 인상을 남기는 핵심 인물 중 하나로, 포켓몬스터 시리즈의 세계관을"
          " 구성하는 중요한 역할을 담당합니다."
      )

elif st.session_state.current_page == "맵 도감":
  st.title("🗺️ 맵 도감")
  st.info("준비 중인 페이지입니다.")
