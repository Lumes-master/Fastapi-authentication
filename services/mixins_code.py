import uuid


class MixinCode:

    @classmethod
    def generate_code(cls) -> str:
        code = str(uuid.uuid1())
        return code