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

if "selected_character" not in st.session_state:
  st.session_state.selected_character = None

if "character_search_history" not in st.session_state:
  st.session_state.character_search_history = []

if "item_category" not in st.session_state:
  st.session_state.item_category = None

if "selected_item" not in st.session_state:
  st.session_state.selected_item = None

if "item_search_query" not in st.session_state:
  st.session_state.item_search_query = ""


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
                "specialty": "바위 타입 포켓몬 전문",
                "desc": "단단한 정신력과 바위처럼 묵직한 전투를 구사하는 관동지방 최초의 체육관 관장입니다.",
                "pokemon": ["꼬마돌", "롱스톤", "데구리", "딱구리", "코뿌리", "뿔카노"],
                "image": "",
            },
            {
                "name": "이슬",
                "title": "블루시티 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": "물 속의 요정이라 불리며, 활기차고 당찬 성격의 체육관 관장입니다.",
                "pokemon": ["별가람", "아쿠스타", "꼬부기", "어니부기", "거북왕", "콘치"],
                "image": "",
            },
            {
                "name": "마티스",
                "title": "갈색체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 전문",
                "desc": "군인 출신으로 스피디한 전기 포켓몬 배틀을 구사하는 관장입니다.",
                "pokemon": ["코일", "라이츄", "피카츄", "레어코일", "찌리리공", "붐볼"],
                "image": "",
            },
            {
                "name": "민화",
                "title": "무지개시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "무지개시티에서 정원을 가꾸며 풀 포켓몬을 다루는 관장입니다.",
                "pokemon": ["라플레시아", "우츠보트", "이상해꽃", "덩쿠리", "나시", "로즈레이드"],
                "image": "",
            },
            {
                "name": "독수",
                "title": "연분홍시티 체육관 관장",
                "type": "독",
                "specialty": "독 타입 포켓몬 전문",
                "desc": "닌자처럼 은밀하게 움직이는 독 타입 전문 체육관 관장입니다.",
                "pokemon": ["또도가스", "냄새꼬", "또도스핀", "도나단", "아보크", "니드킹"],
                "image": "",
            },
            {
                "name": "초련",
                "title": "노랑시티 체육관 관장",
                "type": "에스퍼",
                "specialty": "에스퍼 타입 포켓몬 전문",
                "desc": "초능력을 지닌 신비로운 소녀로, 에스퍼 포켓몬을 다루는 관장입니다.",
                "pokemon": ["후딘", "슬리프", "윤겔라", "슬리퍼", "마임맨", "폴리곤"],
                "image": "",
            },
            {
                "name": "강연",
                "title": "홍련시티 체육관 관장",
                "type": "불꽃",
                "specialty": "불꽃 타입 포켓몬 전문",
                "desc": "은퇴한 과학자 출신으로, 홍련섬에서 불꽃 포켓몬을 연구하는 관장입니다.",
                "pokemon": ["윈디", "가디", "날쌩마", "리자몽", "부스터", "마그마"],
                "image": "",
            },
            {
                "name": "비주기",
                "title": "상록시티 체육관 관장 / 로켓단 보스",
                "type": "땅",
                "specialty": "땅 타입 포켓몬 및 조직 지휘",
                "desc": "관동지방의 마지막 체육관 관장이자, 정체를 숨긴 악의 조직 로켓단의 보스입니다.",
                "pokemon": ["니드킹", "페르시온", "디그다", "닥트리오", "코뿌리", "뿔카노"],
                "image": "",
            },
            {
                "name": "그린",
                "title": "관동리그 챔피언",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "라이벌이자 관동지방 최초의 챔피언으로, 이후 상록체육관 관장으로 부임합니다.",
                "pokemon": ["리자몽", "피죤투", "망나뇽", "잠만보", "윈디", "가디안"],
                "image": "",
            },
            {
                "name": "레드",
                "title": "전설의 포켓몬 트레이너",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "태초마을 출신으로, 관동 지방을 모험하며 포켓몬 리그를 제패한 전설적인 트레이너입니다.",
                "pokemon": ["피카츄", "리자몽", "잠만보", "망나뇽", "윈디", "가디안"],
                "image": "",
            },
            {
                "name": "오박사",
                "title": "관동지방 포켓몬 박사",
                "type": "기타",
                "specialty": "포켓몬 연구",
                "desc": "태초마을에 연구소를 두고 신규 트레이너에게 첫 포켓몬을 나눠주는 저명한 박사입니다.",
                "pokemon": [],
                "image": "",
            },
        ],
    },
    "2세대 (성도)": {
        "color": "#FF8C42",
        "characters": [
            {
                "name": "심향",
                "title": "성도지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "밝고 활기찬 성격으로, 성도지방을 모험하며 챔피언 자리에 오르는 신인 트레이너입니다.",
                "pokemon": ["치코리타", "브케인", "리아코", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "비상",
                "title": "도라지시티 체육관 관장",
                "type": "비행",
                "specialty": "비행 타입 포켓몬 전문",
                "desc": "하늘을 나는 포켓몬을 사랑하는 우아한 성도지방 첫 체육관 관장입니다.",
                "pokemon": ["구구", "피죤투", "피죤", "두두", "두트리오", "파오리"],
                "image": "",
            },
            {
                "name": "호일",
                "title": "고동체육관 관장",
                "type": "벌레",
                "specialty": "벌레 타입 포켓몬 전문",
                "desc": "벌레 포켓몬 연구에 열정적인 소년 관장입니다.",
                "pokemon": ["단데기", "스라크", "도나단", "독침붕", "파라섹트", "콘팡"],
                "image": "",
            },
            {
                "name": "꼭두",
                "title": "금빛시티 체육관 관장",
                "type": "노말",
                "specialty": "노말 타입 포켓몬 전문",
                "desc": "트레이너 경력이 짧지만 밀탱크로 많은 도전자를 울린 관장입니다.",
                "pokemon": ["밀탱크", "푸크린", "캥카", "럭키", "이브이", "페르시온"],
                "image": "",
            },
            {
                "name": "유빈",
                "title": "인주시티 체육관 관장",
                "type": "고스트",
                "specialty": "고스트 타입 포켓몬 전문",
                "desc": "포켓몬탑이 있는 인주시티에서 유령 포켓몬을 다루는 관장입니다.",
                "pokemon": ["팬텀", "고우스트", "고오스", "무우마", "다크펫", "킬가르도"],
                "image": "",
            },
            {
                "name": "사도",
                "title": "진청시티 체육관 관장",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 전문",
                "desc": "호쾌한 성격으로 격투 포켓몬을 단련시키는 관장입니다.",
                "pokemon": ["알통몬", "괴력몬", "근육몬", "시라소몬", "홍수몬", "루카리오"],
                "image": "",
            },
            {
                "name": "규리",
                "title": "담청시티 체육관 관장",
                "type": "강철",
                "specialty": "강철 타입 포켓몬 전문",
                "desc": "성실한 성격으로 강철 포켓몬을 정성껏 키우는 관장입니다.",
                "pokemon": ["강철톤", "코일", "레어코일", "금강펜치", "보스로라", "메탕구"],
                "image": "",
            },
            {
                "name": "류옹",
                "title": "황토시티 체육관 관장",
                "type": "얼음",
                "specialty": "얼음 타입 포켓몬 전문",
                "desc": "인생 경험이 풍부한 노년의 얼음 타입 전문 관장입니다.",
                "pokemon": ["쥬쥬", "얼음귀신", "쥬레곤", "메쨩", "라프라스", "망나뇽"],
                "image": "",
            },
            {
                "name": "이향",
                "title": "검은먹시티 체육관 관장",
                "type": "드래곤",
                "specialty": "드래곤 타입 포켓몬 전문",
                "desc": "자존심이 매우 강하며, 성도지방의 마지막 체육관 관장입니다.",
                "pokemon": ["망나뇽", "미뇽", "신뇽", "보만다", "한카리아스", "킹드라"],
                "image": "",
            },
            {
                "name": "목호",
                "title": "성도리그 챔피언",
                "type": "드래곤",
                "specialty": "드래곤 타입 포켓몬 전문",
                "desc": "관동지방 사천왕 출신으로, 성도지방의 챔피언으로 등극한 강자입니다.",
                "pokemon": ["망나뇽", "미뇽", "신뇽", "보만다", "한카리아스", "킹드라"],
                "image": "",
            },
        ],
    },
    "3세대 (호연)": {
        "color": "#F3C623",
        "characters": [
            {
                "name": "휘웅",
                "title": "호연지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "종길 관장의 아들로, 호연지방을 여행하며 리그 우승과 악의 조직 저지에 앞장서는 트레이너입니다.",
                "pokemon": ["나무돌이", "아차모", "물짱이", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "원규",
                "title": "금탄시티 체육관 관장",
                "type": "바위",
                "specialty": "바위 타입 포켓몬 전문",
                "desc": "바위와 지질학에 조예가 깊은 우수한 학생 관장입니다.",
                "pokemon": ["코산호", "꼬마돌", "데구리", "딱구리", "롱스톤", "코뿌리"],
                "image": "",
            },
            {
                "name": "철구",
                "title": "무로시티 체육관 관장",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 전문",
                "desc": "서핑과 격투기를 즐기는 시원시원한 성격의 관장입니다.",
                "pokemon": ["마크탕", "알통몬", "근육몬", "괴력몬", "시라소몬", "홍수몬"],
                "image": "",
            },
            {
                "name": "암페어",
                "title": "보라시티 체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 전문",
                "desc": "발명을 좋아하는 유쾌한 성격의 전기 타입 전문 관장입니다.",
                "pokemon": ["마그네톤", "피카츄", "라이츄", "코일", "레어코일", "찌리리공"],
                "image": "",
            },
            {
                "name": "민지",
                "title": "용암시티 체육관 관장",
                "type": "불꽃",
                "specialty": "불꽃 타입 포켓몬 전문",
                "desc": "용암시티의 뜨거운 환경 속에서 열정적으로 관장을 맡고 있습니다.",
                "pokemon": ["윤딜라", "가디", "윈디", "날쌩마", "리자몽", "부스터"],
                "image": "",
            },
            {
                "name": "종길",
                "title": "등화시티 체육관 관장",
                "type": "노말",
                "specialty": "노말 타입 포켓몬 전문",
                "desc": "주인공의 아버지이자, 잠만보를 앞세운 노말 타입 전문 관장입니다.",
                "pokemon": ["잠만보", "밀탱크", "푸크린", "캥카", "럭키", "이브이"],
                "image": "",
            },
            {
                "name": "은송",
                "title": "검방울시티 체육관 관장",
                "type": "비행",
                "specialty": "비행 타입 포켓몬 전문",
                "desc": "우아한 태도로 비행 포켓몬을 다루는 검방울시티의 관장입니다.",
                "pokemon": ["보만다", "구구", "피죤", "피죤투", "두두", "두트리오"],
                "image": "",
            },
            {
                "name": "풍&란",
                "title": "이끼시티 체육관 관장",
                "type": "에스퍼",
                "specialty": "에스퍼 타입 포켓몬 전문",
                "desc": "쌍둥이 남매가 함께 맡고 있는 이끼시티의 에스퍼 타입 체육관 관장입니다.",
                "pokemon": ["솔록", "루나톤", "후딘", "윤겔라", "슬리프", "슬리퍼"],
                "image": "",
            },
            {
                "name": "윤진",
                "title": "루네시티 체육관 관장 / 호연리그 챔피언",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": "호연지방의 마지막 관장으로, 이후 호연리그 챔피언 자리에까지 오른 실력자입니다.",
                "pokemon": ["마일리시", "꼬부기", "어니부기", "거북왕", "콘치", "왕콘치"],
                "image": "",
            },
        ],
    },
    "4세대 (신오)": {
        "color": "#1089FF",
        "characters": [
            {
                "name": "광휘",
                "title": "신오지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "신오지방의 시골 마을 태생으로, 은하단의 음모를 저지하고 챔피언에 오르는 트레이너입니다.",
                "pokemon": ["모부기", "불꽃숭이", "팽도리", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "강석",
                "title": "무쇠시티 체육관 관장",
                "type": "바위",
                "specialty": "바위 타입 포켓몬 전문",
                "desc": "탄광업이 발달한 무쇠시티를 이끄는 든든한 관장입니다.",
                "pokemon": ["꼬마돌", "두개도스", "데구리", "딱구리", "롱스톤", "코뿌리"],
                "image": "",
            },
            {
                "name": "유채",
                "title": "영원시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "풀 포켓몬과 대자연을 사랑하는 밝은 성격의 관장입니다.",
                "pokemon": ["체리버", "로즈레이드", "이상해꽃", "라플레시아", "우츠보트", "덩쿠리"],
                "image": "",
            },
            {
                "name": "자두",
                "title": "장막시티 체육관 관장",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 전문",
                "desc": "도장에서 수련하는 어린 나이의 격투 타입 전문 관장입니다.",
                "pokemon": ["루카리오", "알통몬", "근육몬", "괴력몬", "시라소몬", "홍수몬"],
                "image": "",
            },
            {
                "name": "맥실러",
                "title": "들판시티 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": "선원 출신의 호탕한 성격으로 물 포켓몬을 다루는 관장입니다.",
                "pokemon": ["라이보르트", "꼬부기", "어니부기", "거북왕", "콘치", "왕콘치"],
                "image": "",
            },
            {
                "name": "멜리사",
                "title": "연고시티 체육관 관장",
                "type": "고스트",
                "specialty": "고스트 타입 포켓몬 전문",
                "desc": "이국적인 춤과 함께 고스트 포켓몬을 다루는 신비로운 관장입니다.",
                "pokemon": ["미라마사", "팬텀", "고우스트", "고오스", "무우마", "다크펫"],
                "image": "",
            },
            {
                "name": "동관",
                "title": "운하시티 체육관 관장",
                "type": "강철",
                "specialty": "강철 타입 포켓몬 전문",
                "desc": "화석 연구가로도 활동하는 강철 타입 전문 관장입니다.",
                "pokemon": ["금강펜치", "코일", "레어코일", "강철톤", "보스로라", "메탕구"],
                "image": "",
            },
            {
                "name": "무청",
                "title": "선단시티 체육관 관장",
                "type": "얼음",
                "specialty": "얼음 타입 포켓몬 전문",
                "desc": "설산 마을 선단시티에서 얼음 포켓몬을 다루는 관장입니다.",
                "pokemon": ["메쨩", "쥬쥬", "쥬레곤", "얼음귀신", "라프라스", "망나뇽"],
                "image": "",
            },
            {
                "name": "전진",
                "title": "물가시티 체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 전문",
                "desc": "신오지방의 마지막 관장으로, 전기 포켓몬을 이용한 강렬한 배틀이 특징입니다.",
                "pokemon": ["전룡", "피카츄", "라이츄", "코일", "레어코일", "찌리리공"],
                "image": "",
            },
            {
                "name": "시로나",
                "title": "신오리그 챔피언",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "포켓몬 신화를 연구하는 학자이자, 다양한 타입을 능숙하게 다루는 신오리그 챔피언입니다.",
                "pokemon": ["가디안", "밀로틱", "망나뇽", "잠만보", "리자몽", "윈디"],
                "image": "",
            },
        ],
    },
    "5세대 (하나)": {
        "color": "#628E90",
        "characters": [
            {
                "name": "투지",
                "title": "하나지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "하나지방에서 모험을 시작해 이상향을 추구하는 조직 플라즈마단과 맞서는 트레이너입니다.",
                "pokemon": ["꼬마도리", "뚜꾸리", "수댕이", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "덴트",
                "title": "성신시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "소믈리에 능력을 지닌 삼형제 관장 중 첫째입니다.",
                "pokemon": ["야나프", "이상해꽃", "라플레시아", "우츠보트", "덩쿠리", "나시"],
                "image": "",
            },
            {
                "name": "팟",
                "title": "성신시티 체육관 관장",
                "type": "불꽃",
                "specialty": "불꽃 타입 포켓몬 전문",
                "desc": "레스토랑을 함께 운영하는 삼형제 관장 중 둘째입니다.",
                "pokemon": ["바오프", "가디", "윈디", "날쌩마", "리자몽", "부스터"],
                "image": "",
            },
            {
                "name": "콘",
                "title": "성신시티 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": "레스토랑을 함께 운영하는 삼형제 관장 중 막내입니다.",
                "pokemon": ["파오리", "꼬부기", "어니부기", "거북왕", "콘치", "왕콘치"],
                "image": "",
            },
            {
                "name": "알로에",
                "title": "칠보시티 체육관 관장",
                "type": "노말",
                "specialty": "노말 타입 포켓몬 전문",
                "desc": "박물관 관장도 겸임하는 노말 타입 전문 체육관 관장입니다.",
                "pokemon": ["켄호로우", "밀탱크", "푸크린", "캥카", "럭키", "이브이"],
                "image": "",
            },
            {
                "name": "아티",
                "title": "구름시티 체육관 관장",
                "type": "벌레",
                "specialty": "벌레 타입 포켓몬 전문",
                "desc": "예술가로도 활동하는 개성 넘치는 벌레 타입 전문 관장입니다.",
                "pokemon": ["아이앤트", "단데기", "스라크", "도나단", "독침붕", "파라섹트"],
                "image": "",
            },
            {
                "name": "카밀레",
                "title": "뇌문시티 체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 전문",
                "desc": "모델로도 활동하는 화려한 전기 타입 전문 관장입니다.",
                "pokemon": ["제브라이카", "피카츄", "라이츄", "코일", "레어코일", "찌리리공"],
                "image": "",
            },
            {
                "name": "야콘",
                "title": "물풍경시티 체육관 관장",
                "type": "땅",
                "specialty": "땅 타입 포켓몬 전문",
                "desc": "광산 회사를 운영하는 사장이기도 한 땅 타입 전문 관장입니다.",
                "pokemon": ["동미러", "디그다", "닥트리오", "코뿌리", "뿔카노", "니드킹"],
                "image": "",
            },
            {
                "name": "풍란",
                "title": "궐수시티 체육관 관장",
                "type": "비행",
                "specialty": "비행 타입 포켓몬 전문",
                "desc": "비행기 조종사이기도 한 활발한 비행 타입 전문 관장입니다.",
                "pokemon": ["스완나", "구구", "피죤", "피죤투", "두두", "두트리오"],
                "image": "",
            },
            {
                "name": "담죽",
                "title": "설화시티 체육관 관장",
                "type": "얼음",
                "specialty": "얼음 타입 포켓몬 전문",
                "desc": "영화배우 활동 경력도 있는 얼음 타입 전문 관장입니다.",
                "pokemon": ["망키라", "쥬쥬", "쥬레곤", "메쨩", "얼음귀신", "라프라스"],
                "image": "",
            },
            {
                "name": "아이리스",
                "title": "쌍용시티 체육관 관장 / 하나리그 챔피언",
                "type": "드래곤",
                "specialty": "드래곤 타입 포켓몬 전문",
                "desc": "하나지방 마지막 관장으로 등장한 뒤, 후속작에서 챔피언으로 승격한 인물입니다.",
                "pokemon": ["감규옹", "미뇽", "신뇽", "망나뇽", "보만다", "한카리아스"],
                "image": "",
            },
            {
                "name": "아델",
                "title": "하나리그 챔피언",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "자유로운 방랑자 같은 인상으로, 다양한 타입을 다루는 하나리그 챔피언입니다.",
                "pokemon": ["볼트로스", "망나뇽", "잠만보", "리자몽", "윈디", "가디안"],
                "image": "",
            },
        ],
    },
    "6세대 (칼로스)": {
        "color": "#7B1FA2",
        "characters": [
            {
                "name": "칼름",
                "title": "칼로스지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "친구들과 함께 칼로스지방을 여행하며 플레어단의 야망을 저지하는 트레이너입니다.",
                "pokemon": ["도치마론", "푸호꼬", "개구마르", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "비올라",
                "title": "백단시티 체육관 관장",
                "type": "벌레",
                "specialty": "벌레 타입 포켓몬 전문",
                "desc": "사진작가로도 활동하는 칼로스지방 첫 체육관 관장입니다.",
                "pokemon": ["비파리", "단데기", "스라크", "도나단", "독침붕", "파라섹트"],
                "image": "",
            },
            {
                "name": "자크로",
                "title": "삼채시티 체육관 관장",
                "type": "바위",
                "specialty": "바위 타입 포켓몬 전문",
                "desc": "암벽 등반가이기도 한 바위 타입 전문 체육관 관장입니다.",
                "pokemon": ["초투불", "암트르", "꼬마돌", "데구리", "딱구리", "롱스톤"],
                "image": "",
            },
            {
                "name": "코르니",
                "title": "사라시티 체육관 관장",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 및 메가진화",
                "desc": "메가진화의 계승자로, 루카리오와 함께 싸우는 격투 타입 관장입니다.",
                "pokemon": ["루카리오", "알통몬", "근육몬", "괴력몬", "시라소몬", "홍수몬"],
                "image": "",
            },
            {
                "name": "후쿠지",
                "title": "비익시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "정원사이자 인생 경험이 풍부한 노년의 풀 타입 전문 관장입니다.",
                "pokemon": ["트로피우스", "이상해꽃", "라플레시아", "우츠보트", "덩쿠리", "나시"],
                "image": "",
            },
            {
                "name": "시트론",
                "title": "미르시티 체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 및 발명품",
                "desc": "과학 발명을 사랑하는 천재 소년 관장입니다.",
                "pokemon": ["레코디", "일레도리자드", "피카츄", "라이츄", "코일", "레어코일"],
                "image": "",
            },
            {
                "name": "마슈",
                "title": "후늬시티 체육관 관장",
                "type": "페어리",
                "specialty": "페어리 타입 포켓몬 전문",
                "desc": "기모노를 만드는 장인이자, 칼로스지방 최초의 페어리 타입 전문 관장입니다.",
                "pokemon": ["누리레느", "삐삐", "픽시", "푸린", "푸크린", "망나뇽"],
                "image": "",
            },
            {
                "name": "고지카",
                "title": "향전시티 체육관 관장",
                "type": "에스퍼",
                "specialty": "에스퍼 타입 포켓몬 전문",
                "desc": "천체 점술사이기도 한 신비로운 에스퍼 타입 전문 관장입니다.",
                "pokemon": ["염뮤", "후딘", "윤겔라", "슬리프", "슬리퍼", "마임맨"],
                "image": "",
            },
            {
                "name": "우르프",
                "title": "이설시티 체육관 관장",
                "type": "얼음",
                "specialty": "얼음 타입 포켓몬 전문",
                "desc": "눈보라가 몰아치는 이설시티를 지키는 마지막 체육관 관장입니다.",
                "pokemon": ["앱솔", "쥬쥬", "쥬레곤", "메쨩", "얼음귀신", "라프라스"],
                "image": "",
            },
            {
                "name": "카르네",
                "title": "칼로스리그 챔피언",
                "type": "기타",
                "specialty": "올라운더 / 배우",
                "desc": "유명 배우로도 활동하는 칼로스지방의 챔피언입니다.",
                "pokemon": ["가디안", "망나뇽", "잠만보", "리자몽", "윈디", "라이츄"],
                "image": "",
            },
        ],
    },
    "7세대 (알로라)": {
        "color": "#FF7043",
        "characters": [
            {
                "name": "영태",
                "title": "알로라지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "알로라지방으로 이주해 온 뒤, 섬 순례를 통해 초대 챔피언 자리에 오르는 트레이너입니다.",
                "pokemon": ["나몰빼미", "냐오불", "누리레느", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "하라",
                "title": "멜멜섬 섬의 왕(카푸)",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 전문",
                "desc": "알로라지방 체육관 문화를 대신하는 섬 순례 제도에서, 첫 섬을 지키는 격투 타입 섬의 왕입니다.",
                "pokemon": ["코코리스트", "알통몬", "근육몬", "괴력몬", "시라소몬", "홍수몬"],
                "image": "",
            },
            {
                "name": "릴리",
                "title": "수수께끼의 소녀",
                "type": "기타",
                "specialty": "서포터",
                "desc": "포켓몬을 무서워했으나 주인공과 만나며 용기를 얻고 성장하는 소녀입니다.",
                "pokemon": ["코스모스", "망나뇽", "잠만보", "리자몽", "윈디", "가디안"],
                "image": "",
            },
        ],
    },
    "8세대 (가라르)": {
        "color": "#00838F",
        "characters": [
            {
                "name": "승재",
                "title": "가라르지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "챔피언을 꿈꾸며 가라르지방의 챔피언스컵에 도전하는 밝은 성격의 트레이너입니다.",
                "pokemon": ["고릴타", "에이스번", "인텔리레온", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "아킬",
                "title": "터프스타디움 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "가라르지방의 첫 체육관 관장으로, 목장에서 풀 포켓몬을 기릅니다.",
                "pokemon": ["에어무드", "이상해꽃", "라플레시아", "우츠보트", "덩쿠리", "나시"],
                "image": "",
            },
            {
                "name": "야청",
                "title": "바우스타디움 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": "평소에는 차분하지만 배틀 시에는 승부욕이 불타오르는 패션 모델 겸 관장입니다.",
                "pokemon": ["갈가부기", "드레디어", "꼬부기", "어니부기", "거북왕", "콘치"],
                "image": "",
            },
            {
                "name": "순무",
                "title": "엔진스타디움 체육관 관장",
                "type": "불꽃",
                "specialty": "불꽃 타입 포켓몬 전문",
                "desc": "노련한 베테랑 관장으로, 한때 마이너리그로 강등되었다가 복귀했습니다.",
                "pokemon": ["코터스", "가디", "윈디", "날쌩마", "리자몽", "부스터"],
                "image": "",
            },
            {
                "name": "채두",
                "title": "래터럴스타디움 체육관 관장",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 전문",
                "desc": "격투기 도장을 운영하며, 냉철한 승부 근성을 지닌 관장입니다.",
                "pokemon": ["파이서치", "알통몬", "근육몬", "괴력몬", "시라소몬", "홍수몬"],
                "image": "",
            },
            {
                "name": "어니언",
                "title": "래터럴스타디움 체육관 관장",
                "type": "고스트",
                "specialty": "고스트 타입 포켓몬 전문",
                "desc": "말수가 적고 게임을 좋아하는 소년 고스트 타입 전문 관장입니다.",
                "pokemon": ["다크펫", "팬텀", "고우스트", "고오스", "무우마", "킬가르도"],
                "image": "",
            },
            {
                "name": "포플러",
                "title": "아라베스크스타디움 체육관 관장",
                "type": "페어리",
                "specialty": "페어리 타입 포켓몬 전문",
                "desc": "고령에도 화려한 패션 감각을 뽐내는 페어리 타입 전문 관장입니다.",
                "pokemon": ["픽시", "삐삐", "푸린", "푸크린", "누리레느", "망나뇽"],
                "image": "",
            },
            {
                "name": "두송",
                "title": "스파이크체육관 관장",
                "type": "악",
                "specialty": "악 타입 포켓몬 전문 / 싱어송라이터",
                "desc": "가라르지방 최초의 악 타입 체육관 관장이자, 밴드 활동도 하는 인물입니다.",
                "pokemon": ["오브스타", "니로에", "다크펫", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "금랑",
                "title": "너클스타디움 체육관 관장",
                "type": "드래곤",
                "specialty": "드래곤 타입 포켓몬 전문",
                "desc": "챔피언 단델의 라이벌로, 가라르지방 최강급으로 꼽히는 관장입니다.",
                "pokemon": ["우락훌라", "미뇽", "신뇽", "망나뇽", "보만다", "한카리아스"],
                "image": "",
            },
            {
                "name": "단델",
                "title": "가라르리그 챔피언",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "10년 넘게 무패를 자랑하는 가라르지방의 인기 절정 챔피언입니다.",
                "pokemon": ["다이나맥스 리자몽", "망나뇽", "잠만보", "리자몽", "윈디", "가디안"],
                "image": "",
            },
        ],
    },
    "9세대 (팔데아)": {
        "color": "#C2185B",
        "characters": [
            {
                "name": "보민",
                "title": "팔데아지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "그레이프 아카데미에 다니며 전설의 여행을 통해 팔데아지방을 탐험하는 학생입니다.",
                "pokemon": ["나오하", "뜨아거", "꾸왁스", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "단풍",
                "title": "세르클시티 체육관 관장",
                "type": "벌레",
                "specialty": "벌레 타입 포켓몬 전문",
                "desc": "파티시에로도 활동하는 팔데아지방 첫 체육관 관장입니다.",
                "pokemon": ["또도바스", "단데기", "스라크", "도나단", "독침붕", "파라섹트"],
                "image": "",
            },
            {
                "name": "콜사",
                "title": "보울시티 체육관 관장",
                "type": "풀",
                "specialty": "풀 타입 포켓몬 전문",
                "desc": "예술가로 활동하며 풀 포켓몬을 활용한 작품을 만드는 관장입니다.",
                "pokemon": ["파이어스", "이상해꽃", "라플레시아", "우츠보트", "덩쿠리", "나시"],
                "image": "",
            },
            {
                "name": "모야모",
                "title": "누룩스시티 체육관 관장",
                "type": "전기",
                "specialty": "전기 타입 포켓몬 전문",
                "desc": "스트리머로도 활동하는 개성 넘치는 전기 타입 전문 관장입니다.",
                "pokemon": ["무테나", "피카츄", "라이츄", "코일", "레어코일", "찌리리공"],
                "image": "",
            },
            {
                "name": "곤포",
                "title": "카라프시티 체육관 관장",
                "type": "물",
                "specialty": "물 타입 포켓몬 전문",
                "desc": "요리사로도 활동하는 물 타입 전문 체육관 관장입니다.",
                "pokemon": ["웨이니발", "꼬부기", "어니부기", "거북왕", "콘치", "왕콘치"],
                "image": "",
            },
            {
                "name": "청목",
                "title": "참푸르시티 체육관 관장 / 사천왕",
                "type": "노말",
                "specialty": "노말 타입 포켓몬 전문",
                "desc": "체육관 관장과 사천왕(비행 타입)을 동시에 겸임하는 특이한 인물입니다.",
                "pokemon": ["따르지비", "밀탱크", "푸크린", "캥카", "럭키", "이브이"],
                "image": "",
            },
            {
                "name": "라임",
                "title": "프리지시티 체육관 관장",
                "type": "고스트",
                "specialty": "고스트 타입 포켓몬 전문",
                "desc": "래퍼로도 활동하는 개성 강한 고스트 타입 전문 관장입니다.",
                "pokemon": ["킬가르도", "팬텀", "고우스트", "고오스", "무우마", "다크펫"],
                "image": "",
            },
            {
                "name": "리파",
                "title": "베이크시티 체육관 관장",
                "type": "에스퍼",
                "specialty": "에스퍼 타입 포켓몬 전문",
                "desc": "메이크업 아티스트로도 활동하는 에스퍼 타입 전문 관장입니다.",
                "pokemon": ["누리레느", "후딘", "윤겔라", "슬리프", "슬리퍼", "마임맨"],
                "image": "",
            },
            {
                "name": "그루샤",
                "title": "나페산시티 체육관 관장",
                "type": "얼음",
                "specialty": "얼음 타입 포켓몬 전문",
                "desc": "프로 스노보더 출신으로, 팔데아지방 최강으로 꼽히는 관장입니다.",
                "pokemon": ["얼음귀신", "쥬쥬", "쥬레곤", "메쨩", "라프라스", "망나뇽"],
                "image": "",
            },
        ],
    },
    "히스이 지방": {
        "color": "#5C5470",
        "characters": [
            {
                "name": "영빈",
                "title": "히스이지방 주인공",
                "type": "기타",
                "specialty": "올라운더",
                "desc": "현대에서 신비한 힘에 이끌려 과거의 히스이지방으로 전이되어, 은하단의 일원으로 지역 최초의 포켓몬 도감을 완성하는 인물입니다.",
                "pokemon": ["나몰빼미", "브케인", "수댕이", "망나뇽", "잠만보", "리자몽"],
                "image": "",
            },
            {
                "name": "반죽",
                "title": "은하단 조사대 캡틴",
                "type": "격투",
                "specialty": "격투 타입 포켓몬 및 육체 단련",
                "desc": "금강단 소속이자 은하단 캡틴으로, 흑요의 들판에서 왕을 모시며 주인공의 조력자가 되어 주는 호쾌한 인물입니다.",
                "pokemon": ["창파나이트", "알통몬", "근육몬", "괴력몬", "시라소몬", "홍수몬"],
                "image": "",
            },
            {
                "name": "주이",
                "title": "은하단 의료대 캡틴",
                "type": "노멀",
                "specialty": "치유 및 포켓몬 관리",
                "desc": "진주단 출신으로 콧등의 흉터가 특징이며, 다소 쌀쌀맞아 보이지만 포켓몬들을 깊이 아끼는 캡틴입니다.",
                "pokemon": ["잠만보", "밀탱크", "푸크린", "캥카", "럭키", "이브이"],
                "image": "",
            },
            {
                "name": "윤열",
                "title": "은하단 단장",
                "type": "기타",
                "specialty": "종합 전투력",
                "desc": "엄격하고 카리스마 넘치는 은하단의 최고 수장으로, 히스이지방의 혹독한 환경 속에서 사람과 포켓몬의 공존을 위해 철저함을 유지합니다.",
                "pokemon": ["픽시", "윈디", "망나뇽", "잠만보", "리자몽", "가디안"],
                "image": "",
            },
            {
                "name": "폐기",
                "title": "은하단 조사대 리더",
                "type": "에스퍼",
                "specialty": "지략 및 분석",
                "desc": "주인공을 은하단에 영입해 준 장본인이자, 마을과 조사대를 이끄는 든든한 리더입니다.",
                "pokemon": ["레트라", "후딘", "윤겔라", "슬리프", "슬리퍼", "마임맨"],
                "image": "",
            },
        ],
    },
}



# 인물 도감 표시 순서 (주인공 → 라이벌 → 포켓몬 박사 → 체육관 관장 → 포켓몬리그 → 로켓단)
CHARACTER_CATEGORY_ORDER = [
    "주인공",
    "라이벌",
    "포켓몬 박사",
    "체육관 관장",
    "사천왕",
    "포켓몬리그",
    "로켓단",
]

CHARACTER_CATEGORY_ICONS = {
    "주인공": "🧑",
    "라이벌": "⚔️",
    "포켓몬 박사": "🔬",
    "체육관 관장": "🏟️",
    "사천왕": "🎖️",
    "포켓몬리그": "🏆",
    "로켓단": "💀",
    "기타": "👤",
}

CHARACTER_CATEGORY_MAP = {
    "레드": "주인공",
    "심향": "주인공",
    "휘웅": "주인공",
    "광휘": "주인공",
    "투지": "주인공",
    "칼름": "주인공",
    "영태": "주인공",
    "승재": "주인공",
    "보민": "주인공",
    "영빈": "주인공",
    "그린": "라이벌",
    "오박사": "포켓몬 박사",
    "비주기": "로켓단",
    "목호": "포켓몬리그",
    "윤진": "포켓몬리그",
    "시로나": "포켓몬리그",
    "아이리스": "포켓몬리그",
    "아델": "포켓몬리그",
    "카르네": "포켓몬리그",
    "단델": "포켓몬리그",
}


def get_character_category(char):
  if char["name"] in CHARACTER_CATEGORY_MAP:
    return CHARACTER_CATEGORY_MAP[char["name"]]
  if "사천왕" in char["title"] and (
      "체육관" not in char["title"] and "스타디움" not in char["title"]
  ):
    return "사천왕"
  if "체육관" in char["title"] or "스타디움" in char["title"]:
    return "체육관 관장"
  return "기타"


def character_sort_key(char):
  category = get_character_category(char)
  if category in CHARACTER_CATEGORY_ORDER:
    return CHARACTER_CATEGORY_ORDER.index(category)
  return len(CHARACTER_CATEGORY_ORDER)


# 세대별 대표 데뷔작(정식 발매 타이틀)
GENERATION_TO_GAME = {
    "1세대 (관동)": "포켓몬스터 레드·그린",
    "2세대 (성도)": "포켓몬스터 골드·실버",
    "3세대 (호연)": "포켓몬스터 루비·사파이어",
    "4세대 (신오)": "포켓몬스터 디아루가·펄기아",
    "5세대 (하나)": "포켓몬스터 블랙·화이트",
    "6세대 (칼로스)": "포켓몬스터 X·Y",
    "7세대 (알로라)": "포켓몬스터 썬·문",
    "8세대 (가라르)": "포켓몬스터 소드·실드",
    "9세대 (팔데아)": "포켓몬스터 스칼렛·바이올렛",
    "히스이 지방": "포켓몬 레전드 아르세우스",
}

# 확인된 인물 한정 추가 정보 (성별/나이/출신지/가족관계 등). 정보가 없는 인물은
# 기본값("정보 없음")으로 표시됩니다.
CHARACTER_EXTRA_INFO = {
    "레드": {
        "gender": "남성",
        "age": "11세(RGBY/FRLG) → 14세(GSC/HGSS) → 불명(SM/USUM)",
        "hometown": "태초마을",
        "family": "아버지(불명), 어머니",
    },
    "그린": {
        "gender": "남성",
        "age": "11세(RGBY/FRLG) → 14세(GSC/HGSS)",
        "hometown": "태초마을",
        "family": "여동생(블루)",
    },
    "오박사": {
        "gender": "남성",
        "age": "불명(노년)",
        "hometown": "태초마을",
        "family": "손자 그린",
    },
}


def get_character_extra_info(char_name):
  return CHARACTER_EXTRA_INFO.get(
      char_name,
      {"gender": "정보 없음", "age": "정보 없음", "hometown": "정보 없음", "family": "정보 없음"},
  )


# 한글 추천 포켓몬을 위한 영문 매핑
FEATURED_POKEMON_MAP = {
    "켄타로스": "tauros",
    "식스테일": "vulpix",
    "가디": "growlithe",
    "슬리프": "drowzee",
    "나무지기": "treecko",
    "루브도": "smeargle",
}


# 페이지 이동 함수
def go_to_page(page_name):
  st.session_state.current_page = page_name
  if page_name == "포켓몬 도감":
    st.session_state.selected_gen = None
  elif page_name == "인물 도감":
    st.session_state.selected_char_gen = None
    st.session_state.selected_character = None
  elif page_name == "아이템 도감":
    st.session_state.item_category = None
    st.session_state.selected_item = None
    st.session_state.item_search_query = ""


# 검색어 기록 추가 함수
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


# 검색어 업데이트 콜백
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


def update_item_search():
  st.session_state.item_search_query = st.session_state.item_search_input


def update_character_search():
  query = st.session_state.char_user_input
  st.session_state.character_search_query = query
  if query.strip():
    add_character_search_history(query)


# CSS 스타일 적용
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
        border: 2px solid #444444;
        border-radius: 10px;
        padding: 20px;
        background-color: transparent;
        margin-bottom: 15px;
    }
    .char-info-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        font-size: 0.9rem;
        border: 1px solid #444;
    }
    .char-info-table th {
        background-color: #7a2020;
        color: white;
        padding: 10px 8px;
        border: 1px solid #333;
        text-align: left;
        width: 32%;
        font-weight: bold;
    }
    .char-info-table td {
        background-color: #1a1a1a;
        color: #e8c46a;
        padding: 10px 8px;
        border: 1px solid #333;
        text-align: center;
        font-weight: bold;
    }
    .char-name-banner {
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        border: 2px solid #ffffff;
        margin-bottom: 12px;
    }
    .char-portrait {
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 5rem;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
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


@st.cache_data(ttl=604800)
def translate_to_ko(text):
  """영어 도감 설명을 한국어로 변환합니다.

  PokeAPI의 최신 포켓몬(특히 #899~#1025)은 한국어 flavor_text가
  없는 경우가 있습니다. 이 경우 번역 서버를 순차적으로 사용합니다.
  번역 실패 결과를 캐시하지 않는 것이 중요합니다.
  """
  if not text:
    return ""

  clean_text = (
      str(text)
      .replace("\n", " ")
      .replace("\f", " ")
      .strip()
  )

  # 이미 한국어라면 그대로 반환
  korean_count = sum("\uac00" <= ch <= "\ud7a3" for ch in clean_text)
  if korean_count >= 3:
    return clean_text

  # 1차: Google Translate 비공식 웹 엔드포인트
  try:
    res = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={
            "client": "gtx",
            "sl": "en",
            "tl": "ko",
            "dt": "t",
            "q": clean_text,
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    if res.status_code == 200:
      data = res.json()
      translated = "".join(
          part[0]
          for part in data[0]
          if isinstance(part, list) and len(part) > 0 and part[0]
      ).strip()

      if translated and translated != clean_text:
        return translated
  except Exception:
    pass

  # 2차: MyMemory 무료 번역 API
  try:
    res = requests.get(
        "https://api.mymemory.translated.net/get",
        params={
            "q": clean_text,
            "langpair": "en|ko",
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    if res.status_code == 200:
      data = res.json()
      translated = (
          data.get("responseData", {}).get("translatedText", "").strip()
      )
      if translated and translated.lower() != clean_text.lower():
        return translated
  except Exception:
    pass

  # 번역 서버가 모두 실패하면 영어가 그대로 화면에 노출되는 것을 막습니다.
  return "한국어 도감 설명을 불러오는 중입니다. 잠시 후 다시 확인해 주세요."


@st.cache_data(ttl=604800)
def extract_single_flavor_text(species_data):
  """한국어 도감 설명을 우선 사용하고, 없으면 영어를 한국어로 번역합니다."""
  flavor_entries = species_data.get("flavor_text_entries", [])

  # 1순위: PokeAPI에 저장된 한국어 원문
  for entry in flavor_entries:
    if entry.get("language", {}).get("name") == "ko":
      text = entry.get("flavor_text", "")
      if text:
        cleaned = (
            text.replace("\n", " ")
            .replace("\f", " ")
            .strip()
        )

        # 혹시 language=ko인데 내용이 영어로 들어온 경우도 번역
        if any("\uac00" <= ch <= "\ud7a3" for ch in cleaned):
          return normalize_dex_korean_style(cleaned)
        return normalize_dex_korean_style(translate_to_ko(cleaned))

  # 2순위: 영어 원문 → 한국어 번역
  for entry in flavor_entries:
    if entry.get("language", {}).get("name") == "en":
      text = entry.get("flavor_text", "")
      if text:
        return normalize_dex_korean_style(translate_to_ko(text))

  return "도감 설명이 존재하지 않습니다."


def normalize_dex_korean_style(text):
  """도감 문체를 게임 도감처럼 간결한 평서체(~한다/~된다)로 통일합니다."""
  if not text:
    return ""

  text = (
      str(text)
      .replace("\r\n", "\n")
      .replace("\r", "\n")
      .replace("\f", " ")
      .strip()
  )

  # 번역기가 자주 만드는 존댓말/문어체를 도감식 평서체로 변환합니다.
  replacements = [
      ("있습니다.", "있다."),
      ("없습니다.", "없다."),
      ("됩니다.", "된다."),
      ("합니다.", "한다."),
      ("합니다", "한다"),
      ("됩니다", "된다"),
      ("입니다.", "이다."),
      ("입니다", "이다"),
      ("합니다만", "하지만"),
      ("있으며", "있고"),
      ("있습니다만", "있지만"),
      ("사용합니다.", "사용한다."),
      ("사용됩니다.", "사용된다."),
      ("만듭니다.", "만든다."),
      ("만들어집니다.", "만들어진다."),
      ("보냅니다.", "보낸다."),
      ("냅니다.", "낸다."),
      ("줍니다.", "준다."),
      ("얻습니다.", "얻는다."),
      ("배웁니다.", "배운다."),
      ("배웁니다", "배운다"),
      ("생깁니다.", "생긴다."),
      ("생겨납니다.", "생겨난다."),
      ("모입니다.", "모인다."),
      ("모읍니다.", "모은다."),
      ("사라집니다.", "사라진다."),
      ("변합니다.", "변한다."),
      ("변화합니다.", "변화한다."),
      ("움직입니다.", "움직인다."),
      ("빛납니다.", "빛난다."),
      ("빛납니다", "빛난다"),
      ("뿜어냅니다.", "뿜어낸다."),
      ("내뿜습니다.", "내뿜는다."),
      ("가지고 있습니다.", "가지고 있다."),
      ("지니고 있습니다.", "지니고 있다."),
      ("알려져 있습니다.", "알려져 있다."),
      ("여겨집니다.", "여겨진다."),
      ("느껴집니다.", "느껴진다."),
      ("가능합니다.", "가능하다."),
      ("불가능합니다.", "불가능하다."),
      ("유용합니다.", "유용하다."),
      ("강력합니다.", "강력하다."),
      ("특별합니다.", "특별하다."),
      ("중요합니다.", "중요하다."),
      ("필요합니다.", "필요하다."),
      ("위험합니다.", "위험하다."),
      ("귀중한 재료가 됩니다.", "귀중한 재료가 된다."),
      ("재료로 사용됩니다.", "재료로 사용된다."),
  ]

  for old, new in replacements:
    text = text.replace(old, new)

  # "합니다/됩니다"가 활용형으로 남는 경우도 기본적인 도감 평서체로 정리합니다.
  import re
  text = re.sub(r"합니다(?=[.!?])", "한다", text)
  text = re.sub(r"됩니다(?=[.!?])", "된다", text)
  text = re.sub(r"있습니다(?=[.!?])", "있다", text)
  text = re.sub(r"없습니다(?=[.!?])", "없다", text)

  # 도감 문장은 문장별로 줄을 나눠 읽기 쉽게 합니다.
  text = re.sub(r"(?<=[.!?])\s+(?=[가-힣A-Za-z])", "\n", text)
  text = re.sub(r"\n{2,}", "\n", text)

  return text.strip()


@st.cache_data(ttl=86400)
def get_pokemon_name_by_id(pokemon_id):
  for _ in range(2):
    try:
      res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}", timeout=6
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


@st.cache_data(ttl=604800)
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


# #899~#905는 8세대(히스이), #906~#1025는 9세대(팔데아)입니다.
# 두 범위 모두 PokeAPI에 한국어 도감 설명이 없는 포켓몬이 있을 수 있으므로
# extract_single_flavor_text()에서 자동 한국어 번역을 적용합니다.
@st.cache_data(ttl=604800)
def get_pokemon_data(target_id):
  if not target_id:
    return None

  try:
    pokemon_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{target_id}", timeout=8
    )
    if pokemon_res.status_code != 200:
      return None
    pokemon_data = pokemon_res.json()

    species_res = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{target_id}", timeout=8
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


def get_generation_id_range(g_name):
  """인물이 속한 세대의 전국도감 ID 범위를 반환합니다.
  (히스이 지방처럼 GENERATIONS에 없는 세대는 전체 범위에서 탐색합니다.)"""
  if g_name in GENERATIONS:
    return GENERATIONS[g_name]["range"]
  return (1, 1025)


@st.cache_data(ttl=86400)
def find_pokemon_id_by_korean_name(query_name, start_id, end_id):
  """세대 ID 범위 내에서 한글 이름과 정확히 일치하는 포켓몬의
  전국도감 번호를 찾습니다. 이름-번호 매칭은 시간이 지나도 바뀌지 않으므로
  길게 캐싱해도 안전합니다."""
  query_name = (query_name or "").strip()
  if not query_name:
    return None

  # "다이나맥스 리자몽" 처럼 접두어가 붙은 이름은 원래 이름으로도 시도합니다.
  candidates = [query_name]
  for prefix in ("다이나맥스 ", "메가", "원시"):
    if query_name.startswith(prefix) and query_name != prefix:
      stripped = query_name[len(prefix):]
      if stripped and stripped not in candidates:
        candidates.append(stripped)

  for name in candidates:
    for p_id in range(start_id, end_id + 1):
      ko_name = get_pokemon_name_by_id(p_id)
      if ko_name == name:
        return p_id
  return None


@st.cache_data(ttl=600)
def fetch_pokemon_artwork_url(pokemon_id):
  """포켓몬 번호로 공식 아트워크 URL을 가져옵니다.
  네트워크 순간 오류로 실패한 결과가 하루 종일 캐싱되지 않도록
  실패 결과는 10분만 캐싱하고(재시도 유도), 최대 2번까지 재시도합니다."""
  if not pokemon_id:
    return ""
  for _ in range(2):
    try:
      p_res = requests.get(
          f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=6
      )
      if p_res.status_code == 200:
        p_data = p_res.json()
        img_url = (
            p_data["sprites"]["other"]["official-artwork"]["front_default"]
            or p_data["sprites"]["front_default"]
            or ""
        )
        if img_url:
          return img_url
    except Exception:
      pass
  return ""


def resolve_character_pokemon(query_name, start_id, end_id):
  """{"id": 전국도감 번호, "image": 공식 아트워크 URL} 을 반환합니다.
  인물의 세대 범위 안에서 못 찾으면, 다른 세대에서 데려온 포켓몬일 수도 있으니
  전국 도감(1~1025) 전체에서 한 번 더 찾아봅니다. 그래도 없으면 None."""
  pokemon_id = find_pokemon_id_by_korean_name(query_name, start_id, end_id)
  if not pokemon_id and (start_id, end_id) != (1, 1025):
    pokemon_id = find_pokemon_id_by_korean_name(query_name, 1, 1025)
  if not pokemon_id:
    return None
  return {"id": pokemon_id, "image": fetch_pokemon_artwork_url(pokemon_id)}


# ==================== 아이템(도구) 도감 데이터 ====================
# 나무위키 '포켓몬스터/도구/배틀' 문서의 분류 체계를 참고하여
# 배틀에서 쓰이는 지니는 도구를 9가지 갈래로 정리했습니다.

ITEM_CATEGORIES = {
    "기술 강화 도구": {
        "color": "#F08030",
        "icon": "🔥",
        "desc": "특정 타입이나 공격/특수 분류의 기술 위력을 높여주는 도구입니다.",
        "items": [
            {"name": "목탄", "en": "charcoal", "summary": "불꽃 타입 기술 위력 1.2배",
             "detail": "불꽃 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다. 불꽃 타입 에이스에게 자주 채용됩니다."},
            {"name": "신비한물", "en": "mystic-water", "summary": "물 타입 기술 위력 1.2배",
             "detail": "물 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다."},
            {"name": "기적의씨", "en": "miracle-seed", "summary": "풀 타입 기술 위력 1.2배",
             "detail": "풀 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다."},
            {"name": "자석", "en": "magnet", "summary": "전기 타입 기술 위력 1.2배",
             "detail": "전기 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다."},
            {"name": "검은벨트", "en": "black-belt", "summary": "격투 타입 기술 위력 1.2배",
             "detail": "격투 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다."},
            {"name": "흑안경", "en": "black-glasses", "summary": "악 타입 기술 위력 1.2배",
             "detail": "악 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다."},
            {"name": "용의송곳니", "en": "dragon-fang", "summary": "드래곤 타입 기술 위력 1.2배",
             "detail": "드래곤 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다."},
            {"name": "확대경", "en": "expert-belt", "summary": "효과가 뛰어난 기술 위력 1.2배",
             "detail": "상대에게 상성상 효과가 뛰어난(반감이 아닌) 기술을 사용했을 때 위력을 1.2배로 올려주는 범용 강화 도구입니다."},
            {"name": "근육의띠", "en": "muscle-band", "summary": "물리 기술 위력 1.1배",
             "detail": "분류가 물리인 기술의 위력을 1.1배로 소폭 올려주는 도구입니다."},
            {"name": "신사의안경", "en": "wise-glasses", "summary": "특수 기술 위력 1.1배",
             "detail": "분류가 특수인 기술의 위력을 1.1배로 소폭 올려주는 도구입니다."},
        ],
    },
    "능력치 강화 도구": {
        "color": "#6890F0",
        "icon": "📈",
        "desc": "지닌 포켓몬의 특정 능력치를 실수치 기준으로 큰 폭으로 올려주는 도구입니다.",
        "items": [
            {"name": "구애머리띠", "en": "choice-band", "summary": "공격 1.5배 / 기술 고정",
             "detail": "공격 실수치를 1.5배로 올려주지만, 필드에 나온 뒤 처음 사용한 기술만 계속 쓸 수 있게 됩니다."},
            {"name": "구애안경", "en": "choice-specs", "summary": "특수공격 1.5배 / 기술 고정",
             "detail": "특수공격 실수치를 1.5배로 올려주지만, 필드에 나온 뒤 처음 사용한 기술만 계속 쓸 수 있게 됩니다."},
            {"name": "구애스카프", "en": "choice-scarf", "summary": "스피드 1.5배 / 기술 고정",
             "detail": "스피드 실수치를 1.5배로 올려주지만, 필드에 나온 뒤 처음 사용한 기술만 계속 쓸 수 있게 됩니다."},
            {"name": "부스트에너지", "en": "booster-energy", "summary": "고유 특성 발동 시 능력치 상승",
             "detail": "고대·미래 포켓몬 등 전용 특성을 가진 포켓몬이 지니면, 특성이 발동해 공격/특수공격 또는 스피드 중 낮은 능력치가 한 랭크 상승합니다."},
            {"name": "충전지", "en": "cell-battery", "summary": "전기 기술 피격 시 공격 1랭크 상승",
             "detail": "전기 타입 기술에 맞으면 그 데미지를 견디고 공격이 1랭크 상승하는 1회용 도구입니다."},
        ],
    },
    "전용 도구": {
        "color": "#F85888",
        "icon": "🎯",
        "desc": "특정 포켓몬만 효과를 보는 전용 장비로, 다른 포켓몬이 지니면 효과가 없습니다.",
        "items": [
            {"name": "전기구슬", "en": "light-ball", "summary": "피카츄 전용 · 공격/특공 2배",
             "detail": "피카츄가 지니면 공격과 특수공격 실수치가 2배로 상승합니다. 피츄나 라이츄에게는 적용되지 않습니다."},
            {"name": "두꺼운뼈", "en": "thick-club", "summary": "딱구리 계열 전용 · 공격 2배",
             "detail": "딱구리, 딱쥐다리, 텅구리가 지니면 공격 실수치가 2배로 상승합니다."},
            {"name": "딥시통", "en": "deep-sea-tooth", "summary": "골더프 전용 · 특수공격 2배",
             "detail": "골더프가 지니면 특수공격 실수치가 2배로 상승합니다."},
            {"name": "딥시비늘", "en": "deep-sea-scale", "summary": "골더프 전용 · 특수방어 2배",
             "detail": "골더프가 지니면 특수방어 실수치가 2배로 상승합니다."},
            {"name": "금속가루", "en": "metal-powder", "summary": "메타몽 전용 · 방어 2배",
             "detail": "메타몽이 지니면 방어 실수치가 2배로 상승합니다."},
            {"name": "쪽빛구슬", "en": "blue-orb", "summary": "가이오가 전용 · 원시회귀",
             "detail": "가이오가가 지니고 배틀에 나가면 원시회귀하여 원시가이오가가 됩니다."},
            {"name": "주홍구슬", "en": "red-orb", "summary": "그란돈 전용 · 원시회귀",
             "detail": "그란돈이 지니고 배틀에 나가면 원시회귀하여 원시그란돈이 됩니다."},
        ],
    },
    "체력 회복 도구": {
        "color": "#78C850",
        "icon": "💊",
        "desc": "체력이 일정 수준 이하로 떨어지면 자동으로 발동하거나, 매 턴 조금씩 체력을 회복시켜 주는 도구입니다.",
        "items": [
            {"name": "오렌열매", "en": "oran-berry", "summary": "체력 절반 이하 시 10 회복",
             "detail": "체력이 최대체력의 절반 이하로 떨어지면 자동으로 사용되어 체력을 10 회복시키는 나무열매입니다."},
            {"name": "잎사귀열매", "en": "sitrus-berry", "summary": "체력 절반 이하 시 1/4 회복",
             "detail": "체력이 최대체력의 절반 이하로 떨어지면 자동으로 사용되어 최대체력의 1/4을 회복시키는 나무열매입니다."},
            {"name": "먹다남은과자", "en": "leftovers", "summary": "매 턴 1/16 회복",
             "detail": "턴이 끝날 때마다 최대체력의 1/16만큼 서서히 체력을 회복시켜 주는 도구입니다. 오래 버티는 포켓몬에게 특히 유용합니다."},
        ],
    },
    "내성 도구": {
        "color": "#B8B8D0",
        "icon": "🛡️",
        "desc": "특정 상태이상이나 능력치 하락, 특정 타입 기술의 피해를 줄이거나 무효로 만들어 주는 도구입니다.",
        "items": [
            {"name": "하양허브", "en": "white-herb", "summary": "하락한 능력치 1회 원상복구",
             "detail": "능력치가 하락한 상태라면 이를 한 번 원래대로 되돌려주고 사라지는 1회용 도구입니다."},
            {"name": "멘탈허브", "en": "mental-herb", "summary": "정신 계열 상태 1회 해제",
             "detail": "헤롱헤롱, 도발, 사슬묶기 등 정신에 영향을 주는 상태를 한 번 풀어주고 사라지는 1회용 도구입니다."},
            {"name": "진정열매", "en": "persim-berry", "summary": "혼란 상태 회복",
             "detail": "혼란 상태에 걸렸을 때 자동으로 사용되어 혼란을 풀어주는 나무열매입니다."},
        ],
    },
    "교체 도구": {
        "color": "#A890F0",
        "icon": "🔄",
        "desc": "특정 조건이 되면 지닌 포켓몬이나 상대 포켓몬을 강제로 교체시키는 도구입니다.",
        "items": [
            {"name": "탈출버튼", "en": "eject-button", "summary": "피격 시 강제 교체",
             "detail": "기술에 맞아 데미지를 입으면 지닌 포켓몬이 자동으로 필드에서 물러나고, 대기 중인 다른 포켓몬으로 교체됩니다."},
            {"name": "탈출팩", "en": "eject-pack", "summary": "능력치 하락 시 강제 교체",
             "detail": "능력치가 하락하면 자동으로 필드에서 물러나고 다른 포켓몬으로 교체되는 도구입니다."},
            {"name": "빨간카드", "en": "red-card", "summary": "피격 시 상대를 강제 교체",
             "detail": "기술에 맞아 데미지를 입으면 상대 포켓몬을 강제로 다른 포켓몬으로 교체시키는 도구입니다."},
        ],
    },
    "지속시간 증가 도구": {
        "color": "#98D8D8",
        "icon": "⏳",
        "desc": "날씨나 필드, 벽 등의 지속 턴 수를 늘려주는 도구입니다.",
        "items": [
            {"name": "축축한바위", "en": "damp-rock", "summary": "비 지속 턴 연장(8턴)",
             "detail": "비가 내리는 상태의 지속 턴 수를 8턴으로 늘려주는 도구입니다."},
            {"name": "뜨거운바위", "en": "heat-rock", "summary": "쾌청 지속 턴 연장(8턴)",
             "detail": "쾌청 상태의 지속 턴 수를 8턴으로 늘려주는 도구입니다."},
            {"name": "모래바위", "en": "smooth-rock", "summary": "모래바람 지속 턴 연장(8턴)",
             "detail": "모래바람 상태의 지속 턴 수를 8턴으로 늘려주는 도구입니다."},
            {"name": "얼음바위", "en": "icy-rock", "summary": "싸라기눈 지속 턴 연장(8턴)",
             "detail": "싸라기눈(눈) 상태의 지속 턴 수를 8턴으로 늘려주는 도구입니다."},
            {"name": "빛의점토", "en": "light-clay", "summary": "리플렉터·빛의장막 연장(8턴)",
             "detail": "리플렉터와 빛의장막의 지속 턴 수를 8턴으로 늘려주는 도구입니다."},
        ],
    },
    "자기 피해 도구": {
        "color": "#C03028",
        "icon": "💥",
        "desc": "강력한 효과를 주는 대신 사용할 때마다 스스로도 피해를 입는 도구입니다.",
        "items": [
            {"name": "생명의구슬", "en": "life-orb", "summary": "기술 위력 1.3배 / 반동 1/10",
             "detail": "모든 기술의 위력을 1.3배로 올려주지만, 기술을 사용할 때마다 자신의 최대체력 1/10만큼 반동 피해를 입는 고위험 고효율 도구입니다."},
            {"name": "가시열매", "en": "sticky-barb", "summary": "매 턴 1/8 피해 / 접촉 시 전이",
             "detail": "턴이 끝날 때마다 최대체력의 1/8만큼 피해를 입지만, 접촉 기술에 맞으면 상대 포켓몬에게 옮겨갈 수 있는 나무열매 계열 도구입니다."},
        ],
    },
    "기타": {
        "color": "#A8A878",
        "icon": "❓",
        "desc": "위 분류에 속하지 않는 특수한 효과를 가진 도구들입니다.",
        "items": [
            {"name": "쇠구슬", "en": "iron-ball", "summary": "스피드 절반 / 비행·부유 무효화",
             "detail": "스피드를 절반으로 낮추지만, 비행 타입이나 부유 특성을 가진 포켓몬도 땅 타입 기술에 맞을 수 있게 만듭니다."},
            {"name": "갈고리발톱", "en": "grip-claw", "summary": "조이기 기술 지속 턴 연장",
             "detail": "휘감기, 모래지옥 등 상대를 옭아매는 조이기 계열 기술의 지속 턴을 늘려주는 도구입니다."},
        ],
    },
}


# ---- 타입 계열 배틀 도구 일괄 추가 (나무위키 하위 문서 '기술 강화/전용 도구' 등 기준) ----
_TYPE_ENHANCE_ITEMS = {
    "normal": ("실크스카프", "silk-scarf"), "ice": ("안녹는얼음", "never-melt-ice"),
    "poison": ("독바늘", "poison-barb"), "ground": ("부드러운모래", "soft-sand"),
    "flying": ("예리한부리", "sharp-beak"), "psychic": ("이상한스푼", "twisted-spoon"),
    "bug": ("은가루", "silver-powder"), "rock": ("딱딱한돌", "hard-stone"),
    "ghost": ("저주의부적", "spell-tag"), "steel": ("금속코트", "metal-coat"),
}
_TYPE_GEMS = {t: (n + "주얼", f"{t}-gem") for t, n in TYPE_NAME_MAP.items()}
_TYPE_PLATES = {
    "fighting": ("격투의판", "fist-plate"), "flying": ("비행의판", "sky-plate"),
    "poison": ("맹독의판", "toxic-plate"), "ground": ("대지의판", "earth-plate"),
    "rock": ("암석의판", "stone-plate"), "bug": ("벌레의판", "insect-plate"),
    "ghost": ("유령의판", "spooky-plate"), "steel": ("강철의판", "iron-plate"),
    "fire": ("화염의판", "flame-plate"), "water": ("물보라의판", "splash-plate"),
    "grass": ("목초의판", "meadow-plate"), "electric": ("전격의판", "zap-plate"),
    "psychic": ("정신의판", "mind-plate"), "ice": ("고드름의판", "icicle-plate"),
    "dragon": ("용의판", "draco-plate"), "dark": ("공포의판", "dread-plate"),
    "fairy": ("요정의판", "pixie-plate"), "normal": ("대리석판", "blank-plate"),
}
_TYPE_MEMORIES = {
    t: (n + "의 메모리", f"{t}-memory")
    for t, n in TYPE_NAME_MAP.items() if t != "normal"
}
_TYPE_RESIST_BERRIES = {
    "fire": ("오카열매", "occa-berry"), "water": ("꼬시개열매", "passho-berry"),
    "electric": ("초나열매", "wacan-berry"), "grass": ("린드열매", "rindo-berry"),
    "ice": ("플카열매", "yache-berry"), "fighting": ("로플열매", "chople-berry"),
    "poison": ("으름열매", "kebia-berry"), "ground": ("슈캐열매", "shuca-berry"),
    "flying": ("바코열매", "coba-berry"), "psychic": ("야파열매", "payapa-berry"),
    "bug": ("리체열매", "tanga-berry"), "rock": ("루미열매", "charti-berry"),
    "ghost": ("수불열매", "kasib-berry"), "dragon": ("하반열매", "haban-berry"),
    "dark": ("마코열매", "colbur-berry"), "steel": ("바리비열매", "babiri-berry"),
    "normal": ("카리열매", "chilan-berry"), "fairy": ("로셀열매", "roseli-berry"),
}

for _t, (_ko, _en) in _TYPE_ENHANCE_ITEMS.items():
  ITEM_CATEGORIES["기술 강화 도구"]["items"].append({
      "name": _ko, "en": _en,
      "summary": f"{TYPE_NAME_MAP[_t]} 타입 기술 위력 1.2배",
      "detail": f"{TYPE_NAME_MAP[_t]} 타입 기술의 위력을 1.2배로 올려주는 타입 강화 도구입니다.",
  })
for _t, (_ko, _en) in _TYPE_GEMS.items():
  ITEM_CATEGORIES["기술 강화 도구"]["items"].append({
      "name": _ko, "en": _en,
      "summary": f"{TYPE_NAME_MAP[_t]} 타입 기술 위력 1.3배(1회용)",
      "detail": f"{TYPE_NAME_MAP[_t]} 타입 기술을 사용할 때 소모되어 그 기술의 위력을 1.3배로 올려주는 1회용 강화 도구입니다.",
  })
for _t, (_ko, _en) in _TYPE_PLATES.items():
  ITEM_CATEGORIES["전용 도구"]["items"].append({
      "name": _ko, "en": _en,
      "summary": f"아르세우스 전용 · {TYPE_NAME_MAP[_t]} 타입화",
      "detail": f"아르세우스가 지니면 타입이 {TYPE_NAME_MAP[_t]} 타입으로 바뀌고, 전용기 저지먼트도 이 타입이 되며 위력이 1.2배 상승합니다.",
  })
for _t, (_ko, _en) in _TYPE_MEMORIES.items():
  ITEM_CATEGORIES["전용 도구"]["items"].append({
      "name": _ko, "en": _en,
      "summary": f"실버디 전용 · {TYPE_NAME_MAP[_t]} 타입화",
      "detail": f"실버디가 지니면 타입이 {TYPE_NAME_MAP[_t]} 타입으로 바뀌고, 전용기 멀티어택도 이 타입이 됩니다.",
  })
for _t, (_ko, _en) in _TYPE_RESIST_BERRIES.items():
  _label = "노말" if _t == "normal" else TYPE_NAME_MAP[_t]
  ITEM_CATEGORIES["내성 도구"]["items"].append({
      "name": _ko, "en": _en,
      "summary": f"{_label} 타입 피해 절반",
      "detail": f"{_label} 타입 기술에 맞았을 때(노말 타입은 항상, 그 외 타입은 효과가 굉장할 때) 그 피해를 절반으로 줄여주는 타입 반감 나무열매입니다.",
  })

# ---- 랭크업/회복/상태이상 나무열매 일괄 추가 ----
_STAT_UP_BERRIES = [
    ("치리열매", "liechi-berry", "체력 1/4 이하 시 공격 1랭크 상승"),
    ("용아열매", "ganlon-berry", "체력 1/4 이하 시 방어 1랭크 상승"),
    ("캄라열매", "salac-berry", "체력 1/4 이하 시 스피드 1랭크 상승"),
    ("야타비열매", "petaya-berry", "체력 1/4 이하 시 특수공격 1랭크 상승"),
    ("규살열매", "apicot-berry", "체력 1/4 이하 시 특수방어 1랭크 상승"),
    ("랑사열매", "lansat-berry", "체력 1/4 이하 시 급소율 2랭크 상승"),
    ("스타열매", "starf-berry", "체력 1/4 이하 시 랜덤 능력치 1개 2랭크 상승"),
    ("악키열매", "kee-berry", "물리 기술에 맞으면 방어 1랭크 상승"),
    ("타라프열매", "maranga-berry", "특수 기술에 맞으면 특수방어 1랭크 상승"),
]
for _name, _en, _summary in _STAT_UP_BERRIES:
  ITEM_CATEGORIES["능력치 강화 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"{_summary} 자동 발동형 나무열매입니다.",
  })

_FLAVOR_HALF_BERRIES = [
    ("무화열매", "figy-berry", "매운맛"), ("위키열매", "wiki-berry", "떫은맛"),
    ("마고열매", "mago-berry", "단맛"), ("아바열매", "aguav-berry", "쓴맛"),
    ("파야열매", "iapapa-berry", "신맛"),
]
for _name, _en, _flavor in _FLAVOR_HALF_BERRIES:
  ITEM_CATEGORIES["체력 회복 도구"]["items"].append({
      "name": _name, "en": _en, "summary": "체력 1/4 이하 시 최대체력 1/3 회복",
      "detail": f"체력이 최대체력의 1/4 이하로 떨어지면 자동으로 사용되어 최대체력의 1/3을 회복시켜 주지만, {_flavor}을 싫어하는 포켓몬이 먹으면 혼란에 걸릴 수 있는 나무열매입니다.",
  })

_STATUS_CURE_BERRIES = [
    ("버치열매", "cheri-berry", "마비 치료"), ("유루열매", "chesto-berry", "잠듦 치료"),
    ("복슝열매", "pecha-berry", "독 치료"), ("복분열매", "rawst-berry", "화상 치료"),
    ("배리열매", "aspear-berry", "얼음 상태 치료"),
    ("리샘열매", "lum-berry", "거의 모든 상태이상 치료"),
]
for _name, _en, _summary in _STATUS_CURE_BERRIES:
  ITEM_CATEGORIES["내성 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"상태이상에 걸렸을 때 자동으로 사용되어 {_summary.replace(' 치료','을 치료').replace('상태 치료','상태를 치료')}해주는 나무열매입니다.",
  })

for _name, _en, _summary in [
    ("자보열매", "jaboca-berry", "물리공격 피격 시 상대에게 1/8 피해"),
    ("애터열매", "rowap-berry", "특수공격 피격 시 상대에게 1/8 피해"),
]:
  ITEM_CATEGORIES["자기 피해 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"{_summary}를 입히지만, 자신도 함께 소모되는 반격형 나무열매입니다.",
  })

for _name, _en, _summary, _detail in [
    ("미클열매", "micle-berry", "체력 1/4 이하 시 명중률 20% 상승",
     "체력이 최대체력의 1/4 이하로 떨어지면 다음에 사용할 기술의 명중률이 20% 오르는 나무열매입니다."),
    ("애슈열매", "custap-berry", "체력 1/4 이하 시 다음 턴 선공",
     "체력이 최대체력의 1/4 이하로 떨어지면 다음 턴에 우선적으로 행동할 수 있게 해주는 나무열매입니다."),
]:
  ITEM_CATEGORIES["기타"]["items"].append({
      "name": _name, "en": _en, "summary": _summary, "detail": _detail,
  })


# ---- 생존/내성 계열 도구 추가 ----
for _name, _en, _summary, _detail in [
    ("기합의띠", "focus-sash", "체력 최대일 때 즉사기 1회 생존",
     "체력이 가득 찬 상태에서 한 방에 기절할 만한 데미지를 받으면, 대신 체력 1을 남기고 버티게 해주는 1회용 도구입니다. 배수의 진 특성과 함께 자주 쓰입니다."),
    ("기합의머리띠", "focus-band", "일정 확률로 즉사기 생존",
     "기절할 데미지를 입어도 10% 확률로 체력 1을 남기고 버티게 해주는 도구입니다. 기합의띠와 달리 확률제이며 여러 번 발동할 수 있습니다."),
]:
  ITEM_CATEGORIES["내성 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary, "detail": _detail,
  })

# ---- 능력치 강화 계열 도구 추가 ----
for _name, _en, _summary, _detail in [
    ("돌격조끼", "assault-vest", "특수방어 1.5배 / 변화기 사용 불가",
     "특수방어 실수치를 1.5배로 올려주지만, 지닌 포켓몬은 변화 기술을 전혀 사용할 수 없게 되는 도구입니다."),
    ("펀치글러브", "punching-glove", "펀치 기술 위력 1.1배 / 접촉 판정 해제",
     "펀치 계열 기술의 위력을 1.1배로 올려주고, 그 기술들이 접촉 판정을 받지 않게 만들어주는 도구입니다."),
    ("약점보험", "weakness-policy", "효과가 굉장한 기술 피격 시 공격/특공 2랭크 상승",
     "상성상 효과가 굉장한 기술에 맞으면 공격과 특수공격이 한꺼번에 2랭크씩 상승하고 사라지는 1회용 도구입니다."),
    ("허탕보험", "blunder-policy", "기술이 빗나가면 스피드 2랭크 상승",
     "사용한 기술이 빗나갔을 때 스피드가 2랭크 상승하고 사라지는 1회용 도구입니다."),
    ("진화의휘석", "eviolite", "미진화 포켓몬 방어/특수방어 1.5배",
     "아직 진화할 수 있는(최종 진화형이 아닌) 포켓몬이 지니면 방어와 특수방어 실수치가 1.5배로 상승하는 도구입니다."),
    ("빛이끼", "luminous-moss", "물 기술 피격 시 특수방어 1랭크 상승",
     "물 타입 기술에 맞으면 그 데미지를 견디고 특수방어가 1랭크 상승하는 1회용 도구입니다."),
    ("눈덩이", "snowball", "얼음 기술 피격 시 공격 1랭크 상승",
     "얼음 타입 기술에 맞으면 그 데미지를 견디고 공격이 1랭크 상승하는 1회용 도구입니다."),
    ("룸서비스", "room-service", "트릭룸 상태에서 스피드 1랭크 하락",
     "트릭룸이 깔린 상태로 필드에 나오면 스피드가 1랭크 하락하는 1회용 도구로, 트릭룸 활용 포켓몬에게 채용됩니다."),
    ("목스프레이", "throat-spray", "소리 기술 사용 시 특수공격 1랭크 상승",
     "소리를 내는 기술을 사용하면 특수공격이 1랭크 상승하는 도구입니다."),
    ("흉내허브", "mirror-herb", "상대의 능력치 상승을 그대로 복사",
     "상대 포켓몬의 능력치가 상승하면 그와 동일하게 자신의 능력치도 상승시켜 주고 사라지는 1회용 도구입니다."),
    ("일렉트릭시드", "electric-seed", "일렉트릭필드에서 방어 1랭크 상승",
     "필드에 일렉트릭필드가 깔려 있는 상태로 나오면 방어가 1랭크 상승하고 사라지는 시드 계열 도구입니다."),
    ("그래스시드", "grassy-seed", "그래스필드에서 방어 1랭크 상승",
     "필드에 그래스필드가 깔려 있는 상태로 나오면 방어가 1랭크 상승하고 사라지는 시드 계열 도구입니다."),
    ("사이코시드", "psychic-seed", "사이코필드에서 특수방어 1랭크 상승",
     "필드에 사이코필드가 깔려 있는 상태로 나오면 특수방어가 1랭크 상승하고 사라지는 시드 계열 도구입니다."),
    ("미스트시드", "misty-seed", "미스트필드에서 특수방어 1랭크 상승",
     "필드에 미스트필드가 깔려 있는 상태로 나오면 특수방어가 1랭크 상승하고 사라지는 시드 계열 도구입니다."),
]:
  ITEM_CATEGORIES["능력치 강화 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary, "detail": _detail,
  })

# ---- 기타 유명 배틀 도구 추가 ----
for _name, _en, _summary, _detail in [
    ("보호고글", "safety-goggles", "날씨 피해 무효 / 가루 기술 무효",
     "우박 등 날씨로 인한 데미지를 받지 않으며, 포자, 맹독가루 등 가루 계열 기술에도 영향을 받지 않게 해주는 도구입니다."),
    ("만능우산", "utility-umbrella", "쾌청·비 날씨 효과 무효화",
     "쾌청이나 비가 내리는 동안에도 그 날씨로 인한 기술 위력 변화나 특성 효과를 받지 않게 해주는 도구입니다."),
    ("튼튼한부츠", "heavy-duty-boots", "설치형 기술 및 지형 피해 무효",
     "압정뿌리기, 스텔스록 등 필드에 설치된 기술의 효과를 받지 않게 해주고, 가시밭길 등 지형 데미지도 무시하게 해주는 도구입니다."),
    ("보호패드", "protective-pads", "접촉 기술의 추가 효과로부터 보호",
     "상대의 접촉 기술을 맞았을 때 발생하는 정전기, 흰가루 등 접촉 계열 추가 효과를 받지 않게 해주는 도구입니다."),
    ("왕의징표", "king-s-rock", "공격 기술 명중 시 상대를 랜덤하게 풀죽게 함",
     "데미지를 주는 기술을 맞히면 10% 확률로 상대를 풀죽게(그 턴 행동 불가) 만드는 도구입니다."),
    ("재빠른손톱", "quick-claw", "일정 확률로 기술 우선 사용",
     "기술의 우선도와 상관없이 20% 확률로 그 턴에 가장 먼저 행동하게 해주는 도구입니다."),
    ("고급렌즈", "scope-lens", "급소에 맞는 확률 1랭크 상승",
     "소지한 포켓몬이 급소를 맞출 확률을 1랭크 올려주는 도구입니다."),
]:
  ITEM_CATEGORIES["기타"]["items"].append({
      "name": _name, "en": _en, "summary": _summary, "detail": _detail,
  })

# ---- 메가스톤 (6~7세대 메가진화용 도구, 총 46종) ----
ITEM_CATEGORIES["메가스톤"] = {
    "color": "#8B5CF6",
    "icon": "💎",
    "desc": "특정 포켓몬이 지니고 있으면 배틀 중 메가진화를 할 수 있게 해주는 전용 도구입니다.",
    "items": [],
}
_MEGA_STONES = [
    ("이상해꽃나이트", "venusaurite"), ("리자몽나이트X", "charizardite-x"),
    ("리자몽나이트Y", "charizardite-y"), ("거북왕나이트", "blastoisinite"),
    ("독침붕나이트", "beedrillite"), ("피죤투나이트", "pidgeotite"),
    ("후디나이트", "alakazite"), ("야도란나이트", "slowbronite"),
    ("쁘사이저나이트", "pinsirite"), ("갸라도스나이트", "gyaradosite"),
    ("강철톤나이트", "steelixite"), ("헤라크로스나이트", "heracronite"),
    ("나무킹나이트", "sceptilite"), ("번치코나이트", "blazikenite"),
    ("대짱이나이트", "swampertite"), ("깜까미나이트", "sablenite"),
    ("입치트나이트", "mawilite"), ("보스로라나이트", "aggronite"),
    ("요가램나이트", "medichamite"), ("썬더볼트나이트", "manectite"),
    ("파비코리나이트", "altarianite"), ("다크펫나이트", "banettite"),
    ("앱솔나이트", "absolite"), ("얼음귀신나이트", "glalitite"),
    ("라티아스나이트", "latiasite"), ("라티오스나이트", "latiosite"),
    ("한카리아스나이트", "garchompite"), ("루카리오나이트", "lucarionite"),
    ("디안시나이트", "diancite"), ("팬텀나이트", "gengarite"),
    ("캥카나이트", "kangaskhanite"), ("프테라나이트", "aerodactylite"),
    ("뮤츠나이트X", "mewtwonite-x"), ("뮤츠나이트Y", "mewtwonite-y"),
    ("핫삼나이트", "scizorite"), ("헬가나이트", "houndoominite"),
    ("마기라스나이트", "tyranitarite"), ("가디안나이트", "gardevoirite"),
    ("전룡나이트", "ampharosite"), ("샤크니아나이트", "sharpedonite"),
    ("폭타나이트", "cameruptite"), ("보만다나이트", "salamencite"),
    ("메타그로스나이트", "metagrossite"), ("이어롭나이트", "lopunnite"),
    ("눈설왕나이트", "abomasite"), ("엘레이드나이트", "galladite"),
    ("다부니나이트", "audinite"),
]
for _ko, _en in _MEGA_STONES:
  _base = _ko.replace("나이트", "")
  ITEM_CATEGORIES["메가스톤"]["items"].append({
      "name": _ko, "en": _en,
      "summary": f"{_base} 전용 · 메가진화",
      "detail": f"{_base}가 지니고 배틀에 나가면 트레이너의 키스톤과 함께 메가진화하여 능력치와 특성이 강화된 모습으로 변합니다.",
  })

# ---- 진화의 돌 ----
ITEM_CATEGORIES["진화의 돌"] = {
    "color": "#FFB300",
    "icon": "🔮",
    "desc": "특정 포켓몬에게 사용하면 레벨과 상관없이 즉시 진화시켜 주는 소모성 도구입니다.",
    "items": [],
}
for _name, _en, _summary in [
    ("불꽃의돌", "fire-stone", "불꽃 타입 등 특정 포켓몬을 진화시킴"),
    ("물의돌", "water-stone", "물 타입 등 특정 포켓몬을 진화시킴"),
    ("천둥의돌", "thunder-stone", "전기 타입 등 특정 포켓몬을 진화시킴"),
    ("리프의돌", "leaf-stone", "풀 타입 등 특정 포켓몬을 진화시킴"),
    ("달의돌", "moon-stone", "특정 포켓몬을 진화시킴"),
    ("태양의돌", "sun-stone", "특정 포켓몬을 진화시킴"),
    ("빛의돌", "shiny-stone", "특정 포켓몬을 진화시킴"),
    ("어둠의돌", "dusk-stone", "특정 포켓몬을 진화시킴"),
    ("각성의돌", "dawn-stone", "특정 성별의 특정 포켓몬을 진화시킴"),
    ("얼음의돌", "ice-stone", "특정 포켓몬을 진화시킴"),
    ("동글동글돌", "oval-stone", "특정 조건에서 해피너스 이전 단계 포켓몬을 진화시킴"),
]:
  ITEM_CATEGORIES["진화의 돌"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"{_summary}, 사용하면 사라지는 소모성 진화 도구입니다. B버튼으로 진화를 취소할 수 없습니다.",
  })

# ---- 몬스터볼 종류 ----
ITEM_CATEGORIES["포켓볼"] = {
    "color": "#EF5350",
    "icon": "⚪",
    "desc": "야생 포켓몬을 포획할 때 사용하는 도구로, 종류에 따라 포획 확률이나 발동 조건이 다릅니다.",
    "items": [],
}
for _name, _en, _summary in [
    ("몬스터볼", "poke-ball", "가장 기본적인 포획용 볼"),
    ("슈퍼볼", "great-ball", "몬스터볼보다 포획률이 높은 볼"),
    ("하이퍼볼", "ultra-ball", "슈퍼볼보다 포획률이 더 높은 볼"),
    ("마스터볼", "master-ball", "야생 포켓몬을 100% 포획하는 최상급 볼"),
    ("사파리볼", "safari-ball", "사파리존 전용 포획용 볼"),
    ("프리미어볼", "premier-ball", "몬스터볼을 다량 구입하면 덤으로 주는 볼"),
    ("네트볼", "net-ball", "벌레·물 타입 포켓몬 포획률이 오르는 볼"),
    ("다이브볼", "dive-ball", "물속·수중 포켓몬 포획률이 오르는 볼"),
    ("네스트볼", "nest-ball", "레벨이 낮은 포켓몬일수록 포획률이 오르는 볼"),
    ("타이머볼", "timer-ball", "배틀 턴수가 길어질수록 포획률이 오르는 볼"),
    ("리피트볼", "repeat-ball", "이미 도감에 등록된 포켓몬 포획률이 오르는 볼"),
    ("럭셔리볼", "luxury-ball", "잡은 포켓몬의 친밀도가 더 잘 오르는 볼"),
    ("힐볼", "heal-ball", "포획과 동시에 포켓몬의 상태를 완전 회복시키는 볼"),
    ("다크볼", "dusk-ball", "밤이나 동굴 등 어두운 곳에서 포획률이 오르는 볼"),
    ("퀵볼", "quick-ball", "배틀 시작 직후 사용하면 포획률이 크게 오르는 볼"),
    ("레벨볼", "level-ball", "자신의 포켓몬보다 레벨이 낮을수록 포획률이 오르는 볼"),
    ("루어볼", "lure-ball", "낚시로 낚은 포켓몬 포획률이 오르는 볼"),
    ("문볼", "moon-ball", "달의돌로 진화하는 계열 포켓몬 포획률이 오르는 볼"),
    ("러브러브볼", "love-ball", "자신의 포켓몬과 성별이 다른 같은 종 포켓몬 포획률이 오르는 볼"),
    ("헤비볼", "heavy-ball", "무게가 무거운 포켓몬일수록 포획률이 오르는 볼"),
    ("프렌드볼", "friend-ball", "잡은 포켓몬의 초기 친밀도가 높아지는 볼"),
    ("스피드볼", "fast-ball", "재빠른 포켓몬 포획률이 오르는 볼"),
    ("드림볼", "dream-ball", "꿈의 세계·자고 있는 포켓몬 포획에 쓰이는 볼"),
    ("파크볼", "park-ball", "포켓몬 자연공원 대회 전용 볼"),
]:
  ITEM_CATEGORIES["포켓볼"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"{_summary}. 야생 포켓몬에게 던져 사용하는 포획 전용 도구입니다.",
  })


# ---- 성격 민트 (성격의 능력치 보정을 바꿔주는 도구, 총 25종) ----
ITEM_CATEGORIES["성격 민트"] = {
    "color": "#4CAF50",
    "icon": "🌿",
    "desc": "먹인 포켓몬의 성격 자체는 바꾸지 않지만, 능력치 보정을 원하는 성격의 것으로 바꿔주는 도구입니다.",
    "items": [],
}
_MINTS = [
    ("외로움민트", "lonely-mint", "공격 상승 / 방어 하락 보정으로 변경"),
    ("용감민트", "brave-mint", "공격 상승 / 스피드 하락 보정으로 변경"),
    ("고집민트", "adamant-mint", "공격 상승 / 특수공격 하락 보정으로 변경"),
    ("개구쟁이민트", "naughty-mint", "공격 상승 / 특수방어 하락 보정으로 변경"),
    ("대담민트", "bold-mint", "방어 상승 / 공격 하락 보정으로 변경"),
    ("무사태평민트", "relaxed-mint", "방어 상승 / 스피드 하락 보정으로 변경"),
    ("장난꾸러기민트", "impish-mint", "방어 상승 / 특수공격 하락 보정으로 변경"),
    ("촐랑민트", "lax-mint", "방어 상승 / 특수방어 하락 보정으로 변경"),
    ("조심민트", "modest-mint", "특수공격 상승 / 공격 하락 보정으로 변경"),
    ("의젓민트", "mild-mint", "특수공격 상승 / 방어 하락 보정으로 변경"),
    ("덜렁민트", "rash-mint", "특수공격 상승 / 특수방어 하락 보정으로 변경"),
    ("냉정민트", "quiet-mint", "특수공격 상승 / 스피드 하락 보정으로 변경"),
    ("차분민트", "calm-mint", "특수방어 상승 / 공격 하락 보정으로 변경"),
    ("얌전민트", "gentle-mint", "특수방어 상승 / 방어 하락 보정으로 변경"),
    ("신중민트", "careful-mint", "특수방어 상승 / 특수공격 하락 보정으로 변경"),
    ("건방민트", "sassy-mint", "특수방어 상승 / 스피드 하락 보정으로 변경"),
    ("겁쟁이민트", "timid-mint", "스피드 상승 / 공격 하락 보정으로 변경"),
    ("성급민트", "hasty-mint", "스피드 상승 / 방어 하락 보정으로 변경"),
    ("명랑민트", "jolly-mint", "스피드 상승 / 특수공격 하락 보정으로 변경"),
    ("천진난만민트", "naive-mint", "스피드 상승 / 특수방어 하락 보정으로 변경"),
    ("노력민트", "hardy-mint", "능력치 보정 없음(무보정)으로 변경"),
    ("변덕민트", "quirky-mint", "능력치 보정 없음(무보정)으로 변경"),
    ("온순민트", "docile-mint", "능력치 보정 없음(무보정)으로 변경"),
    ("수줍음민트", "bashful-mint", "능력치 보정 없음(무보정)으로 변경"),
    ("성실민트", "serious-mint", "능력치 보정 없음(무보정)으로 변경"),
]
for _name, _en, _summary in _MINTS:
  ITEM_CATEGORIES["성격 민트"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"포켓몬에게 사용하면 {_summary}(성격 자체는 바뀌지 않으며, 유전되지도 않습니다).",
  })

