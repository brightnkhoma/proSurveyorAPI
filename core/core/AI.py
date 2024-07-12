from googletrans import Translator

class AI:
    def __init__(self) -> None:
        pass


    def make_translation(self, text : str):
        trans = Translator()
        response = trans.translate(text)
        return response
