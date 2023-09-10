import folium
import inflection
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu

df = pd.read_csv('zomato.csv')

df1 = df.copy()


# Limpesa de dados nulos e duplicatas
df1.dropna(inplace=True)
df1.drop_duplicates(inplace=True)


# Adicionando a coluna país no dataset

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}


def country_name(country_id):
    return COUNTRIES[country_id]


df1['Country'] = df1['Country Code'].apply(country_name)

# Criação do Tipo de Categoria de Comida


def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"


df1['Price tye'] = df1['Price range'].apply(create_price_tye)

# Criação do nome das Cores

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}


def color_name(color_code):
    return COLORS[color_code]


df1['Rating color'] = df1['Rating color'].apply(color_name)


# Padronizando o nome das colunas

def rename_columns(dataframe):
    df1 = dataframe.copy()
    def title(x): return inflection.titleize(x)
    def snakecase(x): return inflection.underscore(x)
    def spaces(x): return x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1


df1 = rename_columns(df1)

df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])


# SideBar


with st.sidebar:
    selected = option_menu("Menu principal", ["Home", 'Visão País', 'Visão Cidades', 'Visão Restaurantes'],
                           icons=['house', 'globe2', 'building', 'egg-fried'], menu_icon="cast", default_index=1)


# Menu Home
if selected == "Home":
    with st.container():
        st.markdown('# Projeto Fome Zero')

    with st.container():

        col1, col2, col3, col4, col5 = st.columns(5, gap='large')

        total_rest = df1.shape[0]
        total_pais = df1.loc[:, 'country'].nunique()
        total_cidade = df1.loc[:, 'city'].nunique()
        total_avaliacoes = df1.loc[:, 'votes'].sum()
        total_culi = df1.loc[:, 'cuisines'].nunique()

        with col1:
            st.markdown(f'Total de Países cadastrados')
            st.markdown(f'### {total_pais}')

        with col2:
            st.markdown(f'Total de cidades cadastrados')
            st.markdown(f'### {total_cidade}')

        with col3:
            st.markdown(f'Total de restaurantes cadastrados')
            st.markdown(f'### {total_rest}')

        with col4:
            st.markdown(f'Total de avaliações cadastrados')
            st.markdown(f'### {total_avaliacoes}')

        with col5:
            st.markdown(f'Total de tipos de culinarias cadastrados')
            st.markdown(f'### {total_culi}')

    # Selecionando linhas e colunas
    colunas = ['country', 'latitude', 'longitude']
    colunas_groupby = ['country']

    # Criando os segmentos
    data_plot = df1.loc[:, colunas].groupby(
        colunas_groupby).max().reset_index()
    # Criando a área do mapa

    f = folium.Figure(width=500, height=250)
    # Desenhando o mapa
    map = folium.Map(
        location=[data_plot['latitude'].mean(),
                  data_plot['longitude'].mean()],
        zoom_start=1,
        control_scale=True
    )

    # Adicionando os pinos nos mapas
    for index, location_info in data_plot.iterrows():
        folium.Marker([location_info['latitude'],
                       location_info['longitude']],
                      popup=location_info['country']).add_to(map)

    folium_static(map, width=1024, height=600)


# Função que conta a quantidade Y x X

def grafico_contagem(titulo, y, x, labely, labelx):
    st.markdown(f"### {titulo}")
    df_pais = (df1.loc[:, [y, x]].groupby(
        x).nunique()).reset_index().sort_values(by=y, ascending=False)
    y_pais = df_pais[y].head(10)
    x_pais = df_pais[x].head(10)
    fig = px.bar(x=x_pais, y=y_pais, width=1000, height=600,
                 labels={'y': labely, 'x': labelx})
    st.plotly_chart(fig, use_container_width=True)

# Função que plota gráficos com médias


def grafico_media(titulo, y, x, labely, labelx):
    st.markdown(f'### {titulo}')

    media_pais_dois = (df1.loc[:, [y, x]].groupby(
        x).mean().sort_values(y, ascending=False).reset_index())
    y_media = media_pais_dois[y].head(5)
    x_media = media_pais_dois[x].head(5)

    fig = px.bar(x=x_media, y=y_media,
                 width=1000, height=600, labels={'y': labely, 'x': labelx})
    st.plotly_chart(fig, use_container_width=True)


