import json
import math
import urllib.parse
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

# 종족치 & 타입 한글 매핑
STAT_NAME_MAP = {
    'hp': '체력(HP)',
    'attack': '공격',
    'defense': '방어',
    'special-attack': '특수공격',
    'special-defense': '특수방어',
    'speed': '스피드',
}

TYPE_NAME_MAP = {
    'normal': '노멀',
    'fire': '불꽃',
    'water': '물',
    'grass': '풀',
    'electric': '전기',
    'ice': '얼음',
    'fighting': '격투',
    'poison': '독',
    'ground': '땅',
    'flying': '비행',
    'psychic': '에스퍼',
    'bug': '벌레',
    'rock': '바위',
    'ghost': '고스트',
    'dragon': '드래곤',
    'dark': '악',
    'steel': '강철',
    'fairy': '페어리',
}


# 구글 번역 함수
def translate_to_ko(text):
  try:
    encoded_text = urllib.parse.quote(text)
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={encoded_text}'
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      data = res.json()
      return ''.join([item[0] for item in data[0] if item[0]])
  except Exception:
    pass
  return text


# species URL로부터 한글 이름 가져오기
def get_ko_name_from_species_url(url):
  try:
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      data = res.json()
      return next(
          (n['name'] for n in data['names'] if n['language']['name'] == 'ko'),
          data['name'],
      )
  except Exception:
    pass
  return None


# 진화 트리를 재귀 탐색하여 이전/다음 진화체 탐색
def find_evolution_neighbors(chain, target_species_name):
  prev_evos = []
  next_evos = []

  def traverse(node, current_path):
    if node['species']['name'] == target_species_name:
      if current_path:
        prev_evos.append(current_path[-1])
      for child in node.get('evolves_to', []):
        next_evos.append(child['species'])
      return True

    for child in node.get('evolves_to', []):
      if traverse(child, current_path + [node['species']]):
        return True
    return False

  traverse(chain['chain'], [])
  return prev_evos, next_evos


# 육각형 레이더 차트 (SVG)
def generate_hexagon_svg(stats):
  keys = [
      '체력(HP)',
      '공격',
      '방어',
      '특수공격',
      '특수방어',
      '스피드',
  ]
  vals = [stats.get(k, 0) for k in keys]
  max_val = 160.0

  cx, cy, r = 150, 150, 100

  grid_lines = ''
  for step in [0.2, 0.4, 0.6, 0.8, 1.0]:
    pts = []
    for i in range(6):
      angle = math.radians(60 * i - 90)
      x = cx + (r * step) * math.cos(angle)
      y = cy + (r * step) * math.sin(angle)
      pts.append(f'{x:.1f},{y:.1f}')
    grid_lines += (
        f'<polygon points="{" ".join(pts)}" fill="none" stroke="#e0e0e0"'
        ' stroke-width="1"/>'
    )

  axis_lines = ''
  for i in range(6):
    angle = math.radians(60 * i - 90)
    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)
    axis_lines += (
        f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#d0d0d0"'
        ' stroke-width="1"/>'
    )

  data_pts = []
  labels_svg = ''
  for i, (k, v) in enumerate(zip(keys, vals)):
    angle = math.radians(60 * i - 90)
    ratio = min(v / max_val, 1.0)
    x = cx + (r * ratio) * math.cos(angle)
    y = cy + (r * ratio) * math.sin(angle)
    data_pts.append(f'{x:.1f},{y:.1f}')

    lx = cx + (r + 25) * math.cos(angle)
    ly = cy + (r + 15) * math.sin(angle)
    labels_svg += (
        f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#333" font-size="12"'
        f' font-weight="bold" text-anchor="middle">{k}</text>'
    )

  poly_pts = ' '.join(data_pts)

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


