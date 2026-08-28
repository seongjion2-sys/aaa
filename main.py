from flask import Flask, request, redirect, url_for, render_template_string
import requests

app = Flask(__name__)

# 단일 파일 구동을 위한 HTML/CSS/JS 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if pokemon %}{{ pokemon.name }} - 포켓몬 위키{% else %}검색 결과 없음{% endif %}</title>
    <style>
        :root {
            --wiki-main: #008275;
            --wiki-bg: #f8f9fa;
            --wiki-border: #ccc;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--wiki-bg);
            color: #333;
            margin: 0;
            padding: 0;
        }

        /* 상단 헤더 & 검색창 */
        header {
            background-color: var(--wiki-main);
            color: white;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        header h1 {
            margin: 0;
            font-size: 1.2rem;
        }

        header h1 a {
            color: white;
            text-decoration: none;
        }

        .search-box {
            display: flex;
            gap: 5px;
        }

        .search-box input {
            padding: 6px 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            outline: none;
        }

        .search-box button {
            padding: 6px 12px;
            background: #005f55;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        /* 본문 레이아웃 */
        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: white;
            padding: 25px;
            border: 1px solid var(--wiki-border);
            border-radius: 6px;
        }

        /* 나무위키 레이아웃 (본문 + 프로필 상자) */
        .wiki-content {
            display: flex;
            flex-wrap: wrap-reverse;
            gap: 20px;
        }

        .main-text {
            flex: 1;
            min-width: 300px;
        }

        .title-area {
            border-bottom: 2px solid var(--wiki-main);
            padding-bottom: 8px;
            margin-bottom: 15px;
        }

        .title-area h2 {
            margin: 0;
            font-size: 2rem;
            display: inline-block;
        }

        .title-area .sub-title {
            color: #666;
            font-size: 0.9rem;
            margin-left: 10px;
        }

        /* 나무위키 프로필 상자 (Infobox) */
        .infobox {
            width: 300px;
            border: 2px solid var(--wiki-main);
            border-radius: 4px;
            overflow: hidden;
            font-size: 0.9rem;
            align-self: flex-start;
        }

        .infobox-title {
            background-color: var(--wiki-main);
            color: white;
            text-align: center;
            padding: 8px;
            font-weight: bold;
            font-size: 1.1rem;
        }

        .infobox img {
            width: 100%;
            background: #f0f0f0;
            display: block;
        }

        .infobox table {
            width: 100%;
            border-collapse: collapse;
        }

        .infobox th {
            background-color: #f1f3f5;
            border: 1px solid #dee2e6;
            padding: 6px;
            width: 35%;
            text-align: left;
        }

        .infobox td {
            border: 1px solid #dee2e6;
            padding: 6px;
        }

        /* 문단 스타일 */
        .section-header {
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-top: 25px;
            color: var(--wiki-main);
        }

        .not-found {
            text-align: center;
            padding: 50px 0;
        }

        /* 이전/다음 포켓몬 이동 버튼 */
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }

        .nav-buttons a {
            color: var(--wiki-main);
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <header>
        <h1><a href="/">포켓몬 나무위키</a></h1>
        <form class="search-box" action="/search" method="get">
            <input type="text" name="query" placeholder="이름 또는 도감 번호 (예: 리자몽, 6)" required>
            <button type="submit">검색</button>
        </form>
    </header>

    <div class="container">
        {% if pokemon %}
            <div class="title-area">
                <h2>{{ pokemon.name }}</h2>
                <span class="sub-title">{{ pokemon.english_name }} | {{ pokemon.formatted_id }}</span>
            </div>

            <div class="wiki-content">
                <!-- 왼쪽 본문 내용 -->
                <div class="main-text">
                    <h3 class="section-header">1. 개요</h3>
                    <p>{{ pokemon.name }}은(는) {{ pokemon.generation }}에 처음 등장한 {{ pokemon.genus }}입니다.</p>

                    <h3 class="section-header">2. 도감 설명</h3>
                    <blockquote style="background: #f8f9fa; border-left: 4px solid var(--wiki-main); padding: 10px; margin: 0;">
                        "{{ pokemon.description }}"
                    </blockquote>

                    <h3 class="section-header">3. 기본 능력치</h3>
                    <ul>
                        {% for stat_name, val in pokemon.stats.items() %}
                            <li><strong>{{ stat_name.upper() }}:</strong> {{ val }}</li>
                        {% endfor %}
                    </ul>

                    <div class="nav-buttons">
                        {% if pokemon.id > 1 %}
                            <a href="/wiki/{{ pokemon.id - 1 }}">← No.{{ pokemon.id - 1 }} 이전 포켓몬</a>
                        {% else %}
                            <div></div>
                        {% endif %}
                        {% if pokemon.id < 1025 %}
                            <a href="/wiki/{{ pokemon.id + 1 }}">No.{{ pokemon.id + 1 }} 다음 포켓몬 →</a>
                        {% endif %}
                    </div>
                </div>

                <!-- 오른쪽 나무위키식 프로필 인포박스 -->
                <div class="infobox">
                    <div class="infobox-title">{{ pokemon.name }}</div>
                    <img src="{{ pokemon.image }}" alt="{{ pokemon.name }}">
                    <table>
                        <tr>
                            <th>전국도감 번호</th>
                            <td>{{ pokemon.formatted_id }}</td>
                        </tr>
                        <tr>
                            <th>분류</th>
                            <td>{{ pokemon.genus }}</td>
                        </tr>
                        <tr>
                            <th>세대</th>
                            <td>{{ pokemon.generation }}</td>
                        </tr>
                        <tr>
                            <th>타입</th>
                            <td>{{ pokemon.types | join(', ') }}</td>
                        </tr>
                        <tr>
                            <th>신장</th>
                            <td>{{ pokemon.height }} m</td>
                        </tr>
                        <tr>
                            <th>체중</th>
                            <td>{{ pokemon.weight }} kg</td>
                        </tr>
                    </table>
                </div>
            </div>

        {% else %}
            <div class="not-found">
                <h2>'{{ keyword }}' 포켓몬 정보를 찾을 수 없습니다.</h2>
                <p>포켓몬 번호(1~1025) 또는 영문 이름으로 검색해 보세요.</p>
                <a href="/">메인으로 돌아가기</a>
            </div>
        {% endif %}
    </div>

</body>
</html>
"""

def get_pokemon_data(search_query):
    search_query = str(search_query).strip().lower()
    target_id = search_query

    # 한글 이름 검색 처리
    if not search_query.isdigit():
        try:
            species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{search_query}")
            if species_res.status_code != 200:
                return None
            target_id = species_res.json()['id']
        except Exception:
            return None

    try:
        # 기본 스탯/이미지 데이터
        pokemon_res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{target_id}")
        if pokemon_res.status_code != 200:
            return None
        pokemon_data = pokemon_res.json()

        # 세대/도감 설명/한글 이름 데이터
        species_res = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{target_id}")
        species_data = species_res.json()

        ko_name = next((n['name'] for n in species_data['names'] if n['language']['name'] == 'ko'), pokemon_data['name'])
        
        ko_flavor = next((f['flavor_text'] for f in reversed(species_data['flavor_text_entries']) if f['language']['name'] == 'ko'), "설명이 존재하지 않습니다.")
        ko_flavor = ko_flavor.replace('\n', ' ').replace('\f', ' ')

        ko_genus = next((g['genus'] for g in species_data['genera'] if g['language']['name'] == 'ko'), "포켓몬")

        gen_roman = species_data['generation']['name'].replace('generation-', '').upper()
        generation_name = f"{gen_roman} 세대"

        return {
            'id': pokemon_data['id'],
            'formatted_id': f"No.{str(pokemon_data['id']).zfill(4)}",
            'name': ko_name,
            'english_name': pokemon_data['name'].capitalize(),
            'genus': ko_genus,
            'generation': generation_name,
            'height': pokemon_data['height'] / 10,
            'weight': pokemon_data['weight'] / 10,
            'image': pokemon_data['sprites']['other']['official-artwork']['front_default'],
            'description': ko_flavor,
            'types': [t['type']['name'] for t in pokemon_data['types']],
            'stats': {s['stat']['name']: s['base_stat'] for s in pokemon_data['stats']}
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/')
def home():
    return redirect(url_for('wiki_page', keyword='25'))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query:
        return redirect(url_for('wiki_page', keyword=query))
    return redirect(url_for('home'))

@app.route('/wiki/<keyword>')
def wiki_page(keyword):
    pokemon_info = get_pokemon_data(keyword)
    return render_template_string(HTML_TEMPLATE, pokemon=pokemon_info, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
