# Estudo isolado — para-choque dianteiro do Buick Regal NASCAR

O objetivo desta revisão é avaliar apenas a forma do conjunto abaixo dos faróis: para-choque e saia inferior. Não altera nem se encaixa automaticamente na carroceria V1/V2. O modelo é interpretado do desenho fornecido, não escaneado de uma peça real.

## O que foi modelado

- Frente quase plana, com leve curvatura horizontal e retornos laterais curtos.
- Faixa superior saliente, relativamente plana, com um sulco inferior estreito.
- Dois rebaixos laterais de 52 × 12 mm, com cantos suavizados e moldura fina.
- Rebaixo central de 44 × 19 mm para representar a área de placa.
- Saia inferior e lábio na base, com frisos verticais discretos.
- Casca aberta atrás, sem fixações inventadas para o chassi.

Os dois rebaixos laterais têm fundo: são detalhes estéticos, não furos de ventilação. Na vista frontal eles estão destacados em cinza-escuro para leitura; os arquivos STL não contêm cor. A perspectiva sem pintura mostra a mesma geometria.

## Medidas: o que sabemos e o que foi estimado

| Medida | Valor | Origem |
|---|---:|---|
| Largura total | 240 mm | Largura máxima do veículo no desenho, aplicada provisoriamente à peça |
| Altura | 44 mm | Estimativa visual, a confirmar |
| Profundidade máxima/retorno | 40 mm | Hipótese, a confirmar |
| Cantos do trajeto | raio 11 mm antes dos relevos | Hipótese de forma |
| Espessura alvo | aproximadamente 2 mm | Hipótese para o estudo, com compensação interna nas regiões inclinadas |

A espessura interna usa um envelope discreto no trajeto da superfície e na altura, adicionando material atrás dos degraus e rebaixos. Não é uma casca CAD de espessura exata certificada. O relatório registra uma verificação de distância entre superfícies em 3.000 amostras; isso não garante o mínimo global nem a resistência da peça. A malha é simplificada após essa medição com tolerância geométrica de 0,015 mm para reduzir o tamanho dos STL; as malhas finais são reabertas e verificadas.

## Arquivos para avaliar

- `previa_parachoque.png`: perspectiva, frontal, superior e perfil lateral.
- `perspectiva.png`: imagem ampliada sem pintura.
- `frente_medidas.png`: frente com largura e altura indicadas.
- `parachoque_inteiro.stl`: peça completa, em mm; eixos X=profundidade, Y=largura, Z=altura.
- `metade_esquerda.stl` e `metade_direita.stl`: alternativa em duas metades. **Escolha o inteiro ou as duas metades; não imprima os três como uma montagem.**
- `validacao.json`: dimensões, volumes, verificação de componentes e distância entre superfícies.
- `gerar.py`: fonte paramétrica reproduzível com Python 3.12 e as dependências de `requirements.txt`.

As metades têm corte central sem pinos nem folga de união. O alinhamento e a colagem ainda precisam ser definidos após aprovar a forma. A abertura traseira foi mantida livre; não há suporte de chassi. Não foram feitos testes em fatiador, impressão física ou montagem. Importe os STL em milímetros, com escala 100%; a orientação de impressão deve ser escolhida no fatiador.

## Para chegar mais perto da peça escolhida

Enviar preferencialmente:

1. Foto frontal reta, com a câmera centralizada na altura do para-choque. Evitar grande-angular e inclinação.
2. Foto lateral ou em três quartos mostrando a profundidade e o retorno dos cantos.
3. Altura e profundidade desejadas na escala do RC, ou medidas do para-choque real para converter.

Um recorte ampliado da frente do desenho ajuda a escolher frisos e rebaixos, mas não resolve a profundidade escondida. Se as fotos forem de outro ano/versão, indicar qual forma deve prevalecer. Para desenhar os encaixes posteriormente, serão necessárias medidas ou imagens da parte de trás e do chassi.

A carroceria inteira permanece arquivada. Este estudo não afirma reproduzir o original com exatidão; serve para comparar uma peça por vez antes de continuar.
