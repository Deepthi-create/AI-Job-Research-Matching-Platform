from pathlib import Path
import hashlib
import math
import re
import os

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / "backend" / ".env")

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(PROJECT_ROOT))


# ============================================================
# QDRANT CONFIGURATION
# ============================================================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "jobs"

# Lightweight local embedding size.
VECTOR_SIZE = 384


# ============================================================
# QDRANT CLIENT
# ============================================================

_client = None


def get_qdrant_client():
    """
    Create and reuse a Qdrant Cloud client.
    """

    global _client

    if _client is None:

        if not QDRANT_URL:
            raise ValueError(
                "QDRANT_URL environment variable is not set."
            )

        if not QDRANT_API_KEY:
            raise ValueError(
                "QDRANT_API_KEY environment variable is not set."
            )

        _client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

    return _client


# ============================================================
# COLLECTION
# ============================================================

def create_collection():
    """
    Create the jobs collection if it does not already exist.
    """

    client = get_qdrant_client()

    existing_collections = client.get_collections()

    collection_names = {
        collection.name
        for collection in existing_collections.collections
    }

    if COLLECTION_NAME in collection_names:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(
        f"Created Qdrant collection: "
        f"{COLLECTION_NAME}"
    )


# ============================================================
# LIGHTWEIGHT TEXT TOKENIZATION
# ============================================================

def tokenize(text):
    """
    Convert text into normalized tokens.

    This lightweight tokenizer is used instead of
    sentence-transformers.
    """

    if not text:
        return []

    text = str(text).lower()

    return re.findall(
        r"[a-zA-Z0-9+#.-]+",
        text,
    )


# ============================================================
# LIGHTWEIGHT EMBEDDING
# ============================================================

def create_embedding(text):
    """
    Create a deterministic lightweight text embedding.

    Uses hashing instead of a neural embedding model.
    """

    vector = [0.0] * VECTOR_SIZE

    tokens = tokenize(text)

    if not tokens:
        return vector

    for token in tokens:

        digest = hashlib.sha256(
            token.encode("utf-8")
        ).digest()

        for i in range(4):

            start = i * 4

            value = int.from_bytes(
                digest[start:start + 4],
                byteorder="little",
                signed=False,
            )

            index = value % VECTOR_SIZE

            sign = (
                1.0
                if value % 2 == 0
                else -1.0
            )

            vector[index] += sign

    # Normalize vector.
    magnitude = math.sqrt(
        sum(
            value * value
            for value in vector
        )
    )

    if magnitude == 0:
        return vector

    return [
        value / magnitude
        for value in vector
    ]


# ============================================================
# BATCH EMBEDDINGS
# ============================================================

def create_embeddings(
    texts,
    batch_size=64,
):
    """
    Generate lightweight embeddings for multiple texts.

    batch_size is kept for API compatibility.
    """

    if not texts:
        return []

    return [
        create_embedding(text)
        for text in texts
    ]


# ============================================================
# JOB TEXT
# ============================================================

def build_job_text(job):
    """
    Convert a job record into meaningful searchable text.
    """

    roles = job.roles or []
    skills = job.skills or []

    return " ".join(
        [
            f"Job Title: {job.title or ''}",
            f"Company: {job.company or ''}",
            f"Source: {job.source or ''}",
            f"Domain: {job.domain or ''}",
            f"Roles: {', '.join(roles)}",
            f"Skills: {', '.join(skills)}",
            f"Location: {job.location or ''}",
            f"Employment Type: {job.employment_type or ''}",
            f"Schedule Type: {job.schedule_type or ''}",
            (
                "Experience: "
                f"{job.min_experience or ''} "
                "to "
                f"{job.max_experience or ''} years"
            ),
            f"Description: {job.description or ''}",
        ]
    )


# ============================================================
# BATCH JOB TEXTS
# ============================================================

def build_job_texts(jobs):
    """
    Convert multiple jobs into embedding-ready text.
    """

    return [
        build_job_text(job)
        for job in jobs
    ]


# ============================================================
# SOURCE NORMALIZATION
# ============================================================

def normalize_source_value(source):
    """
    Normalize source values before storing/filtering.
    """

    if not source:
        return ""

    source = str(source).strip().lower()

    aliases = {
        "linkedin": "linkedin",
        "linkedin jobs": "linkedin",

        "naukri": "naukri",
        "naukri.com": "naukri",

        "indeed": "indeed",
        "indeed.com": "indeed",

        "internshala": "internshala",
        "internshala.com": "internshala",

        "glassdoor": "glassdoor",

        "bebee": "bebee",

        "grabjobs": "grabjobs",
    }

    return aliases.get(
        source,
        source,
    )


# ============================================================
# LOCATION NORMALIZATION
# ============================================================

def normalize_location_value(location):
    """
    Normalize a location string for generic comparison.

    No cities, states, or countries are hard-coded.
    """

    if not location:
        return ""

    location = str(location).strip().lower()

    if not location:
        return ""

    # Normalize separators
    location = location.replace(",", " ")
    location = location.replace("/", " ")
    location = location.replace("-", " ")

    # Remove extra whitespace
    location = re.sub(
        r"\s+",
        " ",
        location,
    ).strip()

    return location