# ---- 영양제 & 육성 도구 ----
ITEM_CATEGORIES["육성 도구"] = {
    "color": "#26A69A",
    "icon": "🧪",
    "desc": "포켓몬의 노력치나 기술의 사용 횟수(PP)를 늘려주는 육성용 소모 도구입니다.",
    "items": [],
}
for _name, _en, _summary in [
    ("맥스업", "hp-up", "체력 노력치 상승"),
    ("타우린", "protein", "공격 노력치 상승"),
    ("사포닌", "iron", "방어 노력치 상승"),
    ("인돔", "calcium", "특수공격 노력치 상승"),
    ("리제", "zinc", "특수방어 노력치 상승"),
    ("알칼로이드", "carbos", "스피드 노력치 상승"),
]:
  ITEM_CATEGORIES["육성 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"먹이면 해당 능력치의 노력치가 10만큼 오르는 영양제입니다. 능력치별로 노력치 최대 252까지 사용할 수 있습니다.",
  })
for _name, _en, _summary in [
    ("체력의날개", "health-wing", "체력 노력치를 소폭 상승시키는 날개"),
    ("힘의날개", "muscle-wing", "공격 노력치를 소폭 상승시키는 날개"),
    ("방어의날개", "resist-wing", "방어 노력치를 소폭 상승시키는 날개"),
    ("특공의날개", "genius-wing", "특수공격 노력치를 소폭 상승시키는 날개"),
    ("특방의날개", "clever-wing", "특수방어 노력치를 소폭 상승시키는 날개"),
    ("스피드의날개", "swift-wing", "스피드 노력치를 소폭 상승시키는 날개"),
]:
  ITEM_CATEGORIES["육성 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary,
      "detail": f"{_summary}. 영양제보다 상승폭은 작지만 노력치 최대치를 넘기지 않는 한 제한 없이 사용할 수 있습니다.",
  })
