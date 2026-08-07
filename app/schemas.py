from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class EmployeeCreate(BaseModel):
    employee_number: str
    first_name: str
    last_name: str
    email: EmailStr
    job_title: str
    department: str
    manager_id: int | None = None
    location: str = "Remote"

class EmployeeOut(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str

class AnnouncementCreate(BaseModel):
    title: str
    message: str

class AnnouncementOut(AnnouncementCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
