import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px

# import json
# from utils import chart_1

# Number.prototype._called = {};

st.set_page_config(page_title='Dash', page_icon="📊", layout='wide')
st.logo('https://www.luc-estienne.com/web/image/website/1/logo', link='https://www.luc-estienne.com/')

CONFIG = {'displayModeBar': False, 'showAxisDragHandles': False}
COLORS = {'color_discrete_sequence' : None}

def format_k_M(value, digits : int = 2):
    """ 1000 -> 1M, 587 -> 5,87k """
    value = int(value)
    if value < 0 : return '-' + format_k_M(-value, digits)
    if value < 1_000 : return str(value)
    if value < 1_000_000 : return f'{round(value/1000, digits)}k'
    if value < 1_000_000_000 : return f'{round(value/1_000_000, digits)}M'
    return str(value)

# DATA
@st.cache_data
def load_data(file_path : str) -> pd.DataFrame :
    data = pd.read_csv(file_path, sep=';')
    data['Sexe'] = data['Sexe'].replace({'M': 'Homme', 'F': 'Femme'})
    return data

# @st.cache_data
# def json_data_1() -> dict :
#     with open('charts/chart1.json', 'r') as f :
#         res = json.load(f)
#     print(res)
#     return res

data = load_data('data/donnees_pyramide_act.csv')

# SIDEBAR
annee = st.sidebar.number_input('Année', 1991, 2024, 2024, 1)
age_min, age_max = st.sidebar.slider('Age', 0, 99, (0, 99), 1)
sexe = st.sidebar.toggle('Ventiler par sexe')

# SUBDATA
data_annee : pd.DataFrame = data[(data['Année'] == annee) & (age_min <= data['Age']) & (data['Age'] <= age_max)]
data_annee_1 : pd.DataFrame = data[(data['Année'] == annee-1) & (age_min <= data['Age']) & (data['Age'] <= age_max)]
repartition_population : pd.DataFrame = data_annee.sort_values('Age').groupby('Age')['Population'].sum().reset_index()
temp : pd.DataFrame = data[(age_min <= data['Age']) & (data['Age'] <= age_max)]

# BODY
st.title('Population française')

# KPI
col1, col2, col3, col4 = st.columns(4)

# Simple charts
if not sexe :
    population_totale = data_annee['Population'].sum()
    population_totale_y_1 = data_annee_1['Population'].sum()
    col1.metric('Population', format_k_M(population_totale), format_k_M(population_totale-population_totale_y_1), 'normal')

    mediane = 0; cumul = 0
    for i in range(len(repartition_population['Population'])) :
        cumul += repartition_population.loc[i, 'Population']
        if cumul > population_totale/2 :
            mediane = repartition_population.loc[i, 'Age']
            break

    col2.metric('Age médian', f'{mediane} ans')

    evolution_population = temp.groupby('Année')['Population'].sum().reset_index()

    # Line chart
    line_chart = px.line(evolution_population, x='Année', y='Population', title='Evolution de la population depuis 1991')
    st.plotly_chart(line_chart, config=CONFIG)

    # Bar chart
    bar_chart = px.bar(data_annee, x='Age', y='Population', title='Répartion de la population selon l\'age')
    bar_chart.update_layout(bargap=0)
    st.plotly_chart(bar_chart, config=CONFIG)


# Multiple charts
if sexe :
    population_totale = data_annee.sort_values('Sexe').groupby('Sexe')['Population'].sum()
    population_totale_y_1 = data_annee_1.sort_values('Sexe').groupby('Sexe')['Population'].sum()

    col1.metric(
        'Population Féminine', format_k_M(population_totale['Femme']), 
        format_k_M(population_totale['Femme']-population_totale_y_1['Femme']) if annee > 1991 else None
    )
    col2.metric(
        'Population Masculine', format_k_M(population_totale['Homme']), 
        format_k_M(population_totale['Homme']-population_totale_y_1['Homme']) if annee > 1991 else None
    )

    evolution_population = temp.groupby(['Année', 'Sexe'])['Population'].sum().reset_index()

    line_chart = px.line(evolution_population, x='Année', y='Population', color='Sexe', title='Evolution de la population depuis 1991', **COLORS)
    st.plotly_chart(line_chart, config=CONFIG)

    col1, col2 = st.columns(2)
    temp = data_annee.copy()
    temp['Population'] = np.where(temp['Sexe'] == 'Homme', -temp['Population'], temp['Population'])

    bar_chart = px.bar(temp, x='Population', y='Age', color='Sexe', orientation='h', title='Répartition de la population selon l\'age et le sexe', **COLORS)
    bar_chart.update_layout(bargap=0, height=600, width=450)
    col1.plotly_chart(bar_chart, config=CONFIG)
    
    temp = data_annee.groupby('Sexe')['Population'].sum().reset_index()
    pie = px.pie(color=temp['Sexe'], category_orders=temp['Population'], values=temp['Population'], hole=.65, hover_name=temp['Sexe'], **COLORS)
    pie.update_layout(bargap=0, height=600, width=300)
    col2.plotly_chart(pie, config=CONFIG)
