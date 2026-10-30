# Buick Regal 1987 — frente de 240 mm

Novo estudo CAD a partir da prancha de peças separadas. **21 componentes em
STEP, uma montagem e um script que gera 22 arquivos F3D dentro do Autodesk
Fusion instalado no seu computador.** Não há arquivos F3D prontos neste ZIP:
o Fusion não está instalado no ambiente usado para preparar os sólidos.

[Baixar o pacote completo](https://github.com/evildinomar2-dot/MICROTEC/raw/refs/heads/main/Buick_Regal_240_CAD_Fusion.zip)
· [Ver a prévia](PREVIA_BUICK.png)
· [Revisão anterior dos detalhes](COMPARACAO_DETALHES.png)
· [Comparar o perfil dos para-lamas](COMPARACAO_PERFIL.png)
· [Para-lama isolado de lado](PERFIL_PARALAMA.png)
· [Revisão anterior das proporções](COMPARACAO_FRENTE.png)
· [Conferir a inclinação lateral](VISTA_LATERAL_FRENTE.png)
· [Vista superior com capô](VISTA_SUPERIOR_CAPO.png)
· [Comparação dos novos relevos](COMPARACAO_FORMAS.png)
· [Como gerar os F3D](fusion/COMO_GERAR_F3D.md)

![Montagem e peças separadas](PREVIA_BUICK.png)

## Base horizontal sob os faróis

A região entre a faixa saliente do para-choque e os faróis recebeu uma casca
em L, com topo horizontal em Z = 35,5 mm e parede de 2 mm. A face frontal
sobe desde Z = 30 mm. A saliência se recolhe suavemente nas extremidades.
Os conjuntos dos faróis mantêm o recuo anterior: esta revisão modifica a
superfície abaixo deles, em vez de aprofundar novamente as lentes.

[Conferir o corte lateral real do CAD](CORTE_DEGRAU_FAROL.png)
· [Vista ampliada em perspectiva](FRENTE_DEGRAU_APROXIMADA.png)

## Faróis recuados em alojamentos

Os dois conjuntos de faróis (carcaças, molduras, lentes e piscas) recuam mais
4,5 mm. As cavidades da frente foram aprofundadas na mesma medida, criando
paredes e uma base horizontal visível abaixo dos faróis. A grade e a faixa
saliente do para-choque mantêm suas posições. O recuo é uma aproximação visual
da perspectiva enviada pelo usuário; ainda não foi validado por impressão.

[Comparar os alojamentos antes e depois](COMPARACAO_RECUO_FAROIS.png)

## Frente em V suave

A vista superior passa a ter centro avançado e laterais recuadas. A curva em
planta usa centro em -3,5 mm e extremos em +4 mm em relação ao perfil vertical:
são 7,5 mm de diferença entre o centro e Y = ±116 mm, com ponta arredondada.
A grade, os alojamentos dos faróis, os dutos, os frisos e a borda do capô usam
a mesma referência. As posições internas das peças continuam independentes.
O ângulo é uma aproximação visual, pois não foi fornecida uma seção medida.

[Conferir a frente vista de cima](VISTA_SUPERIOR_FLECHA.png)

## Detalhes da frente

A grade agora tem contorno superior arqueado (1 mm de diferença entre centro
e extremidades), moldura dupla e 43 barras verticais de 0,55 mm, sem travessa frontal. O mesmo contorno
é usado no vão e no suporte traseiro. Cada farol recebe um aro frontal fino
adicional. O para-choque tem faixa superior saliente, sulco contínuo de 0,7 mm
e lábio inferior. As duas entradas de ar incluem telas abertas integradas,
com malha diagonal, filamentos de aproximadamente 0,5 mm e passo de 3 mm. São detalhes delicados:
a reprodução depende da impressora e deve ser conferida no fatiador.

O capô tem elevação central na borda dianteira de 3 mm, ressalto longitudinal
de 2,8 mm e vincos junto a Y = ±50 mm.
A frente recebeu ombros ao lado da grade e painel central rebaixado para a placa.
As proporções permanecem aproximadas à ilustração; não se trata de uma reprodução medida do carro real.

## Perfil guiado pela prancha do carro inteiro

A referência principal passa a ser a prancha do carro completo. O arco anterior
estava centrado em Z=0, formando apenas um semicírculo baixo. Nesta revisão,
o centro está em X=118 mm e Z=18 mm, com raio de 34 mm. O topo da abertura
chega a Z=52 mm. Abaixo do centro, as extremidades abrem para fora, evitando
o fechamento do recorte circular junto à base. O topo do para-lama sobe suavemente 7 mm em direção à cabine,
e o capô e seus quatro apoios acompanham a subida. O painel mantém 170 mm de
comprimento para preservar a proporção do módulo frontal, em vez de impor
a cota de 120 mm da prancha secundária. Estas medidas são interpretações
visuais e permanecem editáveis.

## Revisão das superfícies e alojamentos

O ombro do para-lama foi redesenhado com dobra mais curta e lateral mais
plana. Um alargamento de até 3,5 mm se concentra ao redor do arco, diminuindo
ao longo de uma faixa de 15 mm; a borda estreita do arco permanece separada
visualmente desse volume. A frente mantém o envelope de 240 mm.

O capô tem dois vincos longitudinais elevados, próximos a Y=±70 mm, que
se suavizam nas extremidades. A grade e os faróis foram recuados 3,35 mm,
em alojamentos com apoios integrados à frente e folga nominal de 0,30 mm.
Os suportes do capô acompanham a nova seção dos para-lamas. Os pinos continuam
removíveis, sem travas elásticas certificadas.

Estas são revisões da geometria CAD baseadas na interpretação visual da
referência. Não constituem uma reprodução dimensional certificada do carro.

## Revisão com capô e encaixes

A vista superior da referência orientou o estreitamento dos para-lamas:
a borda junto ao capô passa de Y=±80 para ±98 mm. O capô tem 195,4 mm
de largura, com folga lateral de 0,30 mm. Os para-lamas foram prolongados
até X=210,3 mm; o capô termina em X=210 mm. Esses comprimentos são
estimativas visuais da prancha, não cotas certificadas do carro original.
A frente mantém 240 mm. Na revisão visual aprovada, a grade passa a 95 mm.

O capô é uma casca curva nominal de 2 mm, removível para cima, com quatro
pinos de Ø4 mm, batentes de Ø6 mm e alojamentos Ø4,6 mm nos suportes internos dos para-lamas.
São encaixes de posicionamento, sem trava elástica: a retenção final precisa
ser definida/testada na impressão. Os demais componentes mantêm mangas,
abas e montagem descritas abaixo; este conjunto não é um kit de travas
sem cola validado. Não há dobradiças nem fixação ao chassi nesta revisão.

## Abrir no Fusion

1. Extraia o ZIP inteiro.
2. No Fusion, abra **Utilitários → Scripts e complementos → Scripts**.
3. Adicione a pasta **fusion/CriarBuickF3D** e execute **CriarBuickF3D**.
4. Os arquivos nativos `.f3d` serão gravados na pasta **F3D_GERADOS**, dentro
   do pacote extraído. O script mantém a montagem aberta e informa o resultado.

Também é possível abrir `BUICK_FRENTE_MONTAGEM.step` diretamente no Fusion e
usar **Arquivo → Exportar → Fusion Archive (.f3d)**. Nenhuma instalação de
Python ou CadQuery é necessária para abrir os STEP ou executar o script no Fusion.

Os arquivos contêm **sólidos CAD BRep editáveis**, com curvas e superfícies,
e não malhas STL convertidas. O STEP não contém os esboços nem o histórico das
operações originais. A conversão para F3D permite trabalhar no formato do
Fusion, mas **não recria esse histórico**. O script ativa, quando possível,
o registro das novas operações feitas após a importação.

## Peças e dimensões

Medidas em milímetros. Para os componentes da frente, as colunas indicam
largura em Y, altura em Z e profundidade nominal de construção em X.
Na face inclinada, a profundidade total aumenta com o recuo; consulte
`MEDIDAS.csv` para as caixas medidas dos sólidos finais. As peças não são
truncadas para caber na antiga profundidade, preservando os aros superiores. O encaixe dos para-lamas
acrescenta 10 mm à frente do painel de 170 mm.

| Componente | Quantidade | Largura × altura × profundidade |
|---|---:|---|
| Para-choque / frente inteira | 1 | 240 × 68 × 40; centro elevado |
| Grade central com barras | 1 | 95 × 26 × 10 |
| Carcaça do conjunto de dois faróis | 2 | 58 × 20 × 20 |
| Lente do farol | 4 | 21 × 13 × 6 |
| Lente do pisca | 2 | 3,6 × 16,6 × 6 |
| Moldura individual do farol | 4 | 24 × 17 × 5 |
| Duto inferior com tela aberta | 2 | 55 × 12 × 30 |
| Anel de suporte traseiro da grade | 1 | 95 × 26 × 10 |
| Placa opcional | 1 | 50 × 16; parede 1, acompanhando a frente |
| Capô removível | 1 | largura 195,4; comprimento aproximado 200; parede 2 |
| Para-lama dianteiro | 2 | painel: 170 de comprimento × 22 de largura × cerca de 72 de altura |

Os para-lamas têm arco de roda livre de **68 mm de diâmetro**, com centro em X=118 mm e Z=18 mm, e duas abas
integradas por lado. Incluindo as abas, cada sólido mede aproximadamente **180 × 31 × 72 mm**
em X/Y/Z. Esquerda e direita são identificadas olhando para a frente a partir
do interior do carro. X cresce para trás, Y indica a largura, Z aponta para cima.

## Interpretação da prancha e encaixes

A nova prancha frontal foi usada pelas proporções visuais, conforme a escolha
do usuário: largura total de 240 mm, grade de 95 × 26 mm e conjuntos de
faróis de 58 × 20 mm. As cotas incompatíveis da imagem (120 + 95 + 95 mm
em 240 mm, e 155 mm até o capô) não foram reproduzidas. A altura nominal
da casca frontal continua 65 mm. A faixa superior recua cerca de 11 mm
entre Z=33 e Z=65: inclinação média aproximada de 19 graus em relação à
vertical. Este ângulo é uma estimativa de modelagem, não uma medição
certificada da referência. O capô e os encaixes acompanham o novo recuo.

- A frente possui cinco aberturas reais: grade, dois conjuntos de faróis e
  dois dutos inferiores. A região da placa é fechada.
- Mangas e aberturas têm **0,30 mm de folga nominal por lado**. As abas
  externas têm afastamento frontal de 0,25 mm da carroceria.
- A base da carroceria usa parede nominal de 2 mm; frisos e superfícies curvas
  alteram a espessura medida na direção normal. Os aros mais finos, inclusive
  o suporte da grade, exigem conferir os perímetros no fatiador.
- As duas abas de cada para-lama se alojam nas luvas internas da frente. Elas
  acompanham a nova curvatura; a montagem e a retenção por colagem precisam de
  teste físico. A folga longitudinal entre os painéis é de 0,30 mm.
- Grade, molduras, lentes e anel traseiro foram preparados para montagem por
  colagem. Não foram criados encaixes elásticos, roscas ou fixações ao chassi.
- A placa opcional acompanha o perfil curvo e fica no painel rebaixado,
  com folga traseira nominal de 0,35 mm para adesivo. Pode ser ocultada ou removida da montagem.
- As lentes têm estrias decorativas; não incluem cálculo óptico, refletores,
  LED, fiação ou suportes elétricos. A transparência depende do material e do
  acabamento da impressão. A base do emblema na grade não contém letras.

## Conferências realizadas

`validacao_cad.json` registra o resultado dos testes dos arquivos entregues:

- 21 arquivos individuais, cada um com um sólido válido após exportar e reabrir;
- montagem STEP reimportada com 21 sólidos válidos;
- passagem livre pelas cinco aberturas da casca frontal;
- interseção volumétrica entre os pares cujas caixas delimitadoras se sobrepõem.

A prévia é renderizada dos próprios STEP. **A importação no Fusion e a montagem
física ainda não foram testadas.** A ausência de interseção geométrica não
substitui um teste de impressão: imprima primeiro uma pequena região de encaixe
para conferir as folgas na sua impressora. A frente inteira requer espaço para
uma peça de 240 mm ou divisão posterior no Fusion.

## Arquivos e regeneração

- `step/`: 21 peças separadas, posicionadas nas coordenadas da montagem;
- `BUICK_FRENTE_MONTAGEM.step`: conjunto com nomes e cores;
- `fusion/`: script e instruções para gerar os F3D;
- `cad/`: código-fonte do modelo e da verificação;
- `PREVIA_BUICK.png` e `VISTA_FRONTAL.png`: prévias;
- `COMPARACAO_CURVATURA.png`: comparação histórica anterior à inclusão do capô;
- `VISTA_SUPERIOR_CAPO.png`: vista superior desta revisão;
- `MEDIDAS.csv`: dimensões medidas dos sólidos exportados;
- `validacao_cad.json`: relatório de validação.

Para alterar as fontes e regenerar fora do Fusion, use Python 3.12 e as versões
em `requirements.txt`:

```sh
python -m pip install -r requirements.txt
python cad/body.py
python cad/details.py
python cad/assemble.py
python cad/preview.py
```

As medidas-base e as interfaces estão em `cad/common.py`; as seções curvas
estão em `cad/formas_carroceria.py`; a carroceria e os acessórios estão em
`cad/body.py` e `cad/details.py`. Algumas dimensões dos
acessórios são explícitas nesses arquivos e precisam ser ajustadas em conjunto.
No Fusion, ao reduzir o conjunto, selecione todos os componentes e aplique o
mesmo fator de escala; isso também reduz paredes e folgas.

As imagens entregues usam `cad/render_vtk.py`, com normais VTK e renderização
por profundidade em cada pixel. Para regenerá-las em Linux com um compilador
C (`cc`) disponível, execute `python cad/render_vtk.py --sheet-dir .`.
`cad/preview.py` continua disponível como alternativa com Matplotlib.
Esses recursos servem apenas para gerar prévias fora do Fusion; não são
necessários para abrir os STEP nem para executar o gerador F3D no Fusion.
