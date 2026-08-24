from app.retrieval.vector_store import (
    semantic_search,
)


def retrieve_jobs(
    query: str,
    limit: int = 20,
    source: str | None = None,
    location: str | None = None,
):
    """
    Retrieve jobs from Qdrant using semantic similarity.

    Supports:

    - query
    - source
    - location
    """

    if not query or not query.strip():
        return []

    results = semantic_search(
        query=query.strip(),
        limit=limit,
        source=source,
        location=location,
    )

    jobs = []

    for result in results:

        payload = result.payload or {}

        jobs.append(
            {
                "id": payload.get(
                    "job_id"
                ),

                "source_job_id": payload.get(
                    "source_job_id"
                ),

                "source": payload.get(
                    "source"
                ),

                "title": payload.get(
                    "title"
                ),

                "company": payload.get(
                    "company"
                ),

                "domain": payload.get(
                    "domain"
                ),

                "skills": payload.get(
                    "skills",
                    [],
                ),

                "roles": payload.get(
                    "roles",
                    [],
                ),

                "location": payload.get(
                    "location"
                ),

                "location_type": payload.get(
                    "location_type",
                    [],
                ),

                "employment_type": payload.get(
                    "employment_type"
                ),

                "schedule_type": payload.get(
                    "schedule_type"
                ),

                "min_experience": payload.get(
                    "min_experience"
                ),

                "max_experience": payload.get(
                    "max_experience"
                ),

                "min_salary": payload.get(
                    "min_salary"
                ),

                "max_salary": payload.get(
                    "max_salary"
                ),

                "similarity_score": result.score,
            }
        )

    return jobs