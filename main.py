import urllib.parse
import json
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="포켓몬 위키", page_icon="⚡", layout="wide")

# CSS 스타일 적용
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
    </style>
""",
    unsafe_allow_html=True,
)

# 영어 -> 한글 매핑 사전
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


# 간이 무료 번역 함수 (영문 도감 설명을 한글로 번역)
def translate_to_ko(text):
  try:
    encoded_text = urllib.parse.quote(text)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={encoded_text}"
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      data = res.json()
      translated = "".join([item[0] for item in data[0] if item[0]])
      return translated
  except Exception:
    pass
  return text


# 포켓몬 정보 불러오기 함수
@st.cache_data
def get_pokemon_data(query):
  query = str(query).strip()
  target_id = None

  # 1. 입력값이 숫자인 경우
  if query.isdigit():
    target_id = query
  else:
    # 2. 한글/영어 이름인 경우 -> species 전체 목록 또는 개별 조회를 통해 ID 검색
    try:
      # 직접 이름으로 API 요청 시도
      species_res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon-species/{query.lower()}"
      )
      if species_res.status_code == 200:
        target_id = species_res.json()["id"]
      else:
        # 한글 이름 검색을 위해 1~1025 범위 탐색 시도 (성능을 위해 species 검색 API 활용)
        # PokEAPI의 한글 이름으로 ID를 즉시 찾는 엔드포인트 검색
        search_res = requests.get(
            f"https://pokeapi.co/api/v2/pokemon-species?limit=1025"
        )
        if search_res.status_code == 200:
          results = search_res.json()["results"]
          for item in results:
            # 개별 개체 확인 (캐시 적용 환경)
            sp_res = requests.get(item["url"])
            if sp_res.status_code == 200:
              sp_data = sp_res.json()
              names = [n["name"] for n in sp_data["names"]]
              if query in names:
                target_id = sp_data["id"]
                break
    except Exception:
      return None

  if not target_id:
    return None

  try:
    # 기본 스탯/이미지/타입 데이터
    pokemon_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{target_id}"
    )
    if pokemon_res.status_code != 200:
      return None
    pokemon_data = pokemon_res.json()

    # 종(Species) 데이터 (한글 이름, 도감 설명, 포획률 등)
    species_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{target_id}"
    )
    species_data = species_res.json()

    # 한글 이름 추출
    ko_name = next(
        (
            n["name"]
            for n in species_data["names"]
            if n["language"]["name"] == "ko"
        ),
        pokemon_data["name"],
    )

    # 도감 설명 추출 및 한글 번역 처리
    ko_flavor_list = [
        f["flavor_text"]
        for f in species_data["flavor_text_entries"]
        if f["language"]["name"] == "ko"
    ]
    if ko_flavor_list:
      ko_flavor = ko_flavor_list[-1].replace("\n", " ").replace("\f", " ")
    else:
      # 한글 설명이 없는 899번 이후 포켓몬: 영문 설명을 가져와 한글로 자동 번역
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

    # 분류 & 세대
    ko_genus = next(
        (
            g["genus"]
            for g in species_data["genera"]
            if g["language"]["name"] == "ko"
        ),
        "포켓몬",
    )
    gen_roman = (
        species_data["generation"]["name"]
        .replace("generation-", "")
        .upper()
    )

    # 포획률
    capture_rate = species_data.get("capture_rate", "정보 없음")

    # 타입 한글화
    ko_types = [
        TYPE_NAME_MAP.get(t["type"]["name"], t["type"]["name"])
        for t in pokemon_data["types"]
    ]

    # 종족치 계산
    stats_dict = {}
    total_stats = 0
    for s in pokemon_data["stats"]:
      s_name = STAT_NAME_MAP.get(s["stat"]["name"], s["stat"]["name"])
      s_val = s["base_stat"]
      stats_dict[s_name] = s_val
      total_stats += s_val

    # 이미지 경로
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
        "stats": stats_dict,
        "total_stats": total_stats,
    }
  except Exception:
    return None


# 헤더 및 검색창 UI
st.title("⚡ 포켓몬 나무위키")
search_query = st.text_input(
    "포켓몬 이름 또는 도감 번호를 입력하세요 (예: 피카츄, 나오하, 906)",
    value="피카츄",
)

if search_query:
  with st.spinner("포켓몬 정보를 불러오는 중..."):
    data = get_pokemon_data(search_query)

  if data:
    st.markdown(
        f"<h1 class='main-title'>{data['name']} <small style='font-size:1rem;"
        f" color:#666;'>| {data['english_name']}"
        f" ({data['formatted_id']})</small></h1>",
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
          "<h3 class='section-title'>3. 종족치 및 능력치</h3>",
          unsafe_allow_html=True,
      )
      st.bar_chart(data["stats"])

      stat_cols = st.columns(3)
      idx = 0
      for stat_name, stat_val in data["stats"].items():
        with stat_cols[idx % 3]:
          st.metric(label=stat_name, value=stat_val)
        idx += 1

      st.write(f"**종족치 총합:** `{data['total_stats']}`")

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
              "타입",
              "신장",
              "체중",
              "포획률",
          ],
          "정보": [
              data["formatted_id"],
              data["genus"],
              data["generation"],
              ", ".join(data["types"]),
              f"{data['height']} m",
              f"{data['weight']} kg",
              f"{data['capture_rate']}",
          ],
      })
  else:
    st.error(f"'{search_query}' 포켓몬 정보를 찾을 수 없습니다.")
