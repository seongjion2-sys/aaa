import json
import math
import time
import urllib.parse
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="포켓몬 위키", page_icon="⚡", layout="wide")

# Session State 초기화
if "search_query" not in st.session_state:
  st.session_state.search_query = ""  # 초기 검색어를 빈 값으로 설정

if "current_page" not in st.session_state:
  st.session_state.current_page = "메인"  # 기본 페이지: 메인 메뉴


# 페이지 이동 함수
def go_to_page(page_name):
  st.session_state.current_page = page_name


# 검색어 업데이트 콜백
def update_search():
  st.session_state.search_query = st.session_state.user_input
  st.session_state.current_page = "포켓몬 도감"


# CSS 스타일 적용
st.markdown(
    """
    <style>
    :root {
        --wiki-main: #008275;
    }
    /* 검색창 크기 및 스타일 확대 */
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
def get_special_forms(species_data, base_ko_name):
  special_forms = []
  varieties = species_data.get("varieties", [])

  for v in varieties:
    is_default = v.get("is_default", False)
    v_name = v["pokemon"]["name"]

    if is_default:
      continue

    if "-mega" not in v_name and "ash" not in v_name:
      continue

    form_type = ""
    form_ko_title = ""
    form_desc = ""

    if "-mega-x" in v_name:
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
def search_pokemon_id_by_name(query_name):
  query_name = query_name.strip()
  try:
    res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{query_name.lower()}",
        timeout=2,
    )
    if res.status_code == 200:
      return res.json()["id"]
  except Exception:
    pass

  for i in range(1, 1026):
    name = get_pokemon_name_by_id(i)
    if name == query_name:
      return i
  return None


@st.cache_data(ttl=86400)
def get_pokemon_data(query):
  query = str(query).strip()
  target_id = (
      int(query) if query.isdigit() else search_pokemon_id_by_name(query)
  )

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

    special_forms = get_special_forms(species_data, ko_name)

    img_url = (
        pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
        or pokemon_data["sprites"]["front_default"]
    )
    shiny_img_url = (
        pokemon_data["sprites"]["other"]["official-artwork"]["front_shiny"]
        or pokemon_data["sprites"]["shiny_default"]
    )

    base_form_data = {
        "type": "기본",
        "title": f"{ko_name} (기본)",
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
  target_id = search_pokemon_id_by_name(query_name)
  if target_id:
    try:
      res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon/{target_id}", timeout=2
      )
      if res.status_code == 200:
        p_data = res.json()
        return (
            p_data["sprites"]["other"]["official-artwork"]["front_default"]
            or p_data["sprites"]["front_default"]
        )
    except Exception:
      pass
  return ""


# 사이드바 네비게이션 (메인 메뉴만 남김)
st.sidebar.title("⚡ 포켓몬 위키 네비게이션")
if st.sidebar.button("🏠 메인 메뉴", use_container_width=True):
  go_to_page("메인")


# ==================== 페이지 라우팅 ====================

if st.session_state.current_page == "메인":
  st.title("⚡ 포켓몬 나무위키 통합 메인")
  st.write("원하시는 도감을 선택하여 상세 정보를 확인해 보세요!")

  st.write("")
  col1, col2, col3 = st.columns(3)

  with col1:
    st.markdown(
        """
        <div style="border: 2px solid #008275; border-radius: 12px; padding: 20px; text-align: center; background-color: #f8f9fa; height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <h1 style="font-size: 3rem; margin: 0;">📖</h1>
            <h3 style="color: #008275; margin: 10px 0;">포켓몬 도감</h3>
            <p style="color: #555; font-size: 0.9rem;">전국 포켓몬들의 상세 정보, 종족치, 진화 및 타입 상성을 확인하세요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("포켓몬 도감 이동하기", use_container_width=True):
      st.session_state.search_query = ""
      go_to_page("포켓몬 도감")

  with col2:
    st.markdown(
        """
        <div style="border: 2px solid #008275; border-radius: 12px; padding: 20px; text-align: center; background-color: #f8f9fa; height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <h1 style="font-size: 3rem; margin: 0;">👤</h1>
            <h3 style="color: #008275; margin: 10px 0;">인물 도감</h3>
            <p style="color: #555; font-size: 0.9rem;">포켓몬 세계관의 주요 트레이너, 체육관 관장 및 챔피언 정보를 확인하세요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("인물 도감 이동하기", use_container_width=True):
      go_to_page("인물 도감")

  with col3:
    st.markdown(
        """
        <div style="border: 2px solid #008275; border-radius: 12px; padding: 20px; text-align: center; background-color: #f8f9fa; height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <h1 style="font-size: 3rem; margin: 0;">🗺️</h1>
            <h3 style="color: #008275; margin: 10px 0;">맵 도감</h3>
            <p style="color: #555; font-size: 0.9rem;">지방별 주요 필드, 도시, 도로 및 서식지 정보를 탐색해보세요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("맵 도감 이동하기", use_container_width=True):
      go_to_page("맵 도감")

  st.markdown("<h3 class='section-title'>✨ 오늘의 추천 포켓몬 갤러리</h3>", unsafe_allow_html=True)
  
  featured_pokemons = ["딜리버드", "귀뚤뚜기", "헤라크로스", "슬리프", "나무지기", "루브도"]
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

elif st.session_state.current_page == "포켓몬 도감":
  st.title("📖 포켓몬 도감")

  st.write(
      "**포켓몬 이름 또는 도감 번호를 입력하세요 (예: 개굴닌자, 리자몽, 뮤츠)**"
  )
  st.text_input(
      "포켓몬 검색",
      value=st.session_state.search_query,
      key="user_input",
      on_change=update_search,
      label_visibility="collapsed",
      placeholder="포켓몬 이름 또는 도감 번호 입력...",
  )

  if not st.session_state.search_query.strip():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: center; color: #888;'>포켓몬을 검색해"
        " 보세요!</h2>",
        unsafe_allow_html=True,
    )
  else:
    query_text = str(st.session_state.search_query).strip()
    data = get_pokemon_data(query_text)

    if data:
      current_id = data["id"]
      prev_id, next_id = max(1, current_id - 1), min(1025, current_id + 1)
      prev_name = get_pokemon_name_by_id(prev_id) if current_id > 1 else ""
      next_name = get_pokemon_name_by_id(next_id) if current_id < 1025 else ""

      btn_col1, btn_col2, _ = st.columns([1, 1, 2])
      with btn_col1:
        if current_id > 1 and st.button(
            f"◀ 이전: {prev_name} (No.{str(prev_id).zfill(4)})",
            use_container_width=True,
        ):
          st.session_state.search_query = str(prev_id)
          st.rerun()

      with btn_col2:
        if current_id < 1025 and st.button(
            f"다음: {next_name} (No.{str(next_id).zfill(4)}) ▶",
            use_container_width=True,
        ):
          st.session_state.search_query = str(next_id)
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

      form_tab_titles = []
      for f in data["forms"]:
        if f["type"] == "기본":
          form_tab_titles.append("기본 폼")
        else:
          form_tab_titles.append(f["type"])

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
                generate_hexagon_svg(form_info["stats"]), unsafe_allow_html=True
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

            st.write("##### **[방어 상성]** (상대 타입 기술로 공격받을 때 배율)")
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
                st.image(form_info["shiny_image"], use_container_width=True)
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
          f"'{st.session_state.search_query}' 포켓몬 정보를 찾을 수 없습니다."
      )

elif st.session_state.current_page == "인물 도감":
  st.title("👤 인물 도감")
  st.info("준비 중인 페이지입니다. 포켓몬 세계관의 주요 인물들을 만나보세요!")

elif st.session_state.current_page == "맵 도감":
  st.title("🗺️ 맵 도감")
  st.info("준비 중인 페이지입니다. 포켓몬 세계의 다양한 지방과 장소를 탐색해보세요!")
