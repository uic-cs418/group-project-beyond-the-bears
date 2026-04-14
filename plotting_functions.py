import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# Generates a grouped bar chart showing the average salary per position across multiple seasons.
def plot_avg_salary_by_position(df):
    # Group the data by season and position
    position_average = df.groupby(['Season', 'Position'])['Salary (EUR)'].mean().reset_index()

    # Set the style and size
    plt.figure(figsize = (14, 7))
    sns.set_theme(style = "whitegrid")

    # Create the side-by-side bar chart
    ax = sns.barplot(
        data=position_average,
        x = 'Season',
        y = 'Salary (EUR)',
        hue = 'Position',
        palette = 'Set2' 
    )

    # Format the chart
    plt.title('Average Salary per Position by Season', fontsize = 16)
    plt.xlabel('Season', fontsize = 14)
    plt.ylabel('Average Salary (EUR)', fontsize = 14)

    # Format y-axis to show value in millions and add euro sign (Used unicode since euro sign breaks inbetween files)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M'))

    # Move the legend outside the plot
    plt.legend(title = 'Position', bbox_to_anchor = (1.05, 1), loc = 'upper left')

    plt.tight_layout()
    plt.show()

# Generates a boxplot showing the distribution and outliers of salaries for each position across the dataset
def plot_salary_boxplot_by_position(df):
    plt.figure(figsize = (12, 8))
    sns.set_theme(style = "whitegrid")

    # Create the boxplots
    ax = sns.boxplot(
        data=df,
        x = 'Position',
        y = 'Salary (EUR)',
        hue = 'Position',
        palette = 'Set1',
        width = 0.6,      # Thins the boxes slightly for a cleaner look
        fliersize = 5     # Adjusts the size of the outlier dots
    )

    # Format the chart
    plt.title('Salary Distribution and Outliers by Position', fontsize = 16)
    plt.xlabel('Position', fontsize = 14)
    plt.ylabel('Salary (EUR)', fontsize = 14)

    # Format y-axis to show value in millions
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M'))

    plt.tight_layout()
    plt.show()

# Generates a grouped boxplot showing the distribution and outliers of salaries for each position, split across multiple seasons.
def plot_salary_boxplot_by_position_and_season(df):
    # Increased width to 16 to accommodate 5 boxes per position
    plt.figure(figsize = (16, 8))
    sns.set_theme(style = "whitegrid")

    # Create the side-by-side boxplots
    ax = sns.boxplot(
        data=df,
        x = 'Position',
        y = 'Salary (EUR)',
        hue = 'Season',
        palette = 'Set3',
        width = 0.7,      
        fliersize = 4     
    )

    # Format the chart
    plt.title('Salary Distribution and Outliers by Position & Season', fontsize = 16)
    plt.xlabel('Position', fontsize = 14)
    plt.ylabel('Salary (EUR)', fontsize = 14)

    # Format y-axis to show millions
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M'))

    # Move the legend outside the plot
    plt.legend(title = 'Season', bbox_to_anchor = (1.05, 1), loc = 'upper left')

    plt.tight_layout()
    plt.show()

# Generates a scatterplot comparing salary to Sofascore total rating, colored by position and sized by goals
def plot_salary_vs_rating(df):
    # Set the size and theme
    plt.figure(figsize=(14, 7))
    sns.set_theme(style="whitegrid")

    # Create the scatterplot
    ax = sns.scatterplot(
        data = df,
        x = "Salary (EUR)",
        y = "totalRating",
        hue = "Position",
        size = "goals",
        sizes = (50, 400),
        palette = "tab10",
        alpha=0.8
    )

    # Format the chart text
    plt.title("Salary vs Sofascore Rating", fontsize=16)
    plt.xlabel("Salary (EUR)", fontsize=14)
    plt.ylabel("Total Rating", fontsize=14)

    # Format the x-axis to show millions
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'\u20AC{x*1e-6:,.1f}M'))

    # Move the combined legend outside the plot
    plt.legend(bbox_to_anchor = (1.05, 1), loc = 'upper left')

    plt.tight_layout()
    plt.show()