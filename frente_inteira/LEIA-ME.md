# Frente inteira — peça única com cinco vãos

Esta revisão atende ao conjunto completo da frente: painel da grade e dos faróis, faixa do para-choque, saia inferior e retornos laterais. Tudo está unido em **um único STL**, sem corte central.

## Aberturas reais

A casca tem cinco furos atravessantes:

1. Grade central: aproximadamente 92 × 23 mm.
2. Conjunto de dois faróis de um lado: aproximadamente 52 × 16 mm.
3. Conjunto de dois faróis do outro lado: aproximadamente 52 × 16 mm.
4. Entrada inferior de um lado: aproximadamente 50 × 11 mm.
5. Entrada inferior do outro lado: aproximadamente 50 × 11 mm.

Não há fundo, grade, lente ou inserto tampando esses vãos. Cada par de faróis usa um vão comum; a separação dos dois faróis será feita nas molduras futuras. As medidas são larguras/alturas projetadas na vista frontal; os cantos são levemente arredondados.

A área central branca de placa permanece fechada e rebaixada, conforme a referência. Os frisos da carroceria permanecem parte da casca; as molduras em torno da grade e dos faróis não foram feitas nesta etapa.

## Dimensões e interpretação

- Largura máxima: 240 mm.
- Altura da peça: 65 mm, adotando como referência a cota frontal da tabela do desenho.
- Profundidade/retorno lateral: 40 mm, estimada.
- A região superior recua aproximadamente 11 mm e estreita levemente em relação à faixa do para-choque.
- Espessura alvo aproximada: 2 mm, com compensação interna atrás dos frisos/rebaixos.

O desenho é conceitual e suas vistas não são perfeitamente consistentes entre si. A distribuição dos vãos, os cantos e o retorno são interpretações, não medidas de uma peça real. Esta frente é um estudo independente; não foi ajustada às junções da carroceria V1/V2 nem a um chassi.

## Arquivos

- `frente_inteira.stl`: a peça única, em milímetros.
- `previa_frente_inteira.png`: perspectiva, frente, traseira e perfil.
- `perspectiva.png`: imagem ampliada.
- `frontal.png`: vista frontal com dimensões.
- `validacao.json`: resultados das verificações geométricas.
- `gerar.py`: gerador paramétrico; Python 3.12 e dependências de `requirements.txt`.

Todas as imagens são projeções da malha STL real. As áreas claras dos vãos são fundo da imagem, não preenchimentos. Não foram usados desenhos ou imagens geradas para simular geometria ausente.

## Verificações

O STL é reaberto e validado como um único volume conectado, com superfícies fechadas ao redor do material. Isso não significa que as aberturas estão tampadas: a casca possui cinco túneis atravessantes, também verificados pela característica de Euler.

Foram usados 49 raios em cada abertura, atravessando toda a profundidade: nenhum deve atingir material. Cinco raios de controle atingem a área de placa, a faixa do para-choque e as pontes da frente. A distância entre superfícies foi amostrada em 3.000 pontos antes dos cortes e da simplificação de tolerância 0,015 mm; o resultado está no relatório, sem garantia de espessura mínima global.

Não foram realizados fatiamento, impressão física ou teste de resistência/encaixe. A peça inteira tem 240 mm de largura; confira a capacidade da impressora antes de imprimir. Não há fixações de chassi, pinos ou apoios definidos para as molduras futuras. Para reproduzir, instale as dependências em um ambiente virtual e execute `python gerar.py` nesta pasta.