def location_matches(
    requested_location,
    job_location,
):
    """
    Generic location matching.

    The user can enter any location.

    Matching works when the requested location is
    contained within the stored job location.

    No city names are hard-coded.
    """

    requested = normalize_location_value(
        requested_location
    )

    actual = normalize_location_value(
        job_location
    )

    # No location filter
    if not requested:
        return True

    # Job has no location
    if not actual:
        return False

    # Exact match
    if requested == actual:
        return True

    # Requested location appears inside job location
    requested_words = requested.split()
    actual_words = actual.split()

    if all(
        word in actual_words
        for word in requested_words
    ):
        return True

    return False


# ============================================================
# JOB PAYLOAD
# ============================================================

def build_job_payload(job):
    """
    Build metadata stored alongside the vector.

    Source is normalized before storing.
    """

    source = normalize_source_value(
        job.source
    )

    return {
        "job_id": job.id,

        "source_job_id": job.source_job_id,

        "source": source,

        "title": job.title,

        "company": job.company,

        "domain": job.domain,

        "skills": job.skills or [],

        "roles": job.roles or [],

        "location": job.location,

        "location_normalized": normalize_location_value(
            job.location
        ),

        "location_type": job.location_type or [],

        "employment_type": job.employment_type,

        "schedule_type": job.schedule_type,

        "min_experience": job.min_experience,

        "max_experience": job.max_experience,

        "min_salary": job.min_salary,

        "max_salary": job.max_salary,
    }


# ============================================================
# BATCH UPSERT
# ============================================================

def upsert_jobs(
    jobs,
    embedding_batch_size=64,
):
    """
    Generate embeddings for a batch of jobs
    and store them in Qdrant.
    """

    if not jobs:
        return 0

    client = get_qdrant_client()

    create_collection()

    texts = build_job_texts(jobs)

    embeddings = create_embeddings(
        texts,
        batch_size=embedding_batch_size,
    )

    points = []

    for job, embedding in zip(
        jobs,
        embeddings,
    ):

        points.append(
            PointStruct(
                id=job.id,
                vector=embedding,
                payload=build_job_payload(job),
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)


# ============================================================
# SINGLE JOB UPSERT
# ============================================================

def upsert_job(job):
    """
    Convenience function for indexing one job.
    """

    return upsert_jobs(
        [job]
    )


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def semantic_search(
    query,
    limit=10,
    source=None,
    location=None,
):
    """
    Search Qdrant using lightweight vector similarity.

    Supports:

        query
        source
        location

    Source filtering is performed inside Qdrant.

    Location filtering is applied after retrieving a large
    enough set of semantic candidates so that valid jobs are
    not missed simply because they were not in the first
    few semantic results.
    """

    # --------------------------------------------------------
    # VALIDATE QUERY
    # --------------------------------------------------------

    if not query or not query.strip():
        return []

    client = get_qdrant_client()

    # --------------------------------------------------------
    # CREATE QUERY VECTOR
    # --------------------------------------------------------

    query_vector = create_embedding(
        query.strip()
    )

    # --------------------------------------------------------
    # SOURCE FILTER
    # --------------------------------------------------------

    query_filter = None

    if source and source.strip():

        cleaned_source = (
            source.strip().lower()
        )

        # "All Sources" means no source filtering.
        if cleaned_source != "all sources":

            normalized_source = normalize_source_value(
                cleaned_source
            )

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(
                            value=normalized_source
                        ),
                    )
                ]
            )

    # --------------------------------------------------------
    # DETERMINE CANDIDATE LIMIT
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # If location is selected, we must retrieve many more
    # semantic candidates before applying the location filter.
    #
    # Example:
    #
    # Python developer + Indeed + Bengaluru
    #
    # The top semantic result may be Noida.
    #
    # Bengaluru jobs may appear much lower in the semantic
    # ranking.
    #
    # Therefore we retrieve up to 5000 candidates first.
    # --------------------------------------------------------

    if location and location.strip():

        candidate_limit = max(
            limit * 100,
            5000,
        )

    else:

        candidate_limit = limit

    # --------------------------------------------------------
    # SEMANTIC SEARCH
    # --------------------------------------------------------

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=candidate_limit,
        with_payload=True,
    ).points

    # --------------------------------------------------------
    # LOCATION FILTER
    # --------------------------------------------------------

    if location and location.strip():

        candidate_limit = max(
            limit * 100,
            5000,
        )

    else:

        candidate_limit = limit

    if location and location.strip():

        filtered_results = []

        requested_location = (
            location.strip()
        )

        for result in results:

            payload = result.payload or {}

            job_location = payload.get(
                "location"
            )

            if location_matches(
                requested_location,
                job_location,
            ):

                filtered_results.append(
                    result
                )

                # We only need the requested number
                # of final results.
                if len(filtered_results) >= limit:
                    break

        results = filtered_results

    else:

        results = results[:limit]

    return results