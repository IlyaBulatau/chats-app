import factory
from faker import Faker

from chat.auth.forms import RegisterForm


faker = Faker()


class UserRegistrationFactory(factory.Factory):
    class Meta:
        model = RegisterForm
    
    username = factory.LazyAttribute(lambda self: faker.name())
    password1 = factory.LazyAttribute(lambda self: faker.password(length=8))
    password2 = factory.LazyAttribute(lambda self: self.password1)