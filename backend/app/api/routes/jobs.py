from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.job import Job
from backend.app.schemas.job import (
    JobListResponse,
    JobResponse,
)

from backend.app.retrieval.retriever import retrieve_jobs
from backend.app.retrieval.ranking import rank_jobs


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)


# ============================================================
# STANDARD SEARCH + FILTERS
# ============================================================

@router.get(
    "",
    response_model=JobListResponse,
)
def search_jobs(
    q: str | None = Query(
        default=None,
        description="Search by job title, company, description or domain",
    ),

    source: str | None = Query(
        default=None,
        description="Filter jobs by source platform",
    ),

    location: str | None = Query(
        default=None,
        description="Filter by location",
    ),

    employment_type: str | None = Query(
        default=None,
        description="Filter by employment type",
    ),

    domain: str | None = Query(
        default=None,
        description="Filter by job domain",
    ),

    skill: str | None = Query(
        default=None,
        description="Filter by skill",
    ),

    min_experience: int | None = Query(
        default=None,
        ge=0,
        description="Minimum required experience",
    ),

    max_experience: int | None = Query(
        default=None,
        ge=0,
        description="Maximum required experience",
    ),

    location_type: str | None = Query(
        default=None,
        description="Remote, Hybrid or Onsite",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(get_db),
):
    """
    Search and filter jobs using PostgreSQL.
    """

    query = db.query(Job)


    # ========================================================
    # TEXT SEARCH
    # ========================================================

    if q:

        search_term = f"%{q.strip()}%"

        query = query.filter(
            or_(
                Job.title.ilike(search_term),
                Job.company.ilike(search_term),
                Job.description.ilike(search_term),
                Job.domain.ilike(search_term),
            )
        )


    # ========================================================
    # JOB SOURCE
    # ========================================================

    if source:

        query = query.filter(
            Job.source.ilike(
                f"%{source.strip()}%"
            )
        )


    # ========================================================
    # LOCATION
    # ========================================================

    if location:

        query = query.filter(
            Job.location.ilike(
                f"%{location.strip()}%"
            )
        )


    # ========================================================
    # EMPLOYMENT TYPE
    # ========================================================

    if employment_type:

        query = query.filter(
            Job.employment_type.ilike(
                employment_type.strip()
            )
        )


    # ========================================================
    # DOMAIN
    # ========================================================

    if domain:

        query = query.filter(
            Job.domain.ilike(
                domain.strip()
            )
        )


    # ========================================================
    # SKILL
    # ========================================================

    if skill:

        query = query.filter(
            Job.skills.any(
                skill.strip()
            )
        )


    # ========================================================
    # LOCATION TYPE
    # ========================================================

    if location_type:

        query = query.filter(
            Job.location_type.any(
                location_type.strip()
            )
        )


    # ========================================================
    # EXPERIENCE
    # ========================================================

    if min_experience is not None:

        query = query.filter(
            or_(
                Job.max_experience.is_(None),
                Job.max_experience >= min_experience,
            )
        )


    if max_experience is not None:

        query = query.filter(
            or_(
                Job.min_experience.is_(None),
                Job.min_experience <= max_experience,
            )
        )


    # ========================================================
    # TOTAL COUNT
    # ========================================================

    total = query.with_entities(
        func.count(Job.id)
    ).scalar()


    # ========================================================
    # PAGINATION
    # ========================================================

    jobs = (
        query
        .order_by(
            Job.posted_at.desc().nullslast(),
            Job.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return JobListResponse(
        total=total or 0,
        limit=limit,
        offset=offset,
        jobs=jobs,
    )


# ============================================================
# AI SEMANTIC SEARCH
# ============================================================

@router.get(
    "/semantic-search",
)
def semantic_job_search(

    q: str = Query(
        ...,
        min_length=2,
        description="Natural language job search query",
    ),

    source: str | None = Query(
        default=None,
        description="Filter jobs by source platform",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=50,
        description="Number of final results",
    ),

    skill: str | None = Query(
        default=None,
        description="Optional skill filter",
    ),

    location: str | None = Query(
        default=None,
        description="Optional location filter",
    ),

    experience: int | None = Query(
        default=None,
        ge=0,
        description="User experience in years",
    ),
):
    """
    AI-powered semantic job search.

    Pipeline:

        1. Create query embedding.
        2. Retrieve semantic candidates from Qdrant.
        3. Apply source filtering INSIDE Qdrant.
        4. Apply location filter.
        5. Apply skill filter.
        6. Apply experience filter.
        7. Rank remaining jobs.
        8. Return final results.
    """


    # ========================================================
    # NORMALIZE SOURCE
    # ========================================================

    requested_source = None

    if source and source.strip():

        cleaned_source = source.strip()

        if cleaned_source.lower() != "all sources":
            requested_source = cleaned_source


    # ========================================================
    # RETRIEVE SEMANTIC CANDIDATES
    # ========================================================

    # IMPORTANT:
    #
    # When a source is selected, we PASS source directly
    # into retrieve_jobs().
    #
    # This causes Qdrant to search only inside that source.
    #
    # Previously source was NOT passed here, meaning Qdrant
    # searched all platforms first and the backend tried to
    # filter Naukri/Indeed afterwards.
    #
    # That could produce zero results even though valid
    # Naukri/Indeed jobs existed.

    if requested_source:

        retrieval_limit = min(
            max(limit * 25, 200),
            500,
        )

    elif location or skill or experience is not None:

        retrieval_limit = min(
            max(limit * 25, 200),
            500,
        )

    else:

        retrieval_limit = min(
            max(limit * 5, 100),
            200,
        )


    jobs = retrieve_jobs(
        query=q,
        limit=retrieval_limit,
        source=requested_source,
    )


    # ========================================================
    # SAFETY SOURCE FILTER
    # ========================================================

    # Qdrant already filters the source.
    #
    # We keep this small safety check so that even if the
    # vector store implementation changes later, the API
    # still respects the requested source.

    if requested_source:

        requested_source_lower = (
            requested_source
            .strip()
            .lower()
        )

        filtered_jobs = []

        for job in jobs:

            job_source = (
                job.get("source")
                or ""
            ).strip().lower()

            if requested_source_lower in job_source:

                filtered_jobs.append(job)

        jobs = filtered_jobs


    # ========================================================
    # FILTER BY LOCATION
    # ========================================================

    if location and location.strip():

        requested_location = (
            location
            .strip()
            .lower()
        )


        # ----------------------------------------------------
        # LOCATION ALIASES
        # ----------------------------------------------------

        location_aliases = {

            "bengaluru": [
                "bengaluru",
                "bangalore",
            ],

            "bangalore": [
                "bengaluru",
                "bangalore",
            ],

            "mumbai": [
                "mumbai",
                "bombay",
            ],

            "chennai": [
                "chennai",
                "madras",
            ],

            "kolkata": [
                "kolkata",
                "calcutta",
            ],

            "delhi": [
                "delhi",
                "new delhi",
            ],

            "new delhi": [
                "delhi",
                "new delhi",
            ],

            "hyderabad": [
                "hyderabad",
            ],

            "pune": [
                "pune",
            ],

            "gurgaon": [
                "gurgaon",
                "gurugram",
            ],

            "gurugram": [
                "gurgaon",
                "gurugram",
            ],

            "noida": [
                "noida",
            ],
        }


        location_terms = location_aliases.get(
            requested_location,
            [requested_location],
        )


        filtered_jobs = []


        for job in jobs:

            job_location = (
                job.get("location")
                or ""
            ).strip().lower()


            location_matches = any(
                term in job_location
                for term in location_terms
            )


            if location_matches:

                filtered_jobs.append(job)


        jobs = filtered_jobs


    # ========================================================
    # FILTER BY SKILL
    # ========================================================

    if skill and skill.strip():

        requested_skill = (
            skill
            .strip()
            .lower()
        )


        filtered_jobs = []


        for job in jobs:

            job_skills = (
                job.get("skills")
                or []
            )


            if isinstance(
                job_skills,
                str,
            ):

                job_skills = [
                    job_skills
                ]


            skill_matches = any(
                requested_skill
                in str(job_skill).lower()
                for job_skill in job_skills
            )


            if skill_matches:

                filtered_jobs.append(job)


        jobs = filtered_jobs


    # ========================================================
    # FILTER BY EXPERIENCE
    # ========================================================

    if experience is not None:

        filtered_jobs = []


        for job in jobs:

            min_exp = job.get(
                "min_experience"
            )

            max_exp = job.get(
                "max_experience"
            )


            # ------------------------------------------------
            # If experience is unavailable,
            # don't reject the job.
            # ------------------------------------------------

            if (
                min_exp is None
                and max_exp is None
            ):

                filtered_jobs.append(job)

                continue


            # ------------------------------------------------
            # Minimum experience
            # ------------------------------------------------

            if min_exp is not None:

                if experience < min_exp:

                    continue


            # ------------------------------------------------
            # Maximum experience
            # ------------------------------------------------

            if max_exp is not None:

                if experience > max_exp:

                    continue


            filtered_jobs.append(job)


        jobs = filtered_jobs


    # ========================================================
    # PREPARE RANKING SIGNALS
    # ========================================================

    requested_skills = []


    if skill:

        requested_skills = [
            skill.strip()
        ]


    # ========================================================
    # RANK RESULTS
    # ========================================================

    ranked_jobs = rank_jobs(

        jobs=jobs,

        requested_skills=requested_skills,

        requested_roles=[],

        requested_location=location,

        requested_experience=experience,
    )


    # ========================================================
    # FINAL LIMIT
    # ========================================================

    ranked_jobs = ranked_jobs[:limit]


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {

        "query": q,

        "source": source,

        "location": location,

        "skill": skill,

        "experience": experience,

        "total": len(ranked_jobs),

        "results": ranked_jobs,
    }


# ============================================================
# GET SINGLE JOB
# ============================================================

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(

    job_id: int,

    db: Session = Depends(get_db),
):

    """
    Get a single job by database ID.
    """

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id
        )
        .first()
    )


    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )


    return job