import pytest
from faker import Faker

from chat.auth.validators import PasswordValidatorField, UsernameValidatorField
from core.exceptions import InCorrectPassword, MismatchPassword, InCorrectUsername # type: ignore
from chat.core.constancies import USERNAME_LENGHT


faker = Faker()

@pytest.mark.parametrize("validator", [PasswordValidatorField])
class TestPasswordValidatorField:

    @pytest.mark.parametrize("password", ["1234567", "vbjfnwo", "", "****"])
    def test_min_length_password_error(self, validator: PasswordValidatorField, password: str):
        """Минимальная длинна, указана в PasswordValidatorField.MIN_LENGHT"""
        with pytest.raises(InCorrectPassword) as exc:
            validator.is_valid_lenght(password)

        assert exc.value.message == f"Длинна пароля должна быть более {validator.MIN_LENGHT} символов"
        assert exc.value.field == "password"

    @pytest.mark.parametrize("passwords", [("123", "321"), ("", "-"), ("dawd2", "gjdjij2i")])
    def test_match_two_passwords_error(self, validator: PasswordValidatorField, passwords: tuple[str]):
        """Пароли совпадают"""
        password1, password2 = passwords

        with pytest.raises(MismatchPassword) as exc:
            validator.has_match_password(password1, password2)
        
        assert exc.value.message == "Пароли не совпадают"
        assert exc.value.field == "password"

    @pytest.mark.parametrize("password", ["", "(@#@)", "qweecmnKKDw", "dfg"])
    def test_password_have_digit_error(self, validator: PasswordValidatorField, password: str):
        """Пароль имеет цифру"""
        with pytest.raises(InCorrectPassword) as exc:
            validator.is_have_digit(password)
        
        assert exc.value.message == "Пароль должен содержать хотя бы 1 цифру"
        assert exc.value.field == "password"

    @pytest.mark.parametrize("password", [" ", "\n", "\t", " \n\t", "   ", "Hello world\n"])
    def test_password_space_error(self, validator: PasswordValidatorField, password: str):
        """Пароль не содержит знаков пробела"""
        with pytest.raises(InCorrectPassword) as exc:
            validator.is_not_have_space(password)
        
        assert exc.value.message == "Пароль не должен содержать пробелов и знаков табуляции"
        assert exc.value.field == "password"
    
    @pytest.mark.parametrize("password", [faker.password(length=8) for _ in range(5)])
    def test_password_is_valid(self, validator: PasswordValidatorField, password: str):
        """Валидный пароль"""
        validator.validate(password)


@pytest.mark.parametrize("validator", [UsernameValidatorField])
class TestUsernameValidatorField:

    @pytest.mark.parametrize("username", ["Im", "Yo", "Jo", "123", ""])
    def test_min_length_username_error(self, validator: UsernameValidatorField, username: str):
        """Валидная минимальная длинна"""
        with pytest.raises(InCorrectUsername) as exc:
            validator.is_valid_lenght(username)
        
        assert exc.value.message == f"Длинна имени должна быть больше в пределах {validator.MIN_LENGHT}-{USERNAME_LENGHT} символов"
        assert exc.value.field == "username"
    
    
    @pytest.mark.parametrize("username", [faker.password(length=51) for _ in range(5)])
    def test_max_length_username_error(self, validator: UsernameValidatorField, username: str):
        """Валидная максимальная длинна"""
        with pytest.raises(InCorrectUsername) as exc:
            validator.is_valid_lenght(username)
        
        assert exc.value.message == f"Длинна имени должна быть больше в пределах {validator.MIN_LENGHT}-{USERNAME_LENGHT} символов"
        assert exc.value.field == "username"
    
    @pytest.mark.parametrize("username", [123, None, False])
    def test_str_username_error(self, validator: UsernameValidatorField, username: str):
        """Строковое представление"""
        with pytest.raises(InCorrectUsername) as exc:
            validator.is_string(username)
        
        assert exc.value.message == "Имя должно быть строковым представлением"
        assert exc.value.field == "username"