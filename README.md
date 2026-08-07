# employee-directory-api

FastAPI microservice that owns employee directory data and company announcements.

## Why a separate repository?

Employee-directory changes can be versioned, tested, built and deployed without redeploying the workflow service or React UI.

## Local run

Start PostgreSQL:

```bash
docker run --name employee-postgres \
  -e POSTGRES_DB=employee_ops \
  -e POSTGRES_USER=portaladmin \
  -e POSTGRES_PASSWORD=change-me \
  -p 5432:5432 \
  -d postgres:16
```

Then:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

Open:
- http://localhost:8001/docs
- http://localhost:8001/api/directory/health

## Production

The ECS task receives:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` as normal environment variables.
- `DB_PASSWORD` and `INTERNAL_API_KEY` from SSM Parameter Store `SecureString`.

The application never contains production secret values.

GitHub repository variable:
- `AWS_ROLE_ARN` from Terraform output `directory_deploy_role_arn`.
