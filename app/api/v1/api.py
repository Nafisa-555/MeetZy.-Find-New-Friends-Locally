f"""
Main API Router - Combines all endpoint routers.

This module assembles all the individual endpoint routers (auth, users, matches, etc.)
into a single API router that gets mounted in the main application.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, matches, friends, chat , admin

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers with their prefixes and tags
# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(matches.router)
api_router.include_router(friends.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router)

