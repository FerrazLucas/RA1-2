#Entrega 1 - RA1 2 - Lucas Cereda Ferraz

import sys



# leitura do arquivo de entrada

def lerArquivo(nomeArquivo):
    with open(nomeArquivo, "r", encoding="utf-8") as arquivo:
        linhas = [linha.strip() for linha in arquivo.readlines()]
    return [linha for linha in linhas if linha]



# analisador léxico em formato de estados

def parseExpressao(linha):
    tokens = []
    posicao = 0
    lexema = ""

    def guardar(tipo, valor):
        tokens.append((tipo, valor))

    def estado_inicial():
        nonlocal posicao, lexema

        while posicao < len(linha) and linha[posicao].isspace():
            posicao += 1

        if posicao >= len(linha):
            return None

        atual = linha[posicao]

        if atual == "(":
            guardar("LPAREN", "(")
            posicao += 1
            return estado_inicial

        if atual == ")":
            guardar("RPAREN", ")")
            posicao += 1
            return estado_inicial

        if atual == "*":
            guardar("OP", "*")
            posicao += 1
            return estado_inicial

        if atual == "%":
            guardar("OP", "%")
            posicao += 1
            return estado_inicial

        if atual == "^":
            guardar("OP", "^")
            posicao += 1
            return estado_inicial

        if atual == "/":
            lexema = "/"
            posicao += 1
            return estado_barra

        if atual in "+-":
            proximo_e_numero = (
                posicao + 1 < len(linha)
                and (linha[posicao + 1].isdigit() or linha[posicao + 1] == ".")
            )

            if proximo_e_numero:
                lexema = atual
                posicao += 1
                return estado_numero

            guardar("OP", atual)
            posicao += 1
            return estado_inicial

        if atual.isdigit() or atual == ".":
            lexema = atual
            posicao += 1
            return estado_numero

        if atual.isalpha() or atual == "_":
            lexema = atual
            posicao += 1
            return estado_identificador

        raise ValueError(f"Caractere inválido: '{atual}'")

    def estado_barra():
        nonlocal posicao, lexema

        if posicao < len(linha) and linha[posicao] == "/":
            lexema += "/"
            posicao += 1

        guardar("OP", lexema)
        lexema = ""
        return estado_inicial

    def estado_numero():
        nonlocal posicao, lexema

        achou_ponto = "." in lexema
        achou_digito = any(caractere.isdigit() for caractere in lexema)

        while posicao < len(linha):
            atual = linha[posicao]

            if atual.isdigit():
                lexema += atual
                achou_digito = True
                posicao += 1
                continue

            if atual == "." and not achou_ponto:
                lexema += atual
                achou_ponto = True
                posicao += 1
                continue

            break

        if not achou_digito:
            raise ValueError(f"Número inválido: {lexema}")

        guardar("NUM", lexema)
        lexema = ""
        return estado_inicial

    def estado_identificador():
        nonlocal posicao, lexema

        while posicao < len(linha):
            atual = linha[posicao]
            if atual.isalnum() or atual == "_":
                lexema += atual
                posicao += 1
            else:
                break

        if lexema == "RES":
            guardar("RES", "RES")
        else:
            guardar("ID", lexema)

        lexema = ""
        return estado_inicial

    estado_atual = estado_inicial
    while estado_atual is not None:
        estado_atual = estado_atual()

    return tokens





def _criar_numero(valor):
    return {"tipo": "NUM", "valor": valor}


def _criar_identificador(valor):
    return {"tipo": "ID", "valor": valor}


def _criar_operador(valor):
    return {"tipo": "OP", "valor": valor}


def _criar_reservado_res():
    return {"tipo": "RES"}


def _criar_binario(operador, esquerdo, direito):
    return {"tipo": "BINOP", "op": operador, "esq": esquerdo, "dir": direito}


def _criar_mem_get(nome):
    return {"tipo": "MEM_GET", "nome": nome}


def _criar_mem_set(nome, expressao):
    return {"tipo": "MEM_SET", "nome": nome, "expr": expressao}


def _criar_ref_res(valor):
    return {"tipo": "RES_REF", "n": valor}


def _transformar_token_em_item(token):
    tipo, valor = token

    if tipo == "NUM":
        return _criar_numero(valor)
    if tipo == "ID":
        return _criar_identificador(valor)
    if tipo == "OP":
        return _criar_operador(valor)
    if tipo == "RES":
        return _criar_reservado_res()

    raise ValueError(f"Token inesperado: {token}")


def _fechar_grupo(itens):
    if len(itens) == 1 and itens[0]["tipo"] == "ID":
        return _criar_mem_get(itens[0]["valor"])

    if len(itens) == 2 and itens[0]["tipo"] == "NUM" and itens[1]["tipo"] == "RES":
        deslocamento = int(float(itens[0]["valor"]))
        if deslocamento <= 0:
            raise ValueError("RES deve usar um número positivo.")
        return _criar_ref_res(deslocamento)

    if len(itens) == 2 and itens[1]["tipo"] == "ID":
        return _criar_mem_set(itens[1]["valor"], itens[0])

    if len(itens) == 3 and itens[2]["tipo"] == "OP":
        return _criar_binario(itens[2]["valor"], itens[0], itens[1])

    raise ValueError("Expressão inválida.")

#Parser

def _parsear_tokens(tokens):
    indice = 0

    def ler_item():
        nonlocal indice

        if indice >= len(tokens):
            raise ValueError("Fim inesperado da expressão.")

        tipo, valor = tokens[indice]

        if tipo == "LPAREN":
            return ler_parenteses()

        if tipo in ("NUM", "ID", "OP", "RES"):
            indice += 1
            return _transformar_token_em_item((tipo, valor))

        raise ValueError(f"Token inesperado: {(tipo, valor)}")

    def ler_parenteses():
        nonlocal indice

        if indice >= len(tokens) or tokens[indice][0] != "LPAREN":
            raise ValueError("Esperado '('.")

        indice += 1
        conteudo = []

        while True:
            if indice >= len(tokens):
                raise ValueError("Parêntese não fechado.")

            if tokens[indice][0] == "RPAREN":
                indice += 1
                break

            conteudo.append(ler_item())

        return _fechar_grupo(conteudo)

    arvore = ler_item()

    if indice != len(tokens):
        raise ValueError("Tokens sobrando após o fim da expressão.")

    return arvore



# etapa intermediária

def executarExpressao(tokens, historicoResultados, memoria):
    if not tokens:
        raise ValueError("Linha vazia.")

    if tokens[0][0] != "LPAREN" or tokens[-1][0] != "RPAREN":
        raise ValueError("Cada linha deve ser uma expressão entre parênteses.")

    return {
        "tokens": tokens,
        "arvore": _parsear_tokens(tokens),
    }





def _limpar_nome(nome):
    return "".join(caractere if caractere.isalnum() or caractere == "_" else "_" for caractere in nome)


def _nome_memoria(nome):
    return f"mem_{_limpar_nome(nome)}"


def _juntar_constantes_e_memorias(no, constantes, memorias):
    tipo = no["tipo"]

    if tipo == "NUM":
        if no["valor"] not in constantes:
            constantes[no["valor"]] = f"const_{len(constantes)}"
        return

    if tipo == "MEM_GET":
        memorias.add(no["nome"])
        return

    if tipo == "MEM_SET":
        memorias.add(no["nome"])
        _juntar_constantes_e_memorias(no["expr"], constantes, memorias)
        return

    if tipo == "BINOP":
        _juntar_constantes_e_memorias(no["esq"], constantes, memorias)
        _juntar_constantes_e_memorias(no["dir"], constantes, memorias)
        return

    if tipo == "RES_REF":
        return


def _empilhar_d0(codigo):
    codigo.append("    VSTR d0, [r10]")
    codigo.append("    ADD r10, r10, #8")


def _desempilhar_para(codigo, registrador):
    codigo.append("    SUB r10, r10, #8")
    codigo.append(f"    VLDR {registrador}, [r10]")


