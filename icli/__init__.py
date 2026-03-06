"""iCloud CLI package"""

from .mail import MailModule
from .calendar import CalendarModule
from .drive import DriveModule
from .auth import iCloudAuth

class iCloudCLI:
    def __init__(self):
        self.auth = iCloudAuth()
        self.mail = MailModule(self.auth)
        self.calendar = CalendarModule(self.auth)
        self.drive = DriveModule(self.auth)
    
    def run(self):
        """Run the main CLI interface"""
        import importlib
        main_module = importlib.import_module("main")
        main_module.main()