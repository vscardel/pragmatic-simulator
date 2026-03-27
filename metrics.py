import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator


def ms_to_hours(ms):
    """Converte milissegundos para horas (float)"""
    return ms / (1000 * 60 * 60)


def ms_to_minutes(ms):
    """Converte milissegundos para minutos (float)"""
    return ms / (1000 * 60)


def format_hours_minutes(hours_float):
    """Formata horas em float para uma string no formato 'Xh Ym'"""
    if pd.isna(hours_float):
        return "0h 0m"
    h = int(hours_float)
    m = int((hours_float - h) * 60)
    return f"{h}h {m}min"

# Funções auxiliares recebendo o eixo 'ax' para evitar problemas de escopo


def autolabel_minutes(bars, ax):
    """Adiciona rótulos com formatação de 1 casa decimal + 'm'"""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{format_hours_minutes(height/60)}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 pontos de offset vertical
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)


def autolabel_mixed(bars, ax, pct_idx=1):
    """Adiciona rótulos: 'Xh Ym' para horas, 'Z%' para porcentagem"""
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if i == pct_idx:
            label_text = f"{height:.1f}%"
        else:
            label_text = format_hours_minutes(height)

        ax.annotate(label_text,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 pontos de offset vertical
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)


def plot_comparisons(file_human, file_qlearning):
    # Carregar os arquivos
    df_human = pd.read_csv(file_human)
    df_ql = pd.read_csv(file_qlearning)

    # Pegando os valores da última linha
    last_human = df_human.iloc[-1]
    last_ql = df_ql.iloc[-1]

    # Cores solicitadas
    color_human = 'blue'
    color_ql = 'red'
    label_human = 'Humano'
    label_ql = 'QLearning'
    width = 0.35

    # Preparar a figura com 4 subplots (2 linhas x 2 colunas)
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)

    # =========================================================================
    # GRÁFICO 1: Linha - measured_state vs time (em horas)
    # =========================================================================
    ax1 = axs[0, 0]
    ax1.plot(ms_to_hours(df_human['time']), df_human['measured_state'],
             color=color_human, label=label_human, alpha=0.8)
    ax1.plot(ms_to_hours(df_ql['time']), df_ql['measured_state'],
             color=color_ql, label=label_ql, alpha=0.8)
    ax1.set_title('Estado Medido ao Longo do Tempo')
    ax1.set_xlabel('Tempo (Horas)')
    ax1.set_ylabel('Estado da Planta')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)

    # =========================================================================
    # GRÁFICO 2: Barras - Mean Reaction Time (Degraded e Critical) da ÚLTIMA LINHA
    # =========================================================================
    ax2 = axs[0, 1]

    categories_2 = ['Estado Degradado', 'Estado Crítico']

    # Valores convertidos para MINUTOS
    human_reaction = [ms_to_minutes(last_human['mean_reaction_time_degraded']),
                      ms_to_minutes(last_human['mean_reaction_time_critical'])]
    ql_reaction = [ms_to_minutes(last_ql['mean_reaction_time_degraded']),
                   ms_to_minutes(last_ql['mean_reaction_time_critical'])]

    x2 = np.arange(len(categories_2))

    bars_human_2 = ax2.bar(x2 - width/2, human_reaction, width,
                           color=color_human, label=label_human)
    bars_ql_2 = ax2.bar(x2 + width/2, ql_reaction, width,
                        color=color_ql, label=label_ql)

    ax2.set_title('Tempo Médio de Reação')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(categories_2)
    ax2.set_ylabel('Tempo de Reação (Minutos)')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    autolabel_minutes(bars_human_2, ax2)
    autolabel_minutes(bars_ql_2, ax2)

    # =========================================================================
    # GRÁFICO 3: Barras - Seções Diversas (Manutenção e Equipes)
    # =========================================================================
    ax3 = axs[1, 0]

    # Cálculos Humano
    human_maint_time_h = ms_to_hours(last_human['total_maintenance_time'])
    human_unnec_maint_pct = (last_human['unnecessary_maintenances'] /
                             last_human['total_maintenances'] * 100) if last_human['total_maintenances'] > 0 else 0
    human_avail_time_h = ms_to_hours(last_human['time_with_available_teams'])

    # Cálculos QLearning
    ql_maint_time_h = ms_to_hours(last_ql['total_maintenance_time'])
    ql_unnec_maint_pct = (last_ql['unnecessary_maintenances'] /
                          last_ql['total_maintenances'] * 100) if last_ql['total_maintenances'] > 0 else 0
    ql_avail_time_h = ms_to_hours(last_ql['time_with_available_teams'])

    categories_3 = ['Tempo total em Manutenção',
                    'Manutenções Desnecessárias', 'Tempo c/ equipes Disponíveis']
    human_vals = [human_maint_time_h,
                  human_unnec_maint_pct, human_avail_time_h]
    ql_vals = [ql_maint_time_h, ql_unnec_maint_pct, ql_avail_time_h]

    x3 = np.arange(len(categories_3))

    bars_human_3 = ax3.bar(x3 - width/2, human_vals, width,
                           color=color_human, label=label_human)
    bars_ql_3 = ax3.bar(x3 + width/2, ql_vals, width,
                        color=color_ql, label=label_ql)

    ax3.set_title('Métricas de Manutenção e Equipe Disponível')
    ax3.set_xticks(x3)
    ax3.set_xticklabels(categories_3)
    ax3.legend()

    autolabel_mixed(bars_human_3, ax3)
    autolabel_mixed(bars_ql_3, ax3)

    # Oculta eixo Y do gráfico 3 para focar nos labels
    ax3.set_yticks([])

    # =========================================================================
    # GRÁFICO 4: Linha - available_teams vs time (em horas)
    # =========================================================================
    ax4 = axs[1, 1]
    ax4.plot(ms_to_hours(df_human['time']), df_human['available_teams'],
             color=color_human, label=label_human, alpha=0.8)
    ax4.plot(ms_to_hours(df_ql['time']), df_ql['available_teams'],
             color=color_ql, label=label_ql, alpha=0.8)
    ax4.set_title('Equipes Disponíveis ao Longo do Tempo')
    ax4.set_xlabel('Tempo (Horas)')
    ax4.set_ylabel('Quantidade de Equipes')

    # ---> NOVA LINHA: Força o eixo Y a usar apenas números inteiros <---
    ax4.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax4.legend()
    ax4.grid(True, linestyle='--', alpha=0.6)

    # Salvar e mostrar
    plt.tight_layout()
    plt.savefig("graficos_comparativos.png", dpi=300)
    print("Gráficos salvos com sucesso em 'graficos_comparativos.png'.")
    plt.show()


# --- Exemplo de uso ---
if __name__ == "__main__":
    plot_comparisons("results-human-9h-4teams-time5x.csv",
                     "results-qlearning-v5.csv")
