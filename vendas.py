import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. CRIANDO O HISTÓRICO DE VENDAS DO PLAYSTATION 5 (24 MESES)
# DESAFIO 1: seed alterada para os 4 últimos dígitos da matrícula (6409)
np.random.seed(6409)
meses_historico = pd.date_range(start="2024-09-01", periods=24, freq="MS")

# Tendência de crescimento + variação aleatória
tendencia = np.linspace(8000, 15000, 24)
# DESAFIO 1: desvio-padrão do ruído histórico aumentado de 600 para 1500
ruido = np.random.normal(0, 1500, 24)
vendas_historicas = tendencia + ruido

# DataFrame
df = pd.DataFrame(
    {"Data": meses_historico, "Vendas": vendas_historicas}
).set_index("Data")

# 2. SIMULANDO A LÓGICA DO ARIMA (Tendência + AutoRegressão)
# Calculamos a taxa média de crescimento mês a mês (Diferenciação d=1)
#
# DESAFIO 1 - Impacto do aumento do ruído (600 -> 1500) no crescimento_medio:
# - O aumento do desvio-padrão eleva a volatilidade do histórico simulado.
# - A média das diferenças (np.diff().mean()) tem comportamento telescópico:
#   em expectativa ela continua relacionada apenas à diferença entre o
#   primeiro e o último valor da série, ou seja, à inclinação da tendência.
# - Porém, como os pontos extremos também recebem agora um ruído maior, a
#   realização concreta de crescimento_medio fica mais sensível ao sorteio
#   aleatório e à seed (6409). O valor calculado impresso abaixo reflete essa
#   realização específica.
crescimento_medio = np.diff(df["Vendas"]).mean()
ultima_venda = df["Vendas"].iloc[-1]

# DESAFIO 2: horizonte expandido de 6 para 12 meses futuros
meses_futuros = pd.date_range(
    start="2026-09-01", periods=12, freq="MS"
)  # 2026-2027

# DESAFIO 4 (H4): geramos UMA única sequência de ruídos de projeção e a
# reutilizamos nos três cenários. Assim os choques aleatórios por horizonte
# são idênticos e a diferença entre cenários vem principalmente do crescimento.
ruidos_projecao = np.random.normal(0, 100, len(meses_futuros))


def gerar_projecao(multiplicador_crescimento, aplicar_sazonalidade):
    """Gera uma projeção parametrizada pelo multiplicador de crescimento.

    Mantém a lógica original (tendência + variação do mês anterior), usando os
    mesmos ruídos compartilhados (ruidos_projecao) para todos os cenários.

    - multiplicador_crescimento: 1.0 (base), 1.15 (otimista), 0.75 (pessimista)
    - aplicar_sazonalidade: se True, aplica +35% pontual em Novembro/Dezembro
      (DESAFIO 3). O efeito é pontual: não contamina a trajetória do próximo mês.
    """
    projecao = []
    venda_atual = ultima_venda
    for i in range(1, len(meses_futuros) + 1):
        # Trajetória de crescimento normal (mantém a base do próximo mês limpa)
        venda_atual = (
            venda_atual
            + crescimento_medio * multiplicador_crescimento
            + ruidos_projecao[i - 1]
        )

        # DESAFIO 3: sazonalidade pontual de +35% em Nov/Dez usando .month
        # da data corrente (H1: meses_futuros[i-1]). Aplicada apenas ao valor
        # exibido/plotado do mês, sem propagar para Janeiro (H2).
        valor_mes = venda_atual
        if aplicar_sazonalidade and meses_futuros[i - 1].month in (11, 12):
            valor_mes = venda_atual * 1.35

        projecao.append(valor_mes)
    return projecao


# DESAFIO 4: três cenários usando a mesma estrutura de cálculo
# Cenário Base incorpora as regras dos Desafios 2 e 3 (12 meses + sazonalidade)
projecao_base = gerar_projecao(1.0, aplicar_sazonalidade=True)
projecao_otimista = gerar_projecao(1.15, aplicar_sazonalidade=False)
projecao_pessimista = gerar_projecao(0.75, aplicar_sazonalidade=False)

# DESAFIO 2: a incerteza acumulada cresce com sqrt(i) ao longo dos 12 meses
margem_erro = [800 * np.sqrt(i) for i in range(1, len(meses_futuros) + 1)]

df_futuro = pd.DataFrame(
    {
        "Data": meses_futuros,
        "Base": projecao_base,
        "Otimista": projecao_otimista,
        "Pessimista": projecao_pessimista,
    },
    index=meses_futuros,
)

# 3. EXIBINDO OS RESULTADOS NO TERMINAL
print(f"Crescimento médio calculado (unid./mês): {crescimento_medio:,.2f}")
print("--- PROJEÇÃO DE VENDAS - CENÁRIO BASE (PRÓXIMOS 12 MESES) ---")
for data, valor in zip(df_futuro["Data"], df_futuro["Base"]):
    marca = "  <== +35% (Black Friday/Natal)" if data.month in (11, 12) else ""
    print(
        f"Mês: {data.strftime('%m/%Y')} | Previsão: {int(valor):,} unidades{marca}".replace(
            ",", "."
        )
    )

print("--- COMPARATIVO DE CENÁRIOS (unidades) ---")
for data, base, oti, pes in zip(
    df_futuro["Data"],
    df_futuro["Base"],
    df_futuro["Otimista"],
    df_futuro["Pessimista"],
):
    print(
        f"{data.strftime('%m/%Y')} | Base: {int(base):,} | "
        f"Otimista: {int(oti):,} | Pessimista: {int(pes):,}".replace(",", ".")
    )

# 4. GERANDO O GRÁFICO
plt.figure(figsize=(11, 6))
# Histórico: linha azul com marcadores
plt.plot(
    df.index,
    df["Vendas"],
    label="Histórico de Vendas (PS5)",
    color="#003791",
    marker="o",
)
# Cenário Base: vermelho tracejado (Desafios 2 e 3)
plt.plot(
    df_futuro.index,
    df_futuro["Base"],
    label="Cenário Base (+35% Nov/Dez)",
    color="#d62728",
    linestyle="--",
    marker="o",
)
# Cenário Otimista: verde (+15% de crescimento médio)
plt.plot(
    df_futuro.index,
    df_futuro["Otimista"],
    label="Cenário Otimista (+15% cresc.)",
    color="#2ca02c",
    marker="o",
)
# Cenário Pessimista: laranja (-25% de crescimento médio)
plt.plot(
    df_futuro.index,
    df_futuro["Pessimista"],
    label="Cenário Pessimista (-25% cresc.)",
    color="#ff7f0e",
    marker="o",
)

# Margem de Incerteza (Sombra) - SOMENTE do Cenário Base (H5)
limite_superior = df_futuro["Base"] + margem_erro
limite_inferior = df_futuro["Base"] - margem_erro
plt.fill_between(
    df_futuro.index,
    limite_inferior,
    limite_superior,
    color="#ff9896",
    alpha=0.4,
    label="Margem de Incerteza (Base)",
)

plt.title("Simulação de Previsão de Vendas - PlayStation 5", fontsize=12)
plt.xlabel("Mês")
plt.ylabel("Unidades Vendidas")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()
