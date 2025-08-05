# core/nlp.py

import pandas as pd
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer, util


def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_authors(authors_str):
    authors = eval(authors_str) if isinstance(authors_str, str) else authors_str
    return [clean_text(name) for name in authors]


def match_projects_and_papers(projects_csv_path, papers_csv_path, threshold=0.65, top_k=3):
    """
    Load two CSV files (projects + papers), match them using semantic similarity + author filter,
    and return a DataFrame with the best matches.

    Arguments:
    - projects_csv_path: path to projects.csv
    - papers_csv_path: path to papers.csv
    - threshold: minimum similarity score to consider a match
    - top_k: how many top papers to check per project

    Returns:
    - pandas DataFrame with the matched records
    """

    projects_df = pd.read_csv(projects_csv_path)
    papers_df = pd.read_csv(papers_csv_path)

    # clean + normalize
    projects_df["clean_title"] = projects_df["title"].apply(clean_text)
    projects_df["normalized_authors"] = projects_df["authors"].apply(normalize_authors)
    projects_df["acceptance_date"] = pd.to_datetime(projects_df["acceptance_date"])

    papers_df["clean_title"] = papers_df["title"].apply(clean_text)
    papers_df["clean_abstract"] = papers_df["abstract"].apply(clean_text)
    papers_df["normalized_authors"] = papers_df["authors"].apply(normalize_authors)
    papers_df["published_date"] = pd.to_datetime(papers_df["published_date"])
    papers_df["combined_text"] = papers_df["clean_title"] + ". " + papers_df["clean_abstract"]

    # load model
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    # embed
    project_embeddings = model.encode(projects_df["clean_title"].tolist(), convert_to_tensor=True)
    paper_embeddings = model.encode(papers_df["combined_text"].tolist(), convert_to_tensor=True)

    matched_papers = []

    for i in range(len(projects_df)):
        project = projects_df.iloc[i]
        similarities = util.cos_sim(project_embeddings[i], paper_embeddings)[0]
        top_indices = similarities.argsort(descending=True)[:top_k]

        for idx in top_indices:
            paper = papers_df.iloc[idx.item()]
            paper_date = paper["published_date"]
            project_date = project["acceptance_date"]

            if paper_date > project_date:
                # check authors overlap
                shared_authors = set(project["normalized_authors"]) & set(paper["normalized_authors"])
                if shared_authors:
                    similarity = similarities[idx].item()
                    if similarity >= threshold:
                        matched_papers.append({
                            "project_title": project["title"],
                            "paper_title": paper["title"],
                            "similarity": round(similarity, 4),
                            "project_date": project_date.date(),
                            "paper_date": paper_date.date(),
                            "shared_authors": list(shared_authors)
                        })
                    break  # only match the first valid top paper

    matched_df = pd.DataFrame(matched_papers)
    matched_df.to_csv("matched_projects_papers.csv", index=False)
    return matched_df
