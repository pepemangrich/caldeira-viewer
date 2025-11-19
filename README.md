# README — Integral IMI • Software Caldeira

Aplicação Streamlit para visualizar leituras de espessura de paredes de tubos de caldeiras a partir de planilhas .xlsx.
Gera um heatmap interativo por componente (ex.: West Wall), com opções de ajuste das leituras e exibição de foto do ponto clicado.

## O que o app faz

Lê um arquivo .xlsx (aba Summary + abas de componentes, ex.: West Wall, East Wall…).

Converte leituras para mm e a elevação do eixo Y para metros.

Exibe heatmap com:

Escala fixa baseada nos dados originais.

Intervalo de espessuras filtrável via slider.

Valores ≤ 0 mm destacados em preto.

Tooltip (balão) visível inclusive sobre as células pretas.

Permite reduzir leituras em mm e/ou em % (independentes).

Ao clicar em um ponto, tenta exibir a imagem correspondente ao tubo/elevação.

## Nomenclatura das imagens (duas formas)

Você pode relacionar fotos aos pontos de duas maneiras. As duas podem conviver.

### 1) Apenas pelo nome do arquivo (padrões em imgs/fotos/)

Crie o diretório dentro do repositório:

imgs/fotos/


O app tenta encontrar a imagem seguindo estes padrões (nessa ordem):

Em metros (testa 3/2/1/0 casas decimais):

{WALL}_T{TUBO}_E{ELEV:.3f}.jpg
{WALL}_T{TUBO}_E{ELEV:.3f}.png


Em pés (com sufixo ft, também 3/2/1/0 casas):

{WALL}_T{TUBO}_E{ELEVft}ft.jpg
{WALL}_T{TUBO}_E{ELEVft}ft.png


Fallback por tubo (sem elevação):

{WALL}_T{TUBO}.jpg
{WALL}_T{TUBO}.png


Regras importantes

{WALL} = nome exato da aba/parede (ex.: West Wall).

{TUBO} = rótulo do tubo exatamente como no eixo X (ex.: 17 → T17 no nome).

Use ponto como separador decimal (ex.: 12.345, não 12,345).

Exemplos

imgs/fotos/West Wall_T17_E12.345.jpg
imgs/fotos/West Wall_T18_E32.8ft.png
imgs/fotos/West Wall_T17.png

### 2) Planilha opcional Photos no mesmo .xlsx (mapeamento explícito)

Crie uma aba chamada Photos com as colunas (case-insensitive):

wall (ou componente)	tube	elevation_m (ou elevation_ft)	path
West Wall	17	12.345	imgs/fotos/west_T17_E12.345.jpg
West Wall	18	10.000	imgs/fotos/west_T18_E10.png

Como o app faz o “casamento”

Chave: (wall, tube, round(elevation_m, 3)).

wall deve bater com a aba (ex.: West Wall).

tube deve ser o mesmo rótulo que aparece no eixo X (convertido para string).

Prefira elevation_m (metros, ponto decimal). Se usar elevation_ft, o app converte.

path é caminho relativo ou absoluto até a imagem.

## Experiência de uso

Faça login e carregue o .xlsx.

Escolha o componente (aba).

Ajuste (se quiser) mm e/ou %.

Use o slider para focar no intervalo.

Clique em um ponto para ver a foto (se houver).

Dica: se não aparecer foto, confira o nome do arquivo (ou a linha na aba Photos) e se o {WALL}/{TUBO}/elevação correspondem exatamente ao que o gráfico mostra.

## Observações

O heatmap usa escala fixa dos dados originais (antes de reduções).

Células ≤ 0 mm são pintadas em preto, mas continuam com tooltip.

A elevação no Y é exibida em metros (conversão interna de pés → metros).