"""iCloud CLI package"""

from .calendar import CalendarModule
from .drive import DriveModule
from .mail import MailModule
from .auth import iCloudAuth

class iCloudCLI:
    def __init__(self):
        self.auth = iCloudAuth()
        self.calendar = CalendarModule(self.auth)
        self.drive = DriveModule(self.auth)
        self.mail = MailModule(self.auth)
