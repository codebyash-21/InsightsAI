"""
insights.py
-----------
Aggregation and visualisation — concepts are auto-detected by Gemini.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def build_dataframe(results: list[dict]) -> pd.DataFrame:
    """
    Flatten all paper results into one DataFrame.
    Concept is read directly from the AI output — no concept map needed.
    """
    rows = []
    for paper in results:
        paper_num = paper["paper"]
        for q_id, data in paper["questions"].items():
            q_key   = q_id.upper().strip()
            concept = data.get("concept") or "Unknown"
            correct = data.get("correct", False)
            mistake = data.get("mistake") or ("none" if correct else "unspecified")
            rows.append({
                "paper":    paper_num,
                "question": q_key,
                "concept":  concept,
                "correct":  correct,
                "mistake":  mistake,
            })

    if not rows:
        return pd.DataFrame(columns=["paper","question","concept","correct","mistake"])
    return pd.DataFrame(rows)


def concept_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    grouped = df.groupby("concept").agg(
        total=("correct", "count"),
        errors=("correct", lambda x: (x == False).sum()),
    ).reset_index()

    grouped["error_rate"] = (grouped["errors"] / grouped["total"] * 100).round(1)

    top_mistake = (
        df[df["correct"] == False]
        .groupby("concept")["mistake"]
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else "—")
        .reset_index()
        .rename(columns={"mistake": "top_mistake"})
    )

    grouped = grouped.merge(top_mistake, on="concept", how="left")
    grouped["top_mistake"] = grouped["top_mistake"].fillna("—")

    return grouped.sort_values("error_rate", ascending=False).reset_index(drop=True)


def bar_chart(summary_df: pd.DataFrame) -> go.Figure:
    df = summary_df.sort_values("error_rate")
    colors = [
        "#f87171" if r >= 60 else "#fb923c" if r >= 30 else "#4ade80"
        for r in df["error_rate"]
    ]
    fig = go.Figure(go.Bar(
        x=df["error_rate"],
        y=df["concept"],
        orientation="h",
        marker_color=colors,
        text=df["error_rate"].astype(str) + "%",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Error rate: %{x}%<extra></extra>",
    ))
    fig.update_layout(
        title="Concept Error Rate across All Papers",
        xaxis_title="% of papers with errors",
        xaxis=dict(range=[0, 115]),
        yaxis_title="",
        height=max(320, 65 * len(df)),
        margin=dict(l=20, r=60, t=50, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    return fig


def mistake_chart(df: pd.DataFrame) -> go.Figure | None:
    errors = df[df["correct"] == False]
    if errors.empty:
        return None
    counts = errors["mistake"].value_counts().reset_index()
    counts.columns = ["mistake", "count"]
    fig = px.pie(
        counts, names="mistake", values="count",
        hole=0.45, title="Common Mistake Types",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=50,b=10))
    return fig


def question_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(
        index="paper", columns="question",
        values="correct", aggfunc="first",
    ).fillna(False)
    z = pivot.values.astype(int)
    fig = go.Figure(go.Heatmap(
        z=z,
        x=pivot.columns.tolist(),
        y=[f"Paper {p}" for p in pivot.index.tolist()],
        colorscale=[[0, "#f87171"], [1, "#4ade80"]],
        zmin=0, zmax=1, showscale=False,
        hovertemplate="Paper %{y} | %{x}<br>%{customdata}<extra></extra>",
        customdata=[["Correct" if v else "Incorrect" for v in row] for row in z],
    ))
    fig.update_layout(
        title="Paper × Question Correctness",
        xaxis_title="Question", yaxis_title="",
        height=max(300, 60 * len(pivot)),
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def class_stats(df: pd.DataFrame) -> dict:
    total  = len(df)
    errors = (df["correct"] == False).sum()
    return {
        "papers":       df["paper"].nunique(),
        "questions":    df["question"].nunique(),
        "concepts":     df["concept"].nunique(),
        "error_rate":   round(errors / total * 100, 1) if total else 0,
        "correct_rate": round((total - errors) / total * 100, 1) if total else 0,
    }
