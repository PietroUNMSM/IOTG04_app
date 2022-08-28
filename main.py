# main.py
# =============================================================================
# common
import os
import json
from typing import List
# requirements
from dotenv import load_dotenv
import requests
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template, ThemeChangerAIO, template_from_url
import seaborn
#import matplotlib.pyplot as plt
# -----------------------------------------------------------------------------

load_dotenv('./.env')

def variable_riego_info_dframe(fecha: str) -> pd.DataFrame:
    host = os.environ['HOST_API']
    url = f'{host}/fecha/{fecha}'
    headers = {'Content-type': 'application/json'}
    
    print(f'[INFO] url: {url}')
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    return pd.DataFrame(data)

def fig_dashboard_plots(df: pd.DataFrame) -> tuple:
    
    #top 5 temperaturas °C más_comunes
    topTempC = Counter(df['temperaturaC'].tolist()).most_common(5)
    x = [x[0] for x in topTempC]
    y = [x[1] for x in topTempC]

    figTopTempC = go.Bar(x = x,
                     y = y,
                     marker = dict(color = 'rgb(60, 179, 113)',
                                   line = dict(color='rgb(25, 20, 20)',width=1)))

    layout = go.Layout()
    figTopTempC = go.Figure(data = figTopTempC, layout = layout)
    figTopTempC.update_layout(title_text=f'Top 5 Valores de Temperatura en C° Más Comunes')


    #top 5 temperaturas ambientales más_comunes
    topTempAmb = Counter(df['tempAmb'].tolist()).most_common(5)
    xTAmb = [x[0] for x in topTempAmb]
    yTAmb = [x[1] for x in topTempAmb]

    figTopTempAmb = go.Bar(x = xTAmb,
                     y = yTAmb,
                     marker = dict(color = 'rgb(243, 187, 69)',
                                   line = dict(color='rgb(25, 20, 20)',width=1)))

    layout = go.Layout()
    figTopTempAmb = go.Figure(data = figTopTempAmb, layout = layout)
    figTopTempAmb.update_layout(title_text=f'Top 5 Valores de Temperatura Ambiental Más Comunes')


    #top 5 humedades porcentuales más_comunes
    topHumPorc = Counter(df['humedadPorc'].tolist()).most_common(5)
    xHPorc = [x[0] for x in topHumPorc]
    yHPorc = [x[1] for x in topHumPorc]

    figTopHumPorc = go.Bar(x = xHPorc,
                     y = yHPorc,
                     marker = dict(color = 'rgb(143, 173, 222)',
                                   line = dict(color='rgb(25, 20, 20)',width=1)))

    layout = go.Layout()
    figTopHumPorc = go.Figure(data = figTopHumPorc, layout = layout)
    figTopHumPorc.update_layout(title_text=f'Top 5 Valores de Humedad Porcentual más comunes')


    #top 3 humedades de suelo más comunes
    topHumSuelo = Counter(df['humedadSuelo'].tolist()).most_common(3)
    xHSuelo = [x[0] for x in topHumSuelo]
    yHSuelo = [x[1] for x in topHumSuelo]

    figTopHumSuelo = go.Bar(x = xHSuelo,
                     y = yHSuelo,
                     marker = dict(color = 'rgb(143, 173, 222)',
                                   line = dict(color='rgb(25, 20, 20)',width=1)))

    layout = go.Layout()
    figTopHumSuelo = go.Figure(data = figTopHumSuelo, layout = layout)
    figTopHumSuelo.update_layout(title_text=f'Top 3 Valores de Humedad de Suelo más comunes')

    #distribución de temperaturas °C
    Dist_TempC = df.groupby(pd.Grouper(key='temperaturaC')).size().reset_index(name='count')
    figDist_TempC = px.treemap(Dist_TempC, path=['temperaturaC'], values='count')
    figDist_TempC.update_layout(title_text=f'Distribución de los valores de Temperatura en °C')
    figDist_TempC.update_traces(textinfo="label+value")

    #Creamos una grafo de pastel de los valores de humedad Porcentual
    ##pieHumedadPorc=go.Figure(data=[go.Pie(labels=df['fecha'], values=df["humedadPorc"], hole=.3)])
    #pieHumedadPorc.update_layout(title_text='Humedad Porcental')

    #Histograma de las temperaturas °C en base a la Fecha y hora de Registro
    figHistTC = px.histogram(df, x="fecha", color="temperaturaC")
    figHistTC.update_layout(title_text=f'Histograma de las temperaturas °C en base a la Fecha y hora de Registro')

    #SERIESDETIEMPO
    #serie de tiempo de Temperaturas en °C'
    figTimeSerieTC = go.Figure([go.Scatter(x=df['fechaRegistrada'], y=df['humedadPorc'])])
    figTimeSerieTC.update_layout(title_text=f'Serie de Tiempo de Temperaturas en °C')
    
    #serie de tiempo Temperatura del Ambiente
    figTimeSerieTA = go.Figure([go.Scatter(x=df['fechaRegistrada'], y=df['tempAmb'])])
    figTimeSerieTA.update_layout(title_text=f'Serie de Temperatura del Ambiente')

    #serie de tiempo de Humedad Porcentual
    figTimeSerieHP = go.Figure([go.Scatter(x=df['fechaRegistrada'], y=df['humedadPorc'])])
    figTimeSerieHP.update_layout(title_text=f'Serie de Tiempo de Humedad Porcentual')

    
    #serie de tiempo Humedad del Suelo
    figTimeSerieHS = go.Figure([go.Scatter(x=df['fechaRegistrada'], y=df['humedadSuelo'])])
    figTimeSerieHS.update_layout(title_text=f'Serie de Tiempo de Humedad del Suelo')

    
    return figTopTempC, figTopTempAmb, figTopHumPorc, figTopHumSuelo, figDist_TempC, figTimeSerieTC, figTimeSerieTA, figTimeSerieHP, figTimeSerieHS

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

