import time
import dash
import RAKE
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dataframe_image as dfi

from wordcloud import WordCloud
from dash.exceptions import PreventUpdate
from sklearn.naive_bayes import GaussianNB
from dash.dependencies import Input, Output
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score


# ----------------------------------------------------------------------------------------------------------------------

def predprocesiranje_podatkov():
    dataframe_1 = pd.read_json('../scrape/filmi_podrobno.json').set_index('naziv')
    dataframe_2 = pd.read_json('../scrape/filmi_podrobno_rt.json').set_index('naziv')

    dataframe_1['zanr_filma'] = dataframe_1.apply(
        lambda row: row['zanri_filma'][0],
        axis=1
    )

    del dataframe_1['zanri_filma']

    # print("Dataframe 1 - before droping duplicates: " + str(dataframe_1.shape[0]))
    # print("Dataframe 2 - before droping duplicates: " + str(dataframe_2.shape[0]))

    dataframe_1 = dataframe_1[~dataframe_1.index.duplicated(keep='first')]
    dataframe_2 = dataframe_2[~dataframe_2.index.duplicated(keep='first')]

    # print("Dataframe 1 - after droping duplicates: " + str(dataframe_1.shape[0]))
    # print("Dataframe 2 - after droping duplicates: " + str(dataframe_2.shape[0]))

    dataframe = pd.merge(dataframe_1, dataframe_2, left_index=True, right_index=True)

    dataframe.dropna(how='any', axis=0, inplace=True)

    # print("Dataframe 1 - after droping null value rows: " + str(dataframe_1.shape[0]))
    # print("Dataframe 2 - after droping null value rows: " + str(dataframe_2.shape[0]))

    dataframe['ocena_uporabnikov_x'] = dataframe['ocena_uporabnikov_x'] * 10

    dataframe['ocena_kritikov'] = (dataframe['ocena_kritikov_x'] + dataframe['ocena_kritikov_y']) / 2
    dataframe['ocena_uporabnikov'] = (dataframe['ocena_uporabnikov_x'] + dataframe['ocena_uporabnikov_y']) / 2

    del dataframe['ocena_kritikov_x']
    del dataframe['ocena_kritikov_y']
    del dataframe['ocena_uporabnikov_x']
    del dataframe['ocena_uporabnikov_y']
    del dataframe['leto_izida_y']

    dataframe.rename(columns={'leto_izida_x': 'leto_izida'}, inplace=True)

    dataframe['trajanje_filma'] = dataframe['trajanje_filma'].astype(float).astype(int)
    dataframe['ocena_kritikov'] = dataframe['ocena_kritikov'].astype(float).astype(int)
    dataframe['ocena_uporabnikov'] = dataframe['ocena_uporabnikov'].astype(float).astype(int)

    # print("Final dataframe size: " + str(dataframe.shape[0]))

    # dfi.export(dataframe, "dataframe.png", max_rows=10)

    heatmap = sns.heatmap(dataframe.corr(), xticklabels=1, yticklabels=1)
    fig = heatmap.get_figure()
    fig.set_figheight(14)
    fig.set_figwidth(14)
    fig.savefig("heatmap.png")

    return dataframe


def prikazi_rezultate(rezultati, y_test):
    df_2 = pd.DataFrame(columns=['dejanske_vrednosti', 'napovedane_vrednosti'])

    for i in range(len(rezultati)):
        df_2 = df_2.append({
            'dejanske_vrednosti': y_test[i],
            'napovedane_vrednosti': rezultati[i]
        }, ignore_index=True)

    df_2[:100].plot.line()
    plt.show()


