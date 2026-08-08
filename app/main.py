from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import SessionLocal, get_session, initialize_database
from .models import Announcement, Employee
from .schemas import AnnouncementCreate, AnnouncementOut, EmployeeCreate, EmployeeOut
from .auth import CurrentUser, get_current_user, require_roles

async def seed() -> None:
    async with SessionLocal() as session:
        count = await session.scalar(select(func.count(Employee.id)))
        if count == 0:
            session.add_all([
                Employee(
                    employee_number="EMP-1001",
                    first_name="Aarav",
                    last_name="Sharma",
                    email="aarav.sharma@example.com",
                    job_title="Software Engineer",
                    department="Engineering",
                    manager_id=2,
                    location="New York",
                ),
                Employee(
                    employee_number="EMP-1002",
                    first_name="Maya",
                    last_name="Patel",
                    email="maya.patel@example.com",
                    job_title="Engineering Manager",
                    department="Engineering",
                    manager_id=None,
                    location="New York",
                ),
            ])
            session.add(
                Announcement(
                    title="Welcome to Employee Operations",
                    message="Use this portal for directory information and employee workflows.",
                )
            )
            await session.commit()

@asynccontextmanager
async def lifespan(_: FastAPI):
    if not settings.skip_db_init:
        await initialize_database()
        await seed()
    yield

app = FastAPI(title="Employee Directory API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/directory/health")
async def health():
    return {
        "service": "employee-directory-api",
        "status": "healthy",
    }
@app.get(
    "/api/directory/employees",
    response_model=list[EmployeeOut],
)
async def list_employees(
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
):
    result = await session.scalars(
        select(Employee).order_by(Employee.id)
    )
    return list(result)

@app.get(
    "/api/directory/employees/{employee_id}",
    response_model=EmployeeOut,
)
async def get_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
):
    employee = await session.get(Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return employee

@app.post(
    "/api/directory/employees",
    response_model=EmployeeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    payload: EmployeeCreate,
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(require_roles("ADMIN")),
):
    employee = Employee(**payload.model_dump())

    session.add(employee)

    await session.commit()
    await session.refresh(employee)

    return employee

@app.get(
    "/api/directory/announcements",
    response_model=list[AnnouncementOut],
)
async def list_announcements(
    session: AsyncSession = Depends(get_session),
    _: CurrentUser = Depends(get_current_user),
):
    result = await session.scalars(
        select(Announcement)
        .order_by(Announcement.created_at.desc())
    )

    return list(result)

@app.post("/api/directory/internal/announcements", response_model=AnnouncementOut)
async def create_announcement(
    payload: AnnouncementCreate,
    x_internal_api_key: str = Header(alias="X-Internal-API-Key"),
    session: AsyncSession = Depends(get_session),
):
    if x_internal_api_key != settings.internal_api_key:
        raise HTTPException(status_code=401, detail="Invalid internal API key")

    announcement = Announcement(**payload.model_dump())
    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement
