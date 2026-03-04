"""Calendar module for iCloud CLI"""

class CalendarModule:
    def __init__(self, auth=None):
        self.auth = auth
    
    def list_events(self):
        """List upcoming calendar events"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud calendar.")
            return
        
        # Check session activity
        self.auth.check_session_activity()
        
        try:
            calendar_service = self.auth.get_calendar_service()
            if not calendar_service:
                print("❌ Calendar service not available")
                return
            
            print("Loading events from iCloud...")
            # Get events from primary calendar
            events = calendar_service.events()
            
            if not events:
                print("No upcoming events found.")
                return
            
            print(f"Found {len(events)} upcoming events:")
            for i, event in enumerate(events[:5], 1):  # Show first 5 events
                print(f"{i}. {event.summary} - {event.start}")
            
        except Exception as e:
            print(f"❌ Error loading calendar events: {str(e)}")
            print("   Please check your internet connection and try again.")
        
    def create_event(self, title, date, time):
        """Create a new calendar event"""
        print(f"Creating event: {title} on {date} at {time}")
        # TODO: Implement actual event creation