def ucenje_modela(dataframe, algoritem, x_vrednost, y_vrednost):
    nominalni_stolpci = dataframe.select_dtypes(exclude=['int32', 'int64']).columns

    dataframe = pd.get_dummies(dataframe, columns=nominalni_stolpci)

    izhodni_podatek = 'zasluzek'
    vhodni_podatki = dataframe.columns.drop([izhodni_podatek])

    x_train, x_test, y_train, y_test = train_test_split(dataframe[vhodni_podatki], dataframe[izhodni_podatek],
                                                        test_size=0.10, random_state=0)
    rezultat = []
    if algoritem == 1:
        dtr = DecisionTreeRegressor()
        rezultat = dtr.fit(x_train, y_train).predict(x_test)
        print("MAE: ", mean_absolute_error(rezultat, y_test))
        print("MSE: ", mean_squared_error(rezultat, y_test))
        print("EVS: ", explained_variance_score(rezultat, y_test))

    elif algoritem == 2:
        gnb = GaussianNB()
        rezultat = gnb.fit(x_train, y_train).predict(x_test)
        print("MAE: ", mean_absolute_error(rezultat, y_test))
        print("MSE: ", mean_squared_error(rezultat, y_test))
        print("EVS: ", explained_variance_score(rezultat, y_test))

    prikazi_rezultate(rezultat, y_test)

    dataframe2 = pd.DataFrame(columns=['dejanske_vrednosti', 'napovedane_vrednosti', 'napaka'])
    for i in range(len(rezultat)):
        dataframe2 = dataframe2.append({
            'naziv': x_test.index[i],
            'dejanske_vrednosti': int(y_test[i]),
            'napovedane_vrednosti': rezultat[i],
            'napaka': int(y_test[i]) - rezultat[i]
        }, ignore_index=True)
    dataframe2.set_index('naziv', inplace=True)

    dataframe2['napaka'] = abs(dataframe2['napaka'])
    dataframe2['y_os'] = dataframe2['dejanske_vrednosti'] if y_vrednost == 'dejanske_vrednosti' \
        else dataframe2['napovedane_vrednosti']
    dataframe2['x_os'] = x_test[x_vrednost]

    # print(dataframe2)

    dfi.export(dataframe2, "dataframe2.png", max_rows=50)

    return dataframe2


def rake_algoritem(opis):
    rake_obj = RAKE.Rake('content/SmartStoplist.txt')
    list_kljucnih_besed_dict = dict((x, int(y)) for x, y in rake_obj.run(opis))
    return WordCloud(width=1000, height=500).generate_from_frequencies(list_kljucnih_besed_dict)


def nastavi_vr_parametrov(list_parametrov):
    dict_list_param = []
    for param in list_parametrov:
        label = param.replace('_', ' ').capitalize()
        dict_list_param.append({'label': label, 'value': param})
    return dict_list_param


def nastavi_vr_filmov(filmi):
    dict_list_filmov = []
    for index, film in enumerate(filmi):
        dict_list_filmov.append({'label': film, 'value': index})
    return dict_list_filmov


def nastavi_barvo_pike(vrednost):
    if vrednost <= 0:
        return 'red'
    elif vrednost > 0:
        return 'green'


def nastavi_velikost_pike(vrednost):
    if vrednost <= 1000000:
        return 5
    elif 1000000 < vrednost <= 10000000:
        return 10
    elif 10000000 < vrednost <= 100000000:
        return 15
    elif 100000000 < vrednost <= 1000000000:
        return 20
    elif 1000000000 < vrednost:
        return 25


# ----------------------------------------------------------------------------------------------------------------------

pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 20)

index_posodobitve = 0

df = predprocesiranje_podatkov()

