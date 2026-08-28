import json
import math
import urllib.parse
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="포켓몬 위키", page_icon="⚡", layout="wide")

# Session State 초기화
if "search_query" not in st.session_state:
  st.session_state.search_query = "5"  # 기본값: No.5 (리자드)


# 검색어 업데이트 콜백
def update_search():
  st.session_state.search_query = st.session_state.user_input


# CSS 스타일 적용 (나무위키 스타일 테이블 & 타입 배경색 정의)
st.markdown(
    """
    <style>
    :root {
        --wiki-main: #008275;
    }
    .main-title {
        color: var(--wiki-main);
        font-weight: bold;
        border-bottom: 2px solid var(--wiki-main);
        padding-bottom: 5px;
        display: flex;
        align-items: baseline;
        gap: 10px;
        flex-wrap: wrap;
    }
    .type-badge {
        background-color: var(--wiki-main);
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: normal;
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

    /* 나무위키 상성 표 스타일 */
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
        color: white;
        font-weight: bold;
        font-size: 0.82rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }

    /* 포켓몬 공식 타입별 고유 색상 */
    .bg-normal { background-color: #A8A878; }
    .bg-fire { background-color: #F08030; }
    .bg-water { background-color: #6890F0; }
    .bg-grass { background-color: #78C850; }
    .bg-electric { background-color: #F8D030; color: #000 !important; }
    .bg-ice { background-color: #98D8D8; color: #000 !important; }
    .bg-fighting { background-color: #C03028; }
    .bg-poison { background-color: #A040A0; }
    .bg-ground { background-color: #E0C068; color: #000 !important; }
    .bg-flying { background-color: #A890F0; }
    .bg-psychic { background-color: #F85888; }
    .bg-bug { background-color: #A8B820; }
    .bg-rock { background-color: #B8A038; }
    .bg-ghost { background-color: #70559B; }
    .bg-dragon { background-color: #7038F8; }
    .bg-dark { background-color: #705848; }
    .bg-steel { background-color: #B8B8D0; color: #000 !important; }
    .bg-fairy { background-color: #EE99AC; color: #000 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# 종족치 & 타입 한글 매핑
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

ALL_TYPES = list(TYPE_NAME_MAP.keys())


# 방어 및 공격 상성 상세 계산 함수
@st.cache_data(ttl=86400)
def calculate_type_effectiveness(raw_types):
  # 1. 방어 상성 (상대가 나에게 주는 피해 배율)
  defense_relations = {t: 1.0 for t in ALL_TYPES}
  for t_name in raw_types:
    try:
      res = requests.get(
          f"https://pokeapi.co/api/v2/type/{t_name}", timeout=3
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

  # 2. 공격 상성 (내가 가진 자속 타입 기술로 상대에게 주는 최대 피해 배율)
  attack_relations = {t: 0.0 for t in ALL_TYPES}
  for t_name in raw_types:
    try:
      res = requests.get(
          f"https://pokeapi.co/api/v2/type/{t_name}", timeout=3
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


# 상성 HTML 표 생성 함수
def render_type_table(grouped_data, is_defense=True):
  # 방어 시 배율 목록 (4배~0배)
  if is_defense:
    multipliers = [4.0, 2.0, 1.0, 0.5, 0.25, 0.0]
  else:  # 공격 시 배율 목록 (2배~0배)
    multipliers = [2.0, 1.0, 0.5, 0.0]

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


# 구글 번역 함수
def translate_to_ko(text):
  try:
    encoded_text = urllib.parse.quote(text)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={encoded_text}"
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      data = res.json()
      return "".join([item[0] for item in data[0] if item[0]])
  except Exception:
    pass
  return text


# ID로 포켓몬 한글 이름 가져오는 함수 (캐싱 적용)
@st.cache_data(ttl=86400)
def get_pokemon_name_by_id(pokemon_id):
  try:
    res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}", timeout=3
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


# species URL로부터 한글 이름, 도감 번호, 이미지 가져오기
def get_pokemon_info_from_species_url(url):
  try:
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      data = res.json()
      p_id = data["id"]
      formatted_id = f"No.{str(p_id).zfill(4)}"
      ko_name = next(
          (n["name"] for n in data["names"] if n["language"]["name"] == "ko"),
          data["name"],
      )

      p_res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon/{p_id}", timeout=3
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


# 진화 트리를 탐색하여 이전/다음 진화체 찾기
def find_evolution_neighbors(chain, target_species_name):
  prev_evos = []
  next_evos = []

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


# 육각형 레이더 차트 (SVG)
def generate_hexagon_svg(stats):
  keys = ["체력(HP)", "공격", "방어", "특수공격", "특수방어", "스피드"]
  vals = [stats.get(k, 0) for k in keys]
  max_val = 160.0

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


# 한국어 이름 -> ID 검색 (캐싱)
@st.cache_data(ttl=86400)
def search_pokemon_id_by_name(query_name):
  query_name = query_name.strip()

  # 1. 영문명 시도
  try:
    res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{query_name.lower()}",
        timeout=2,
    )
    if res.status_code == 200:
      return res.json()["id"]
  except Exception:
    pass

  # 2. 전국도감 범위 내 한글 검색
  for i in range(1, 1026):
    name = get_pokemon_name_by_id(i)
    if name == query_name:
      return i

  return None


# 포켓몬 데이터 가져오기
@st.cache_data
def get_pokemon_data(query):
  query = str(query).strip()
  target_id = None

  if query.isdigit():
    target_id = int(query)
  else:
    target_id = search_pokemon_id_by_name(query)

  if not target_id:
    return None

  try:
    pokemon_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{target_id}", timeout=3
    )
    if pokemon_res.status_code != 200:
      return None
    pokemon_data = pokemon_res.json()

    species_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{target_id}", timeout=3
    )
    species_data = species_res.json()

    # 한글 이름
    ko_name = next(
        (
            n["name"]
            for n in species_data["names"]
            if n["language"]["name"] == "ko"
        ),
        pokemon_data["name"],
    )

    # 도감 설명
    ko_flavor_list = [
        f["flavor_text"]
        for f in species_data["flavor_text_entries"]
        if f["language"]["name"] == "ko"
    ]
    if ko_flavor_list:
      ko_flavor = ko_flavor_list[-1].replace("\n", " ").replace("\f", " ")
    else:
      en_flavor_list = [
          f["flavor_text"]
          for f in species_data["flavor_text_entries"]
          if f["language"]["name"] == "en"
      ]
      if en_flavor_list:
        raw_en = en_flavor_list[-1].replace("\n", " ").replace("\f", " ")
        ko_flavor = translate_to_ko(raw_en)
      else:
        ko_flavor = "도감 설명이 존재하지 않습니다."

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

    # 방어 상성 및 공격 상성 계산
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

    # 진화 상세 정보
    prev_evos_info = []
    next_evos_info = []

    evo_url = species_data.get("evolution_chain", {}).get("url")
    if evo_url:
      evo_res = requests.get(evo_url, timeout=3)
      if evo_res.status_code == 200:
        evo_chain = evo_res.json()
        raw_prev, raw_next = find_evolution_neighbors(
            evo_chain, species_data["name"]
        )

        for p in raw_prev:
          info = get_pokemon_info_from_species_url(p["url"])
          if info:
            prev_evos_info.append(info)

        for n in raw_next:
          info = get_pokemon_info_from_species_url(n["url"])
          if info:
            next_evos_info.append(info)

    img_url = (
        pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
        or pokemon_data["sprites"]["front_default"]
    )

    return {
        "id": pokemon_data["id"],
        "formatted_id": f"No.{str(pokemon_data['id']).zfill(4)}",
        "name": ko_name,
        "english_name": pokemon_data["name"].capitalize(),
        "genus": ko_genus,
        "generation": f"{gen_roman} 세대",
        "capture_rate": capture_rate,
        "height": pokemon_data["height"] / 10,
        "weight": pokemon_data["weight"] / 10,
        "image": img_url,
        "description": ko_flavor,
        "types": ko_types,
        "def_effectiveness": def_effectiveness,
        "atk_effectiveness": atk_effectiveness,
        "stats": stats_dict,
        "total_stats": total_stats,
        "prev_evos": prev_evos_info,
        "next_evos": next_evos_info,
    }
  except Exception:
    return None


# 메인 화면 UI
st.title("⚡ 포켓몬 나무위키")

# 검색 입력창
st.text_input(
    "포켓몬 이름 또는 도감 번호를 입력하세요 (예: 피카츄, 5, Pikachu)",
    value=st.session_state.search_query,
    key="user_input",
    on_change=update_search,
)

if st.session_state.search_query:
  query_text = str(st.session_state.search_query).strip()

  if query_text.isdigit():
    loading_msg = (
        f"⚡ No.{query_text} 포켓몬 정보 조회 중... (예상 대기시간: 약 0.5초)"
    )
  elif query_text.isascii():
    loading_msg = (
        f"⚡ '{query_text}' 영문 정보 조회 중... (예상 대기시간: 약 0.5초)"
    )
  else:
    loading_msg = (
        f"🔍 '{query_text}' 한글 포켓몬 검색 중... (예상 대기시간: 최초 1~3초,"
        " 재검색 시 즉시)"
    )

  with st.spinner(loading_msg):
    data = get_pokemon_data(query_text)

  if data:
    current_id = data["id"]
    prev_id = max(1, current_id - 1)
    next_id = min(1025, current_id + 1)

    # 이전 / 다음 포켓몬 이름 불러오기
    prev_name = get_pokemon_name_by_id(prev_id) if current_id > 1 else ""
    next_name = get_pokemon_name_by_id(next_id) if current_id < 1025 else ""

    # 이전 / 다음 포켓몬 버튼 이동 제어
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    with btn_col1:
      if current_id > 1:
        if st.button(
            f"◀ 이전: {prev_name} (No.{str(prev_id).zfill(4)})",
            use_container_width=True,
        ):
          st.session_state.search_query = str(prev_id)
          st.rerun()

    with btn_col2:
      if current_id < 1025:
        if st.button(
            f"다음: {next_name} (No.{str(next_id).zfill(4)}) ▶",
            use_container_width=True,
        ):
          st.session_state.search_query = str(next_id)
          st.rerun()

    type_badges_html = "".join(
        [f"<span class='type-badge'>{t}</span>" for t in data["types"]]
    )

    st.markdown(
        f"""
        <h1 class='main-title'>
            {data['name']}
            <small style='font-size:1rem; color:#666;'>| {data['english_name']} ({data['formatted_id']})</small>
            {type_badges_html}
        </h1>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.8, 1.2])

    with col1:
      st.markdown(
          "<h3 class='section-title'>1. 개요</h3>", unsafe_allow_html=True
      )
      st.write(
          f"**{data['name']}**은(는) {data['generation']}에 처음 등장한"
          f" {data['genus']}입니다."
      )

      st.markdown(
          "<h3 class='section-title'>2. 도감 설명</h3>",
          unsafe_allow_html=True,
      )
      st.info(f'"{data["description"]}"')

      st.markdown(
          "<h3 class='section-title'>3. 육각형 종족치 그래프</h3>",
          unsafe_allow_html=True,
      )
      st.markdown(generate_hexagon_svg(data["stats"]), unsafe_allow_html=True)

      stat_cols = st.columns(3)
      idx = 0
      for stat_name, stat_val in data["stats"].items():
        with stat_cols[idx % 3]:
          st.metric(label=stat_name, value=stat_val)
        idx += 1

      st.write(f"**종족치 총합:** `{data['total_stats']}`")

      # '4. 진화' 섹션
      if data["prev_evos"] or data["next_evos"]:
        st.markdown(
            "<h3 class='section-title'>4. 진화</h3>", unsafe_allow_html=True
        )

        if data["prev_evos"]:
          st.write("**이전 진화 형태**")
          cols = st.columns(min(len(data["prev_evos"]), 3))
          for i, evo in enumerate(data["prev_evos"]):
            with cols[i % 3]:
              st.markdown(
                  f"""
                                <div class='evo-card'>
                                    <img src='{evo['image']}'>
                                    <div class='evo-info'>
                                        <div class='evo-id'>{evo['formatted_id']}</div>
                                        <div class='evo-name'>{evo['name']}</div>
                                    </div>
                                </div>
                            """,
                  unsafe_allow_html=True,
              )

        if data["next_evos"]:
          st.write("**다음 진화 형태**")
          cols = st.columns(min(len(data["next_evos"]), 3))
          for i, evo in enumerate(data["next_evos"]):
            with cols[i % 3]:
              st.markdown(
                  f"""
                                <div class='evo-card'>
                                    <img src='{evo['image']}'>
                                    <div class='evo-info'>
                                        <div class='evo-id'>{evo['formatted_id']}</div>
                                        <div class='evo-name'>{evo['name']}</div>
                                    </div>
                                </div>
                            """,
                  unsafe_allow_html=True,
              )

      # '5. 타입 상성' 섹션
      st.markdown(
          "<h3 class='section-title'>5. 타입 상성</h3>", unsafe_allow_html=True
      )

      # 5.1 공격 상성
      st.write("##### **[공격 상성]** (자신의 타입 기술로 공격 시 배율)")
      st.markdown(
          render_type_table(data["atk_effectiveness"], is_defense=False),
          unsafe_allow_html=True,
      )

      # 5.2 방어 상성
      st.write("##### **[방어 상성]** (상대 타입 기술로 공격받을 때 배율)")
      st.markdown(
          render_type_table(data["def_effectiveness"], is_defense=True),
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          f"""
                <div class='infobox'>
                    <div class='infobox-title'>{data['name']}</div>
                </div>
            """,
          unsafe_allow_html=True,
      )
      st.image(data["image"], use_container_width=True)

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
              f"{data['height']} m",
              f"{data['weight']} kg",
              f"{data['capture_rate']}",
          ],
      })
  else:
    st.error(
        f"'{st.session_state.search_query}' 포켓몬 정보를 찾을 수 없습니다."
    )