load_figure_template("MORPH")

# => app dashboard 
app = Dash(__name__, external_stylesheets=[dbc.themes.MORPH])
server = app.server

df = variable_riego_info_dframe(def_fecha := '2022-08-23')
figTopTempC, figTopTempAmb, figTopHumPorc, figTopHumSuelo, figDist_TempC, figTimeSerieTC, figTimeSerieTA, figTimeSerieHP, figTimeSerieHS = fig_dashboard_plots(df)

squared_style = {'width': '50%', 'display': 'inline-block'}


fecha_options = ['2022-08-22', '2022-08-23', '2022-08-24', '2022-08-25',
       '2022-08-26']

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

header = html.H4(
    "Visualización de los resultados del Sistema de Riego", className="bg-primary text-white p-4 mb-2 text-center"
)

footer = html.Footer(
    'Elaborado por el Grupo 04 - Curso IoT - Agosto 2022',
    className="bg-primary text-white p-4 mb-2 text-center"
    )

selectorFecha = html.H3(dcc.Dropdown(
        options=fecha_options,
        value=def_fecha, 
        id='fecha-list',
        placeholder="Seleccione una fecha",
        style={'width':'85%', 'display':'inline-block'}
    ))

botonEjecutar = html.Button('Ejecutar', id='submit-button', n_clicks=0, 
            style={'width':'40%', 'hover':'border-opacity-100', 'hover':'text-gray-800', 'hover':'bg-white','display':'inline-block'})

