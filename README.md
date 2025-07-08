 Análise de Execuções de DAGs no Airflow
 Descrição
Projeto desenvolvido para monitoramento (inicialmente manual) das execuções de DAGs no Apache Airflow, utilizando como base os logs processados via Excel. O principal objetivo é identificar sobrecargas e conflitos de execução causados por DAGs que rodam simultaneamente.

O gráfico gerado em HTML fornece uma análise visual dos horários:

🔴 Vermelho: DAGs que colidem com outras (executam exatamente no mesmo horário).

🟢 Verde: DAGs que executam de forma isolada, sem concorrência.

⚠️ DAGs com execuções frequentes (como a cada 5 ou 30 minutos) foram removidas da regra de colisão para evitar poluição visual — essas ocupam muitos pontos e estariam sempre em vermelho.

Tecnologias Utilizadas
Python

Pandas

Plotly (HTML interativo)

Excel (entrada de dados)

Apache Airflow (origem dos dados)

▶Como Utilizar
Extraia os logs ou horários de execução das DAGs.

Organize os dados em um arquivo Excel com os horários no formato HH:MM ou HH:MM:SS.

Execute o script Python para gerar o gráfico:

bash
Copiar
Editar
python grafico_dags.py
Abra o arquivo grafico_dags.html no navegador.

 Exemplo (Screenshot)
(Aqui você pode adicionar um print do gráfico ou um link de visualização caso tenha hospedado o HTML)

Melhorias Futuras
Automatizar a leitura dos logs diretamente do Composer / GCP

Criar uma interface via Streamlit

Classificar DAGs por projeto ou carga média
