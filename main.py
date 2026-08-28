import streamlit as st
import requests

# 페이지 기본 설정
st.set_page_config(page_title="포켓몬 위키", page_icon="⚡", layout="wide")

# CSS 스타일 적용 (나무위키 스타일)
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
        margin-top: 20px;
    }
    .infobox {
        border: 2px solid var(--wiki-main);
        border-radius: 8px;
        padding: 15px;
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

# 포켓몬 정보 불러오기 함수
@st.cache_data
def get_pokemon_data(query):
    query = str(query).strip().lower()
    target_id = query

    if not query.isdigit():
        try:
            species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{query}")
            if species_res.status_code != 200:
                return None
            target_id = species_res.json()['id']
        except Exception:
            return None

    try:
        pokemon_res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{target_id}")
        if pokemon_res.status_code != 200:
            return None
        pokemon_data = pokemon_res.json()

        species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{target_id}")
        species_data = species_res.json()

        ko_name = next((n['name'] for n in species_data['names'] if n['language']['name'] == 'ko'), pokemon_data['name'])
        ko_flavor = next((f['flavor_text'] for f in reversed(species_data['flavor_text_entries']) if f['language']['name'] == 'ko'), "설명이 존재하지 않습니다.")
        ko_flavor = ko_flavor.replace('\n', ' ').replace('\f', ' ')
        ko_genus = next((g['genus'] for g in species_data['genera'] if g['language']['name'] == 'ko'), "포켓몬")
        gen_roman = species_data['generation']['name'].replace('generation-', '').upper()

        return {
            'id': pokemon_data['id'],
            'formatted_id': f"No.{str(pokemon_data['id']).zfill(4)}",
            'name': ko_name,
            'english_name': pokemon_data['name'].capitalize(),
            'genus': ko_genus,
            'generation': f"{gen_roman} 세대",
            'height': pokemon_data['height'] / 10,
            'weight': pokemon_data['weight'] / 10,
            'image': pokemon_data['sprites']['other']['official-artwork']['front_default'],
            'description': ko_flavor,
            'types': [t['type']['name'] for t in pokemon_data['types']],
            'stats': {s['stat']['name']: s['base_stat'] for s in pokemon_data['stats']}
        }
    except Exception:
        return None

# 상단 헤더 및 검색창
st.title("⚡ 포켓몬 나무위키")
search_query = st.text_input("포켓몬 이름 또는 번호를 입력하세요", value="피카츄")

if search_query:
    data = get_pokemon_data(search_query)

    if data:
        st.markdown(f"<h1 class='main-title'>{data['name']} <small style='font-size:1rem; color:#666;'>| {data['english_name']} ({data['formatted_id']})</small></h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])

        # 왼쪽 본문 내용
        with col1:
            st.markdown("<h3 class='section-title'>1. 개요</h3>", unsafe_allow_html=True)
            st.write(f"**{data['name']}**은(는) {data['generation']}에 처음 등장한 {data['genus']}입니다.")

            st.markdown("<h3 class='section-title'>2. 도감 설명</h3>", unsafe_allow_html=True)
            st.info(f'"{data["description"]}"')

            st.markdown("<h3 class='section-title'>3. 기본 능력치</h3>", unsafe_allow_html=True)
            for stat, val in data['stats'].items():
                st.write(f"• **{stat.upper()}**: {val}")

        # 오른쪽 나무위키 프로필 상자
        with col2:
            st.markdown(f"""
                <div class='infobox'>
                    <div class='infobox-title'>{data['name']}</div>
                </div>
            """, unsafe_allow_html=True)
            st.image(data['image'], use_container_width=True)
            
            st.table({
                "속성": ["전국도감 번호", "분류", "세대", "타입", "신장", "체중"],
                "정보": [
                    data['formatted_id'],
                    data['genus'],
                    data['generation'],
                    ", ".join(data['types']),
                    f"{data['height']} m",
                    f"{data['weight']} kg"
                ]
            })
    else:
        st.error(f"'{search_query}' 포켓몬 정보를 찾을 수 없습니다.")
