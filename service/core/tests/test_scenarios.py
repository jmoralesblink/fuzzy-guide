from core.tests.factories import UserFactory


def create_user(username=None, email=None, password=None):
    user = UserFactory.create(
        username=username or "test",
        email=email or "test-email",
        password=password or "password",
    )
    return user
