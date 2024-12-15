import streamlit as st
import geopandas as gpd 
import plotly.express as px
import altair as alt
import pandas as pd
df_S=pd.read_csv('pages/melted_data_cp949_cleaned.csv', encoding='euc-kr')

with st.sidebar:
    st.title('연도별 Scatter plot, Tree map')
    
    year_list = list(df_S.Year.unique())[::-1]  # 연도 리스트를 내림차순으로 정렬
    category_list = list(df_S.Category.unique())  # 카테고리 리스트
    
    selected_year = st.selectbox('연도 선택', year_list) # selectbox에서 연도 선택

    df_selected_year = df_S.query('Year == @selected_year') # 선택한 연도와 카테고리에 해당하는 데이터만 가져오기
    df_selected_year_sorted = df_selected_year.sort_values(by="Count", ascending=False) # 선택한 연도와 카테고리에 해당하는 데이터를 인구수를 기준으로 내림차순 정렬

tab_1, tab_2, tab_3= st.tabs(['Scatter chart', 'Tree map','Pie Chart']) 
with tab_1:
 st.header("Scatter chart를 이용한 분석")
 def make_scatter(input_df, input_year):
  filter_df = input_df[input_df['Year'] == input_year]
  st.divider() # 구분선
  st.scatter_chart(filter_df, x="Region", y="Count",   color="Category")
 make_scatter(df_S, selected_year)
 
 
with tab_2:
 st.write('## Tree map 을 이용한 분석')
 st.write('### 지역별 공급업체 차이를 한눈에 알아보기 위해 Treemap을 이용해 봤습니다')
 # Plotly Treemap 생성
 def make_treemap(input_df, input_year):
   filter_df = input_df[input_df['Year'] == input_year]
   fig=px.treemap(filter_df, 
                 path=["Region"],  # 계층적 구조에서 사용할 열
                 values="Count",  # 크기 기준
                 title="시군구별별 인구수 Treemap")
   st.plotly_chart(fig, use_container_width=True)
 make_treemap(df_S, selected_year)

with tab_3:
  st.write('## Pie Chart 를 이용한 분석')
  def make_pie(input_df, input_year):
    filter_df = input_df[input_df['Year'] == input_year]
    fig2 = px.pie(filter_df, names='Region' ,values='Count',color='Region',title='지역별 공급업체수')
    st.plotly_chart(fig2, use_container_width=True)
  make_pie(df_S, selected_year)
 
