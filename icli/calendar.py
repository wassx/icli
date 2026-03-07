"""Calendar module for iCloud CLI - Real iCloud Calendar Integration"""

from datetime import datetime, timedelta

class CalendarModule:
    def __init__(self, auth=None):
        self.auth = auth
        self._use_real_data = True  # Always use real data (no mock)
    
    def list_calendars(self):
        """List all available calendars"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud calendar.")
            return None
        
        # Check session activity
        self.auth.check_session_activity()
        
        try:
            calendar_service = self.auth.get_calendar_service()
            if not calendar_service:
                print("❌ Calendar service not available")
                return None
            
            print("📅 Loading calendars from iCloud...")
            calendars = calendar_service.get_calendars(as_objs=True)
            
            if not calendars:
                print("No calendars found.")
                return []
            
            print(f"📅 Found {len(calendars)} calendars:")
            print("=" * 60)
            
            calendar_list = []
            for i, calendar in enumerate(calendars, 1):
                calendar_info = {
                    'id': i,
                    'name': calendar.title,
                    'color': calendar.color,
                    'object': calendar
                }
                calendar_list.append(calendar_info)
                
                # Show calendar info
                symbol = "📅 " if getattr(calendar, 'is_default', False) else "📆 "
                print(f"{i:2d}. {symbol}{calendar.title}")
                if calendar.description:
                    print(f"     {calendar.description}")
            
            print("=" * 60)
            return calendar_list
            
        except Exception as e:
            print(f"❌ Error loading calendars: {str(e)}")
            print("   Please check your internet connection and try again.")
            return None
    
    def list_events(self, calendar_index=None, days_ahead=30):
        """List upcoming calendar events"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud calendar.")
            return None
        
        # Check session activity
        self.auth.check_session_activity()
        
        try:
            calendar_service = self.auth.get_calendar_service()
            if not calendar_service:
                print("❌ Calendar service not available")
                return None
            
            # Get the target calendar
            target_calendar = None
            if calendar_index is not None:
                calendars = self.list_calendars()
                if calendars and 1 <= calendar_index <= len(calendars):
                    target_calendar = calendars[calendar_index - 1]['object']
            
            print("📅 Loading events from iCloud...")
            
            # Calculate date range (today to days_ahead days from now)
            today = datetime.today()
            end_date = today + timedelta(days=days_ahead)
            
            # Get events for the date range
            if target_calendar:
                # Filter for specific calendar
                all_events = calendar_service.get_events(
                    from_dt=today, 
                    to_dt=end_date, 
                    as_objs=True
                )
                events = [e for e in all_events if hasattr(e, 'pguid') and e.pguid == target_calendar.guid]
            else:
                # Get all events from all calendars
                events = calendar_service.get_events(
                    from_dt=today, 
                    to_dt=end_date, 
                    as_objs=True
                )
            
            if not events:
                print("No upcoming events found.")
                return []
            
            # Sort events by start date
            events.sort(key=lambda x: x.start_date if x.start_date else datetime.min)
            
            print(f"📅 Found {len(events)} upcoming events (next {days_ahead} days):")
            print("=" * 80)
            
            event_list = []
            for i, event in enumerate(events[:10], 1):  # Show first 10 events
                event_info = self._format_event_for_display(event, i)
                event_list.append(event_info)
                
                # Display event
                print(f"{i:2d}. {event_info['display']}")
            
            print("=" * 80)
            return event_list
            
        except Exception as e:
            print(f"❌ Error loading calendar events: {str(e)}")
            print("   Please check your internet connection and try again.")
            return None
    
    def _format_event_for_display(self, event, index):
        """Format event information for display"""
        # Format date and time
        if event.all_day:
            date_str = event.start_date.strftime("%a, %b %d, %Y")
            time_str = "All Day"
        else:
            date_str = event.start_date.strftime("%a, %b %d, %Y")
            time_str = event.start_date.strftime("%I:%M %p")
            if event.end_date:
                end_time_str = event.end_date.strftime("%I:%M %p")
                time_str += f" - {end_time_str}"
        
        # Build display string
        title = event.title if event.title else "Untitled Event"
        location = f" @ {event.location}" if event.location else ""
        
        display_str = f"{title}{location}"
        display_str += f"\n   📅 {date_str} • {time_str}"
        
        if event.recurrence_master:
            display_str += " • 🔄 Recurring"
        
        return {
            'id': index,
            'title': title,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'location': event.location,
            'all_day': event.all_day,
            'recurring': event.recurrence_master,
            'object': event,
            'display': display_str
        }
    
    def show_event_details(self, event_obj):
        """Show detailed information about a specific event"""
        if not event_obj or not hasattr(event_obj, 'object'):
            print("❌ Invalid event object")
            return
        
        event = event_obj['object']
        
        print("\n📅 Event Details")
        print("=" * 60)
        
        # Title
        title = event.title if event.title else "Untitled Event"
        print(f"Title: {title}")
        
        # Dates and Times
        print("\n📅 When:")
        if event.all_day:
            if event.start_date and event.end_date:
                start_str = event.start_date.strftime("%A, %B %d, %Y")
                end_str = event.end_date.strftime("%A, %B %d, %Y")
                if start_str == end_str:
                    print(f"  All Day on {start_str}")
                else:
                    print(f"  {start_str} to {end_str} (All Day)")
            else:
                print(f"  All Day Event")
        else:
            if event.start_date:
                print(f"  Starts: {event.start_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
            if event.end_date:
                print(f"  Ends:   {event.end_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
                duration = event.end_date - event.start_date
                days = duration.days
                hours, remainder = divmod(duration.seconds, 3600)
                minutes = remainder // 60
                if days > 0:
                    print(f"  Duration: {days} days, {hours} hours, {minutes} minutes")
                elif hours > 0:
                    print(f"  Duration: {hours} hours, {minutes} minutes")
                else:
                    print(f"  Duration: {minutes} minutes")
        
        # Location
        if event.location:
            print(f"\n📍 Location: {event.location}")
        
        # Description/Notes
        if hasattr(event, 'notes') and event.notes:
            print(f"\n📝 Notes:")
            print(f"  {event.notes}")
        
        # Recurrence
        if event.recurrence_master:
            print(f"\n🔄 Recurrence: This is a recurring event")
        
        # Organizer
        if hasattr(event, 'organizer') and event.organizer:
            print(f"\n👤 Organizer: {event.organizer}")
        
        # Attendees
        if hasattr(event, 'invitees') and event.invitees:
            print(f"\n👥 Attendees ({len(event.invitees)}):")
            for i, invitee in enumerate(event.invitees, 1):
                print(f"  {i}. {invitee}")
        
        # Calendar
        if hasattr(event, 'calendar') and event.calendar:
            print(f"\n📆 Calendar: {event.calendar.title}")
        
        print("=" * 60)
    
    def browse_events(self):
        """Interactive calendar event browser"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud calendar.")
            return
        
        # Check session activity
        self.auth.check_session_activity()
        
        print("\n=== iCloud Calendar Browser ===")
        print("📅 Viewing your iCloud calendar events")
        print("Commands: [number] to view event, b=back, q=quit, r=refresh")
        print("=" * 60)
        
        while True:
            # List calendars first
            calendars = self.list_calendars()
            if not calendars:
                break
            
            # Ask user to select a calendar
            calendar_choice = input("\n📅 Select calendar (1-99, or 'q' to quit): ").strip().lower()
            
            if calendar_choice == 'q':
                print("Exiting calendar browser...")
                break
            
            if calendar_choice.isdigit():
                calendar_index = int(calendar_choice)
                if 1 <= calendar_index <= len(calendars):
                    # List events for selected calendar
                    events = self.list_events(calendar_index)
                    if events:
                        # Ask user to select an event
                        event_choice = input("\n📅 Select event (1-99, b=back, q=quit): ").strip().lower()
                        
                        if event_choice == 'q':
                            print("Exiting calendar browser...")
                            break
                        elif event_choice == 'b':
                            continue  # Back to calendar selection
                        elif event_choice.isdigit():
                            event_index = int(event_choice)
                            if 1 <= event_index <= len(events):
                                self.show_event_details(events[event_index - 1])
                            else:
                                print("❌ Invalid event number")
                        else:
                            print("❌ Invalid choice")
                else:
                    print("No events found for this calendar")
            else:
                print("❌ Invalid choice. Use numbers to select a calendar or 'q' to quit.")
    
    def create_event(self, title, date, start_time):
        """Create a new calendar event - DISABLED for read-only mode"""
        print("❌ Event creation is disabled in read-only mode")
        return False
    
    def edit_event(self, event_id, **kwargs):
        """Edit an existing event - DISABLED for read-only mode"""
        print("❌ Event editing is disabled in read-only mode")
        return False
    
    def delete_event(self, event_id):
        """Delete an event - DISABLED for read-only mode"""
        print("❌ Event deletion is disabled in read-only mode")
        return False
