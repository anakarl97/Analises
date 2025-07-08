import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta, time
import plotly.express as px
import plotly.graph_objects as go

# Lê a planilha a partir da linha correta (linha 16 = índice 15)
df = pd.read_excel('dags.xlsx', header=15)

print(df.columns.tolist())

# Normaliza os nomes das colunas
df.columns = df.columns.str.strip().str.upper()

# Filtra colunas principais
df = df[['DAG', 'HR_ATUALIZACAO_BRA', 'DURACAO_CARGA']].dropna()

# Expande múltiplos horários (separados por vírgula)
df['HR_ATUALIZACAO_BRA'] = df['HR_ATUALIZACAO_BRA'].astype(str)
df = df.assign(HORA_EXPANDIDA=df['HR_ATUALIZACAO_BRA'].str.split(',')).explode('HORA_EXPANDIDA')
df['HORA_EXPANDIDA'] = df['HORA_EXPANDIDA'].str.strip()

# Tratamento de expressões como */5, */30
def gerar_intervalos(hora_str):
    hora_str = hora_str.strip()
    if hora_str.startswith('*/'):
        try:
            intervalo = int(hora_str.replace('*/', ''))
            return [time(hour=h, minute=m) for h in range(24) for m in range(0, 60, intervalo)]
        except:
            return []
    try:
        return [datetime.strptime(hora_str, '%H:%M:%S').time()]
    except:
        return []

df['HORA_LISTA'] = df['HORA_EXPANDIDA'].apply(gerar_intervalos)
df = df.explode('HORA_LISTA')
df = df.dropna(subset=['HORA_LISTA'])
df['IS_FREQUENTE'] = df['HORA_EXPANDIDA'].str.strip().isin(['*/5', '*/30'])

# Trata a duração e converte para timedelta
def ajustar_duracao(valor):
    valor = str(valor).strip()
    partes = valor.split(':')
    if len(partes) == 1:
        try:
            hora = int(float(partes[0]))
            return f"{hora:02d}:00:00"
        except:
            return None
    if len(partes) == 2:
        return f"{partes[0]:0>2}:{partes[1]:0>2}:00"
    if len(partes) == 3:
        return f"{partes[0]:0>2}:{partes[1]:0>2}:{partes[2]:0>2}"
    return None

df['DURACAO_TRATADA'] = df['DURACAO_CARGA'].apply(ajustar_duracao)
df['DURACAO_TRATADA'] = pd.to_timedelta(df['DURACAO_TRATADA'], errors='coerce')
df = df.dropna(subset=['DURACAO_TRATADA'])

# Cria colunas de INÍCIO e FIM para o gráfico
df['INICIO'] = df['HORA_LISTA'].apply(lambda t: datetime.combine(datetime.today(), t))
df['FIM'] = df['INICIO'] + df['DURACAO_TRATADA']

# Identifica DAGs simultâneas
def verificar_conflito(row, todas):
    if row['IS_FREQUENTE']:
        return 'dodgerblue'
    inicio, fim = row['INICIO'], row['FIM']
    conflitos = todas[
        (todas['INICIO'] < fim) &
        (todas['FIM'] > inicio) &
        (todas['DAG'] != row['DAG'])
    ]
    conflitos_reais = conflitos[~conflitos['IS_FREQUENTE']]
    return 'red' if not conflitos_reais.empty else 'green'

df['COR'] = df.apply(lambda row: verificar_conflito(row, df), axis=1)

# Ordena DAGs pelo nome
dags_unicas = sorted(df['DAG'].unique())
dag_idx = {dag: i for i, dag in enumerate(dags_unicas)}
num_dags = len(dag_idx)
altura_total = max(10, num_dags * 0.8)

# Prepara DataFrame para plotagem
df_plot = df.copy()
df_plot['DAG_NOME'] = df_plot['DAG']
df_plot['INICIO'] = pd.to_datetime(df_plot['INICIO'])
df_plot['FIM'] = pd.to_datetime(df_plot['FIM'])

# Cria gráfico Gantt
fig = px.timeline(
    df_plot,
    x_start='INICIO',
    x_end='FIM',
    y='DAG_NOME',
    color='COR',
    color_discrete_map={
        'green': 'green',
        'red': 'red',
        'dodgerblue': 'dodgerblue'
    },
    hover_data=['DAG', 'HR_ATUALIZACAO_BRA', 'DURACAO_CARGA']
)

# Remove legenda automática
fig.for_each_trace(lambda t: t.update(showlegend=False) if t.name in ['green', 'red', 'dodgerblue'] else None)

# Inverte eixo Y (ordem alfabética)
fig.update_yaxes(autorange="reversed")

# Define faixa do eixo X de 00:00 a 00:00 do dia seguinte
inicio_x = datetime.combine(datetime.today(), datetime.min.time())
fim_x = inicio_x + timedelta(days=1)

# Aplica layout com eixo superior adicional
fig.update_layout(
    title="Execução das DAGs - Frequências",
    xaxis=dict(
        title="Horário",
        side="bottom",
        tickformat="%H:%M",
        dtick=3600000,
        range=[inicio_x, fim_x],
        showline=True,
        ticks="outside"
    ),
    xaxis2=dict(
        title="Horário",
        side="top",
        overlaying="x",
        tickformat="%H:%M",
        dtick=3600000,
        range=[inicio_x, fim_x],
        showline=True,
        showticklabels=True,
        ticks="outside"
    ),
    yaxis=dict(title="DAGs"),
    height=max(800, len(dag_idx) * 25),
)

# Força renderização do eixo superior (x2)
fig.add_trace(go.Scatter(
    x=[inicio_x],
    y=[None],
    xaxis="x2",
    mode="markers",
    marker=dict(color='rgba(0,0,0,0)'),
    showlegend=False
))

# Legenda personalizada
fig.add_trace(go.Scatter(
    x=[None], y=[None],
    mode='markers',
    marker=dict(size=10, color='green'),
    name='Isolada'
))
fig.add_trace(go.Scatter(
    x=[None], y=[None],
    mode='markers',
    marker=dict(size=10, color='red'),
    name='Carga paralela'
))
fig.add_trace(go.Scatter(
    x=[None], y=[None],
    mode='markers',
    marker=dict(size=10, color='dodgerblue'),
    name='Execução frequente'
))

# Abre gráfico no navegador
fig.write_html("grafico_dags_interativo.html", auto_open=True)