if selected == "Visão País":
    st.sidebar.markdown("## Filtros")

    countries = st.sidebar.multiselect(
        "Escolha os Paises que Deseja visualizar as Informações",
        df1.loc[:, "country"].unique().tolist(),
        default=["Brazil", "England", "Qatar",
                 "South Africa", "Canada", "Australia"],
    )
    linhas_selecionadas = df1['country'].isin(countries)
    df1 = df1.loc[linhas_selecionadas, :]

    # Container com gráfico de paises com mais cidades resgistradas
    with st.container():

        grafico_contagem('Top 10 Paises com mais cidades registradas',
                         'city', 'country', 'Quantidade de cidades', 'Países')


# Gráficos com países com mais restaurantes
    with st.container():
        col1, col2 = st.columns(2, gap='large')

        with col1:
            grafico_contagem('Países com mais restaurante cadastrados',
                             'restaurant_name', 'country', 'Quantidade de restaurantes', 'Países')

        # Coluna 2 com com os países mais caros
        with col2:
            st.markdown('### Top 5 países mais caros')
            filtro_pais_preco = df1[(df1['price_range'] == 4)]
            pais_preco = (filtro_pais_preco.loc[:, ['restaurant_name', 'country']].groupby(
                'country').nunique()).reset_index().sort_values(by='restaurant_name', ascending=False, )
            pais_preco_y = pais_preco['restaurant_name'].head(5)
            pais_preco_x = pais_preco['country'].head(5)
            fig = px.bar(x=pais_preco_x, y=pais_preco_y,
                         width=1000, height=600, labels={'y': 'Quantidade de restaurantes com o preço caro', 'x': 'Países'})
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        grafico_media('Países com o custo para 2 mais alto',
                      'average_cost_for_two', 'country', 'Valor para dois', 'Países')


if selected == "Visão Cidades":
    # Container com gráfico de cidades x avaliação
    with st.container():
        st.markdown('### 10 Cidades com mais restaurantes bem avaliados')

        filtro = df1[(df1['aggregate_rating'] >= 4)]
        cidade_media_av = (filtro.loc[:, ['aggregate_rating', 'city']].groupby(
            'city').count()).reset_index().sort_values(by='aggregate_rating', ascending=False)

        y_cidade_media_av = cidade_media_av['aggregate_rating'].head(10)
        x_cidade_media_av = cidade_media_av['city'].head(10)

        fig = px.bar(x=x_cidade_media_av, y=y_cidade_media_av,
                     width=700, height=300, labels={'y': 'restaurantes com nota altas', 'x': 'Cidades'})
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        grafico_media('Cidades mais com o custo para dois mais elevados',
                      'average_cost_for_two', 'city', 'Valor do prato para dois', 'Cidades')

        # Container com gráfico de paises com a culinaria mais diferenciada
    with st.container():
        st.markdown('### 10 Cidades com mais tipos de culinaria')
        culinaria_cidade = (df1.loc[:, ['cuisines', 'city']].groupby(
            'city').count()).reset_index().sort_values(by='cuisines', ascending=False)
        top_culinaria = culinaria_cidade.head(10)
        st.dataframe(top_culinaria, use_container_width=True)


if selected == 'Visão Restaurantes':
    # Slider de seleção de quantidades de restaurantes a vizualizar
    filtro_qtd_restaurante = st.sidebar.slider("Please select a rating range",
                                               min_value=1,
                                               max_value=20, value=10
                                               )
    with st.container():
        grafico_contagem('Restaurantes mais avaliados',
                         'votes', 'restaurant_name', 'Quantidade de avaliações', 'Restaurantes')

    with st.container():
        st.markdown(
            f'### Top {filtro_qtd_restaurante} restaurantes com as maiores avaliações')
        nota_media_restaurantes = (df1.loc[:, ['aggregate_rating', 'restaurant_name']].groupby(
            'restaurant_name')).mean().reset_index().sort_values(by='aggregate_rating', ascending=False)
        topdez = nota_media_restaurantes.head(filtro_qtd_restaurante)
        st.dataframe(topdez, use_container_width=True)

    with st.container():
        st.markdown('### Restaurantes com os pratos para dois mais caros')
        colunas = ['restaurant_name', 'average_cost_for_two']
        duas_pessoas_restaurante = df1.loc[:, colunas]
        duas_pessoas_restaurante.sort_values(
            'average_cost_for_two', ascending=False)
        y_duas_pessoas_restaurante = duas_pessoas_restaurante['average_cost_for_two'].head(
            filtro_qtd_restaurante)

        x_duas_pessoas_restaurante = duas_pessoas_restaurante['restaurant_name'].head(
            filtro_qtd_restaurante)

        fig = px.bar(x=x_duas_pessoas_restaurante,
                     y=y_duas_pessoas_restaurante, width=1000, height=600, labels={
                         'y': 'Valor do prato para dois', 'x': 'Restaurantes'})
        st.plotly_chart(fig, use_container_width=True)
