import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import json
import numpy as np


st.set_page_config(
    page_title="Japan Population Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")



st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {

    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 30%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 30%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)



population_df = pd.read_csv('data/japan_population_1975_2023.csv')

population_prediction = pd.read_csv('data/forecast/population_forecasts_2024.csv')

total_prediction = population_prediction['predicted_population_2024'].sum()
ci_ranges = population_prediction['confidence_interval_upper'] - population_prediction['confidence_interval_lower']
pooled_std = np.sqrt(np.sum((ci_ranges / 3.92) ** 2))
total_ci_lower = total_prediction - 1.96 * pooled_std
total_ci_upper = total_prediction + 1.96 * pooled_std

population_prediction.rename(columns={"predicted_population_2024":"population"}, inplace=True)
population_prediction['year'] = 2024
population_prediction = population_prediction[["prefecture", "population", "year"]]

prefecture_mapping = population_df[['prefecture', 'region', 'region_code', 'prefecture_code']].drop_duplicates()

population_prediction = population_prediction.merge(prefecture_mapping, on='prefecture', how='left')

population_prediction = population_prediction[['region', 'region_code', 'prefecture', 'prefecture_code', 'year', 'population']]

population_df = pd.concat([population_df, population_prediction], ignore_index=True)





with st.sidebar:
    st.title(f'日本 | Japan Population Dashboard')
    
    year_list = list(population_df.year.unique())[::-1]
    
    selected_year = st.selectbox('Year', year_list)
    population_df_year = population_df[population_df.year == selected_year]
    population_df_year_sorted = population_df_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'blues_r', 'greens', 'reds', 'portland', 'speed', 'electric']
    selected_color_theme = st.selectbox('Color theme', color_theme_list)
    




def make_line_chart(input_df, selected_year=selected_year):

    input_df = input_df[input_df['year'] <= selected_year]
    df_yearly_population = input_df.groupby(by='year')['population'].sum().reset_index()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_yearly_population['year'],
        y=df_yearly_population['population'],
        mode='lines',
        name='Total Population'
    ))

    fig.update_layout(
        title="Japan Population Growth",
        xaxis_title="Year",
        yaxis_title="Total Population",
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="category",
            fixedrange=True
                ),
        
        height=600,
        width=900
    )

    return fig


def make_choropleth(input_df, input_color_theme):
    with open('data/jp_geo.json') as f:
        japan_geojson = json.load(f)

    choropleth = px.choropleth(
        input_df,
        geojson=japan_geojson,
        locations='prefecture_code',
        featureidkey="properties.id",
        color='population',
        color_continuous_scale=input_color_theme,
        range_color=(0, max(input_df['population'])),
        hover_data={'prefecture': True, 'population': True}
    )

    choropleth.update_geos(fitbounds="locations", visible=False)
    choropleth.update_layout(
        geo=dict(
        bgcolor='rgba(220, 220, 220, 0)'
        ),
        coloraxis_colorbar=dict(
        title="Population"
        ),
        plot_bgcolor='rgba(220, 220, 220, 0)',
        paper_bgcolor='rgba(220, 220, 220, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )

    return choropleth
    



def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'



def calculate_population_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
  selected_year_data['population_difference_absolute'] = abs(selected_year_data['population_difference'])
  return pd.concat([selected_year_data.region, selected_year_data.region_code, selected_year_data.prefecture, selected_year_data.prefecture_code, selected_year_data.population, selected_year_data.population_difference, selected_year_data.population_difference_absolute], axis=1).sort_values(by="population_difference", ascending=False)


if selected_year <= 2023:
    st.markdown(f"<h2 style='text-align: center; '>Population information for {selected_year}</h2>", unsafe_allow_html=True)
else:
    st.markdown(f"<h2 style='text-align: center; '>Population prediction for {selected_year}</h2>", unsafe_allow_html=True)
    
    
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:


    st.markdown("#### Total Population")
    
    df_yearly_population = population_df.groupby(by='year')['population'].sum().reset_index()
    
    if selected_year > 1975:
        japan_name = "Japan"
        japan_population = format_number(df_yearly_population[df_yearly_population["year"]==selected_year].population.iloc[0])
        japan_population_delta = format_number(df_yearly_population[df_yearly_population["year"]==selected_year].population.iloc[0] - df_yearly_population[df_yearly_population["year"]==(selected_year-1)].population.iloc[0])
    
    else:
        japan_name = "Japan"
        japan_population = format_number(df_yearly_population[df_yearly_population["year"]==selected_year].population.iloc[0])
        japan_population_delta = ""
    st.metric(label=japan_name, value=japan_population, delta=japan_population_delta)
    
    if selected_year > 2023:
        lower = round(float(total_ci_lower)/1000000, 2)
        upper = round(float(total_ci_upper)/1000000, 2)
        
        if lower < df_yearly_population[df_yearly_population["year"]==selected_year-1].population.iloc[0]:
            lower_col = "red"
        else:
            lower_col = "green"
        
        if upper < df_yearly_population[df_yearly_population["year"]==selected_year-1].population.iloc[0]:
            upper_col = "red"
        else:
            upper_col = "green"

        st.markdown(f"<b>[<span style='color: {lower_col}'>{lower}M</span>, <span style='color: {upper_col}'>{upper}M</span>]*</b>", unsafe_allow_html=True)
        # + f"<small><b> (95% CI)*</b></small>"
    
    st.markdown('#### Extreme Prefecture Dynamics')

    df_population_difference_sorted = calculate_population_difference(population_df, selected_year)

    if selected_year > 1975:
        first_prefecture_name = df_population_difference_sorted.prefecture.iloc[0]
        first_prefecture_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_prefecture_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_prefecture_name = '-'
        first_prefecture_population = '-'
        first_prefecture_delta = ''
    st.metric(label=first_prefecture_name, value=first_prefecture_population, delta=first_prefecture_delta)

    if selected_year > 1975:
        last_prefecture_name = df_population_difference_sorted.prefecture.iloc[-1]
        last_prefecture_population = format_number(df_population_difference_sorted.population.iloc[-1])   
        last_prefecture_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])   
    else:
        last_prefecture_name = '-'
        last_prefecture_population = '-'
        last_prefecture_delta = ''
    st.metric(label=last_prefecture_name, value=last_prefecture_population, delta=last_prefecture_delta)

    

    
with col[1]:

    st.markdown('#### Population Change')
    
    population_chart = make_line_chart(population_df)
    st.plotly_chart(population_chart, use_container_width=True)
    
    st.markdown('#### Prefectures Population Map')
    
    choropleth = make_choropleth(population_df_year, selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    

with col[2]:
    st.markdown('#### Ranked Prefectures')

    st.dataframe(population_df_year_sorted,
                 column_order=("prefecture", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "prefecture": st.column_config.TextColumn(
                        "Prefecture",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(population_df_year_sorted.population),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Created by editing Statistics Dashboard (https://dashboard.e-stat.go.jp/en/); license: Creative Commons Attribution 4.0
            - Japan GIS data: [Simplemaps](https://simplemaps.com/gis/country/jp#admin1); license: Creative Commons Attribution 4.0
            - :orange[**Extreme Prefecture Dynamics**]: first and last prefecture in population growth rank
            - :orange[*]: 95% confidence interval for the predicted population of Japan in 2024
                ''')
