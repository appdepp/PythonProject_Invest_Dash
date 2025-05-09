import matplotlib.pyplot as plt

def plot_prices(df_prices):
    df_prices.plot(figsize=(10, 5), title="Цены акций")
    plt.xlabel("Дата")
    plt.ylabel("Цена ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_returns(returns):
    returns.plot(figsize=(10, 5), title="Дневная доходность")
    plt.xlabel("Дата")
    plt.ylabel("Доходность (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()