def _gerar_no(no, codigo, constantes, linha_atual):
    tipo = no["tipo"]

    if tipo == "NUM":
        codigo.append(f"    LDR r0, ={constantes[no['valor']]}")
        codigo.append("    VLDR d0, [r0]")
        return

    if tipo == "MEM_GET":
        codigo.append(f"    LDR r0, ={_nome_memoria(no['nome'])}")
        codigo.append("    VLDR d0, [r0]")
        return

    if tipo == "RES_REF":
        linha_destino = linha_atual - no["n"]
        if linha_destino <= 0:
            raise ValueError(f"Linha {linha_atual}: RES aponta para antes do início do arquivo.")
        codigo.append(f"    LDR r0, =res_{linha_destino}")
        codigo.append("    VLDR d0, [r0]")
        return

    if tipo == "MEM_SET":
        _gerar_no(no["expr"], codigo, constantes, linha_atual)
        codigo.append(f"    LDR r0, ={_nome_memoria(no['nome'])}")
        codigo.append("    VSTR d0, [r0]")
        return

    if tipo == "BINOP":
        _gerar_no(no["esq"], codigo, constantes, linha_atual)
        _empilhar_d0(codigo)

        _gerar_no(no["dir"], codigo, constantes, linha_atual)
        _empilhar_d0(codigo)

        _desempilhar_para(codigo, "d1")
        _desempilhar_para(codigo, "d0")

        operador = no["op"]

        if operador == "+":
            codigo.append("    VADD.F64 d0, d0, d1")
        elif operador == "-":
            codigo.append("    VSUB.F64 d0, d0, d1")
        elif operador == "*":
            codigo.append("    VMUL.F64 d0, d0, d1")
        elif operador == "/":
            codigo.append("    VDIV.F64 d0, d0, d1")
        elif operador == "//":
            codigo.append("    BL op_div_inteira")
        elif operador == "%":
            codigo.append("    BL op_resto")
        elif operador == "^":
            codigo.append("    BL op_potencia")
        else:
            raise ValueError(f"Operador inválido: {operador}")
        return

    raise ValueError(f"Nó inválido: {tipo}")



# geração do assembly

