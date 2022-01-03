import os
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
import seaborn as sns

from paths import DICT_PATH, FORM_PATH, SAVE_PATH


ZOOM = 2


@dataclass
class WordScore:
    pos: bool
    neg: bool


def construct_word_scores() -> Dict[str, WordScore]:
    df = pd.read_csv(DICT_PATH)
    return {
        row.Word: WordScore(
            pos=True if row.Positive else False, neg=True if row.Negative else False
        )
        for row in df.itertuples()
        if row.Positive or row.Negative
    }


def get_filenames(year: int, quarter: int) -> List[str]:
    return [f for f in os.listdir(FORM_PATH) if f.startswith(f"{year}-{quarter}")]


def compute_score(file: str, word_scores: Dict[str, WordScore]) -> int:
    with open(os.path.join(FORM_PATH, file), "r") as f:
        contents = f.read()
    words = [w.replace("\n", "") for w in contents.split(" ")]

    score = 0
    for word in words:
        if word not in word_scores:
            continue
        ws = word_scores[word]
        score += 1 if ws.pos else 0
        score -= 1 if ws.neg else 0

    return score / len(words)


def plot_chart(df: pd.DataFrame):
    plt = df.plot(
        x="year",
        y="avg_score",
        title=f"Average Sentiment Analysis Score per year to the 10E6 power",
    )
    figure = plt.get_figure()
    w, h = figure.get_size_inches()
    figure.set_size_inches(w * ZOOM, h * ZOOM)
    figure.savefig(
        os.path.join(SAVE_PATH, "sentiment-analysis.png"),
        dpi=figure.get_dpi() * ZOOM,
    )


def save_stats(df: pd.DataFrame):
    table = pd.DataFrame(
        {
            "mean": df["avg_score"].mean(),
            "median": df["avg_score"].median(),
            "mode": df["avg_score"].mode(),
            "range": df["avg_score"].max() - df["avg_score"].min(),
        }
    )
    table = table.iloc[0]
    table.to_csv(os.path.join(SAVE_PATH, "descriptive-stats.csv"))


def main():
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    word_scores = construct_word_scores()

    rows = []
    for year in range(1995, 2022):
        print(f"Computing avg score for year: {year}")
        scores = []
        for quarter in range(1, 5):
            scores.extend(
                [compute_score(f, word_scores) for f in get_filenames(year, quarter)]
            )
        rows.append({"year": year, "avg_score": sum(scores) / len(scores)})

    df = pd.DataFrame(rows)
    df["avg_score"] = df["avg_score"] * 1000000

    save_stats(df)
    plot_chart(df)


main()
