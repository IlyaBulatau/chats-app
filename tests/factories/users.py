import factory
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from chat.auth.forms import RegisterForm
from core.domains import User # type: ignore
from chat.auth.password import hash_password


faker = Faker()


class UserRegistrationFactory(factory.Factory):
    class Meta:
        model = RegisterForm
    
    username = factory.LazyAttribute(lambda self: faker.name())
    password1 = factory.LazyAttribute(lambda self: faker.password(length=8))
    password2 = factory.LazyAttribute(lambda self: self.password1)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda self: int('%d' % self))
    username = factory.LazyAttribute(lambda self: faker.name())
    password = factory.LazyAttribute(lambda self: faker.password(length=8))

    @classmethod
    def set_session(cls, session: AsyncSession) -> None:
        cls._meta.sqlalchemy_session = session

    @classmethod
    def create(cls, **kwargs):
        session: AsyncSession = cls._meta.sqlalchemy_session
        result = super().create(**kwargs)

        async def _create():
            await session.commit()
            return result

        return _create()
    
    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]