# 포켓몬 정보 불러오기
@st.cache_data
def get_pokemon_data(query):
  query = str(query).strip()
  target_id = None

  if query.isdigit():
    target_id = query
  else:
    try:
      species_res = requests.get(
          f'https://pokeapi.co/api/v2/pokemon-species/{query.lower()}'
      )
      if species_res.status_code == 200:
        target_id = species_res.json()['id']
      else:
        search_res = requests.get(
            'https://pokeapi.co/api/v2/pokemon-species?limit=1025'
        )
        if search_res.status_code == 200:
          results = search_res.json()['results']
          for item in results:
            sp_res = requests.get(item['url'])
            if sp_res.status_code == 200:
              sp_data = sp_res.json()
              names = [n['name'] for n in sp_data['names']]
              if query in names:
                target_id = sp_data['id']
                break
    except Exception:
      return None

  if not target_id:
    return None

  try:
    pokemon_res = requests.get(
        f'https://pokeapi.co/api/v2/pokemon/{target_id}'
    )
    if pokemon_res.status_code != 200:
      return None
    pokemon_data = pokemon_res.json()

    species_res = requests.get(
        f'https://pokeapi.co/api/v2/pokemon-species/{target_id}'
    )
    species_data = species_res.json()

    # 한글 이름
    ko_name = next(
        (
            n['name']
            for n in species_data['names']
            if n['language']['name'] == 'ko'
        ),
        pokemon_data['name'],
    )

    # 도감 설명
    ko_flavor_list = [
        f['flavor_text']
        for f in species_data['flavor_text_entries']
        if f['language']['name'] == 'ko'
    ]
    if ko_flavor_list:
      ko_flavor = ko_flavor_list[-1].replace('\n', ' ').replace('\f', ' ')
    else:
      en_flavor_list = [
          f['flavor_text']
          for f in species_data['flavor_text_entries']
          if f['language']['name'] == 'en'
      ]
      if en_flavor_list:
        raw_en = en_flavor_list[-1].replace('\n', ' ').replace('\f', ' ')
        ko_flavor = translate_to_ko(raw_en)
      else:
        ko_flavor = '도감 설명이 존재하지 않습니다.'

    ko_genus = next(
        (
            g['genus']
            for g in species_data['genera']
            if g['language']['name'] == 'ko'
        ),
        '포켓몬',
    )
    gen_roman = (
        species_data['generation']['name']
        .replace('generation-', '')
        .upper()
    )

    capture_rate = species_data.get('capture_rate', '정보 없음')
    ko_types = [
        TYPE_NAME_MAP.get(t['type']['name'], t['type']['name'])
        for t in pokemon_data['types']
    ]

    stats_dict = {}
    total_stats = 0
    for s in pokemon_data['stats']:
      s_name = STAT_NAME_MAP.get(s['stat']['name'], s['stat']['name'])
      s_val = s['base_stat']
      stats_dict[s_name] = s_val
      total_stats += s_val

    # 진화 정보 처리
    prev_evos_names = []
    next_evos_names = []

    evo_url = species_data.get('evolution_chain', {}).get('url')
    if evo_url:
      evo_res = requests.get(evo_url)
      if evo_res.status_code == 200:
        evo_chain = evo_res.json()
        raw_prev, raw_next = find_evolution_neighbors(
            evo_chain, species_data['name']
        )

        for p in raw_prev:
          name = get_ko_name_from_species_url(p['url'])
          if name:
            prev_evos_names.append(name)

        for n in raw_next:
          name = get_ko_name_from_species_url(n['url'])
          if name:
            next_evos_names.append(name)

    img_url = (
        pokemon_data['sprites']['other']['official-artwork']['front_default']
        or pokemon_data['sprites']['front_default']
    )

    return {
        'id': pokemon_data['id'],
        'formatted_id': f"No.{str(pokemon_data['id']).zfill(4)}",
        'name': ko_name,
        'english_name': pokemon_data['name'].capitalize(),
        'genus': ko_genus,
        'generation': f'{gen_roman} 세대',
        'capture_rate': capture_rate,
        'height': pokemon_data['height'] / 10,
        'weight': pokemon_data['weight'] / 10,
        'image': img_url,
        'description': ko_flavor,
        'types': ko_types,
        'stats': stats_dict,
        'total_stats': total_stats,
        'prev_evos': prev_evos_names,
        'next_evos': next_evos_names,
    }
  except Exception:
    return None


# 메인 화면 UI
st.title('⚡ 포켓몬 나무위키')
search_query = st.text_input(
    '포켓몬 이름 또는 도감 번호를 입력하세요 (예: 파이리, 리자드, 리자몽, 칠색조)',
    value='리자드',
)

if search_query:
  with st.spinner('포켓몬 정보를 조회하는 중...'):
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
          "<h3 class='section-title'>3. 육각형 종족치 그래프</h3>",
          unsafe_allow_html=True,
      )
      st.markdown(
          generate_hexagon_svg(data['stats']), unsafe_allow_html=True
      )

      stat_cols = st.columns(3)
      idx = 0
      for stat_name, stat_val in data['stats'].items():
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
      st.image(data['image'], use_container_width=True)

      # 오른쪽 테이블 동적 구성 (이전/다음 진화체가 있을 경우만 추가)
      info_dict = {
          '전국도감 번호': data['formatted_id'],
          '분류': data['genus'],
          '세대': data['generation'],
          '타입': ', '.join(data['types']),
          '신장': f"{data['height']} m",
          '체중': f"{data['weight']} kg",
          '포획률': f"{data['capture_rate']}",
      }

      if data['prev_evos']:
        info_dict['이전 진화체'] = ', '.join(data['prev_evos'])
      if data['next_evos']:
        info_dict['다음 진화체'] = ', '.join(data['next_evos'])

      st.table({
          '속성': list(info_dict.keys()),
          '정보': list(info_dict.values()),
      })
  else:
    st.error(f"'{search_query}' 포켓몬 정보를 찾을 수 없습니다.")