list_filmov = df.index.values.tolist()
list_param = df.columns.drop(['zasluzek', 'opis'])
param_prva_izvedba = ['trajanje_filma', 'mesec_izida', 'oznacba_primernosti_filma', 'zanr_filma', 'ocena_kritikov',
                      'st_ocen_kritikov', 'st_ocen_uporabnikov']

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Učenje modela in prikaz rezultatov', children=[
            html.Div([
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls',
                                      children=[
                                          html.H2('UČENJE MODELA IN PRIKAZ REZULTATOV'),
                                          html.Label(
                                              'Izberite parametre katerih vrednosti bomo uporabili pri učenju '
                                              'modela:'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(id='parametri',
                                                                    options=nastavi_vr_parametrov(list_param),
                                                                    multi=True,
                                                                    value=param_prva_izvedba,
                                                                    style={'backgroundColor': '#1E1E1E'})
                                                   ],
                                                   style={'color': '#1E1E1E'}),
                                          html.Label(
                                              'Izberite algoritem s pomočjo katerega bomo ustvarili model '
                                              'znanja:'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(id='algoritem',
                                                                    options=[
                                                                        {'label': 'Regresijsko drevo', 'value': 1},
                                                                        {'label': 'Naivni Bayes', 'value': 2}
                                                                    ],
                                                                    multi=False,
                                                                    value=2,
                                                                    style={'backgroundColor': '#1E1E1E'})
                                                   ],
                                                   style={'color': '#1E1E1E'}),
                                          html.Label('Izberite vrednost x osi:'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(id='vrednost_x',
                                                                    multi=False,
                                                                    value='ocena_kritikov',
                                                                    style={'backgroundColor': '#1E1E1E'})
                                                   ],
                                                   style={'color': '#1E1E1E'}),
                                          html.Label('Izberite vrednost y osi:'),
                                          html.Div(className='div-for-dropdown',
                                                   children=[
                                                       dcc.Dropdown(id='vrednost_y',
                                                                    options=[{'label': 'Dejanske vrednosti',
                                                                              'value': 'dejanske_vrednosti'},
                                                                             {'label': 'Napovedane vrednosti',
                                                                              'value': 'napovedane_vrednosti'}],
                                                                    multi=False,
                                                                    value='napovedane_vrednosti',
                                                                    style={'backgroundColor': '#1E1E1E'})
                                                   ],
                                                   style={'color': '#1E1E1E'})
                                      ]),
                             html.Div(id='graf', className='eight columns div-for-charts bg-grey')
                         ])
            ])
        ]),
        dcc.Tab(label='Ekstrakcija ključnih besed', children=[
            html.Div([
                html.Div(className='row',
                         children=[
                             html.Div(className='four columns div-user-controls', children=[
                                 html.H2('EKSTRAKCIJA KLJUČNIH BESED'),
                                 html.Label('Izberite film:'),
                                 html.Div(className='div-for-dropdown',
                                          children=[
                                              dcc.Dropdown(id='film',
                                                           options=nastavi_vr_filmov(list_filmov),
                                                           multi=False,
                                                           style={'backgroundColor': '#1E1E1E'})
                                          ],
                                          style={'color': '#1E1E1E'})
                             ]),
                             html.Div(className='eight columns div-for-charts bg-grey',
                                      children=[
                                          html.Img(id='slika')
                                      ])
                         ])
            ])
        ])
    ])
])


# ----------------------------------------------------------------------------------------------------------------------


@app.callback(
    Output('slika', 'src'),
    Input('film', 'value'))
def posodobi_sliko(film):
    global index_posodobitve
    if film is None:
        raise PreventUpdate
    wordcloud = rake_algoritem(df.iloc[film]['opis'])
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.savefig('assets/wordcloud' + str(index_posodobitve) + '.png', bbox_inches='tight', pad_inches=0)
    plt.close()
    time.sleep(1)
    asset_url = app.get_asset_url('wordcloud' + str(index_posodobitve) + '.png')
    index_posodobitve = index_posodobitve + 1
    return asset_url


@app.callback(
    Output('vrednost_x', 'options'),
    [Input('parametri', 'value')])
def posodobi_dropdown(parametri):
    if 'reziser' in parametri:
        parametri.remove('reziser')
    if 'zanr_filma' in parametri:
        parametri.remove('zanr_filma')
    if 'mesec_izida' in parametri:
        parametri.remove('mesec_izida')
    if 'produkcijska_hisa' in parametri:
        parametri.remove('produkcijska_hisa')
    if 'oznacba_primernosti_filma' in parametri:
        parametri.remove('oznacba_primernosti_filma')
    return nastavi_vr_parametrov(parametri)


@app.callback(
    Output('graf', 'children'),
    [Input('parametri', 'value')],
    Input('algoritem', 'value'),
    Input('vrednost_x', 'value'),
    Input('vrednost_y', 'value'))
def posodobi_ucenje_modela_graf(parametri, algoritem, x, y):
    if parametri is None or x is None or y is None:
        return PreventUpdate

    parametri.append('zasluzek')
    df_lr = ucenje_modela(df[parametri].copy(), algoritem, x, y)

    children = [
        dcc.Graph(figure=go.Figure(
            data=go.Scatter(
                x=df_lr['x_os'],
                y=df_lr['y_os'],
                mode='markers',
                opacity=0.7,
                text=list(df.index.values),
                textposition='bottom center',
                marker=dict(
                    size=list(map(nastavi_velikost_pike, df_lr['napaka'])),
                    color=list(map(nastavi_barvo_pike, df_lr['y_os'])))
            )
        ))
    ]

    return children


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
