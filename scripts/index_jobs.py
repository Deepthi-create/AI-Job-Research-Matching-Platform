import sys
from pathlib import Path
from collections import Counter


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from backend.app.core.database import SessionLocal
from backend.app.models.job import Job

from backend.app.retrieval.vector_store import (
    create_collection,
    upsert_jobs,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Number of jobs loaded from PostgreSQL at a time
DB_BATCH_SIZE = 500

# Number of texts embedded together
EMBEDDING_BATCH_SIZE = 64


# ============================================================
# INDEX JOBS
# ============================================================

def index_jobs():

    print("=" * 70)
    print("JOB VECTOR INDEXING")
    print("=" * 70)

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # CREATE QDRANT COLLECTION
        # ----------------------------------------------------

        create_collection()

        print("\nQdrant collection ready.")

        # ----------------------------------------------------
        # COUNT TOTAL JOBS
        # ----------------------------------------------------

        total_jobs = (
            db.query(Job)
            .count()
        )

        print(
            f"Total jobs in PostgreSQL: "
            f"{total_jobs:,}"
        )

        # ----------------------------------------------------
        # SOURCE COUNTS
        # ----------------------------------------------------

        print("\nChecking job sources...")

        source_rows = (
            db.query(Job.source)
            .all()
        )

        source_counter = Counter()

        for row in source_rows:

            source = row[0]

            if source:
                normalized_source = (
                    str(source)
                    .strip()
                    .lower()
                )
            else:
                normalized_source = "unknown"

            source_counter[
                normalized_source
            ] += 1

        print("\nJobs by source:")

        for source, count in sorted(
            source_counter.items()
        ):
            print(
                f"  {source:<20} {count:,}"
            )

        # ----------------------------------------------------
        # COUNTERS
        # ----------------------------------------------------

        indexed = 0
        errors = 0

        # ----------------------------------------------------
        # KEYSET PAGINATION
        # ----------------------------------------------------
        #
        # WHERE id > last_id
        #
        # This avoids OFFSET pagination and is more efficient
        # for large datasets.
        # ----------------------------------------------------

        last_id = 0

        while True:

            # ------------------------------------------------
            # FETCH NEXT BATCH
            # ------------------------------------------------

            jobs = (
                db.query(Job)
                .filter(
                    Job.id > last_id
                )
                .order_by(
                    Job.id
                )
                .limit(
                    DB_BATCH_SIZE
                )
                .all()
            )

            # ------------------------------------------------
            # NO MORE JOBS
            # ------------------------------------------------

            if not jobs:
                break

            first_id = jobs[0].id
            last_batch_id = jobs[-1].id

            print(
                "\nProcessing database IDs "
                f"{first_id:,} - "
                f"{last_batch_id:,}"
            )

            # ------------------------------------------------
            # SHOW SOURCES IN CURRENT BATCH
            # ------------------------------------------------

            batch_sources = Counter()

            for job in jobs:

                if job.source:

                    source = (
                        str(job.source)
                        .strip()
                        .lower()
                    )

                else:

                    source = "unknown"

                batch_sources[source] += 1

            print(
                "Sources in this batch:"
            )

            for source, count in sorted(
                batch_sources.items()
            ):

                print(
                    f"  {source:<20} {count:,}"
                )

            # ------------------------------------------------
            # GENERATE EMBEDDINGS
            # AND UPSERT TO QDRANT
            # ------------------------------------------------

            try:

                count = upsert_jobs(
                    jobs,
                    embedding_batch_size=(
                        EMBEDDING_BATCH_SIZE
                    ),
                )

                indexed += count

                print(
                    f"Indexed: "
                    f"{indexed:,} / "
                    f"{total_jobs:,}"
                )

            except Exception as error:

                print(
                    "\nERROR processing batch:"
                )

                print(error)

                # ------------------------------------------------
                # FALLBACK:
                # PROCESS EACH JOB INDIVIDUALLY
                # ------------------------------------------------

                print(
                    "\nTrying jobs individually..."
                )

                for job in jobs:

                    try:

                        upsert_jobs(
                            [job],
                            embedding_batch_size=1,
                        )

                        indexed += 1

                    except Exception as job_error:

                        errors += 1

                        print(
                            f"\nFailed job ID: "
                            f"{job.id}"
                        )

                        print(
                            f"Title: "
                            f"{job.title}"
                        )

                        print(
                            f"Source: "
                            f"{job.source}"
                        )

                        print(
                            f"Error: "
                            f"{job_error}"
                        )

                print(
                    "\nRecovered from batch failure."
                )

                print(
                    f"Indexed: "
                    f"{indexed:,} / "
                    f"{total_jobs:,}"
                )

            # ------------------------------------------------
            # MOVE TO NEXT BATCH
            # ------------------------------------------------

            last_id = last_batch_id

        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        print("\n" + "=" * 70)
        print("VECTOR INDEXING COMPLETE")
        print("=" * 70)

        print(
            f"Total jobs in PostgreSQL: "
            f"{total_jobs:,}"
        )

        print(
            f"Successfully indexed:     "
            f"{indexed:,}"
        )

        print(
            f"Errors:                    "
            f"{errors:,}"
        )

        # ----------------------------------------------------
        # FINAL SOURCE SUMMARY
        # ----------------------------------------------------

        print("\nSource distribution:")

        for source, count in sorted(
            source_counter.items()
        ):

            print(
                f"  {source:<20} {count:,}"
            )

        print("=" * 70)

        if errors == 0:

            print(
                "\nSUCCESS: All jobs were indexed."
            )

        else:

            print(
                f"\nWARNING: {errors} jobs "
                f"could not be indexed."
            )

    finally:

        db.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    index_jobs()