class Language:
    def __init__(self, eng_name: str, native_name: str):
        self.eng_name = eng_name
        self.native_name = native_name

    def __repr__(self):
        return str(self.__dict__)


lang_map = dict(
    es=Language(eng_name="Spanish", native_name="Español"),
    en=Language(eng_name="English", native_name="English"),

)