for _name, _en, _summary, _detail in [
    ("포인트업", "pp-up", "기술 하나의 최대 PP 상승",
     "포켓몬이 배운 기술 하나를 골라 그 기술의 최대 PP를 늘려주는 도구입니다."),
    ("포인트맥스", "pp-max", "기술 하나의 최대 PP를 한계까지 상승",
     "포켓몬이 배운 기술 하나를 골라 그 기술의 최대 PP를 한 번에 최대치까지 늘려주는 상급 도구입니다."),
    ("이상한사탕", "rare-candy", "포켓몬 레벨을 1 상승",
     "먹이면 배틀 없이도 포켓몬의 레벨을 1만큼 즉시 올려주는 귀중한 사탕입니다."),
]:
  ITEM_CATEGORIES["육성 도구"]["items"].append({
      "name": _name, "en": _en, "summary": _summary, "detail": _detail,
  })


@st.cache_data(ttl=86400)
def get_item_image_url(en_name):
  """도구의 영문 슬러그로 PokeAPI 스프라이트 저장소의 아이콘 URL을 만듭니다."""
  if not en_name:
    return ""
  return (
      "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
      f"sprites/items/{en_name}.png"
  )


def find_item_by_name(item_name):
  for cat_name, cat_data in ITEM_CATEGORIES.items():
    for it in cat_data["items"]:
      if it["name"] == item_name:
        return cat_name, cat_data, it
  return None, None, None


