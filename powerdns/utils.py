from datetime import timedelta, datetime

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
        # email = repr(email)
        new_mail_parts = ''
        mail_parts = email.split("@")
        new_mail_parts += "\.".join(mail_parts[0].split("."))
        new_mail_parts += "."
        new_mail_parts += mail_parts[1]
        new_mail_parts += "."
        return str(new_mail_parts)

    @classmethod
    def convert_to_email(cls, email):
        email = repr(email)
        dirty_mail_parts = email.split(r'\.')
        mail_party = dirty_mail_parts[-1:]
        last_item_before_at=mail_party[0].split(".")
        return str(".".join(dirty_mail_parts[0:-1]+[last_item_before_at[0]])).replace("\.", ".")+"@"+".".join(bar[1:])

    def get_email(self):
        return self._email

    def get_soa_email(self):
        return self.__class__.convert_from_email(self._email)


class SOARecord:

    def __init__(self, mname, rname, serial, refresh=timedelta(seconds=86400), retry=timedelta(seconds=7200), expire=timedelta(seconds=604800), ttl=timedelta(seconds=3600)):
        self.mname = mname
        self.rrname = rname
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.ttl = ttl

    def get_content(self):
        return "{mname} {rrname} {serial} {refresh} {retry} {expire} {ttl}".format(
            mname=self.mname,
            rrname=self.rrname.get_soa_email(),
            serial=self.serial.get_serial(),
            refresh=int(self.refresh.total_seconds()),
            retry=int(self.retry.total_seconds()),
            expire=int(self.expire.total_seconds()),
            ttl=int(self.ttl.total_seconds())
        )

    @classmethod
    def parser(cls, soa_record):
        part = soa_record.split(" ")

        return cls(mname=part[0],
                   rname=EMail.parse(part[1]),
                   serial=Serial.parse(part[2]),
                   refresh=timedelta(seconds=part[3]),
                   expire=timedelta(seconds=part[4]),
                   ttl=timedelta(seconds=part[5]))

class Serial:

    def __init__(self, date, change_count):
        self.date = date
        self.change_count = int(change_count)

    @classmethod
    def parser(cls, serial):
        date_part = serial[:-2]
        change_count = serial[-2:]
        return cls(datetime.strptime(date_part, "%Y%m%d"), change_count)

    def get_serial(self):
        return "{}{}".format(self.date.strftime("%Y%m%d"), str(self.change_count).rjust(2, "0"))

    def update(self):
        if self.date.date() == datetime.date():
            self.change_count = self.change_count+1
        else:
            self.date = datetime.now().date()
            self.change_count = 1

    @classmethod
    def new(cls):
        return cls(datetime.now(), 0)