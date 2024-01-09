import streamlit as st
import random
import numpy as np
#from streamlit_folium import folium_static
import pandas as pd
from haversine import haversine
from collections import deque
import datetime




#좌표가 저장될 리스트 초기화
if 'random_coords' not in st.session_state:
    st.session_state['random_coords'] = []

#----------3분 이상 정차----------------------
# selectbox 활성화 여부
if 'show_selectbox' not in st.session_state:
    st.session_state['show_selectbox'] = False   

# 메시지 발송 표시 여부
if 'selected_pm' not in st.session_state:
    st.session_state['selected_pm'] = None
    
# 메시지를 보내기 위한 초기 상태 설정
if 'message' not in st.session_state:
    st.session_state['message'] = None
#----------3분 이상 정차----------------------
#----------사고다발 구역----------------------
# selectbox 활성화 여부
if 'PM_selectbox' not in st.session_state:
    st.session_state['PM_selectbox'] = False   

# 메시지 발송 표시 여부
if 'PMselected_pm' not in st.session_state:
    st.session_state['PMselected_pm'] = None
    
# 메시지를 보내기 위한 초기 상태 설정
if 'PMmessage' not in st.session_state:
    st.session_state['message'] = None
#----------사고다발 구역----------------------
# 사고 다발 구역 내 PM수를 확인 하기 위해 초기화
if 'number_of_pms1' not in st.session_state:
    st.session_state['number_of_pms1'] = 0

# 3분 간 움직임이 없는 PM수를 확인 하기 위해 초기화
if 'number_of_pms2' not in st.session_state:
    st.session_state['number_of_pms2'] = 0




#페이지 전체화면을 위해 생성
st.set_page_config(layout="wide")


# 로고 이미지 생성
st.image(image='streamlit/big/SWING_1.png', width=300)

st.markdown('<hr style="border:1px solid orange">', unsafe_allow_html=True)

st.subheader('강남 구역 내 CCTV 현황')

st.markdown('<hr style="border:1px solid orange">', unsafe_allow_html=True)

#CCTV확인을 위한 레이아웃 생성
c_c1, c_c2, c_c3,c_c4 = st.columns(4)
st.markdown('<hr style="border:1px solid orange">', unsafe_allow_html=True)
info1, info2 = st.columns(2)
st.markdown('<hr style="border:1px solid orange">', unsafe_allow_html=True)
#지도와 버튼 레이아웃을 위해 생성
column1, column2= st.columns(2)





#--------------------------------------------------
# 사고다발 구역 지정하기
#데이터 불러오기
data = pd.read_excel('streamlit/big/2022년_강남_PM사고.xlsx')
    
#위도 경도 추출
col = ['위도','경도']
data = data[col]
    
#데이터 프레임 리스트 변환
location_list = data.values.tolist()
    
# !pip install haversine
def calculate_polygon_center(vertices):
    num_vertices = len(vertices)
        
    # 각 차원별로 꼭지점 좌표를 합산
    total_x = sum(vertex[0] for vertex in vertices)
    total_y = sum(vertex[1] for vertex in vertices)
        
    # 평균 계산
    center_x = total_x / num_vertices
    center_y = total_y / num_vertices    
    return center_x, center_y
    
    # 반경 100m내 사고 다발구간 찾기
accident = [] # 사고다발구간
coordinance = deque(location_list)
    
while coordinance:
    center = coordinance[0] # 최초 중심점은 자기 자신
    group = []
    before = 0
    after = 1
    while before != after:
        before = len(group)
        sub = []
        while coordinance:
            a = coordinance.popleft()
            dis = haversine(center, a, unit = 'm') # 센터와 사고 지점의 거리 구하기
            if dis <= 100:
                group.append(a)
            else:
                sub.append(a)
        center = calculate_polygon_center(group) # 해당 그룹의 센터를 다시 구하기
        after = len(group)
        coordinance = deque(sub)
    
    if len(group) >= 3: # 그룹에 3개 이상의 사건이 포함된 경우 사고다발구간으로 지정
        accident.append(center)

#사고 다발구간
#-------------------------------------------------------------------------------------




#-------------------------------------------------------------------------------------
# CCTV레이아웃
with c_c1:
    st.image(image='streamlit/big/cctv.gif')
with c_c2:
    st.image(image='streamlit/big/cctv_ec1.png')
with c_c3:
    st.image(image='streamlit/big/cctv_ec2.png')
with c_c4:
    st.image(image='streamlit/big/cctv_ec3.png')
#-------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
# 사고 지점 확인하기
df = pd.read_csv('streamlit/big/dummy_data.csv')


#PM위치를 확인할 좌표
coords = [
    (37.5064641, 127.0180169),
    (37.5072825, 127.0545532),
    (37.4938007, 127.0177135),
    (37.4940896, 127.054007)
]




def add_random_coords(n=40, lat_min=37.4938007, lat_max=37.5072825, long_min=127.0177135, long_max=127.0545532):
    new_coords = []
    # 각 속성에 대한 랜덤 샘플 선택
    details = df.sample(n)
    for i in range(n):
        random_lat = random.uniform(lat_min, lat_max)
        random_long = random.uniform(long_min, long_max)
        random_coord = (random_lat, random_long)
        name = details.iloc[i]['이름']
        gender = details.iloc[i]['성별']
        age = details.iloc[i]['나이']
        phone = details.iloc[i]['전화번호']
        # 랜덤 정차 시간을 생성
        stop_time = datetime.time(minute=random.randint(0, 3), second=random.randint(0, 59)).strftime("%M:%S")
        # 좌표, 기타 세부사항 및 정차 시간을 저장
        new_coords.append((random_coord, name, gender, age, phone, i+1, stop_time))

    return new_coords



