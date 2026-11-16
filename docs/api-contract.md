# DeploySense API Contract

Base URL during local development: `http://127.0.0.1:8000`

## Health

### `GET /health`

Checks that the API can reach PostgreSQL.

Successful response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

## Repositories

### `POST /api/repositories`

Creates a repository record.

Request:

```json
{
  "full_name": "owner/project"
}
```

Successful response: `201 Created`, with the repository's `id` and `full_name`.

### `GET /api/repositories`

Returns the repository list.

### `GET /api/repositories/{repository_id}`

Returns one repository. Returns `404` if it does not exist.

### `PATCH /api/repositories/{repository_id}`

Changes a repository name.

Request:

```json
{
  "full_name": "owner/renamed-project"
}
```

Returns `404` if the repository does not exist and `409` if the name is already used.

### `DELETE /api/repositories/{repository_id}`

Deletes the repository and its linked workflow runs. Returns `204 No Content`, or `404` if it does not exist.

## Workflow runs

### `POST /api/runs`

Creates a workflow run. `repository_id` must refer to an existing repository.

Request:

```json
{
  "repository_id": 1,
  "github_id": "demo-run-001",
  "workflow_name": "CI",
  "branch": "main",
  "commit_sha": null,
  "status": "completed",
  "conclusion": "failure",
  "started_at": "2026-11-16T10:00:00Z",
  "duration_seconds": 93,
  "html_url": "https://github.com/owner/project/actions/runs/1"
}
```

Returns `404` if the repository does not exist or `409` if that GitHub run already exists for the repository.

### `GET /api/runs`

Returns workflow runs, newest first.

Query parameters:

- `page`: page number, starting at 1; defaults to 1.
- `page_size`: results per page, from 1 to 100; defaults to 20.
- `repository_id`: optional filter for one repository.

The response includes `items`, `total`, `page`, and `page_size`. Each item includes its repository.

### `GET /api/runs/{run_id}`

Returns one workflow run, including its repository. Returns `404` if it does not exist.

### `PATCH /api/runs/{run_id}`

Updates one or more of these fields: `status`, `conclusion`, `duration_seconds`, `html_url`.

Example request:

```json
{
  "status": "completed",
  "conclusion": "failure",
  "duration_seconds": 96
}
```

Returns `404` if the run does not exist.

### `DELETE /api/runs/{run_id}`

Deletes one workflow run. Returns `204 No Content`, or `404` if it does not exist.

## Common error responses

- `404 Not Found`: requested repository or run does not exist.
- `409 Conflict`: duplicate repository name or duplicate GitHub run.
- `422 Unprocessable Entity`: request data is missing or invalid.
