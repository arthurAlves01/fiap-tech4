import matplotlib.pyplot as plt

def render_risk_chart(prob):
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.barh([0], [prob], height=0.6)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel('Probabilidade (%)')
    ax.set_title('Probabilidade Estimada de Obesidade')
    # cor por faixa
    if prob < 30:
        color = '#2ECC71'
    elif prob < 60:
        color = '#F1C40F'
    else:
        color = '#E74C3C'
    ax.patches[0].set_color(color)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig