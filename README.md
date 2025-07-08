Projeto desenvolvido para monitoramento (inicialmente manual) das execuções de DAGs no Apache Airflow, 
utilizando como base os logs extraídos e tratados em Excel. 

O objetivo é identificar possíveis sobrecargas e conflitos de execução em períodos simultâneos de atualização de dados.

O gráfico gerado em HTML destaca visualmente esses conflitos:

Vermelho: DAGs que colidem (executam exatamente no mesmo horário que outras).

Verde: DAGs que executam de forma isolada, sem concorrência.

Para evitar poluição visual, DAGs que rodam em alta frequência (ex: a cada 5 ou 30 minutos) foram excluídas da regra de colisão, pois ocupam muitos pontos no gráfico e estariam sempre marcadas em vermelho.
