const API_BASE_URL = "http://127.0.0.1:8000";


// ============================================================
// STANDARD JOB SEARCH
// ============================================================

export async function searchJobs(params = {}) {
  const queryParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      queryParams.append(key, String(value));
    }
  });

  const response = await fetch(
    `${API_BASE_URL}/api/jobs?${queryParams.toString()}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to fetch jobs: ${response.status} ${errorText}`
    );
  }

  return response.json();
}


// ============================================================
// AI SEMANTIC JOB SEARCH
// ============================================================

export async function semanticSearchJobs({
  query,
  source = "",
  skill = "",
  location = "",
  experience = "",
  limit = 20,
}) {
  const queryParams = new URLSearchParams();

  // ----------------------------------------------------------
  // SEARCH QUERY
  // ----------------------------------------------------------

  if (query) {
    queryParams.append(
      "q",
      query.trim()
    );
  }

  // ----------------------------------------------------------
  // RESULT LIMIT
  // ----------------------------------------------------------

  queryParams.append(
    "limit",
    String(limit)
  );

  // ----------------------------------------------------------
  // JOB SOURCE
  // ----------------------------------------------------------

  if (source) {
    queryParams.append(
      "source",
      source.trim()
    );
  }

  // ----------------------------------------------------------
  // SKILL
  // ----------------------------------------------------------

  if (skill) {
    queryParams.append(
      "skill",
      skill.trim()
    );
  }

  // ----------------------------------------------------------
  // LOCATION
  // ----------------------------------------------------------

  if (location) {
    queryParams.append(
      "location",
      location.trim()
    );
  }

  // ----------------------------------------------------------
  // EXPERIENCE
  // ----------------------------------------------------------

  if (
    experience !== "" &&
    experience !== null &&
    experience !== undefined
  ) {
    queryParams.append(
      "experience",
      String(experience)
    );
  }

  // ----------------------------------------------------------
  // API REQUEST
  // ----------------------------------------------------------

  const response = await fetch(
    `${API_BASE_URL}/api/jobs/semantic-search?${queryParams.toString()}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Semantic search failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}


// ============================================================
// AI ASSISTANT SEARCH
// ============================================================

export async function assistantSearch({
  query,
  limit = 10,
}) {
  const queryParams = new URLSearchParams();

  if (query) {
    queryParams.append(
      "q",
      query.trim()
    );
  }

  queryParams.append(
    "limit",
    String(limit)
  );

  const response = await fetch(
    `${API_BASE_URL}/api/assistant?${queryParams.toString()}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Assistant search failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}


// ============================================================
// GET SINGLE JOB
// ============================================================

export async function getJob(jobId) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}`
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Failed to fetch job: ${response.status} ${errorText}`
    );
  }

  return response.json();
}