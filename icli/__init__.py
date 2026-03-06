"""iCloud CLI package"""

from .calendar import CalendarModule
from .drive import DriveModule
from .auth import iCloudAuth

class iCloudCLI:
    def __init__(self):
        self.auth = iCloudAuth()
        self.calendar = CalendarModule(self.auth)
        self.drive = DriveModule(self.auth)
