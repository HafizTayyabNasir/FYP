import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, AsyncSessionLocal
from app.models import Base, User, PricingPlan
from app.core.security import get_password_hash

async def init_db() -> None:
    """Initialize database tables and seed default data."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed default data
    async with AsyncSessionLocal() as session:
        await seed_pricing_plans(session)
        await seed_admin_user(session)

async def seed_pricing_plans(session: AsyncSession) -> None:
    """Seed the default pricing plans."""
    from sqlalchemy import select
    
    # Check if plans exist
    result = await session.execute(select(PricingPlan))
    if result.scalars().first():
        return # Already seeded
        
    individual = PricingPlan(
        slug="individual",
        name="Individual",
        price=0.0,
        description="For FYP demos and manual testing",
        features=["Lead discovery", "Website audit", "Email finder", "Local data storage"],
        is_popular=False,
        trial_days=90
    )
    
    team = PricingPlan(
        slug="team",
        name="Team",
        price=49.0,
        description="For teams running repeat outreach",
        features=["Everything in Starter", "Campaign management", "Inbox workflow", "AI outreach generation", "Higher usage limits", "Team-ready workflow", "Priority support"],
        is_popular=True,
        trial_days=0
    )
    
    session.add_all([individual, team])
    await session.commit()

async def seed_admin_user(session: AsyncSession) -> None:
    """Seed the default admin user."""
    from sqlalchemy import select
    
    result = await session.execute(select(User).where(User.email == "admin@elvionsolutions.com"))
    if result.scalars().first():
        return # Admin already exists
        
    admin = User(
        full_name="Admin",
        email="admin@elvionsolutions.com",
        hashed_password=get_password_hash("admin123"),
        is_verified=True,
        is_active=True,
        role="admin",
        plan="team"
    )
    
    session.add(admin)
    await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
