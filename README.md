# Linguagens-Formais-e-Compiladores
Trabalhos da materia de Linguagens Formais e Compiladores

- Instituição:PUCPR
- Disciplina: Linguagens Formais e Compiladores
- Professor: Frank Coelho de Alcantra
- Aluno: Lucas Ferraz
- GitHub do aluno: FerrazLucas

# Entrega 1 - Analisador Léxico e Gerador de Assembly para ARMv7

# Resumo

Este trabalho implementa a primeira fase de um compilador simples. O programa lê um arquivo de entrada com expressões da linguagem proposta, faz a análise léxica, organiza a estrutura da expressão e gera um arquivo Assembly compatível com ARMv7. Ao final da execução também são gravados os tokens reconhecidos em arquivo texto.

# O que o programa faz

O arquivo principal contém as funções pedidas na atividade:

- lerArquivo
- parseExpressao
- executarExpressao
- gerarAssembly
- exibirResultados

O fluxo do programa é:

1. ler o arquivo de entrada;
2. tokenizar cada linha;
3. montar a estrutura interna da expressão;
4. gerar o código Assembly;
5. salvar os tokens e o Assembly gerado.

# Linguagem aceita pelo programa

Cada linha do arquivo deve ser uma expressão entre parênteses.

# Operadores suportados

- +
- -
- *
- /
- //
- %
- ^

### Comandos suportados

- (MEM) → leitura de memória
- (V MEM) → gravação em memória
- (N RES) → referência a resultado anterior
- (A B OP) → operação binária em notação pós-fixa

### Exemplos de entrada

```text
(3.0 4.0 +)
(7.0 A)
(A)
(1 RES)
((2.0 3.0 +) 4.0 *)
```

# Como executar

Este projeto foi feito em Python 3.

No terminal, execute:

```bash
python main.py teste1.txt
```

Também é possível usar os outros arquivos de teste:

```bash
python main.py teste2.txt
python main.py teste3.txt
```

# Arquivos gerados

Ao executar o programa, são gerados:

- tokens_saida.txt → lista de tokens reconhecidos em cada linha
- saida.s → Assembly ARMv7 gerado a partir do arquivo de entrada

# Como testar no simulador

O Assembly gerado pode ser montado e executado no CPULATOR, usando o modelo ARMv7 DEC1-SOC (v16.1).

Procedimento usado nos testes:

1. executar o programa em Python para gerar saida.s;
2. abrir o saida.s no CPULATOR;
3. compilar e executar;
4. verificar os resultados nas labels res_1, res_2, res_3 etc.;
5. verificar variáveis de memória nas labels mem_*.

# Descrição resumida das funções

# lerArquivo(nomeArquivo)
Lê o arquivo de entrada, remove espaços extras e ignora linhas vazias.

# parseExpressao(linha)
Faz a análise léxica da linha usando estados e devolve uma lista de tokens.

# executarExpressao(tokens, historicoResultados, memoria)
Valida o formato da expressão e monta a estrutura interna usada na geração do Assembly.

# gerarAssembly(expressoesProcessadas, historicoResultados, memoria)
Gera o arquivo Assembly ARMv7 com área de dados, memória, resultados e sub-rotinas auxiliares.

# exibirResultados(tokensPorLinha, assemblyFinal)
Grava os arquivos de saída do trabalho.


