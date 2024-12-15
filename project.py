import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd 
import plotly.express as px
import altair as alt
import pandas as pd
import json
st.set_page_config(
    page_title="지역별 공급체수 데이터",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")
 
alt.themes.enable("dark")

df_S=pd.read_csv('melted_data_cp949_cleaned.csv', encoding='euc-kr')

with st.sidebar:
    st.title('🏂 대한민국 인구 대시보드')
    
    year_list = list(df_S.Year.unique())[::-1]  # 연도 리스트를 내림차순으로 정렬
    category_list = list(df_S.Category.unique())  # 카테고리 리스트
    
    selected_year = st.selectbox('연도 선택', year_list) # selectbox에서 연도 선택
    selected_category = st.selectbox('카테고리 선택', category_list) # selectbox에서 카테고리 선택

    df_selected_year = df_S.query('Year == @selected_year & Category == @selected_category') # 선택한 연도와 카테고리에 해당하는 데이터만 가져오기
    df_selected_year_sorted = df_selected_year.sort_values(by="Count", ascending=False) # 선택한 연도와 카테고리에 해당하는 데이터를 인구수를 기준으로 내림차순 정렬

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('컬러 테마 선택', color_theme_list)

# geopandas 라이브러리 불러오기
# geopandas의 read_file 함수로 데이터 불러오기
gdf_seoul_gu = gpd.read_file('korea_map.json')
import pandas as pd

alt.themes.enable('dark')

def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="연도", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

def make_choropleth(input_df, input_gj, input_column, input_color_theme):
    choropleth = px.choropleth_mapbox(input_df,
                               geojson=input_gj,
                               locations='code', 
                               featureidkey='properties.CTPRVN_CD',
                               mapbox_style='carto-darkmatter',
                               zoom=5, 
                               center = {"lat": 35.9, "lon": 126.98},
                               color=input_column, 
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df.Count)),
                               labels={'Count':'공급체수', 'code':'시도코드', 'Region':'시도명'},
                               hover_data=['Region', 'Count']
                              )
    choropleth.update_geos(fitbounds="locations", visible=False)
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

col = st.columns((1.5, 4.5, 2), gap='medium')

def calculate_population_difference(input_df, input_year, input_category):
  selected_year_data = input_df.query('Year == @input_year & Category == @input_category').reset_index()
  previous_year_data = input_df.query('Year == @input_year-1 & Category == @input_category').reset_index()
  selected_year_data['supplier_difference'] = selected_year_data['Count'].sub(previous_year_data['Count'], fill_value=0)
  selected_year_data['supplier_difference_abs'] = abs(selected_year_data['supplier_difference'])
  return pd.concat([
    selected_year_data['Region'], 
    selected_year_data['code'], 
    selected_year_data['Count'], 
    selected_year_data['supplier_difference'], 
    selected_year_data['supplier_difference_abs']
    ], axis=1).sort_values(by='supplier_difference', ascending=False)

import altair as alt
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

def format_number(num):
    if num > 1:
        if not num % 1:
            return f'{num // 1}'
        return f'{round(num / 1, 1)}'
    return f'{num // 1}'

with col[0]: # 왼쪽
    st.markdown('#### 증가/감소')

    df_supplier_difference_sorted = calculate_population_difference(df_S, selected_year, selected_category)

    if selected_year > 2016:
        first_state_name = df_supplier_difference_sorted.Region.iloc[0]
        first_state_population = format_number(df_supplier_difference_sorted.Count.iloc[0])
        first_state_delta = format_number(df_supplier_difference_sorted.supplier_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2016:
        last_state_name = df_supplier_difference_sorted.Region.iloc[-1]
        last_state_population = format_number(df_supplier_difference_sorted.Count.iloc[-1]) 
        last_state_delta = format_number(df_supplier_difference_sorted.supplier_difference.iloc[-1]) 
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)



    st.markdown('#### States Migration')
 
    st.markdown('#### 변동 시도 비율')

    if selected_year > 2016:
        # Filter states with population difference > 5000
        # df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
        df_greater_5000 = df_supplier_difference_sorted[df_supplier_difference_sorted.supplier_difference > 5]
        df_less_5000 = df_supplier_difference_sorted[df_supplier_difference_sorted.supplier_difference < -5]
        
        # % of States with population difference > 5000
        states_migration_greater = round((len(df_greater_5000)/df_supplier_difference_sorted.Region.nunique())*100)
        states_migration_less = round((len(df_less_5000)/df_supplier_difference_sorted.Region.nunique())*100)
        donut_chart_greater = make_donut(states_migration_greater, '전입', 'green')
        donut_chart_less = make_donut(states_migration_less, '전출', 'red')
    else:
        states_migration_greater = 0
        states_migration_less = 0
        donut_chart_greater = make_donut(states_migration_greater, '전입', 'green')
        donut_chart_less = make_donut(states_migration_less, '전출', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### ' + str(selected_year) + '년 ' + str(selected_category))
    
    choropleth = make_choropleth(df_selected_year, gdf_seoul_gu, 'Count', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(df_S, 'Year', 'Region', 'Count', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)
    
with col[2]:
    st.markdown('#### 시도별 ' + str(selected_category))

    st.dataframe(df_selected_year_sorted,
                 column_order=("Region", "Count"),
                 hide_index=True,
                 width=500,
                 column_config={
                    "Region": st.column_config.TextColumn(
                        "시도명",
                    ),
                    "Count": st.column_config.ProgressColumn(
                        str(selected_category),
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.Count),
                     )}
                 )
with col[2]:
     st.expander('정보', expanded=True)
     st.write('''
            - 데이터: [지역별 공급업체수](https://kosis.kr/statHtml/statHtml.do?orgId=354&tblId=DT_HIRA_DRUG_02&vw_cd=MT_ZTITLE&list_id=D1_35403_A01&seqNo=&lang_mode=ko&language=kor&obj_var_id=&itm_id=&conn_path=MT_ZTITLE).
            - :orange[**증가/감소**]: 선택 연도에서 가장 많이 증가/감소한 시도 
            - :orange[**변동 시도 비율**]: 선택 연도에서 공급업체가 5개 증가/감소한 시도의 비율
            ''')
