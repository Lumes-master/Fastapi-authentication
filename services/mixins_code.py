import uuid
from passlib.hash import bcrypt

class MixinCode:

    @classmethod
    def generate_code(cls) -> str:
        code = str(uuid.uuid1())
        return code

    @classmethod
    def hash_password(cls, raw_password) -> str:
        return bcrypt.hash(raw_password)