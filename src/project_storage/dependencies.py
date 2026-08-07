from project_storage.use_cases.register_user import RegisterUserUseCase
from project_storage.infra.pg.user_repository import PgUserRepository


def get_register_user_uc():
    return RegisterUserUseCase(get_user_repository())


def get_user_repository():
    return PgUserRepository()
