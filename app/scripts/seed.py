
import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from pwdlib import PasswordHash
from sqlalchemy import select

from app.core.enums import (
    ProjectStatus,
    TaskPriority,
    TaskStatus,
    UserRole,
    WorkspaceRole,
)
from app.db.session import AsyncSessionLocal
from app.models.comment import Comment
from app.models.label import Label
from app.models.project import Project
from app.models.task import Task
from app.models.task_label import TaskLabel
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

IDS = {
    "admin": "11111111-1111-4111-8111-111111111111",
    "an": "22222222-2222-4222-8222-222222222222",
    "binh": "33333333-3333-4333-8333-333333333333",
    "workspace": "44444444-4444-4444-8444-444444444444",
    "backend": "55555555-5555-4555-8555-555555555555",
    "frontend": "66666666-6666-4666-8666-666666666666",
}

EMAILS = {
    "admin": "admin@example.com",
    "an": "an@example.com",
    "binh": "binh@example.com",
}


async def seed_data() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as session, session.begin():
        # Check whether seed data already exists
        existing = await session.scalar(
            select(User.id).where(
                User.id == UUID(IDS["admin"])
            )
        )

        if existing is not None:
            print("Seed data already exists. Skipping.")
            return

        # 1. USERS
        password_hasher = PasswordHash.recommended()
        password_hash = password_hasher.hash("TaskHubTest123!")

        admin = User(
            id=UUID(IDS["admin"]),
            email=EMAILS["admin"],
            full_name="Admin TaskHub",
            hashed_password=password_hash,
            role=UserRole.ADMIN,
            is_active=True,
            created_at=now,
        )

        an = User(
            id=UUID(IDS["an"]),
            email=EMAILS["an"],
            full_name="Nguyen Van An",
            hashed_password=password_hash,
            role=UserRole.MEMBER,
            is_active=True,
            created_at=now,
        )

        binh = User(
            id=UUID(IDS["binh"]),
            email=EMAILS["binh"],
            full_name="Tran Thi Binh",
            hashed_password=password_hash,
            role=UserRole.MEMBER,
            is_active=True,
            created_at=now,
        )

        session.add_all([admin, an, binh])
        await session.flush()

        # 2. WORKSPACE
        workspace = Workspace(
            id=UUID(IDS["workspace"]),
            name="Development Team",
            owner_id=admin.id,
            created_at=now,
        )

        session.add(workspace)
        await session.flush()

        # 3. WORKSPACE MEMBERS
        session.add_all(
            [
                WorkspaceMember(
                    workspace_id=workspace.id,
                    user_id=admin.id,
                    role=WorkspaceRole.OWNER,
                ),
                WorkspaceMember(
                    workspace_id=workspace.id,
                    user_id=an.id,
                    role=WorkspaceRole.EDITOR,
                ),
                WorkspaceMember(
                    workspace_id=workspace.id,
                    user_id=binh.id,
                    role=WorkspaceRole.VIEWER,
                ),
            ]
        )

        # 4. PROJECTS
        backend = Project(
            id=UUID(IDS["backend"]),
            workspace_id=workspace.id,
            name="TaskHub Backend",
            description="FastAPI and PostgreSQL",
            status=ProjectStatus.ACTIVE,
            created_at=now,
        )

        frontend = Project(
            id=UUID(IDS["frontend"]),
            workspace_id=workspace.id,
            name="TaskHub Frontend",
            description="Web application interface",
            status=ProjectStatus.ACTIVE,
            created_at=now,
        )

        session.add_all([backend, frontend])
        await session.flush()

        # 5. TASKS
        task_specs = [
            (
                "Setup PostgreSQL",
                backend.id,
                an.id,
                TaskStatus.DONE,
                TaskPriority.HIGH,
            ),
            (
                "Create SQLAlchemy Models",
                backend.id,
                an.id,
                TaskStatus.IN_REVIEW,
                TaskPriority.HIGH,
            ),
            (
                "Implement Task CRUD",
                backend.id,
                binh.id,
                TaskStatus.IN_PROGRESS,
                TaskPriority.MEDIUM,
            ),
            (
                "Design Dashboard",
                frontend.id,
                binh.id,
                TaskStatus.TODO,
                TaskPriority.MEDIUM,
            ),
            (
                "Write API Documentation",
                backend.id,
                an.id,
                TaskStatus.TODO,
                TaskPriority.LOW,
            ),
        ]

        tasks = []

        for index, (
            title,
            project_id,
            assignee_id,
            task_status,
            priority,
        ) in enumerate(task_specs):
            task = Task(
                id=uuid4(),
                project_id=project_id,
                assignee_id=assignee_id,
                created_by=admin.id,
                title=title,
                description=f"Sample task: {title}",
                status=task_status,
                priority=priority,
                due_date=now + timedelta(days=index + 3),
                created_at=now,
            )
            tasks.append(task)

        session.add_all(tasks)
        await session.flush()

        # 6. LABELS
        labels = [
            Label(
                id=uuid4(),
                project_id=backend.id,
                name="Bug",
                color="#EF4444",
            ),
            Label(
                id=uuid4(),
                project_id=backend.id,
                name="Feature",
                color="#22C55E",
            ),
            Label(
                id=uuid4(),
                project_id=backend.id,
                name="Documentation",
                color="#3B82F6",
            ),
        ]

        session.add_all(labels)
        await session.flush()

        # 7. TASK LABELS
        session.add_all(
            [
                TaskLabel(
                    task_id=tasks[0].id,
                    label_id=labels[1].id,
                ),
                TaskLabel(
                    task_id=tasks[1].id,
                    label_id=labels[1].id,
                ),
                TaskLabel(
                    task_id=tasks[2].id,
                    label_id=labels[0].id,
                ),
                TaskLabel(
                    task_id=tasks[2].id,
                    label_id=labels[1].id,
                ),
                TaskLabel(
                    task_id=tasks[4].id,
                    label_id=labels[2].id,
                ),
            ]
        )

        # 8. COMMENTS
        comments = [
            (
                tasks[0].id,
                admin.id,
                "Database setup completed.",
            ),
            (
                tasks[1].id,
                an.id,
                "Models are ready for review.",
            ),
            (
                tasks[2].id,
                binh.id,
                "Working on CRUD endpoints.",
            ),
            (
                tasks[4].id,
                admin.id,
                "Please update the API documentation.",
            ),
        ]

        session.add_all(
            [
                Comment(
                    id=uuid4(),
                    task_id=task_id,
                    author_id=author_id,
                    content=content,
                    created_at=now,
                )
                for task_id, author_id, content in comments
            ]
        )

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
