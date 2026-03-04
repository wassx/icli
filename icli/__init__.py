"""iCloud CLI package"""

from .mail import MailModule
from .calendar import CalendarModule
from .drive import DriveModule

class iCloudCLI:
    def __init__(self):
        self.mail = MailModule()
        self.calendar = CalendarModule()
        self.drive = DriveModule()
    
    def run(self):
        """Run the main CLI interface"""
        from ..main import main
        main()