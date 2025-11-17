import pandas as pd
import re


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----- REGRAS DE NORMALIZAÇÃO DE DOMÍNIO -----#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Regras com a classificação do tipo de auxílio/PI 

_TIPO_PATTERNS = [
    # Assistência estudantil
    (r"\bRESTAURANTE\s+UNIVERSITARIO\b", "Alimentação"),
    (r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*ALIMENTACAO", "Alimentação"),
    (r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*MORADIA", "Moradia"),
    (r"RUFET|(AUXILIO[.\s-]*RESID.+UNIVERSITARIA)", "Moradia"),
    (r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*TRANSPORTE|TRANSPORTE", "Transporte"),
    (r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*CRECHE|CRECHE", "Pré-Escolar"),
    (r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*EMERGENCIAL[.\s-]+(?:ESTUDANTIL|DE\s+ALIMENTACAO)\b", "Emergencial"),
    (r"ACESSIB.|ACESSIBILIDADE|INCLUSAO|ACESSIVEL", "Inclusão e Acessibilidade"),
    (r"PROMISAES", "Estudante Estrangeiro (PROMISAES)"),
    (r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*INTERCAMBIO[.\s-]+ACADEMICO", "Intercâmbio Acadêmico"),
    (r"CONECTIVIDADE|INTERNET|TECNOLOGIA", "Conectividade"),
    # Ensino
    (r"\bMONITORIA\b",                          "Bolsa Monitoria"),
    (r"\bPIBID\b",                              "PIBID"),
    (r"RESIDENCIA\s+PEDAGOGICA",                "Residência Pedagógica"),
    (r"PROLICEN|PRO LICEN",                     "Prolicen"),
    (r"PROTUT|TUTORIA",                         "Tutoria"),
    # Pesquisa
    (r"\bPIBIC\b|\bPIBITI\b|\bIC\b",            "IC/PIBIC/PIBITI"),
    (r"INICIACAO\s+CIENTIFICA",                 "Iniciação Científica"),
    (r"CNPQ|CAPES",                             "Agências (CNPq/CAPES)"),
    # Extensão
    (r"PROBEX|Extensão",                        "Extensão (PROBEX)"),
    # Gestão/Admin (para não cair em 'Outros')
    (r"DIARIAS|PASSAGENS|HOSPEDAGEM",           "Diárias/Passagens"),
    (r"MANUTENCAO|CONSERVACAO|SERVICO|SERVICOS|OBRA|OBRAS", "Manutenção/Serviços"),
    (r"MATERIAL|EQUIPAMENTO|COMPUTADOR|IMPRESSORA", "Material/Equipamento"),
]

# Regras com as unidades gestoras para classificar os grupos que são macros

_UG_RULES = [
    # Assistência
    (r"PRO[-\s]?REITORIA DE ASSIST.*PROMOCAO ESTUDANTIL|PRAPE|PRAE", "Assistência"),
    # Extensão (UFPB: PRAC historicamente ligada a extensão/assuntos comunitários)
    (r"PRO[-\s]?REITORIA PARA ASSUNTOS COMUNITARIOS|PROEX|Extensão|PRAC\b", "Extensão"),
    # Ensino (graduação)
    (r"PRO[-\s]?REITORIA DE GRADUACAO|\bPRG\b|GRADUACAO", "Ensino"),
    # Pesquisa/Pós
    (r"PRO[-\s]?REITORIA DE POS[-\s]?GRADUACAO|\bPRPG\b|PESQUISA/UFPB|PESQUISA", "Pesquisa"),
    # Hospital universitário -> Ensino (por padrão)
    (r"HOSPITAL UNIVERSITARIO", "Ensino"),
]

# Palavras-Chave no ds_pi (Por Ordem de Prioridade Deliberada) para classificar o grupo macro

_PI_RULES = {
    "Assistência": [
        r"RESTAURANTE\s+UNIVERSITARIO",
        r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*ALIMENTACAO",
        r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*MORADIA|MORADIA",
        r"AUXILIO[.\s-]*RESID.+UNIVERSITARIA",
        r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*TRANSPORTE|TRANSPORTE",
        r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*CRECHE|CRECHE",
        r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*EMERGENCIAL[.\s-]+(?:ESTUDANTIL|DE\s+ALIMENTACAO)\b",
        r"ACESSIB.|ACESSIBILIDADE|INCLUSAO|ACESSIVEL",
        r"PERMANENCIA|VULNERABILIDADE|PROMISAES",
        r"(?:AUX(?:ILIO)?|AUX\.)[.\s-]*INTERCAMBIO[.\s-]+ACADEMICO",
        r"CONECTIVIDADE|INTERNET",
    ],
    "Pesquisa": [
        r"\bPIBIC\b|\bPIBITI\b|\bIC\b|INICIACAO\s+CIENTIFICA",
        r"CNPQ|CAPES",
        r"LABORATORIO.*PESQUISA|PROJETO.*PESQUISA",
    ],
    "Ensino": [
        r"\bMONITORIA\b",
        r"\bPIBID\b",
        r"RESIDENCIA\s+PEDAGOGICA",
        r"PROLICEN|PRO LICEN",
        r"PROTUT|TUTORIA",
        r"CURRICULO|DISCIPLINA|DOCENCIA",
    ],
    "Extensão": [
        r"PROBEX|EXTENSAO|PROJETO\s+DE\s+EXTENSAO|ACAO\s+EXTENSIONISTA|EVENTO\s+EXTENSIONISTA",
        r"COMUNITARIO|COMUNIDADE",
    ],
    # Gestão/Admin para auditoria (evita jogar “diárias/obras” em Ensino por engano)
    "Gestão": [
        r"DIARIAS|PASSAGENS|HOSPEDAGEM",
        r"MANUTENCAO|CONSERVACAO|SERVICO|SERVICOS|OBRA|OBRAS|CABEAMENTO|INSTALACAO",
        r"MATERIAL|EQUIPAMENTO|COMPUTADOR|IMPRESSORA|AQUISICAO",
        r"VEICULO|FROTA",
    ],
}

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----- PRÉ-COMPILAÇÃO DAS REGRAS DE NORMALIZAÇÃO DE DOMÍNIOS  -----#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

_COMPILED_UG_RULES = [(re.compile(p), g) for p, g in _UG_RULES]

_COMPILED_PI_RULES = {g: [re.compile(p) for p in pats] for g, pats in _PI_RULES.items()}

_COMPILED_TIPO_PATTERNS = [(re.compile(p), label) for p, label in _TIPO_PATTERNS]

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----- TRANSFORMAÇÃO DAS REGRAS DE DOMÍNIO  -----#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def normalizar_auxilios_pi(df: pd.DataFrame, col_pi: str = "ds_pi") -> pd.DataFrame:
    """
    Aplica as regras de tipo de dados para novas variáveis (tipo, campus, nível) na descrição do PI.
    - Limpeza dos dados já ocorreu na função transformer.
    """
    out = df.copy()
    txt = out[col_pi].fillna("") # Preenche NaN com string vazia para evitar erro no map

    def _tipo(txti: str) -> str:
        # Usará os padrões pré-compilados e já estabelecidos.
        for pat, label in _COMPILED_TIPO_PATTERNS:
            if pat.search(txti):
                return label
        return "Outros"

    def _campus(txti: str):
        m = re.search(r"CAMPUS\s*([IVX]+)", txti)
        if m and m.group(1) in {"I","II","III","IV"}:
            return f"Campus {m.group(1)}"
        if "TODOS OS CAMPI" in txti:
            return "Todos"
        if "CAVN" in txti:
            return "III"
        if "CCAE" in txti:
            return "IV"
        if "ETS" in txti:
            return "I"
        return "Nao_Aplicavel" 
    
    def _nivel(txti: str):
        return ("CAVN" in txti) or ("ETS" in txti)
    
    # Aplicação dos maps
    out["nivel_tecnico"] = txt.map(_nivel).astype(bool) # Garantir tipo booleano
    out["tipo_auxilio"] = txt.map(_tipo)
    out["campus"] = txt.map(_campus)
    
    return out

def classificar_grupo_auxilio(df: pd.DataFrame, col_ug: str = "ds_ug", col_pi: str = "ds_pi") -> pd.DataFrame:
    """
    Aplica as regras de classificação hierárquica (ds_pi > ds_ug) para definir o grupo macro.
    - Limpeza dos dados já ocorreu na função transformer.
    """
    out = df.copy()
    ug = out[col_ug].fillna("")
    pi = out[col_pi].fillna("")
    
    grupos, origem = [], []
    for ug_txt, pi_txt in zip(ug, pi):
        decided, src = None, None

        # 1) Sinais fortes no ds_pi (Prioridade: Assistência > Pesquisa > Ensino > Extensão > Gestão)
        for g in ["Assistência", "Pesquisa", "Ensino", "Extensão", "Gestão"]:
            # Usa os padrões pré-compilados
            if any(r.search(pi_txt) for r in _COMPILED_PI_RULES[g]):
                decided, src = g, "ds_pi"
                break

        # 2) Se não tiver nada, usa ds_ug
        if decided is None:
            # Usa os padrões pré-compilados
            for r, g in _COMPILED_UG_RULES:
                if r.search(ug_txt):
                    decided, src = g, "ds_ug"
                    break

        # 3) Heurística e Fallback
        if decided is None and ug_txt.startswith("CENTRO "):
            decided, src = "Ensino", "heuristica_centro"
        
        if decided is None:
            decided, src = "Nao_Classificado", "fallback"

        grupos.append(decided)
        origem.append(src)

    out["grupo_auxilio"] = grupos
    out["origem_classif"] = origem
    return out
