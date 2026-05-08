import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker


sns.set_theme(
    style="whitegrid",
    context="notebook",
    font_scale=0.95  # slightly smaller text
)

plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold"
})


def plot_avg_salary_by_position(df):
    position_average = df.groupby(['Season', 'Position'])['Salary (EUR)'].mean().reset_index()

    plt.figure(figsize=(5, 3))  # smaller

    ax = sns.barplot(
        data=position_average,
        x='Season',
        y='Salary (EUR)',
        hue='Position',
        palette='pastel',
        edgecolor='black'
    )

    plt.title('Average Salary per Position by Season', pad=10, fontsize=12)
    plt.xlabel('Season', fontsize=10)
    plt.ylabel('Avg Salary (€)', fontsize=10)

    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M')
    )

    sns.despine()

    plt.legend(
        title='Position',
        frameon=False,
        fontsize=8,
        title_fontsize=9,
        bbox_to_anchor=(1.02, 1),
        loc='upper left'
    )

    plt.tight_layout()
    plt.show()



def plot_salary_boxplot_by_position(df):
    plt.figure(figsize=(5, 3))  # smaller

    ax = sns.boxplot(
        data=df,
        x='Position',
        y='Salary (EUR)',
        palette='Set2',
        width=0.5,
        linewidth=1,
        fliersize=3
    )

    plt.title('Salary Distribution by Position', pad=10, fontsize=12)
    plt.xlabel('Position', fontsize=10)
    plt.ylabel('Salary (€)', fontsize=10)

    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M')
    )

    sns.despine()

    plt.tight_layout()
    plt.show()


def plot_salary_boxplot_by_position_and_season(df):
    plt.figure(figsize=(5, 3))  # smaller than before

    ax = sns.boxplot(
        data=df,
        x='Position',
        y='Salary (EUR)',
        hue='Season',
        palette='Set3',
        width=0.6,
        fliersize=3
    )

    plt.title('Salary by Position & Season', pad=10, fontsize=12)
    plt.xlabel('Position', fontsize=10)
    plt.ylabel('Salary (€)', fontsize=10)

    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M')
    )

    sns.despine()

    plt.legend(
        title='Season',
        frameon=False,
        fontsize=8,
        title_fontsize=9,
        bbox_to_anchor=(1.02, 1),
        loc='upper left'
    )

    plt.tight_layout()
    plt.show()



def plot_salary_vs_rating(df):
    plt.figure(figsize=(5, 3))  # smaller

    ax = sns.scatterplot(
        data=df,
        x="Salary (EUR)",
        y="totalRating",
        hue="Position",
        size="goals",
        sizes=(30, 180),
        palette="deep",
        alpha=0.7
    )

    plt.title("Salary vs Sofascore Rating", pad=10, fontsize=12)
    plt.xlabel("Salary (€)", fontsize=10)
    plt.ylabel("Rating", fontsize=10)

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M')
    )

    sns.despine()

    plt.legend(
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        frameon=False,
        fontsize=8
    )

    plt.tight_layout()
    plt.show()