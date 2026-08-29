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

# 세대별 주요 인물 데이터 (체육관 관장, 챔피언, 주요 트레이너 등)
CHARACTER_GENERATIONS = {
    "1세대 (관동)": {
        "color": "#FF5959",
        "characters": [
            {
                "name": "웅",
                "title": "회색시티 체육관 관장",
                "type": "바위",
                "specialty": "바위 타입 포켓몬을 다루는 관장",
                "desc": (
                    "단단한 정신력과 바위처럼 묵직한 포켓몬 전투를 구사하는"
                    " 포켓몬 브리더입니다."
                ),
                "pokemon": ["꼬마돌", "롱스톤"],
            },
            {
                "name": "이슬",
                "title": "블루시티 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": (
                    "물 속의 요정이라 불리며, 활기차고 당찬 성격의 체육관"
                    " 관장입니다."
                ),
                "pokemon": ["별가람", "아쿠스타"],
            },
            {
                "name": "레드",
                "title": "전설의 포켓몬 트레이너",
                "type": "기타",
                "specialty": "올라운더",
                "desc": (
                    "태초마을 출신으로, 관동 지방을 모험하며 포켓몬 리그를"
                    " 제패한 전설적인 트레이너입니다."
                ),
                "pokemon": ["피카츄", "리자몽", "잠만보"],
            },
        ],
    },
    "2세대 (성도)": {
        "color": "#FF8C42",
        "characters": [
            {
                "name": "죽란",
                "title": "도라지시티 체육관 관장",
                "type": "비행",
                "specialty": "비행 타입 포켓몬 전문",
                "desc": "하늘을 나는 포켓몬을 사랑하는 우아한 관장입니다.",
                "pokemon": ["구구", "야부엉"],
            },
            {
                "name": "호일",
                "title": "고마도시티 체육관 관장",
                "type": "벌레",
                "specialty": "벌레 타입 포켓몬 전문",
                "desc": "벌레 포켓몬 연구에 열정적인 소년 관장입니다.",
                "pokemon": ["단데기", "스라크"],
            },
        ],
    },
    "3세대 (호연)": {
        "color": "#F3C623",
        "characters": [
            {
                "name": "원규",
                "title": "금시티 체육관 관장",
                "type": "바위",
                "specialty": "바위 타입 포켓몬 전문",
                "desc": "바위와 지질학에 조예가 깊은 우수한 학생 관장입니다.",
                "pokemon": ["꼬마돌", "코코파스"],
            },
            {
                "name": "철헌",
                "title": "무로시티 체육관 관장",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 전문",
                "desc": "서핑과 격투기를 즐기는 시원시원한 성격의 관장입니다.",
                "pokemon": ["알통몬", "마하펀치"],
            },
        ],
    },
    "4세대 (신오)": {
        "color": "#1089FF",
        "characters": [
            {
                "name": "강석",
                "title": "무쇠시티 체육관 관장",
                "type": "바위",
                "specialty": "바위 타입 포켓몬 전문",
                "desc": "탄광업이 발달한 무쇠시티를 이끄는 든든한 관장입니다.",
                "pokemon": ["꼬마돌", "두개도스"],
            },
            {
                "name": "유채",
                "title": "영원시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "풀 포켓몬과 대자연을 사랑하는 밝은 성격의 관장입니다.",
                "pokemon": ["체리버", "로즈레이드"],
            },
        ],
    },
    "5세대 (하나)": {
        "color": "#628E90",
        "characters": [
            {
                "name": "덴트",
                "title": "삼요시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "소믈리에 능력을 지닌 삼형제 관장 중 첫째입니다.",
                "pokemon": ["야나프"],
            }
        ],
    },
    "6세대 (칼로스)": {
        "color": "#7B1FA2",
        "characters": [
            {
                "name": "시트론",
                "title": "미로시티 체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 및 발명품",
                "desc": "과학 발명을 사랑하는 천재 소년 관장입니다.",
                "pokemon": ["레코디", "일레도리자드"],
            }
        ],
    },
    "7세대 (알로라)": {
        "color": "#FF7043",
        "characters": [
            {
                "name": "릴리",
                "title": "수수께끼의 소녀",
                "type": "기타",
                "specialty": "서포터",
                "desc": (
                    "포켓몬을 무서워했으나 주인공과 만나며 용기를 얻고"
                    " 성장하는 소녀입니다."
                ),
                "pokemon": ["코스모스"],
            }
        ],
    },
    "8세대 (가라르)": {
        "color": "#00838F",
        "characters": [
            {
                "name": "야청",
                "title": "너클시티/원더시티 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": (
                    "평소에는 차분하지만 배틀 시에는 승부욕이 불타오르는"
                    " 패션 모델 겸 관장입니다."
                ),
                "pokemon": ["갈가부기", "드레디어"],
            }
        ],
    },
    "9세대 (팔데아)": {
        "color": "#C2185B",
        "characters": [
            {
                "name": "모니카",
                "title": "보울시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "올리브 농장을 운영하며 마을을 사랑하는 관장입니다.",
                "pokemon": ["올리비"],
            }
        ],
    },
    "히스이 지방": {
        "color": "#5C5470",
        "characters": [
            {
                "name": "반죽",
                "title": "은하단 조사대 캡틴",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 및 육체 단련",
                "desc": (
                    "금강단 소속이자 은하단 캡틴으로, 흑요의 들판에서"
                    " 왕을 모시며 주인공의 조력자가 되어 주는 호쾌한"
                    " 인물입니다."
                ),
                "pokemon": ["창파나이트", "알통몬"],
            },
            {
                "name": "주이",
                "title": "은하단 의료대 캡틴",
                "type": "노멀",
                "specialty": "치유 및 포켓몬 관리",
                "desc": (
                    "진주단 출신으로 콧등의 흉터가 특징이며, 다소 쌀쌀맞아"
                    " 보이지만 포켓몬들을 깊이 아끼는 캡틴입니다."
                ),
                "pokemon": ["잠만보"],
            },
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


def add_search_history(query):
  query = query.strip()
  if query:
    if query in st.session_state.search_history:
      st.session_state.search_history.remove(query)
    st.session_state.search_history.insert(0, query)
    if len(st.session_state.search_history) > 10:
      st.session_state.search_history.pop()


def add_character_search_history(query):
  query = query.strip()
  if query:
    if query in st.session_state.character_search_history:
      st.session_state.character_search_history.remove(query)
    st.session_state.character_search_history.insert(0, query)
    if len(st.session_state.character_search_history) > 10:
      st.session_state.character_search_history.pop()


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


def update_character_search():
  query = st.session_state.char_user_input
  st.session_state.character_search_query = query
  if query.strip():
    add_character_search_history(query)


# CSS 스타일
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
    .type-badge {
        color: white !important;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: bold;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        display: inline-block;
    }
    .section-title {
        color: var(--wiki-main);
        border-bottom: 1px solid #ccc;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .infobox {
        border: 2px solid var(--wiki-main);
        border-radius: 8px;
        padding: 10px;
        background-color: #f8f9fa;
        text-align: center;
    }
    .infobox-title {
        background-color: var(--wiki-main);
        color: white;
        padding: 8px;
        font-weight: bold;
        font-size: 1.2rem;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .evo-card {
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 8px 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        background-color: transparent;
        margin-bottom: 10px;
        width: max-content;
        min-width: 180px;
    }
    .evo-card img {
        width: 60px;
        height: 60px;
        object-fit: contain;
    }
    .evo-info {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }
    .evo-id {
        font-size: 0.8rem;
        color: #aaaaaa;
    }
    .evo-name {
        font-size: 1.05rem;
        font-weight: bold;
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
    .char-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
    }
    .type-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        text-align: center;
        font-size: 0.9rem;
        border: 1px solid #008275;
    }
    .type-table th {
        background-color: #008275;
        color: white;
        padding: 6px 4px;
        border: 1px solid #00665c;
        font-weight: bold;
    }
    .type-table td {
        background-color: #1a1a1a;
        padding: 10px 4px;
        border: 1px solid #333;
        vertical-align: top;
    }
    .type-chip {
        display: inline-block;
        padding: 3px 8px;
        margin: 2px;
        border-radius: 6px;
        color: white !important;
        font-weight: bold;
        font-size: 0.82rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .bg-normal { background-color: #A8A878 !important; }
    .bg-fire { background-color: #F08030 !important; }
    .bg-water { background-color: #6890F0 !important; }
    .bg-grass { background-color: #78C850 !important; }
    .bg-electric { background-color: #F8D030 !important; color: #000 !important; }
    .bg-ice { background-color: #98D8D8 !important; color: #000 !important; }
    .bg-fighting { background-color: #C03028 !important; }
    .bg-poison { background-color: #A040A0 !important; }
    .bg-ground { background-color: #E0C068 !important; color: #000 !important; }
    .bg-flying { background-color: #A890F0 !important; }
    .bg-psychic { background-color: #F85888 !important; }
    .bg-bug { background-color: #A8B820 !important; }
    .bg-rock { background-color: #B8A038 !important; }
    .bg-ghost { background-color: #70559B !important; }
    .bg-dragon { background-color: #7038F8 !important; }
    .bg-dark { background-color: #705848 !important; }
    .bg-steel { background-color: #B8B8D0 !important; color: #000 !important; }
    .bg-fairy { background-color: #EE99AC !important; color: #000 !important; }
    .bg-unknown { background-color: #008275 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

STAT_NAME_MAP = {
    "hp": "체력(HP)",
    "attack": "공격",
    "defense": "방어",
    "special-attack": "특수공격",
    "special-defense": "특수방어",
    "speed": "스피드",
}

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

TYPE_EN_MAP = {v: k for k, v in TYPE_NAME_MAP.items()}
ALL_TYPES = list(TYPE_NAME_MAP.keys())


def get_type_color_class(ko_type_name):
  en_type = TYPE_EN_MAP.get(ko_type_name, "unknown")
  return f"bg-{en_type}"


@st.cache_data(ttl=86400)
def calculate_type_effectiveness(raw_types):
  defense_relations = {t: 1.0 for t in ALL_TYPES}
  for t_name in raw_types:
    try:
      res = requests.get(
          f"https://pokeapi.co/api/v2/type/{t_name}", timeout=2
      )
      if res.status_code == 200:
        rel = res.json()["damage_relations"]
        for d in rel["double_damage_from"]:
          defense_relations[d["name"]] *= 2.0
        for h in rel["half_damage_from"]:
          defense_relations[h["name"]] *= 0.5
        for n in rel["no_damage_from"]:
          defense_relations[n["name"]] *= 0.0
    except Exception:
      pass

  def_grouped = {4.0: [], 2.0: [], 1.0: [], 0.5: [], 0.25: [], 0.0: []}
  for t_name, mult in defense_relations.items():
    if mult in def_grouped:
      def_grouped[mult].append(t_name)

  attack_relations = {t: 0.0 for t in ALL_TYPES}
  for t_name in raw_types:
    try:
      res = requests.get(
          f"https://pokeapi.co/api/v2/type/{t_name}", timeout=2
      )
      if res.status_code == 200:
        rel = res.json()["damage_relations"]
        double_to = [x["name"] for x in rel["double_damage_to"]]
        half_to = [x["name"] for x in rel["half_damage_to"]]
        no_to = [x["name"] for x in rel["no_damage_to"]]

        for target_t in ALL_TYPES:
          mult = 1.0
          if target_t in double_to:
            mult = 2.0
          elif target_t in half_to:
            mult = 0.5
          elif target_t in no_to:
            mult = 0.0

          attack_relations[target_t] = max(attack_relations[target_t], mult)
    except Exception:
      pass

  atk_grouped = {2.0: [], 1.0: [], 0.5: [], 0.0: []}
  for t_name, mult in attack_relations.items():
    if mult in atk_grouped:
      atk_grouped[mult].append(t_name)

  return def_grouped, atk_grouped


def render_type_table(grouped_data, is_defense=True):
  multipliers = (
      [4.0, 2.0, 1.0, 0.5, 0.25, 0.0] if is_defense else [2.0, 1.0, 0.5, 0.0]
  )
  active_mults = [m for m in multipliers if len(grouped_data.get(m, [])) > 0]

  if not active_mults:
    return "<p>상성 정보가 없습니다.</p>"

  headers_html = "".join([
      f"<th>{f'{m:g}' if m % 1 != 0 else int(m)}배</th>" for m in active_mults
  ])

  cells_html = ""
  for m in active_mults:
    chips = ""
    for t_en in grouped_data[m]:
      t_ko = TYPE_NAME_MAP.get(t_en, t_en)
      chips += f"<span class='type-chip bg-{t_en}'>{t_ko}</span>"
    cells_html += f"<td>{chips}</td>"

  return f"""
    <table class="type-table">
        <thead>
            <tr>{headers_html}</tr>
        </thead>
        <tbody>
            <tr>{cells_html}</tr>
        </tbody>
    </table>
    """


def translate_to_ko(text):
  try:
    encoded_text = urllib.parse.quote(text)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={encoded_text}"
    res = requests.get(url, timeout=2)
    if res.status_code == 200:
      data = res.json()
      return "".join([item[0] for item in data[0] if item[0]])
  except Exception:
    pass
  return text


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


def get_pokemon_info_from_species_url(url):
  try:
    res = requests.get(url, timeout=2)
    if res.status_code == 200:
      data = res.json()
      p_id = data["id"]
      formatted_id = f"No.{str(p_id).zfill(4)}"
      ko_name = next(
          (n["name"] for n in data["names"] if n["language"]["name"] == "ko"),
          data["name"],
      )

      p_res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon/{p_id}", timeout=2
      )
      img_url = ""
      if p_res.status_code == 200:
        p_data = p_res.json()
        img_url = (
            p_data["sprites"]["other"]["official-artwork"]["front_default"]
            or p_data["sprites"]["front_default"]
        )

      return {
          "id": p_id,
          "formatted_id": formatted_id,
          "name": ko_name,
          "image": img_url,
      }
  except Exception:
    pass
  return None


def find_evolution_neighbors(chain, target_species_name):
  prev_evos, next_evos = [], []

  def traverse(node, current_path):
    if node["species"]["name"] == target_species_name:
      if current_path:
        prev_evos.append(current_path[-1])
      for child in node.get("evolves_to", []):
        next_evos.append(child["species"])
      return True

    for child in node.get("evolves_to", []):
      if traverse(child, current_path + [node["species"]]):
        return True
    return False

  traverse(chain["chain"], [])
  return prev_evos, next_evos


def generate_hexagon_svg(stats):
  keys = ["체력(HP)", "공격", "방어", "특수공격", "특수방어", "스피드"]
  vals = [stats.get(k, 0) for k in keys]
  max_val = 255.0
  cx, cy, r = 150, 150, 100

  grid_lines = ""
  for step in [0.2, 0.4, 0.6, 0.8, 1.0]:
    pts = []
    for i in range(6):
      angle = math.radians(60 * i - 90)
      x = cx + (r * step) * math.cos(angle)
      y = cy + (r * step) * math.sin(angle)
      pts.append(f"{x:.1f},{y:.1f}")
    grid_lines += (
        f'<polygon points="{" ".join(pts)}" fill="none" stroke="#e0e0e0"'
        ' stroke-width="1"/>'
    )

  axis_lines = ""
  for i in range(6):
    angle = math.radians(60 * i - 90)
    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)
    axis_lines += (
        f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#d0d0d0"'
        ' stroke-width="1"/>'
    )

  data_pts = []
  labels_svg = ""
  for i, (k, v) in enumerate(zip(keys, vals)):
    angle = math.radians(60 * i - 90)
    ratio = min(v / max_val, 1.0)
    x = cx + (r * ratio) * math.cos(angle)
    y = cy + (r * ratio) * math.sin(angle)
    data_pts.append(f"{x:.1f},{y:.1f}")

    lx = cx + (r + 25) * math.cos(angle)
    ly = cy + (r + 15) * math.sin(angle)
    labels_svg += (
        f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#333" font-size="12"'
        f' font-weight="bold" text-anchor="middle">{k}</text>'
    )

  poly_pts = " ".join(data_pts)

  return f"""
    <div style="display:flex; justify-content:center; align-items:center; margin: 10px 0;">
        <svg width="360" height="320" viewBox="0 0 300 300">
            {grid_lines}
            {axis_lines}
            <polygon points="{poly_pts}" fill="rgba(0, 130, 117, 0.4)" stroke="#008275" stroke-width="2.5"/>
            {labels_svg}
        </svg>
    </div>
    """


@st.cache_data(ttl=86400)
def extract_single_flavor_text(species_data):
  flavor_entries = species_data.get("flavor_text_entries", [])
  for entry in flavor_entries:
    if entry["language"]["name"] == "ko":
      return entry["flavor_text"].replace("\n", " ").replace("\f", " ")

  for entry in flavor_entries:
    if entry["language"]["name"] == "en":
      text = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
      return translate_to_ko(text)

  return "도감 설명이 존재하지 않습니다."


@st.cache_data(ttl=86400)
def get_special_forms(species_data, base_ko_name, species_name):
  special_forms = []
  varieties = species_data.get("varieties", [])

  for v in varieties:
    is_default = v.get("is_default", False)
    v_name = v["pokemon"]["name"]

    if is_default:
      continue

    form_type = ""
    form_ko_title = ""
    form_desc = ""

    if "-alola" in v_name:
      form_type = "알로라폼"
      form_ko_title = f"{base_ko_name} (알로라의 모습)"
      form_desc = "알로라지방의 기후와 환경에 적응해 변화한 모습입니다."
    elif "-galar" in v_name:
      form_type = "가라르폼"
      form_ko_title = f"{base_ko_name} (가라르의 모습)"
      form_desc = "가라르지방의 독특한 환경에서 살아가는 모습입니다."
    elif "-hisui" in v_name:
      form_type = "히스이폼"
      form_ko_title = f"{base_ko_name} (히스이의 모습)"
      form_desc = "과거 히스이지방의 대자연 속에서 살아오며 변화한 모습입니다."
    elif "-mega-x" in v_name:
      form_type = "메가진화"
      form_ko_title = f"메가{base_ko_name} X"
      form_desc = "메가스톤을 이용해 한계를 넘어선 진화를 이룹니다."
    elif "-mega-y" in v_name:
      form_type = "메가진화"
      form_ko_title = f"메가{base_ko_name} Y"
      form_desc = "메가스톤을 이용해 한계를 넘어선 진화를 이룹니다."
    elif "-mega" in v_name:
      form_type = "메가진화"
      form_ko_title = f"메가{base_ko_name}"
      form_desc = "메가스톤을 이용해 한계를 넘어선 진화를 이룹니다."
    elif "-primal" in v_name:
      form_type = "원시회귀"
      form_ko_title = f"원시{base_ko_name}"
      form_desc = (
          "고대의 원시 에너지를 되찾아 본래의 압도적인 힘을 발휘하는 모습입니다."
      )
    elif "-unbound" in v_name:
      form_type = "해방폼"
      form_ko_name = "후파" if "hoopa" in v_name else base_ko_name
      form_ko_title = f"{form_ko_name} (해방된 모습)"
      form_desc = (
          "원래의 끔찍하고 거대한 원래의 모습을 되찾아 모든 것을 꿰뚫는"
          " 파괴력을 가집니다."
      )
    elif "-eternal" in v_name:
      form_type = "영원의꽃"
      form_ko_title = f"{base_ko_name} (영원의 꽃)"
      form_desc = (
          "3천 년 전 왕이 건네주었다는 특별한 영원의 꽃을 품고 있는 모습입니다."
      )
    elif "ash" in v_name:
      form_type = "유대진화"
      form_ko_title = f"{base_ko_name} (지우개굴닌자)"
      form_desc = (
          "트레이너와의 강한 유대로 인해 한계 이상으로 변한 유대진화 모습입니다."
      )
    else:
      continue

    try:
      p_res = requests.get(v["pokemon"]["url"], timeout=2)
      if p_res.status_code == 200:
        p_data = p_res.json()
        img_url = (
            p_data["sprites"]["other"]["official-artwork"]["front_default"]
            or p_data["sprites"]["front_default"]
        )
        shiny_img_url = (
            p_data["sprites"]["other"]["official-artwork"]["front_shiny"]
            or p_data["sprites"]["shiny_default"]
        )

        types_raw = [t["type"]["name"] for t in p_data["types"]]
        types_ko = [TYPE_NAME_MAP.get(t, t) for t in types_raw]
        def_eff, atk_eff = calculate_type_effectiveness(types_raw)

        stats_dict = {}
        total_stats = 0
        for s in p_data["stats"]:
          s_name = STAT_NAME_MAP.get(s["stat"]["name"], s["stat"]["name"])
          s_val = s["base_stat"]
          stats_dict[s_name] = s_val
          total_stats += s_val

        main_flavor = extract_single_flavor_text(species_data)

        special_forms.append({
            "type": form_type,
            "title": form_ko_title,
            "image": img_url,
            "shiny_image": shiny_img_url,
            "types": types_ko,
            "raw_types": types_raw,
            "def_effectiveness": def_eff,
            "atk_effectiveness": atk_eff,
            "stats": stats_dict,
            "total_stats": total_stats,
            "height": p_data["height"] / 10,
            "weight": p_data["weight"] / 10,
            "desc": form_desc or main_flavor,
        })
    except Exception:
      pass

  return special_forms


@st.cache_data(ttl=86400)
def search_pokemon_id_in_generation(query_name, start_id, end_id):
  query_name = query_name.strip().lower()

  if query_name.isdigit():
    num = int(query_name)
    if start_id <= num <= end_id:
      return num
    return None

  try:
    for p_id in range(start_id, end_id + 1):
      ko_name = get_pokemon_name_by_id(p_id)
      if ko_name and query_name in ko_name.lower():
        return p_id
  except Exception:
    pass

  return None


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
  if not target_id:
    return None

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

    main_flavor = extract_single_flavor_text(species_data)

    ko_genus = next(
        (
            g["genus"]
            for g in species_data["genera"]
            if g["language"]["name"] == "ko"
        ),
        "포켓몬",
    )
    gen_roman = (
        species_data["generation"]["name"].replace("generation-", "").upper()
    )
    capture_rate = species_data.get("capture_rate", "정보 없음")

    raw_types = [t["type"]["name"] for t in pokemon_data["types"]]
    ko_types = [TYPE_NAME_MAP.get(t, t) for t in raw_types]

    def_effectiveness, atk_effectiveness = calculate_type_effectiveness(
        raw_types
    )

    stats_dict = {}
    total_stats = 0
    for s in pokemon_data["stats"]:
      s_name = STAT_NAME_MAP.get(s["stat"]["name"], s["stat"]["name"])
      s_val = s["base_stat"]
      stats_dict[s_name] = s_val
      total_stats += s_val

    prev_evos_info, next_evos_info = [], []
    evo_url = species_data.get("evolution_chain", {}).get("url")
    if evo_url:
      evo_res = requests.get(evo_url, timeout=2)
      if evo_res.status_code == 200:
        raw_prev, raw_next = find_evolution_neighbors(
            evo_res.json(), species_data["name"]
        )
        for p in raw_prev:
          info = get_pokemon_info_from_species_url(p["url"])
          if info:
            prev_evos_info.append(info)
        for n in raw_next:
          info = get_pokemon_info_from_species_url(n["url"])
          if info:
            next_evos_info.append(info)

    special_forms = get_special_forms(
        species_data, ko_name, pokemon_data["name"]
    )

    img_url = (
        pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
        or pokemon_data["sprites"]["front_default"]
    )
    shiny_img_url = (
        pokemon_data["sprites"]["other"]["official-artwork"]["front_shiny"]
        or pokemon_data["sprites"]["shiny_default"]
    )

    base_form_data = {
        "type": "기본폼",
        "title": f"{ko_name} (기본폼)",
        "image": img_url,
        "shiny_image": shiny_img_url,
        "types": ko_types,
        "raw_types": raw_types,
        "def_effectiveness": def_effectiveness,
        "atk_effectiveness": atk_effectiveness,
        "stats": stats_dict,
        "total_stats": total_stats,
        "height": pokemon_data["height"] / 10,
        "weight": pokemon_data["weight"] / 10,
        "desc": main_flavor,
    }

    all_forms = [base_form_data] + special_forms

    return {
        "id": pokemon_data["id"],
        "formatted_id": f"No.{str(pokemon_data['id']).zfill(4)}",
        "name": ko_name,
        "english_name": pokemon_data["name"].capitalize(),
        "genus": ko_genus,
        "generation": f"{gen_roman} 세대",
        "capture_rate": capture_rate,
        "forms": all_forms,
        "prev_evos": prev_evos_info,
        "next_evos": next_evos_info,
    }
  except Exception:
    return None


@st.cache_data(ttl=86400)
def get_featured_pokemon_image(query_name):
  try:
    en_name = FEATURED_POKEMON_MAP.get(query_name, query_name.lower())
    res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{en_name}",
        timeout=2,
    )
    if res.status_code == 200:
      p_id = res.json()["id"]
      p_res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon/{p_id}", timeout=2
      )
      if p_res.status_code == 200:
        p_data = p_res.json()
        return (
            p_data["sprites"]["other"]["official-artwork"]["front_default"]
            or p_data["sprites"]["front_default"]
        )
  except Exception:
    pass
  return ""


# 사이드바 네비게이션
st.sidebar.title("⚡ 포켓몬 위키 네비게이션")
if st.sidebar.button("🏠 메인 메뉴", use_container_width=True):
  go_to_page("Main")

if st.sidebar.button("📖 세대별 도감", use_container_width=True):
  go_to_page("포켓몬 도감")

if st.sidebar.button("👤 인물 도감", use_container_width=True):
  go_to_page("인물 도감")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕒 최근 검색 기록")
if st.session_state.search_history:
  if st.sidebar.button("기록 전체 삭제", use_container_width=True):
    st.session_state.search_history = []
    st.rerun()

  for h_item in st.session_state.search_history:
    if st.sidebar.button(
        f"🔍 {h_item}", key=f"side_hist_{h_item}", use_container_width=True
    ):
      st.session_state.search_query = h_item
      if st.session_state.current_page == "Main":
        st.session_state.current_page = "전국 도감"
      st.rerun()
else:
  st.sidebar.write("최근 검색한 기록이 없습니다.")


# ==================== 페이지 라우팅 ====================

if st.session_state.current_page == "Main":
  st.title("⚡ 포켓몬 나무위키 통합 메인")
  st.write("원하시는 도감을 선택하여 상세 정보를 확인해 보세요!")

  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.markdown(
        """
        <div class="menu-card">
            <div style="font-size: 2.0rem; margin-bottom: 6px;">📖</div>
            <div style="font-weight: bold; font-size: 1.1rem; color: #008275; margin-bottom: 4px;">포켓몬 도감</div>
            <div style="font-size: 0.8rem; color: #666;">세대별 포켓몬 목록 및 종족치 확인</div>
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
            <div style="font-size: 0.8rem; color: #666;">트레이너 및 체육관 관장 정보</div>
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

  st.markdown(
      "<h3 class='section-title'>✨ 오늘의 추천 포켓몬 갤러리</h3>",
      unsafe_allow_html=True,
  )
  featured_pokemons = ["켄타로스", "식스테일", "가디", "슬리프", "나무지기", "루브도"]
  f_cols = st.columns(6)
  for idx, p_name in enumerate(featured_pokemons):
    img_url = get_featured_pokemon_image(p_name)
    with f_cols[idx]:
      st.markdown(
          f"""
          <div style="border: 1px solid #333; border-radius: 8px; padding: 10px; text-align: center; background-color: rgba(255,255,255,0.03);">
              <img src="{img_url}" style="width: 100%; height: 100px; object-fit: contain;">
              <p style="font-weight: bold; margin-top: 8px; margin-bottom: 0;">{p_name}</p>
          </div>
          """,
          unsafe_allow_html=True,
      )
      if st.button("이동하기", key=f"feat_btn_{idx}", use_container_width=True):
        st.session_state.search_query = p_name
        st.session_state.selected_gen = None
        add_search_history(p_name)
        go_to_page("전국 도감")
        st.rerun()

elif st.session_state.current_page == "전국 도감":
  st.title("🌐 전국 포켓몬 도감 (No.1 ~ No.1025)")
  st.write("1세대부터 9세대까지 모든 포켓몬을 통합 검색하고 상세 정보를 확인하세요.")

  st.text_input(
      "전국 포켓몬 통합 검색",
      value=st.session_state.search_query,
      key="national_user_input",
      on_change=update_national_search,
      placeholder="포켓몬 이름 또는 번호 입력 (예: 피카츄, 25)...",
  )

  if st.session_state.search_history:
    st.markdown("**최근 검색:**")
    hist_cols = st.columns(min(len(st.session_state.search_history), 8))
    for i, h_term in enumerate(st.session_state.search_history[:8]):
      with hist_cols[i]:
        if st.button(
            f"📌 {h_term}", key=f"nat_chip_hist_{i}", use_container_width=True
        ):
          target_id = search_national_pokemon_id(h_term)
          if target_id:
            st.session_state.search_query = h_term
            st.rerun()
          else:
            st.warning(f"'{h_term}'에 해당하는 포켓몬을 찾을 수 없습니다.")

  query_text = str(st.session_state.search_query).strip()

  if not query_text:
    st.markdown(
        "<h5 style='color: #008275; margin-top:20px;'>위 검색창에 포켓몬 이름이나 번호를 입력하세요. (전체 1025마리 통합)</h5>",
        unsafe_allow_html=True,
    )
  else:
    target_id = search_national_pokemon_id(query_text)

    if target_id and 1 <= target_id <= 1025:
      data = get_pokemon_data(target_id)
      if data:
        current_id = data["id"]
        prev_id = max(1, current_id - 1) if current_id > 1 else None
        next_id = min(1025, current_id + 1) if current_id < 1025 else None

        prev_name = get_pokemon_name_by_id(prev_id) if prev_id else ""
        next_name = get_pokemon_name_by_id(next_id) if next_id else ""

        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
        with btn_col1:
          if prev_id and st.button(
              f"◀ 이전: {prev_name} (No.{str(prev_id).zfill(4)})",
              key="nat_prev",
              use_container_width=True,
          ):
            st.session_state.search_query = str(prev_id)
            add_search_history(prev_name)
            st.rerun()

        with btn_col2:
          if next_id and st.button(
              f"다음: {next_name} (No.{str(next_id).zfill(4)}) ▶",
              key="nat_next",
              use_container_width=True,
          ):
            st.session_state.search_query = str(next_id)
            add_search_history(next_name)
            st.rerun()

        st.markdown(
            f"""
            <h1 class='main-title'>
                {data['name']}
                <small style='font-size:1rem; color:#666;'>| {data['english_name']} ({data['formatted_id']})</small>
            </h1>
            """,
            unsafe_allow_html=True,
        )

        form_tab_titles = [f["type"] for f in data["forms"]]
        form_tabs = st.tabs(form_tab_titles)

        for tab_idx, form_info in enumerate(data["forms"]):
          with form_tabs[tab_idx]:
            type_badges_html = "".join([
                f"<span class='type-badge"
                f" {get_type_color_class(t)}'>{t}</span>"
                for t in form_info["types"]
            ])
            st.markdown(
                f"### {form_info['title']} {type_badges_html}",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1.8, 1.2])

            with col1:
              st.markdown(
                  "<h3 class='section-title'>1. 개요 및 도감 설명</h3>",
                  unsafe_allow_html=True,
              )
              st.info(form_info["desc"])

              st.markdown(
                  "<h3 class='section-title'>2. 육각형 종족치 그래프</h3>",
                  unsafe_allow_html=True,
              )
              st.markdown(
                  generate_hexagon_svg(form_info["stats"]),
                  unsafe_allow_html=True,
              )

              stat_cols = st.columns(3)
              for idx, (stat_name, stat_val) in enumerate(
                  form_info["stats"].items()
              ):
                with stat_cols[idx % 3]:
                  st.metric(label=stat_name, value=stat_val)

              st.write(f"**종족치 총합:** `{form_info['total_stats']}`")

              if tab_idx == 0 and (data["prev_evos"] or data["next_evos"]):
                st.markdown(
                    "<h3 class='section-title'>3. 진화</h3>",
                    unsafe_allow_html=True,
                )
                if data["prev_evos"]:
                  st.write("**이전 진화 형태**")
                  cols = st.columns(min(len(data["prev_evos"]), 3))
                  for i, evo in enumerate(data["prev_evos"]):
                    with cols[i % 3]:
                      st.markdown(
                          f"<div class='evo-card'><img"
                          f" src='{evo['image']}'><div"
                          " class='evo-info'><div"
                          f" class='evo-id'>{evo['formatted_id']}</div><div"
                          f" class='evo-name'>{evo['name']}</div></div></div>",
                          unsafe_allow_html=True,
                      )
                if data["next_evos"]:
                  st.write("**다음 진화 형태**")
                  cols = st.columns(min(len(data["next_evos"]), 3))
                  for i, evo in enumerate(data["next_evos"]):
                    with cols[i % 3]:
                      st.markdown(
                          f"<div class='evo-card'><img"
                          f" src='{evo['image']}'><div"
                          " class='evo-info'><div"
                          f" class='evo-id'>{evo['formatted_id']}</div><div"
                          f" class='evo-name'>{evo['name']}</div></div></div>",
                          unsafe_allow_html=True,
                      )

              st.markdown(
                  "<h3 class='section-title'>4. 타입 상성</h3>",
                  unsafe_allow_html=True,
              )
              st.write("##### **[공격 상성]** (자신의 타입 기술로 공격 시 배율)")
              st.markdown(
                  render_type_table(
                      form_info["atk_effectiveness"], is_defense=False
                  ),
                  unsafe_allow_html=True,
              )

              st.write(
                  "##### **[방어 상성]** (상대 타입 기술로 공격받을 때 배율)"
              )
              st.markdown(
                  render_type_table(
                      form_info["def_effectiveness"], is_defense=True
                  ),
                  unsafe_allow_html=True,
              )

            with col2:
              st.markdown(
                  f"<div class='infobox'><div"
                  f" class='infobox-title'>{form_info['title']}</div></div>",
                  unsafe_allow_html=True,
              )

              sub_tab1, sub_tab2 = st.tabs(["일반", "✨ 이로치"])
              with sub_tab1:
                st.image(form_info["image"], use_container_width=True)
              with sub_tab2:
                if form_info["shiny_image"]:
                  st.image(
                      form_info["shiny_image"], use_container_width=True
                  )
                else:
                  st.write("이로치 이미지가 없습니다.")

              st.table({
                  "속성": [
                      "전국도감 번호",
                      "분류",
                      "세대",
                      "신장",
                      "체중",
                      "포획률",
                  ],
                  "정보": [
                      data["formatted_id"],
                      data["genus"],
                      data["generation"],
                      f"{form_info['height']} m",
                      f"{form_info['weight']} kg",
                      f"{data['capture_rate']}",
                  ],
              })
    else:
      st.error(f"'{query_text}'에 해당하는 포켓몬을 찾을 수 없습니다.")

elif st.session_state.current_page == "포켓몬 도감":
  st.title("📖 세대별 포켓몬 도감")

  if not st.session_state.selected_gen:
    st.write(
        "**원하시는 세대 도감을 선택하여 해당 세대 포켓몬만 탐색 및 검색하세요.**"
    )
    st.markdown(
        "<h3 class='section-title'>📦 세대별 도감 선택</h3>", unsafe_allow_html=True
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
                st.session_state.search_query = ""
                st.rerun()

  else:
    g_name = st.session_state.selected_gen
    start_id, end_id = GENERATIONS[g_name]["range"]

    col_back, col_title = st.columns([1, 4])
    with col_back:
      if st.button("◀ 세대 목록으로", use_container_width=True):
        st.session_state.selected_gen = None
        st.session_state.search_query = ""
        st.rerun()
    with col_title:
      st.markdown(f"### ⚡ {g_name} 도감 (No.{start_id} ~ No.{end_id})")

    st.text_input(
        f"{g_name} 포켓몬 검색",
        value=st.session_state.search_query,
        key="user_input",
        on_change=update_search,
        placeholder=(
            f"{g_name} 범위 내 이름 또는 번호 입력 (No.{start_id}~{end_id})..."
        ),
    )

    if st.session_state.search_history:
      st.markdown("**최근 검색:**")
      hist_cols = st.columns(min(len(st.session_state.search_history), 8))
      for i, h_term in enumerate(st.session_state.search_history[:8]):
        with hist_cols[i]:
          if st.button(
              f"📌 {h_term}", key=f"chip_hist_{i}", use_container_width=True
          ):
            target_id = search_pokemon_id_in_generation(
                h_term, start_id, end_id
            )
            if target_id:
              st.session_state.search_query = h_term
              st.rerun()
            else:
              st.warning(
                  f"'{h_term}'은(는) {g_name} 도감(No.{start_id}~{end_id})"
                  " 범위에 없습니다."
              )

    query_text = str(st.session_state.search_query).strip()

    if not query_text:
      st.markdown(
          f"<h5 style='color: #008275; margin-top:20px;'>포켓몬을 선택하거나"
          " 위 검색창에 이름을 입력하세요.</h5>",
          unsafe_allow_html=True,
      )

      poke_cols = st.columns(3)
      for p_id in range(start_id, end_id + 1):
        p_name = get_pokemon_name_by_id(p_id)
        col_idx = (p_id - start_id) % 3
        with poke_cols[col_idx]:
          if st.button(
              f"No.{str(p_id).zfill(4)} {p_name}",
              key=f"poke_list_{p_id}",
              use_container_width=True,
          ):
            st.session_state.search_query = str(p_id)
            add_search_history(p_name)
            st.rerun()

    else:
      target_id = search_pokemon_id_in_generation(
          query_text, start_id, end_id
      )

      if target_id and start_id <= target_id <= end_id:
        data = get_pokemon_data(target_id)
        if data:
          current_id = data["id"]
          prev_id = (
              max(start_id, current_id - 1) if current_id > start_id else None
          )
          next_id = (
              min(end_id, current_id + 1) if current_id < end_id else None
          )

          prev_name = get_pokemon_name_by_id(prev_id) if prev_id else ""
          next_name = get_pokemon_name_by_id(next_id) if next_id else ""

          btn_col1, btn_col2, _ = st.columns([1, 1, 2])
          with btn_col1:
            if prev_id and st.button(
                f"◀ 이전: {prev_name} (No.{str(prev_id).zfill(4)})",
                use_container_width=True,
            ):
              st.session_state.search_query = str(prev_id)
              add_search_history(prev_name)
              st.rerun()

          with btn_col2:
            if next_id and st.button(
                f"다음: {next_name} (No.{str(next_id).zfill(4)}) ▶",
                use_container_width=True,
            ):
              st.session_state.search_query = str(next_id)
              add_search_history(next_name)
              st.rerun()

          st.markdown(
              f"""
              <h1 class='main-title'>
                  {data['name']}
                  <small style='font-size:1rem; color:#666;'>| {data['english_name']} ({data['formatted_id']})</small>
              </h1>
              """,
              unsafe_allow_html=True,
          )

          form_tab_titles = [f["type"] for f in data["forms"]]
          form_tabs = st.tabs(form_tab_titles)

          for tab_idx, form_info in enumerate(data["forms"]):
            with form_tabs[tab_idx]:
              type_badges_html = "".join([
                  f"<span class='type-badge"
                  f" {get_type_color_class(t)}'>{t}</span>"
                  for t in form_info["types"]
              ])
              st.markdown(
                  f"### {form_info['title']} {type_badges_html}",
                  unsafe_allow_html=True,
              )

              col1, col2 = st.columns([1.8, 1.2])

              with col1:
                st.markdown(
                    "<h3 class='section-title'>1. 개요 및 도감 설명</h3>",
                    unsafe_allow_html=True,
                )
                st.info(form_info["desc"])

                st.markdown(
                    "<h3 class='section-title'>2. 육각형 종족치 그래프</h3>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    generate_hexagon_svg(form_info["stats"]),
                    unsafe_allow_html=True,
                )

                stat_cols = st.columns(3)
                for idx, (stat_name, stat_val) in enumerate(
                    form_info["stats"].items()
                ):
                  with stat_cols[idx % 3]:
                    st.metric(label=stat_name, value=stat_val)

                st.write(f"**종족치 총합:** `{form_info['total_stats']}`")

                if tab_idx == 0 and (data["prev_evos"] or data["next_evos"]):
                  st.markdown(
                      "<h3 class='section-title'>3. 진화</h3>",
                      unsafe_allow_html=True,
                  )
                  if data["prev_evos"]:
                    st.write("**이전 진화 형태**")
                    cols = st.columns(min(len(data["prev_evos"]), 3))
                    for i, evo in enumerate(data["prev_evos"]):
                      with cols[i % 3]:
                        st.markdown(
                            f"<div class='evo-card'><img"
                            f" src='{evo['image']}'><div"
                            " class='evo-info'><div"
                            f" class='evo-id'>{evo['formatted_id']}</div><div"
                            f" class='evo-name'>{evo['name']}</div></div></div>",
                            unsafe_allow_html=True,
                        )
                  if data["next_evos"]:
                    st.write("**다음 진화 형태**")
                    cols = st.columns(min(len(data["next_evos"]), 3))
                    for i, evo in enumerate(data["next_evos"]):
                      with cols[i % 3]:
                        st.markdown(
                            f"<div class='evo-card'><img"
                            f" src='{evo['image']}'><div"
                            " class='evo-info'><div"
                            f" class='evo-id'>{evo['formatted_id']}</div><div"
                            f" class='evo-name'>{evo['name']}</div></div></div>",
                            unsafe_allow_html=True,
                        )

                st.markdown(
                    "<h3 class='section-title'>4. 타입 상성</h3>",
                    unsafe_allow_html=True,
                )
                st.write(
                    "##### **[공격 상성]** (자신의 타입 기술로 공격 시 배율)"
                )
                st.markdown(
                    render_type_table(
                        form_info["atk_effectiveness"], is_defense=False
                    ),
                    unsafe_allow_html=True,
                )

                st.write(
                    "##### **[방어 상성]** (상대 타입 기술로 공격받을 때 배율)"
                )
                st.markdown(
                    render_type_table(
                        form_info["def_effectiveness"], is_defense=True
                    ),
                    unsafe_allow_html=True,
                )

              with col2:
                st.markdown(
                    f"<div class='infobox'><div"
                    f" class='infobox-title'>{form_info['title']}</div></div>",
                    unsafe_allow_html=True,
                )

                sub_tab1, sub_tab2 = st.tabs(["일반", "✨ 이로치"])
                with sub_tab1:
                  st.image(form_info["image"], use_container_width=True)
                with sub_tab2:
                  if form_info["shiny_image"]:
                    st.image(
                        form_info["shiny_image"], use_container_width=True
                    )
                  else:
                    st.write("이로치 이미지가 없습니다.")

                st.table({
                    "속성": [
                        "전국도감 번호",
                        "분류",
                        "세대",
                        "신장",
                        "체중",
                        "포획률",
                    ],
                    "정보": [
                        data["formatted_id"],
                        data["genus"],
                        data["generation"],
                        f"{form_info['height']} m",
                        f"{form_info['weight']} kg",
                        f"{data['capture_rate']}",
                    ],
                })
      else:
        st.error(
            f"'{query_text}'은(는) {g_name} 도감(No.{start_id} ~ No.{end_id})"
            " 범위 내에서 찾을 수 없습니다."
        )

elif st.session_state.current_page == "인물 도감":
  st.title("👤 세대별 인물 도감")

  if not st.session_state.selected_char_gen:
    st.write(
        "**원하시는 세대를 선택하여 해당 세대에 등장하는 주요 인물 및 관장"
        " 정보를 탐색하세요.**"
    )
    st.markdown(
        "<h3 class='section-title'>📦 세대별 인물 도감 선택</h3>",
        unsafe_allow_html=True,
    )

    # 9세대는 8세대 우측, 히스이 지방은 8세대 아래에 배치된 레이아웃 구조
    row1 = ["1세대 (관동)", "2세대 (성도)", "3세대 (호연)"]
    row2 = ["4세대 (신오)", "5세대 (하나)", "6세대 (칼로스)"]
    row3 = ["7세대 (알로라)", "8세대 (가라르)", "9세대 (팔데아)"]
    row4 = [None, "히스이 지방", None]

    layout_rows = [row1, row2, row3, row4]

    for r_idx, r_items in enumerate(layout_rows):
      cols = st.columns(3)
      for c_idx, g_name in enumerate(r_items):
        if g_name is not None and g_name in CHARACTER_GENERATIONS:
          g_info = CHARACTER_GENERATIONS[g_name]
          with cols[c_idx]:
            st.markdown(
                f"""
                <div class="char-banner" style="background-color: {g_info['color']};">
                    {g_name}<br>
                    <span style="font-size: 0.85rem; font-weight: normal;">주요 인물 및 관장 목록</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"{g_name} 인물 도감 입장",
                key=f"char_gen_btn_{r_idx}_{c_idx}",
                use_container_width=True,
            ):
              st.session_state.selected_char_gen = g_name
              st.session_state.character_search_query = ""
              st.rerun()

  else:
    g_name = st.session_state.selected_char_gen
    g_data = CHARACTER_GENERATIONS[g_name]

    col_back, col_title = st.columns([1, 4])
    with col_back:
      if st.button("◀ 세대 목록으로", use_container_width=True):
        st.session_state.selected_char_gen = None
        st.session_state.character_search_query = ""
        st.rerun()
    with col_title:
      st.markdown(f"### 👤 {g_name} 인물 도감")

    st.text_input(
        f"{g_name} 인물 검색",
        value=st.session_state.character_search_query,
        key="char_user_input",
        on_change=update_character_search,
        placeholder=f"{g_name} 인물 이름을 입력하세요...",
    )

    query_text = str(st.session_state.character_search_query).strip()

    characters = g_data["characters"]
    if query_text:
      characters = [
          c for c in characters if query_text.lower() in c["name"].lower()
      ]

    if not characters:
      st.warning(f"'{query_text}'에 해당하는 인물을 찾을 수 없습니다.")
    else:
      for char in characters:
        st.markdown(
            f"""
            <div class="char-card">
                <h3 style="margin-top: 0; color: #008275;">{char['name']} <small style="font-size: 0.9rem; color: #666;">({char['title']})</small></h3>
                <p><b>전문 분야:</b> {char['specialty']}</p>
                <p><b>설명:</b> {char['desc']}</p>
                <p><b>주요 포켓몬:</b> {', '.join(char['pokemon'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif st.session_state.current_page == "맵 도감":
  st.title("🗺️ 맵 도감")
  st.info("준비 중인 페이지입니다.")
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
