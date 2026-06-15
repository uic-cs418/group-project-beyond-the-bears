# Soccer Misspricing: Premier League Salary vs. Performance Analytics

A data science and web scraping pipeline that evaluates "value for money" in the English Premier League. By extracting financial data from Capology and performance metrics from FBref, this project maps player weekly wages against their clinical output on the pitch to visualize the correlation between massive contracts and actual goals scored.

## 🚀 Features
* **Automated Web Scraping:** Bypasses dynamic JavaScript rendering and anti-bot measures to extract clean sports finance data.
* **Data Pipelines:** Cleans, flattens, and type-casts complex MultiIndex tabular data into structured Pandas DataFrames.
* **Fuzzy Name Matching:** Resolves cross-platform player spelling inconsistencies and diacritics (e.g., matching "Martin Ødegaard" to "Martin Odegaard").
* **Insights & Visualization:** Generates Seaborn scatterplots identifying league superstars, clinical bargains, and financial underperformers without scientific notation skewing the scale.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Data Libraries:** Pandas, NumPy
* **Scraping Architecture:** ScraperFC
* **Visualization:** Seaborn, Matplotlib
