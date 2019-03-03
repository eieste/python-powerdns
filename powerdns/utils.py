import re


class EMail:

    def __init__(self, email):
        self._email = email

    @classmethod
    def parse(cls, data):
        if "@" in data:
            return cls(data)
        else:
            return cls(cls.convert_to_email(data))

    @classmethod
    def convert_from_email(cls, email):
        email = repr(email)
        new_mail_parts = r''
        mail_parts = email.split("@")
        new_mail_parts += "\.".join(mail_parts[0].split("."))
        new_mail_parts += "."
        new_mail_parts += mail_parts[1]
        return new_mail_parts

    @classmethod
    def convert_to_email(cls, email):
        email = repr(email)
        dirty_mail_parts = email.split(r'\.')
        mail_party = dirty_mail_parts[-1:]
        bar=mail_party[0].split(".")
        return str(".".join(dirty_mail_parts[0:-1]+[bar[0]])).replace("\.", ".")+"@"+".".join(bar[1:])

    def get_email(self):
        return self._email

    def get_soa_email(self):
        return self.__class__.convert_from_email(self._email)