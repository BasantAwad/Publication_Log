# core/nlp.py

import pandas as pd
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

from projects.models import Project, Publication, MatchRequest

# Function to clean a text string by removing punctuation, digits, extra spaces, and converting to lowercase
def clean_text(text):
    if pd.isna(text):         # If the text is NaN (missing), return empty string
        return ""
    text = text.lower()       # Convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\d+", "", text)      # Remove digits
    text = re.sub(r"\s+", " ", text).strip()   # Replace multiple spaces with single space
    return text

# Function to normalize a list of author names
def normalize_authors(authors_list):
    if isinstance(authors_list, float) or pd.isna(authors_list):
        return []
    if isinstance(authors_list, str):
        try:
            authors_list = eval(authors_list)
        except:
            authors_list = []
    if not isinstance(authors_list, (list, tuple)):
        return []
    return [clean_text(a) for a in authors_list]

# Main function to match projects and publications (papers) using NLP similarity and shared authors
def match_projects_and_papers(publication=None, user=None, threshold=0.65, top_k=3):
    # Fetch all projects and papers from the database
    projects = Project.objects.all().values("id", "title", "team", "created")
    papers = Publication.objects.all().values("id", "title", "abstract", "collaborators", "uploaded_at")

    if not projects or not papers:
        return

    # Convert projects and papers to pandas DataFrames for easier manipulation
    projects_df = pd.DataFrame(projects)
    papers_df = pd.DataFrame(papers)

    # Clean and preprocess project fields
    projects_df["clean_title"] = projects_df["title"].apply(clean_text)
    projects_df["normalized_authors"] = projects_df["team"].apply(normalize_authors)
    projects_df["created"] = pd.to_datetime(projects_df["created"])

    # Clean and preprocess paper fields
    papers_df["clean_title"] = papers_df["title"].apply(clean_text)
    papers_df["clean_abstract"] = papers_df["abstract"].apply(clean_text)
    papers_df["normalized_authors"] = papers_df["collaborators"].apply(normalize_authors)
    papers_df["published_date"] = pd.to_datetime(papers_df["uploaded_at"])
    papers_df["combined_text"] = papers_df["clean_title"] + ". " + papers_df["clean_abstract"]

    # Load a pre-trained NLP sentence transformer model for semantic similarity
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    # Encode project titles and paper combined texts into embedding vectors
    project_embeddings = model.encode(projects_df["clean_title"].tolist(), convert_to_tensor=True)
    paper_embeddings = model.encode(papers_df["combined_text"].tolist(), convert_to_tensor=True)

    matched_papers = []  # List to store details of matched papers

    # For each project, find top_k most similar papers
    for i in range(len(projects_df)):
        project = projects_df.iloc[i]
        similarities = util.cos_sim(project_embeddings[i], paper_embeddings)[0]  # Cosine similarity vector
        top_indices = similarities.argsort(descending=True)[:top_k]  # Indices of top_k similar papers

        for idx in top_indices:
            paper = papers_df.iloc[idx.item()]
            paper_date = paper["published_date"]
            project_date = project["created"]

            # Only match papers published after the project's acceptance date
            if paper_date > project_date:
                # Find shared authors between project and paper
                shared_authors = set(project["normalized_authors"]) & set(paper["normalized_authors"])
                if shared_authors:
                    similarity = similarities[idx].item()
                    # Only save matches above the similarity threshold
                    if similarity >= threshold:
                        # Create a MatchRequest record in the database
                        MatchRequest.objects.create(
                            project_id=project["id"],
                            publication_id=paper["id"],
                            match_title=paper["title"],
                            match_score=round(similarity, 4),
                            match_authors=", ".join(shared_authors),
                            approved=None  # Not reviewed yet
                        )

                        # Add match details to the results list
                        matched_papers.append({
                            "project_title": project["title"],
                            "paper_title": paper["title"],
                            "similarity": round(similarity, 4),
                            "shared_authors": list(shared_authors)
                        })
                    break

    # Save matched results to a CSV file for inspection
    matched_df = pd.DataFrame(matched_papers)
    matched_df.to_csv("matched_projects_papers.csv", index=False)
    return matched_df