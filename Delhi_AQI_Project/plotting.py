import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set global style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")

OUTPUT_DIR = "outputs/plots"

def save_plot(fig, filename):
    """Saves the figure to the plots directory."""
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    return path

def plot_bar(df, x_col, y_col, title, filename, xlabel=None, ylabel=None, color='#4C72B0'):
    """Generates a standard bar plot."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x=x_col, y=y_col, color=color, ax=ax)
    ax.set_title(title, fontsize=16, fontweight='bold')
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    return save_plot(fig, filename)

def plot_scatter(df, x_col, y_col, title, filename, xlabel=None, ylabel=None):
    """Generates a standard scatter plot."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col, s=100, alpha=0.7, ax=ax)
    ax.set_title(title, fontsize=16, fontweight='bold')
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    return save_plot(fig, filename)

def plot_line(df, x_col, y_col, title, filename, xlabel=None, ylabel=None, error_y=None):
    """Generates a line plot, optionally with error bars."""
    fig, ax = plt.subplots(figsize=(10, 6))
    if error_y:
        ax.errorbar(df[x_col], df[y_col], yerr=df[error_y], fmt='-o', capsize=5, ecolor='gray')
    else:
        sns.lineplot(data=df, x=x_col, y=y_col, marker='o', ax=ax)
        
    ax.set_title(title, fontsize=16, fontweight='bold')
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    plt.grid(True, linestyle='--', alpha=0.7)
    return save_plot(fig, filename)

def plot_heatmap(df, title, filename, xlabel=None, ylabel=None):
    """Generates a heatmap from a pivot table or correlation matrix."""
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(df, cmap='coolwarm', annot=False, fmt=".2f", ax=ax)
    ax.set_title(title, fontsize=16, fontweight='bold')
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    return save_plot(fig, filename)
