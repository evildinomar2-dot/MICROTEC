# Buick Regal NASCAR 1987 — carroceria RC V2

Modelo interpretado a partir do esboço do usuário, em milímetros. Esta é uma revisão geométrica para avaliação, não uma reprodução CAD de fábrica nem um projeto validado em impressão física.

## O que mudou em relação à V1

- Capô e teto com curvatura transversal e transições longitudinais mais suaves.
- Ombros elevados nos para-lamas, relevo junto às passagens de roda e vincos inferiores nas laterais.
- Aberturas laterais e molduras de para-brisa corrigidas; cabine separada em duas partes com o teto incluído.
- Faces dianteira e traseira divididas ao meio.
- Grade com aletas, quatro faróis e duas lanternas como peças individuais, com alojamentos na carroceria.
- Prévia com iluminação calculada sobre as próprias malhas. Nenhuma imagem gerada foi usada como substituto da geometria.

## Conteúdo

- `stl/`: 22 peças de montagem mais 1 modelo de tala reta para eventual colagem interna (23 arquivos).
- `montagem_referencia.stl`: todas as peças nas coordenadas de montagem, exceto a tala. Somente para visualização; não imprimir como peça única.
- `previa_v2.png`: perspectiva, vista explodida, lateral e frontal.
- `validacao.json`: lista exata de peças, dimensões e volumes.
- `verificacao_exportacao.json`: resultado de reabrir e validar todos os STL e testar interferências volumétricas.
- `gerar.py` e `verificar.py`: fontes para reproduzir a geometria e as verificações.

## Dimensões

Comprimento 620 mm, largura máxima 240 mm e entre-eixos 400 mm. Centros das passagens de roda em X=120 e X=520 mm, Z=33 mm; raio de abertura 46 mm. A altura do teto é Z=155 mm em relação ao solo de referência. A borda inferior está em Z=8 mm: a altura real do conjunto STL é 147 mm.

A espessura é definida por deslocamentos de aproximadamente 2 mm nas coordenadas da casca; não é uma operação de espessura normal constante. Há variação nas inclinações e nos relevos. As faces dianteira e traseira começam com 5 mm para permitir os alojamentos. Isso ainda deve ser avaliado no fatiador.

## Montagem e impressão

Importe em milímetros e escala 100%. Os arquivos preservam suas posições de montagem; coloque cada peça na mesa e escolha a orientação no fatiador. O maior comprimento entre os painéis individuais é cerca de 217 mm; consulte o manifesto para todas as dimensões. O volume da impressora ainda não foi informado e nenhuma orientação com suportes foi validada.

Os painéis da carroceria se encontram nominalmente sem folga na linha de corte. Não há pinos de alinhamento ou fixação ao chassi. A tala reta de 24 × 12 × 2 mm é uma peça auxiliar genérica; use somente após verificar assentamento em superfícies internas compatíveis, nunca forçando uma curva. A união definitiva ainda precisa ser projetada para o material e o processo de impressão.

Grade, faróis e lanternas têm folgas nominais de 0,2–0,3 mm nos alojamentos. Essas folgas são hipóteses para prova de encaixe, não tolerâncias confirmadas. Os faróis são sólidos com relevo, sem alojamento de LED ou transparência física. O spoiler é uma peça independente; sua base e forma de fixação ainda precisam de ajuste à tampa.

Não há rodas, chassi, vidros, interior, dobradiças ou fixações de RC. Antes de imprimir o conjunto, confira as rodas reais, o esterçamento, o curso da suspensão, as medidas do chassi e a espessura útil nas regiões estreitas. Recomenda-se começar por uma prova pequena de encaixe de farol/grade.

## Verificação realizada

Todos os 23 STL foram reabertos, com verificação de malha fechada, volume positivo, uma única componente conectada e dimensões correspondentes ao manifesto. A montagem mede 620 × 240 × 147 mm. Os 13 pares com sobreposição das caixas delimitadoras foram examinados por interseção booleana: nenhuma interferência acima de 0,05 mm³. Nenhum fragmento foi descartado na geração final. Esses testes não comprovam resistência, espessura mínima, qualidade de impressão ou compatibilidade com o RC.

Não foram realizados fatiamento, impressão física ou testes no chassi.

## Reproduzir

Com Python 3.12, crie um ambiente virtual, instale `requirements.txt`, rode `python gerar.py` e depois `python verificar.py`. O gerador atualiza os arquivos desta pasta; arquivos STL antigos fora do manifesto atual são removidos da subpasta `stl/`. Preserve modificações manuais antes de regenerar.
