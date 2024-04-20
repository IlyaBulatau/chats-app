import pytest

from tests.factories.users import UserRegistrationFactory
from chat.auth.user import Registration
from chat.core.database.repositories.user import UserRepository


@pytest.mark.parametrize("user_form", UserRegistrationFactory.create_batch(5))
class TestRegistrationProcess:

    async def test_save_registration_user(self, user_form, db_session):
        user_repo = UserRepository()
        user_registration = Registration(user_form, user_repo, db_session)

        await user_registration()

        get_registrated_user = await user_repo.get(db_session, username=user_form.username)
        assert get_registrated_user.username == user_form.username