app.layout = html.Div(children=[
        
    header,
    #html.H1('Visualización de los resultados del Sistema de Riego'),
    dbc.Row(
        [
            dbc.Col(ThemeChangerAIO(aio_id="theme", radio_props={"value":dbc.themes.MORPH}), width=2,),
            dbc.Col(selectorFecha),
            dbc.Col(botonEjecutar),
        ],
        className="mt-4 text-center",
    ),
    
    #,
    #dbc.Button("Success", color="success", id="submit-button"),
    html.Div(id='description', children='', className="text-center"),
    
    
    #GRAFOS DE DATOS
    #,,,,,,,,,,
    #, , , , , , , , ,  
    #dcc.Graph(id='figTopJuegos', figure=figTopJuegos),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='figTopTempC', figure=figTopTempC), lg=6),
            dbc.Col(dcc.Graph(id='figTopTempAmb', figure=figTopTempAmb), lg=6),
        ],
        className="mt-4 dbc",
    ),

    #dcc.Graph(id='figTopTempC', figure=figTopTempC, style=squared_style),
    #dcc.Graph(id='figTopTempAmb', figure=figTopTempAmb, style=squared_style),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='figTopHumPorc', figure=figTopHumPorc), lg=6),
            dbc.Col(dcc.Graph(id='figTopHumSuelo', figure=figTopHumSuelo), lg=6),
        ],
        className="mt-4 dbc",
    ),
    #dcc.Graph(id='figTopHumPorc', figure=figTopHumPorc, style=squared_style), #, style=squared_style),
    #dcc.Graph(id='figTopHumSuelo', figure=figTopHumSuelo, style=squared_style), #, style=squared_style),

    dbc.Row(
        dcc.Graph(id='figDist_TempC', figure=figDist_TempC),
        className = "mt-4 dbc",
    ),

    #dcc.Graph(id='figDist_TempC', figure=figDist_TempC), 
    #dcc.Graph(id='pieHumedadPorc', figure=pieHumedadPorc),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='figTimeSerieTC', figure=figTimeSerieTC), lg=6),
            dbc.Col(dcc.Graph(id='figTimeSerieTA', figure=figTimeSerieTA), lg=6),
        ],
        className="mt-4 dbc",
    ),

    #dcc.Graph(id='figTimeSerieTC', figure=figTimeSerieTC, style=squared_style),
    #dcc.Graph(id='figTimeSerieTA', figure=figTimeSerieTA, style=squared_style),
    
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='figTimeSerieHP', figure=figTimeSerieHP), lg=6),
            dbc.Col(dcc.Graph(id='figTimeSerieHS', figure=figTimeSerieHS), lg=6),
        ],
        className="mt-4 dbc",
    ),
    #dcc.Graph(id='figTimeSerieHP', figure=figTimeSerieHP, style=squared_style),
    #dcc.Graph(id='figTimeSerieHS', figure=figTimeSerieHS, style=squared_style),
    #dcc.Graph(id='figESRB', figure=figESRB)
    #figTopPublishers,figDistDevs,figTopDevelopers,fig_brating,fig_bv,pie1,fig_publisher,fig_dev,fig_users,fig_critic
    footer,
])

@app.callback(    Output('description', 'children'),    Input('submit-button', 'n_clicks'),
    State('fecha-list', 'value')) #Input --> nclicks, State --> cvalue

def update_output_descrip(n_clicks, cvalue: str):
    return f'Resultados obtenidos del {cvalue.capitalize()}.'

@app.callback(
    #,,,,,,,,,,
    #Output('figTopJuegos', 'figure'),
    Output('figTopTempC', 'figure'),
    Output('figTopTempAmb', 'figure'),
    Output('figTopHumPorc', 'figure'),
    Output('figTopHumSuelo', 'figure'),

    Output('figDist_TempC', 'figure'),
    #Output('pieHumedadPorc', 'figure'),
    
    Output('figTimeSerieTC', 'figure'),
    Output('figTimeSerieTA', 'figure'),
    Output('figTimeSerieHP', 'figure'),
    Output('figTimeSerieHS', 'figure'),
    #Output('figESRB', 'figure'),

    Input('submit-button', 'n_clicks'),
    #State('console_serie-list', 'value'),
    State('fecha-list', 'value')
    #Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def update_output_plots(n_clicks, cvalue: str):
    try:
        df = variable_riego_info_dframe(cvalue)
        figTopTempC, figTopTempAmb, figTopHumPorc, figTopHumSuelo, figDist_TempC, figTimeSerieTC, figTimeSerieTA, figTimeSerieHP, figTimeSerieHS  = fig_dashboard_plots(df)
        return figTopTempC, figTopTempAmb, figTopHumPorc, figTopHumSuelo, figDist_TempC, figTimeSerieTC, figTimeSerieTA, figTimeSerieHP, figTimeSerieHS 
    except:
        return html.Div(
            html.H1('Solicitud No Disponible')
            )

if __name__ == '__main__':
    app.run_server(debug=True)