# 사이드바 네비게이션
st.sidebar.title("⚡ 포켓몬 위키 네비게이션")
if st.sidebar.button("🏠 메인 메뉴", use_container_width=True):
  go_to_page("Main")

if st.sidebar.button("📖 세대별 도감", use_container_width=True):
  go_to_page("포켓몬 도감")

if st.sidebar.button("👤 인물 도감", use_container_width=True):
  go_to_page("인물 도감")

if st.sidebar.button("🎒 아이템 도감", use_container_width=True):
  go_to_page("아이템 도감")

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
            <div style="font-size: 2.0rem; margin-bottom: 6px;">🎒</div>
            <div style="font-weight: bold; font-size: 1.1rem; color: #008275; margin-bottom: 4px;">아이템 도감</div>
            <div style="font-size: 0.8rem; color: #666;">배틀 도구 종류별 효과 정보</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("아이템 도감", key="btn_item", use_container_width=True):
      go_to_page("아이템 도감")
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

    row1 = ["1세대 (관동)", "2세대 (성도)", "3세대 (호연)"]
    row2 = ["4세대 (신오)", "5세대 (하나)", "6세대 (칼로스)"]
    row3 = ["7세대 (알로라)", "8세대 (가라르)", "9세대 (팔데아)"]
    row4 = [None, "전국 도감", None]  # 8세대(가라르) 바로 아래에 전국 도감 배치

    layout_rows = [row1, row2, row3, row4]

    for r_idx, r_items in enumerate(layout_rows):
      cols = st.columns(3)
      for c_idx, item_name in enumerate(r_items):
        if item_name is None:
          continue
        with cols[c_idx]:
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
                  key=f"gen_btn_{r_idx}_{c_idx}",
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
  if not st.session_state.selected_char_gen:
    st.title("👤 세대별 인물 도감")

    st.write(
        "**세대별로 등장하는 주요 인물 및 관장 정보를 한눈에 확인하세요.**"
    )
    st.markdown(
        "<h3 class='section-title'>📦 세대별 인물 도감 선택</h3>",
        unsafe_allow_html=True,
    )

    # 9세대는 원래 자리(8세대 우측)에 두고, 히스이 지방을 8세대 아래로 배치
    row1 = ["1세대 (관동)", "2세대 (성도)", "3세대 (호연)"]
    row2 = ["4세대 (신오)", "5세대 (하나)", "6세대 (칼로스)"]
    row3 = ["7세대 (알로라)", "8세대 (가라르)", "9세대 (팔데아)"]
    row4 = [None, "히스이 지방", None]  # 8세대(가라르) 바로 아래에 히스이 지방 배치

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
              st.rerun()

  else:
    g_name = st.session_state.selected_char_gen
    g_data = CHARACTER_GENERATIONS[g_name]

    if st.session_state.selected_character:
      # 인물 상세 페이지
      if st.button("◀ 인물 목록으로", use_container_width=False):
        st.session_state.selected_character = None
        st.rerun()

      char_name = st.session_state.selected_character
      char = next(
          (c for c in g_data["characters"] if c["name"] == char_name), None
      )

      if char is None:
        st.warning("인물 정보를 찾을 수 없습니다.")
      else:
        category = get_character_category(char)
        extra = get_character_extra_info(char["name"])
        debut_game = GENERATION_TO_GAME.get(g_name, "정보 없음")
        gen_color = g_data["color"]

        st.markdown(
            f"# {char['name']} <span style='font-size:1rem; color:#aaaaaa;'>({char['title']})</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span class='type-chip' style='background-color:{gen_color};'>{category}</span> "
            f"<span class='type-chip' style='background-color:#555555;'>{char['type']}</span>",
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([2, 1])

        with col_left:
          st.markdown("### 1. 개요 및 설명")
          st.info(char["desc"])

          st.markdown("### 2. 사용 포켓몬")
          if char["pokemon"]:
            start_id, end_id = get_generation_id_range(g_name)
            with st.spinner("사용 포켓몬 정보를 불러오는 중..."):
              pkmn_cols = st.columns(len(char["pokemon"]))
              for p_col, p_name in zip(pkmn_cols, char["pokemon"]):
                with p_col:
                  resolved = resolve_character_pokemon(
                      p_name, start_id, end_id
                  )
                  img_url = resolved["image"] if resolved else ""
                  if img_url:
                    st.image(img_url, caption=p_name, use_container_width=True)
                  else:
                    st.markdown(
                        f"""
                        <div style='text-align:center;'>
                            <span class='type-chip' style='background-color:{gen_color};'>{p_name}</span><br>
                            <span style='font-size:0.75rem; color:#999;'>이미지 없음</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                  if resolved:
                    if st.button(
                        "📖 도감에서 보기",
                        key=f"char_pkmn_link_{char['name']}_{p_name}",
                        use_container_width=True,
                    ):
                      st.session_state.current_page = "전국 도감"
                      st.session_state.search_query = str(resolved["id"])
                      add_search_history(p_name)
                      st.rerun()
          else:
            st.write("정보 없음")

        with col_right:
          st.markdown(
              f"<div class='char-name-banner' style='background-color:{gen_color};'>{char['name']}</div>",
              unsafe_allow_html=True,
          )
          char_image_url = char.get("image", "")
          if char_image_url:
            st.image(char_image_url, use_container_width=True)
          st.markdown(
              f"""
              <table class="char-info-table">
                  <tr><th>성별</th><td>{extra['gender']}</td></tr>
                  <tr><th>나이</th><td>{extra['age']}</td></tr>
                  <tr><th>트레이너 계급</th><td>{category}</td></tr>
                  <tr><th>지방</th><td>{g_name}</td></tr>
                  <tr><th>출신지</th><td>{extra['hometown']}</td></tr>
                  <tr><th>가족 관계</th><td>{extra['family']}</td></tr>
                  <tr><th>주된 타입</th><td>{char['type']}</td></tr>
                  <tr><th>데뷔작</th><td>{debut_game}</td></tr>
              </table>
              """,
              unsafe_allow_html=True,
          )

    else:
      if st.button("◀ 세대 목록으로", use_container_width=False):
        st.session_state.selected_char_gen = None
        st.session_state.character_search_query = ""
        st.rerun()

      st.title(f"👤 {g_name} 인물 도감")

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

      characters = sorted(characters, key=character_sort_key)

      if not characters:
        st.warning(f"'{query_text}'에 해당하는 인물을 찾을 수 없습니다.")
      else:
        # 나무위키 목차처럼 카테고리(주인공/라이벌/체육관 관장 등)별로 묶어서 표시
        grouped = {}
        for char in characters:
          category = get_character_category(char)
          grouped.setdefault(category, []).append(char)

        ordered_categories = [
            c for c in CHARACTER_CATEGORY_ORDER if c in grouped
        ] + [c for c in grouped if c not in CHARACTER_CATEGORY_ORDER]

        btn_idx = 0
        for category in ordered_categories:
          icon = CHARACTER_CATEGORY_ICONS.get(category, "👤")
          st.markdown(
              f"""
              <h3 style="color:{g_data['color']}; border-bottom: 2px solid {g_data['color']};
                  padding-bottom: 6px; margin-top: 32px;">
                  {icon} {category} <span style="font-size:0.8rem; color:#999;">({len(grouped[category])})</span>
              </h3>
              """,
              unsafe_allow_html=True,
          )
          for char in grouped[category]:
            st.markdown(
                f"""
                <div class="char-card">
                    <h3 style="margin-top: 0; margin-bottom: 0; color: #008275;">{char['name']} <small style="font-size: 0.9rem; color: #aaaaaa;">({char['title']})</small></h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"{char['name']} 상세 보기",
                key=f"char_detail_btn_{btn_idx}",
                use_container_width=True,
            ):
              st.session_state.selected_character = char["name"]
              st.rerun()
            btn_idx += 1

elif st.session_state.current_page == "아이템 도감":

  if st.session_state.selected_item:
    # ---------- 아이템 상세 페이지 ----------
    if st.button("◀ 아이템 목록으로", use_container_width=False):
      st.session_state.selected_item = None
      st.rerun()

    cat_name, cat_data, item = find_item_by_name(st.session_state.selected_item)

    if item is None:
      st.warning("아이템 정보를 찾을 수 없습니다.")
    else:
      st.markdown(
          f"# {item['name']} <span style='font-size:1rem; color:#aaaaaa;'>({cat_name})</span>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"<span class='type-chip' style='background-color:{cat_data['color']};'>"
          f"{cat_data['icon']} {cat_name}</span>",
          unsafe_allow_html=True,
      )

      col_left, col_right = st.columns([1, 2])
      with col_left:
        img_url = get_item_image_url(item["en"])
        st.markdown(
            f"""
            <div class="infobox">
                <img src="{img_url}" style="width:96px; height:96px; object-fit:contain; image-rendering:pixelated;">
            </div>
            """,
            unsafe_allow_html=True,
        )
      with col_right:
        st.markdown("### 개요")
        st.info(item["summary"])
        st.markdown("### 상세 설명")
        st.write(item["detail"])

  elif st.session_state.item_category:
    # ---------- 카테고리별 아이템 목록 ----------
    cat_name = st.session_state.item_category

    if st.button("◀ 분류 목록으로", use_container_width=False):
      st.session_state.item_category = None
      st.session_state.item_search_query = ""
      st.rerun()

    if cat_name == "전체 도구칸":
      all_items = []
      for c_name, c_data in ITEM_CATEGORIES.items():
        for it in c_data["items"]:
          all_items.append((c_name, c_data, it))
      st.title("🎒 전체 도구칸")
      st.write(f"**등록된 배틀 도구 전체 {len(all_items)}종을 한눈에 확인하세요.**")
      cat_color = "#008275"
    else:
      cat_data = ITEM_CATEGORIES[cat_name]
      all_items = [(cat_name, cat_data, it) for it in cat_data["items"]]
      st.title(f"{cat_data['icon']} {cat_name}")
      st.write(f"**{cat_data['desc']}**")
      cat_color = cat_data["color"]

    st.text_input(
        "아이템 검색",
        value=st.session_state.item_search_query,
        key="item_search_input",
        on_change=update_item_search,
        placeholder="아이템 이름을 입력하세요...",
    )

    query_text = str(st.session_state.item_search_query).strip()
    if query_text:
      all_items = [
          t for t in all_items if query_text.lower() in t[2]["name"].lower()
      ]

    if not all_items:
      st.warning(f"'{query_text}'에 해당하는 아이템을 찾을 수 없습니다.")
    else:
      n_cols = 4
      cols = st.columns(n_cols)
      for idx, (c_name, c_data, it) in enumerate(all_items):
        with cols[idx % n_cols]:
          img_url = get_item_image_url(it["en"])
          st.markdown(
              f"""
              <div class="char-card" style="text-align:center;">
                  <img src="{img_url}" style="width:64px; height:64px; object-fit:contain; image-rendering:pixelated;"><br>
                  <b>{it['name']}</b><br>
                  <span class='type-chip' style='background-color:{c_data["color"]}; font-size:0.7rem;'>{c_name}</span>
                  <p style="font-size:0.8rem; color:#999; margin-top:6px;">{it['summary']}</p>
              </div>
              """,
              unsafe_allow_html=True,
          )
          if st.button("상세 보기", key=f"item_detail_btn_{idx}", use_container_width=True):
            st.session_state.selected_item = it["name"]
            st.rerun()

  else:
    # ---------- 아이템 분류 선택 화면 ----------
    st.title("🎒 아이템 도감")
    st.write("**배틀에서 사용하는 지니는 도구를 종류별로 확인하세요.**")
    st.markdown(
        "<h3 class='section-title'>📦 도구 분류 선택</h3>",
        unsafe_allow_html=True,
    )

    category_names = list(ITEM_CATEGORIES.keys())
    total_count = sum(len(c["items"]) for c in ITEM_CATEGORIES.values())

    tiles = [
        {
            "name": "전체 도구칸",
            "color": "#008275",
            "icon": "🎒",
            "sub": f"전체 도구 {total_count}종 모아보기",
        }
    ] + [
        {
            "name": n,
            "color": ITEM_CATEGORIES[n]["color"],
            "icon": ITEM_CATEGORIES[n]["icon"],
            "sub": f"{len(ITEM_CATEGORIES[n]['items'])}종",
        }
        for n in category_names
    ]

    n_cols = 3
    for row_start in range(0, len(tiles), n_cols):
      row_tiles = tiles[row_start:row_start + n_cols]
      cols = st.columns(n_cols)
      for c_idx, tile in enumerate(row_tiles):
        with cols[c_idx]:
          st.markdown(
              f"""
              <div class="char-banner" style="background-color: {tile['color']};">
                  {tile['icon']} {tile['name']}<br>
                  <span style="font-size: 0.85rem; font-weight: normal;">{tile['sub']}</span>
              </div>
              """,
              unsafe_allow_html=True,
          )
          if st.button(
              f"{tile['name']} 보기",
              key=f"item_cat_btn_{row_start}_{c_idx}",
              use_container_width=True,
          ):
            st.session_state.item_category = tile["name"]
            st.rerun()
