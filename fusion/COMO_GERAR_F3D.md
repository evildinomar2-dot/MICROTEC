# Abrir as pecas e gerar F3D no Fusion

O pacote contem solidos CAD em STEP, prontos para abrir e editar no Autodesk
Fusion. **Os arquivos F3D sao gerados no seu computador pelo proprio Fusion.**
Este pacote nao foi exportado nem testado dentro do Fusion no ambiente em que
foi preparado, pois o programa nao esta instalado nesse ambiente.

## Conversao automatica

1. Baixe o ZIP e **extraia tudo** para uma pasta do seu computador. Nao execute
   o script dentro do ZIP. Mantenha `BUICK_FRENTE_MONTAGEM.step`, a pasta `step`
   e a pasta `fusion` na mesma pasta principal.
2. Abra o Fusion. No espaco de trabalho **Design**, procure **Utilitarios >
   Scripts e complementos** (*Utilities > Scripts and Add-Ins*). Dependendo da
   versao, o comando aparece no menu **Ferramentas**. Ele tambem pode ser
   encontrado pela busca de comandos do Fusion.
3. Na aba **Scripts**, use a opcao **Adicionar** / **+** para adicionar um script
   existente. Selecione a pasta `fusion/CriarBuickF3D` que voce extraiu. Ela contem
   os arquivos `CriarBuickF3D.py` e `CriarBuickF3D.manifest`.
4. Selecione **CriarBuickF3D** na lista e clique em **Executar** (*Run*).
   Se o Fusion pedir a localizacao do pacote, escolha a pasta principal que
   contem `BUICK_FRENTE_MONTAGEM.step`.
5. Aguarde a mensagem final. A conversao cria uma subpasta exclusiva dentro de
   **F3D_GERADOS**, ao lado dos STEP, com um F3D da montagem e um de cada arquivo
   da pasta `step`. A montagem permanece aberta no Fusion.

Nao precisa instalar Python, CadQuery ou qualquer pacote adicional. O script
usa somente os recursos que acompanham o Fusion. Novas execucoes geram novas
pastas e preservam os arquivos anteriores. Os documentos que ja estavam
abertos antes da execucao permanecem abertos.

O arquivo `relatorio_fusion.json` informa quais pecas foram convertidas e
registra eventuais falhas. Em caso de falha, envie esse arquivo para verificacao.

## Abrir manualmente, sem script

No Fusion, use **Arquivo > Abrir > Abrir do meu computador** e escolha
`BUICK_FRENTE_MONTAGEM.step` ou um STEP individual da pasta `step`. Se a sua
versao abrir STEP pelo painel de dados, use **Carregar / Upload** e depois abra
o desenho importado. Com o desenho aberto, use **Arquivo > Exportar** e escolha
**Fusion Archive (.f3d)**. Salve no computador.

## O que fica editavel

- Sao corpos CAD BRep, nao malhas trianguladas de STL.
- Voce pode selecionar faces, fazer novos furos, recortes, extrusoes e outras
  edicoes no Fusion. A montagem e as pecas individuais usam milimetros.
- O STEP nao contem os esbocos, cotas de esboco ou operacoes que deram origem
  aos corpos. **Salvar como F3D nao recria esse historico.** O script tenta
  ativar o historico para registrar suas novas operacoes.
- As cores dependem do suporte de importacao STEP da sua versao do Fusion.
  Voce pode aplicar aparencias no proprio Fusion.

Para reduzir o conjunto, selecione todas as pecas e use o mesmo fator de escala.
Isso tambem altera espessuras, folgas e encaixes; confira esses detalhes antes
de imprimir.
