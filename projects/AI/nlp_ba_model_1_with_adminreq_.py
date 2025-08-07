# core/nlp.py

import pandas as pd
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

from projects.models import Project, Publication, MatchRequest


def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_authors(authors_list):
    if isinstance(authors_list, str):
        try:
            authors_list = eval(authors_list)
        except:
            authors_list = []
    return [clean_text(a) for a in authors_list]


def match_projects_and_papers(publication=None, user=None, threshold=0.65, top_k=3):
    # Fetch data from DB
    projects = Project.objects.all().values("id", "title", "team", "created")
    papers = Publication.objects.all().values("id", "title", "abstract", "collaborators", "uploaded_at")

    if not projects or not papers:
        return

    # Create DataFrames
    projects_df = pd.DataFrame(projects)
    papers_df = pd.DataFrame(papers)

    # clean and preprocess
    projects_df["clean_title"] = projects_df["title"].apply(clean_text)
    projects_df["normalized_authors"] = projects_df["collaborators"].apply(normalize_authors)
    projects_df["created"] = pd.to_datetime(projects_df["created"])

    papers_df["clean_title"] = papers_df["title"].apply(clean_text)
    papers_df["clean_abstract"] = papers_df["abstract"].apply(clean_text)
    papers_df["normalized_authors"] = papers_df["collaborators"].apply(normalize_authors)
    papers_df["published_date"] = pd.to_datetime(papers_df["published_date"])
    papers_df["combined_text"] = papers_df["clean_title"] + ". " + papers_df["clean_abstract"]

    # Load NLP model
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

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
                shared_authors = set(project["normalized_authors"]) & set(paper["normalized_authors"])
                if shared_authors:
                    similarity = similarities[idx].item()
                    if similarity >= threshold:
                        # Save match request to DB
                        MatchRequest.objects.create(
                            project_id=project["id"],
                            publication_id=paper["id"],
                            match_title=paper["title"],
                            match_score=round(similarity, 4),
                            match_authors=", ".join(shared_authors),
                            approved=None  # not reviewed yet
                        )

                        matched_papers.append({
                            "project_title": project["title"],
                            "paper_title": paper["title"],
                            "similarity": round(similarity, 4),
                            "shared_authors": list(shared_authors)
                        })
                    break

    matched_df = pd.DataFrame(matched_papers)
    matched_df.to_csv("matched_projects_papers.csv", index=False)
    return matched_df