def gerarAssembly(expressoesProcessadas, historicoResultados, memoria):
    constantes = {"0.0": "const_zero", "1.0": "const_um"}
    memorias = set(memoria.keys())

    for expressao in expressoesProcessadas:
        _juntar_constantes_e_memorias(expressao["arvore"], constantes, memorias)

    codigo = []
    codigo.append(".data")
    codigo.append("")
    codigo.append("const_zero: .double 0.0")
    codigo.append("const_um: .double 1.0")

    for valor, rotulo in constantes.items():
        if valor in ("0.0", "1.0"):
            continue
        codigo.append(f"{rotulo}: .double {valor}")

    codigo.append("")
    for nome in sorted(memorias):
        codigo.append(f"{_nome_memoria(nome)}: .double 0.0")

    codigo.append("")
    for numero_linha in range(1, len(expressoesProcessadas) + 1):
        codigo.append(f"res_{numero_linha}: .double 0.0")

    codigo.append("")
    codigo.append("pilha: .space 8192")
    codigo.append("")
    codigo.append(".text")
    codigo.append(".global _start")
    codigo.append("")
    codigo.append("_start:")
    codigo.append("    LDR r10, =pilha")
    codigo.append("")

    for numero_linha, expressao in enumerate(expressoesProcessadas, start=1):
        _gerar_no(expressao["arvore"], codigo, constantes, numero_linha)
        codigo.append(f"    LDR r0, =res_{numero_linha}")
        codigo.append("    VSTR d0, [r0]")
        codigo.append("")

    codigo.append("fim:")
    codigo.append("    B fim")
    codigo.append("")

    codigo.extend([
        "op_div_inteira:",
        "    VCVT.S32.F64 s0, d0",
        "    VMOV r0, s0",
        "    VCVT.S32.F64 s1, d1",
        "    VMOV r1, s1",
        "    CMP r1, #0",
        "    BEQ op_div_zero",
        "    MOV r2, #0",
        "    MOV r3, #0",
        "    CMP r0, #0",
        "    BGE op_div_a_ok",
        "    RSB r0, r0, #0",
        "    EOR r3, r3, #1",
        "op_div_a_ok:",
        "    CMP r1, #0",
        "    BGE op_div_b_ok",
        "    RSB r1, r1, #0",
        "    EOR r3, r3, #1",
        "op_div_b_ok:",
        "op_div_loop:",
        "    CMP r0, r1",
        "    BLT op_div_fim_loop",
        "    SUB r0, r0, r1",
        "    ADD r2, r2, #1",
        "    B op_div_loop",
        "op_div_fim_loop:",
        "    CMP r3, #0",
        "    BEQ op_div_sinal_ok",
        "    RSB r2, r2, #0",
        "op_div_sinal_ok:",
        "    VMOV s0, r2",
        "    VCVT.F64.S32 d0, s0",
        "    BX lr",
        "",
        "op_resto:",
        "    VCVT.S32.F64 s0, d0",
        "    VMOV r0, s0",
        "    VCVT.S32.F64 s1, d1",
        "    VMOV r1, s1",
        "    CMP r1, #0",
        "    BEQ op_div_zero",
        "    MOV r3, #0",
        "    CMP r0, #0",
        "    BGE op_rest_a_ok",
        "    RSB r0, r0, #0",
        "    MOV r3, #1",
        "op_rest_a_ok:",
        "    CMP r1, #0",
        "    BGE op_rest_b_ok",
        "    RSB r1, r1, #0",
        "op_rest_b_ok:",
        "op_rest_loop:",
        "    CMP r0, r1",
        "    BLT op_rest_fim_loop",
        "    SUB r0, r0, r1",
        "    B op_rest_loop",
        "op_rest_fim_loop:",
        "    CMP r3, #0",
        "    BEQ op_rest_sinal_ok",
        "    RSB r0, r0, #0",
        "op_rest_sinal_ok:",
        "    VMOV s0, r0",
        "    VCVT.F64.S32 d0, s0",
        "    BX lr",
        "",
        "op_potencia:",
        "    VMOV.F64 d2, d0",
        "    VCVT.S32.F64 s1, d1",
        "    VMOV r1, s1",
        "    LDR r0, =const_um",
        "    VLDR d0, [r0]",
        "    CMP r1, #0",
        "    BEQ op_pot_fim",
        "    MOV r2, #0",
        "    CMP r1, #0",
        "    BGE op_pot_exp_ok",
        "    RSB r1, r1, #0",
        "    MOV r2, #1",
        "op_pot_exp_ok:",
        "op_pot_loop:",
        "    CMP r1, #0",
        "    BEQ op_pot_loop_fim",
        "    VMUL.F64 d0, d0, d2",
        "    SUB r1, r1, #1",
        "    B op_pot_loop",
        "op_pot_loop_fim:",
        "    CMP r2, #0",
        "    BEQ op_pot_fim",
        "    LDR r0, =const_um",
        "    VLDR d1, [r0]",
        "    VDIV.F64 d0, d1, d0",
        "op_pot_fim:",
        "    BX lr",
        "",
        "op_div_zero:",
        "    LDR r0, =const_zero",
        "    VLDR d0, [r0]",
        "    BX lr",
    ])

    return "\n".join(codigo)



# saída

def exibirResultados(tokensPorLinha, assemblyFinal):
    with open("tokens_saida.txt", "w", encoding="utf-8") as arquivo_tokens:
        for numero_linha, lista_tokens in enumerate(tokensPorLinha, start=1):
            arquivo_tokens.write(f"Linha {numero_linha}:\n")
            for tipo, valor in lista_tokens:
                arquivo_tokens.write(f"  ({tipo}, {valor})\n")
            arquivo_tokens.write("\n")

    with open("saida.s", "w", encoding="utf-8") as arquivo_assembly:
        arquivo_assembly.write(assemblyFinal)

    print("Arquivos gerados com sucesso:")
    print("- tokens_saida.txt")
    print("- saida.s")



# main

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.txt")
        return

    nomeArquivo = sys.argv[1]

    try:
        linhas = lerArquivo(nomeArquivo)
        tokensPorLinha = []
        expressoesProcessadas = []
        historicoResultados = []
        memoria = {}

        for numero_linha, linha in enumerate(linhas, start=1):
            tokens_linha = parseExpressao(linha)
            estrutura_linha = executarExpressao(tokens_linha, historicoResultados, memoria)

            tokensPorLinha.append(tokens_linha)
            expressoesProcessadas.append(estrutura_linha)
            historicoResultados.append(f"res_{numero_linha}")

        assemblyFinal = gerarAssembly(expressoesProcessadas, historicoResultados, memoria)
        exibirResultados(tokensPorLinha, assemblyFinal)

    except Exception as erro:
        print(f"Erro: {erro}")


if __name__ == "__main__":
    main()
