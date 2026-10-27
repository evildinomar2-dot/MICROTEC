# Buick Regal NASCAR 1987 — carroceria RC, protótipo V1

Modelo geométrico inicial interpretado a partir da imagem fornecida. Não é uma reprodução CAD fiel nem uma peça já validada fisicamente. Superfícies simplificadas; detalhes e encaixes serão refinados.

## Arquivos
- `stl/`: uma peça por arquivo, em milímetros, na posição de montagem.
- `montagem_referencia.stl`: conjunto para visualizar; não usar como peça única de impressão.
- `previa.png`: vistas montada e explodida geradas a partir das malhas.
- `gerar.py`: fonte paramétrica editável.
- `validacao.json`: dimensões e verificação de cada peça.

## Medidas e hipóteses
- Comprimento 620 mm; largura máxima 240 mm.
- Teto na cota Z=155 mm; borda inferior Z=8 mm. A altura da malha é portanto 147 mm; 155 mm é a altura em relação ao solo de referência.
- Eixos em X=120 e X=520 mm: entre-eixos 400 mm.
- Aberturas de roda com raio 46 mm e centros em Z=34 mm. São hipóteses, não dimensões confirmadas do seu RC; verificar esterçamento e curso da suspensão.
- Casca com deslocamento nominal de 2 mm nas coordenadas; espessura normal varia nas superfícies inclinadas. Não há garantia de espessura uniforme de 2 mm.
- Parte inferior e janelas abertas. Sem chassi, rodas, vidros, interior ou postes de fixação.
- Portas incluem colunas; para-choques incluem painéis frontal/traseiro. Sem dobradiças ou articulação.
- Peças se encontram nas linhas de divisão, sem folga, pinos ou abas de colagem nesta versão. Fragmentos isolados abaixo de 50 mm³ decorrentes dos cortes foram descartados.

## Antes de imprimir
Importe cada STL em milímetros (escala 100%). Use a função do fatiador de colocar na mesa e escolha a orientação individualmente: os arquivos preservam coordenadas de montagem, não orientações de impressão. Verifique suportes, paredes finas e dimensões no fatiador. Para-choques chegam a 234 mm de largura; ainda não foi definida uma mesa de impressão. Não foi realizado teste de fatiamento nem impressão física. Faça primeiro uma peça de teste; ainda não há sistema de união projetado.

## Reproduzir
Python 3.12. Em um ambiente virtual, instale as dependências de `requirements.txt` e execute `python gerar.py` nesta pasta. Isso regenera STL, prévia e relatório. Ao alterar a divisão, use uma pasta de saída limpa para evitar arquivos antigos misturados.

A próxima revisão deve usar medidas do chassi e das rodas, volume da impressora e feedback visual para definir encaixes, espessuras, detalhes de grade/faróis, fixações e subdivisões.
