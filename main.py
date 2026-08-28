import streamlit as st
import requests
import plotly.graph_objects as go
from deep_translator import GoogleTranslator

# 페이지 기본 설정
st.set_page_config(page_title="포켓몬 위키", page_icon="⚡", layout="wide")

# CSS 스타일 적용
st.markdown("""
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
""", unsafe_allow_html=True)

# 종족치 & 타입 한글 매핑
STAT_NAME_MAP = {
    'hp': '체력(HP)',
    'attack': '공격',
    'defense': '방어',
    'special-attack': '특수공격',
    'special-defense': '특수방어',
    'speed': '스피드'
}

TYPE_NAME_MAP = {
    'normal': '노멀', 'fire': '불꽃', 'water': '물', 'grass': '풀',
    'electric': '전기', 'ice': '얼음', 'fighting': '격투', 'poison': '독',
    'ground': '땅', 'flying': '비행', 'psychic': '에스퍼', 'bug': '벌레',
    'rock': '바위', 'ghost': '고스트', 'dragon': '드래곤', 'dark': '악',
    'steel': '강철', 'fairy': '페어리'
}

# 영문 도감 설명 한글 번역 함수
def translate_to_ko(text):
    try:
        translated = GoogleTranslator(source='auto', target='ko').translate(text)
        return translated
    except Exception:
        return text

# 포켓몬 정보 불러오기
@st.cache_data
def get_pokemon_data(query):
    query = str(query).strip()
    target_id = None

    if query.isdigit():
        target_id = query
    else:
        try:
            # 1차: 직접 이름 검색
            species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{query.lower()}")
            if species_res.status_code == 200:
                target_id = species_res.json()['id']
            else:
                # 2차: 한글 이름 검색 (전체 목록 내 매칭)
                search_res = requests.get("https://pokeapi.co/api/v2/pokemon-species?limit=1025")
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
        pokemon_res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{target_id}")
        if pokemon_res.status_code != 200:
            return None
        pokemon_data = pokemon_res.json()

        species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{target_id}")
        species_data = species_res.json()

        # 한글 이름
        ko_name = next((n['name'] for n in species_data['names'] if n['language']['name'] == 'ko'), pokemon_data['name'])

        # 도감 설명 (한글이 없으면 영어 추출 후 확실하게 한글 번역)
        ko_flavor_list = [f['flavor_text'] for f in species_data['flavor_text_entries'] if f['language']['name'] == 'ko']
        if ko_flavor_list:
            ko_flavor = ko_flavor_list[-1].replace('\n', ' ').replace('\f', ' ')
        else:
            en_flavor_list = [f['flavor_text'] for f in species_data['flavor_text_entries'] if f['language']['name'] == 'en']
            if en_flavor_list:
                raw_en = en_flavor_list[-1].replace('\n', ' ').replace('\f', ' ')
                ko_flavor = translate_to_ko(raw_en)
            else:
                ko_flavor = "도감 설명이 존재하지 않습니다."

        # 분류 및 세대
        ko_genus = next((g['genus'] for g in species_data['genera'] if g['language']['name'] == 'ko'), "포켓몬")
        gen_roman = species_data['generation']['name'].replace('generation-', '').upper()

        # 포획률 & 타입
        capture_rate = species_data.get('capture_rate', '정보 없음')
        ko_types = [TYPE_NAME_MAP.get(t['type']['name'], t['type']['name']) for t in pokemon_data['types']]

        # 종족치
        stats_dict = {}
        total_stats = 0
        for s in pokemon_data['stats']:
            s_name = STAT_NAME_MAP.get(s['stat']['name'], s['stat']['name'])
            s_val = s['base_stat']
            stats_dict[s_name] = s_val
            total_stats += s_val

        img_url = pokemon_data['sprites']['other']['official-artwork']['front_default'] or pokemon_data['sprites']['front_default']

        return {
            'id': pokemon_data['id'],
            'formatted_id': f"No.{str(pokemon_data['id']).zfill(4)}",
            'name': ko_name,
            'english_name': pokemon_data['name'].capitalize(),
            'genus': ko_genus,
            'generation': f"{gen_roman} 세대",
            'capture_rate': capture_rate,
            'height': pokemon_data['height'] / 10,
            'weight': pokemon_data['weight'] / 10,
            'image': img_url,
            'description': ko_flavor,
            'types': ko_types,
            'stats': stats_dict,
            'total_stats': total_stats
        }
    except Exception:
        return None

# 메인 화면 UI
st.title("⚡ 포켓몬 나무위키")
search_query = st.text_input("포켓몬 이름 또는 도감 번호를 입력하세요 (예: 피카츄, 무쇠손, 906)", value="피카츄")

if search_query:
    with st.spinner("포켓몬 정보를 조회하는 중..."):
        data = get_pokemon_data(search_query)

    if data:
        st.markdown(f"<h1 class='main-title'>{data['name']} <small style='font-size:1rem; color:#666;'>| {data['english_name']} ({data['formatted_id']})</small></h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1.8, 1.2])

        with col1:
            st.markdown("<h3 class='section-title'>1. 개요</h3>", unsafe_allow_html=True)
            st.write(f"**{data['name']}**은(는) {data['generation']}에 처음 등장한 {data['genus']}입니다.")

            st.markdown("<h3 class='section-title'>2. 도감 설명</h3>", unsafe_allow_html=True)
            st.info(f'"{data["description"]}"')

            st.markdown("<h3 class='section-title'>3. 육각형 종족치 그래프</h3>", unsafe_allow_html=True)
            
            # 첨부 이미지 형태의 육각형(Polygon) 육성 그래프 생성
            categories = ['체력(HP)', '공격', '방어', '스피드', '특수방어', '특수공격']
            values = [data['stats'][cat] for cat in categories]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(0, 130, 117, 0.35)',
                line=dict(color='#008275', width=2.5),
                name=data['name']
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(max(values) + 10, 160)],
                        showticklabels=True,
                        gridcolor='#cccccc'
                    ),
                    angularaxis=dict(
                        gridcolor='#cccccc'
                    ),
                    gridshape='polygon' # 원형이 아닌 이미지와 같은 육각형 격자
                ),
                showlegend=False,
                margin=dict(l=50, r=50, t=20, b=20),
                height=380
            )

            st.plotly_chart(fig, use_container_width=True)

            # 종족치 수치 표기
            stat_cols = st.columns(3)
            idx = 0
            for stat_name, stat_val in data['stats'].items():
                with stat_cols[idx % 3]:
                    st.metric(label=stat_name, value=stat_val)
                idx += 1
            
            st.write(f"**종족치 총합:** `{data['total_stats']}`")

        with col2:
            st.markdown(f"""
                <div class='infobox'>
                    <div class='infobox-title'>{data['name']}</div>
                </div>
            """, unsafe_allow_html=True)
            st.image(data['image'], use_container_width=True)
            
            st.table({
                "속성": ["전국도감 번호", "분류", "세대", "타입", "신장", "체중", "포획률"],
                "정보": [
                    data['formatted_id'],
                    data['genus'],
                    data['generation'],
                    ", ".join(data['types']),
                    f"{data['height']} m",
                    f"{data['weight']} kg",
                    f"{data['capture_rate']}"
                ]
            })
    else:
        st.error(f"'{search_query}' 포켓몬 정보를 찾을 수 없습니다.")