# 지도 생성 및 랜덤 좌표 및 사고다발구역 표시 함수
def create_map(center_location, initial_coords, accident_coords):
    m = folium.Map(location=center_location, zoom_start=15)
    
    # 랜덤 좌표 마커 추가
    for coord, name, gender, age, phone, number, stop_time in initial_coords:  # 수정된 부분
        # 사고 다발구역 내에 있는지 확인
        is_accident_area = any(haversine(acc, coord, unit='m') <= 150 for acc in accident_coords)
        # 팝업 텍스트로 PM 번호와 이름을 포함
        popup_text = f"PM {number}"
        if is_accident_area:
            folium.Marker(coord, icon=folium.Icon(color='red'), popup=popup_text).add_to(m)
        else:
            folium.Marker(coord, icon=folium.Icon(color='blue'), popup=popup_text).add_to(m)
    
    # 사고 다발 지점 빨간 원으로 표시
    for acc_coord in accident_coords:
        folium.Circle(
            location=acc_coord,
            radius=150,  # 반경 100미터
            color='red',
            fill=True,
            fill_color='red'
        ).add_to(m)
    
    return m





with column2:
    # 버튼 클릭 처리
    if st.button('PM위치 확인하기'):
        st.session_state['show_selectbox'] = True
        new_coords = add_random_coords()  # 랜덤 좌표 생성
        st.session_state['random_coords'] = new_coords  # 새로운 좌표로 세션 상태 업데이트
    
        # 사고다발 구역 내 PM 위치 데이터 저장
        accident_pm_data = []
        for coord, name, gender, age, phone, number, stop_time in new_coords:
            is_accident_area = any(haversine(acc, coord, unit = 'm') <= 150 for acc in accident)
            if is_accident_area:
                accident_pm_data.append((number, name, gender, age, phone,stop_time, coord[0], coord[1]))
        
        # 사고다발 데이터프레임 생성
        st.error('사고다발 구역 내 PM 목록')
        accident_pm_df = pd.DataFrame(accident_pm_data, columns=['PM 번호', '이름', '성별', '나이', '전화번호','정차시간', '위도', '경도'])
        st.session_state['accident_pm_df'] = accident_pm_df  # 데이터 프레임을 세션 상태에 저장
        st.dataframe(st.session_state['accident_pm_df'], width=500)

        # 정차시간 3분 이상 데이터 저장
        stop_3min_pm_data = []
        for coord, name, gender, age, phone, number, stop_time in new_coords:
             if stop_time >= '03:00':
                stop_3min_pm_data.append((number, name, gender, age, phone, stop_time, coord[0], coord[1]))
        # 3분이상 정차 데이터 프레임 생성
        st.error('정차시간 3분이상 PM 목록')
        stop_3min_pm_df = pd.DataFrame(stop_3min_pm_data, columns=['PM 번호', '이름', '성별', '나이', '전화번호','정차시간', '위도', '경도'])
        st.session_state['stop_3min_pm_df'] = stop_3min_pm_df
        st.dataframe(stop_3min_pm_df, width=500)
        
        # 사고 다발 구역 내 PM수 & 3분간 움직임이 없는 PM의 수 넘기기
        st.session_state['number_of_pms1'] = len(accident_pm_data)
        st.session_state['number_of_pms2'] = len(stop_3min_pm_data)




#----------------------------------------------------------------
#3분 이상 정차pm select box
        
    if st.session_state['show_selectbox']:
    # 콤보박스 옵션 설정
        if 'stop_3min_pm_df' in st.session_state and not st.session_state['stop_3min_pm_df'].empty:
            options = st.session_state['stop_3min_pm_df']['PM 번호'].tolist()  # PM 번호를 리스트로 변환
        else:
            options = ["No PM data available"]  # 사고다발 구역 내 PM 데이터가 없는 경우
            
        # 콤보박스에서 선택된 옵션을 세션 상태에 저장
        st.session_state['selected_pm'] = st.selectbox("경고를 보낼 PM번호", options)
    
        # 선택된 옵션이 유효한 경우에만 버튼 표시
        if st.session_state['selected_pm'] and st.session_state['selected_pm'] != "No PM data available": 
            col1, col2 = st.columns(2)
                
            with col1:
                # PM 경고버튼
                if st.button('PM 경고 메시지 발송'):
                    st.session_state['message'] = f'{st.session_state["selected_pm"]} 사용자에게 경고 메시지가 발송되었습니다.'
            
            with col2:
                # PM 응급구조 버튼
                if st.button('PM 응급구조 요청'):
                    st.session_state['message'] = f'{st.session_state["selected_pm"]}의 위치에 응급구조 요청이 전송되었습니다.'
            
            # columns 외부에서 메시지 표시
        if st.session_state['message']:
            st.warning(st.session_state['message'])

#3분 이상 정차pm select box
#----------------------------------------------------------------------------------------------------------------



with column1:
    # 지도를 생성하고 Streamlit에 표시
    m = create_map(center_location=[37.5003975, 127.0356175], initial_coords=st.session_state['random_coords'], accident_coords=accident)
    folium_static(m, width=850)
# PM번호, 위도, 경도 표시(표)



#사고다발 구역 내 PM수 & 3분간 움직임이 없는 PM의 수 표현하기
with info1 :
    st.subheader(f'사고다발구역 내 PM _ {st.session_state["number_of_pms1"]}대')
with info2 : 
    st.subheader(f'3분간 움직임이 없는 PM _{st.session_state["number_of_pms2"]}대')

# streamlit run streamlit\big\big_v2x.py
