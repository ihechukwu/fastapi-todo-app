from fastapi import APIRouter
from app.todos.todos_routes import todos_router
from app.users.user_routes import users_router
from app.auth.auth_routes import auth_router

api_router = APIRouter()

api_router.include_router(todos_router, prefix="/todos", tags=["Todos"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
