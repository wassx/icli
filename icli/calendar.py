"""Calendar module for iCloud CLI - Real iCloud Calendar Integration"""

import logging
from datetime import datetime, timedelta
from calendar import monthrange, month_name
from collections import defaultdict
from icli.utils import separator, Spinner

logger = logging.getLogger(__name__)

class CalendarModule:
    def __init__(self, auth=None):
        self.auth = auth
        self._use_real_data = True  # Always use real data (no mock)
    
    def _safe_format_date(self, date_obj, format_str):
        """Safely format date objects, handling various API return formats"""
        try:
            if date_obj is None:
                return "Unknown"
            
            # Handle list format (Apple's 7-element date array)
            if isinstance(date_obj, list) and len(date_obj) >= 7:
                # Apple format: [YYYYMMDD, YYYY, MM, DD, HH, MM, minutes_from_midnight]
                year = date_obj[1]
                month = date_obj[2]
                day = date_obj[3]
                hour = date_obj[4]
                minute = date_obj[5]
                
                # Create datetime object
                from datetime import datetime
                dt = datetime(year, month, day, hour, minute)
                return dt.strftime(format_str)
            
            # Handle datetime objects
            elif hasattr(date_obj, 'strftime'):
                return date_obj.strftime(format_str)
            
            # Handle string dates
            elif isinstance(date_obj, str):
                # Try to parse common date string formats
                from datetime import datetime
                try:
                    # Try ISO format first
                    dt = datetime.fromisoformat(date_obj)
                    return dt.strftime(format_str)
                except ValueError:
                    # Try other common formats
                    for fmt in ["%Y-%m-%d", "%Y%m%d", "%m/%d/%Y"]:
                        try:
                            dt = datetime.strptime(date_obj, fmt)
                            return dt.strftime(format_str)
                        except ValueError:
                            continue
                    return "Unknown"
            
            # Fallback
            return str(date_obj)
            
        except Exception as e:
            print(f"⚠️  Error formatting date {date_obj}: {e}")
            return "Unknown"
    
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
            print(separator())
            
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
            
            print(separator())
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
            
            # Calculate date range
            today = datetime.today()
            end_date = today + timedelta(days=days_ahead)
            
            with Spinner("Loading events from iCloud"):
                # Get events for the date range
                if target_calendar:
                    all_events = calendar_service.get_events(
                        from_dt=today, 
                        to_dt=end_date, 
                        as_objs=True
                    )
                    events = [e for e in all_events if hasattr(e, 'pguid') and e.pguid == target_calendar.guid]
                else:
                    events = calendar_service.get_events(
                        from_dt=today, 
                        to_dt=end_date, 
                        as_objs=True
                    )
            
            if not events:
                print(f"ℹ️  No upcoming events in the next {days_ahead} days.")
                extend = input("   Show a wider range? Enter number of days (or Enter to skip): ").strip()
                if extend.isdigit() and int(extend) > 0:
                    return self.list_events(calendar_index, days_ahead=int(extend))
                return []
            
            # Sort events by start date
            events.sort(key=lambda x: x.start_date if x.start_date else datetime.min)
            
            print(f"📅 Found {len(events)} upcoming events (next {days_ahead} days):")
            print(separator())
            
            event_list = []
            for i, event in enumerate(events, 1):
                event_info = self._format_event_for_display(event, i)
                event_list.append(event_info)
                print(f"{i:2d}. {event_info['display']}")
            
            print(separator())
            return event_list
            
        except Exception as e:
            logger.debug("Error loading calendar events: %s", e, exc_info=True)
            print("❌ Error loading calendar events. Please check your connection.")
            return None
    
    def _format_event_for_display(self, event, index):
        """Format event information for display"""
        # Format date and time with proper type checking
        try:
            if event.all_day:
                date_str = self._safe_format_date(event.start_date, "%a, %b %d, %Y")
                time_str = "All Day"
            else:
                date_str = self._safe_format_date(event.start_date, "%a, %b %d, %Y")
                time_str = self._safe_format_date(event.start_date, "%I:%M %p")
                if event.end_date:
                    end_time_str = self._safe_format_date(event.end_date, "%I:%M %p")
                    time_str += f" - {end_time_str}"
        except Exception as e:
            print(f"⚠️  Error formatting event dates: {e}")
            date_str = "Unknown date"
            time_str = "Unknown time"
        
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
        # Enhanced event object validation
        if not event_obj:
            print("❌ Invalid event object: None")
            return
        
        # Handle different event object formats
        if isinstance(event_obj, dict) and 'object' in event_obj:
            event = event_obj['object']
        elif hasattr(event_obj, 'start_date'):  # Direct EventObject
            event = event_obj
        else:
            print(f"❌ Invalid event object format: {type(event_obj)}")
            print(f"   Content: {event_obj}")
            return
        
        # Validate the event object
        if not event:
            print("❌ Event object is None")
            return
        
        # Check if it has basic event properties
        if not hasattr(event, 'title') and not hasattr(event, 'start_date'):
            print("❌ Object doesn't appear to be a valid event")
            print(f"   Available attributes: {dir(event)}")
            return
        
        print("\n📅 Event Details")
        print(separator())
        
        # Title
        title = event.title if event.title else "Untitled Event"
        print(f"Title: {title}")
        
        # Dates and Times
        print("\n📅 When:")
        try:
            if event.all_day:
                if event.start_date and event.end_date:
                    start_str = self._safe_format_date(event.start_date, "%A, %B %d, %Y")
                    end_str = self._safe_format_date(event.end_date, "%A, %B %d, %Y")
                    if start_str == end_str:
                        print(f"  All Day on {start_str}")
                    else:
                        print(f"  {start_str} to {end_str} (All Day)")
                else:
                    print(f"  All Day Event")
            else:
                if event.start_date:
                    print(f"  Starts: {self._safe_format_date(event.start_date, '%A, %B %d, %Y at %I:%M %p')}")
                if event.end_date:
                    print(f"  Ends:   {self._safe_format_date(event.end_date, '%A, %B %d, %Y at %I:%M %p')}")
                    # Calculate duration safely
                    try:
                        if hasattr(event.start_date, '__sub__') and hasattr(event.end_date, '__sub__'):
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
                    except Exception:
                        print(f"  Duration: Unknown")
        except Exception as e:
            print(f"⚠️  Error displaying event dates: {e}")
            print(f"  Start: {getattr(event, 'start_date', 'Unknown')}")
            print(f"  End: {getattr(event, 'end_date', 'Unknown')}")
        
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
        
        print(separator())
    
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
        print(separator())
        
        # Cache calendar list for this session; re-fetch only on 'r'
        cached_calendars = None
        
        try:
            while True:
                if cached_calendars is None:
                    cached_calendars = self.list_calendars()
                calendars = cached_calendars
                
                if not calendars:
                    break
                
                # Show actual count in prompt
                calendar_choice = input(f"\n📅 Select calendar (1-{len(calendars)}, r=refresh, q=quit): ").strip().lower()
                
                if calendar_choice == 'r':
                    cached_calendars = None  # Force re-fetch on next iteration
                    continue
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
                            event_choice = input(f"\n📅 Select event (1-{len(events)}, b=back, q=quit): ").strip().lower()
                            
                            if event_choice == 'q':
                                print("Exiting calendar browser...")
                                break
                            elif event_choice == 'b':
                                continue  # Back to calendar selection
                            elif event_choice.isdigit():
                                event_index = int(event_choice)
                                if 1 <= event_index <= len(events):
                                    selected_event = events[event_index - 1]
                                    self.show_event_details(selected_event)
                                else:
                                    print("❌ Invalid event number")
                            else:
                                print("❌ Invalid choice")
                        else:
                            print("   No events found. Press Enter to choose a different calendar.")
                            input()
                    else:
                        print(f"❌ Please enter a number between 1 and {len(calendars)}")
                else:
                    print("❌ Invalid choice. Use a number, r=refresh, or q=quit.")
        except KeyboardInterrupt:
            print("\n❌ Interrupted. Returning to menu.")
    
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
    
    def show_calendar_grid(self, year=None, month=None):
        """
        Display calendar events in a grid view
        
        Args:
            year: Year to display (current year if None)
            month: Month to display (current month if None)
        """
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud calendar.")
            return False
        
        # Check session activity
        self.auth.check_session_activity()
        
        try:
            calendar_service = self.auth.get_calendar_service()
            if not calendar_service:
                print("❌ Calendar service not available")
                return False
            
            # Use current year/month if not specified
            today = datetime.today()
            year = year if year is not None else today.year
            month = month if month is not None else today.month
            
            print(f"\n📅 Calendar Grid View - {month_name[month]} {year}")
            print(separator())
            
            # Get all events for this month
            first_day, num_days = monthrange(year, month)
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, num_days, 23, 59, 59)
            
            events = calendar_service.get_events(
                from_dt=start_date,
                to_dt=end_date,
                as_objs=True
            )
            
            # Organize events by day
            events_by_day = defaultdict(list)
            for event in events:
                if event.start_date:
                    day = event.start_date.day
                    events_by_day[day].append(event)
            
            # Display calendar grid
            self._display_calendar_grid(year, month, num_days, first_day, events_by_day)
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading calendar grid: {str(e)}")
            return False
    
    def _display_calendar_grid(self, year, month, num_days, first_day, events_by_day):
        """
        Display calendar grid with events
        
        Args:
            year: Year being displayed
            month: Month being displayed
            num_days: Number of days in the month
            first_day: Day of week for first day (0=Monday, 6=Sunday)
            events_by_day: Dictionary mapping day to events
        """
        # Calendar header
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        print("   ", end="")
        for day in days_of_week:
            print(f" {day:^5}", end="")
        print()
        
        # Calendar grid
        print("   ", end="")
        for _ in range(first_day):
            print("     ", end="")
        
        for day in range(1, num_days + 1):
            # Print day number
            print(f" {day:>3} ", end="")
            
            # Check if there are events on this day
            if day in events_by_day:
                print("📅", end="")
            else:
                print(" ", end="")
            
            # New line for Sunday
            if (day + first_day) % 7 == 0:
                print()
                if day < num_days:
                    print("   ", end="")
        
        print("\n")
        print(separator())
        
        # Show event legend
        if events_by_day:
            print("\n📅 Events this month:")
            for day, events in sorted(events_by_day.items()):
                print(f"  {month_name[month]} {day}: {len(events)} event(s)")
        else:
            print("\nNo events this month")
        
        # Offer to view specific day
        print("\nOptions:")
        print("1. View specific day")
        print("2. Back to calendar menu")
        
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            day_choice = input("Enter day number (1-31): ").strip()
            if day_choice.isdigit():
                day_num = int(day_choice)
                if 1 <= day_num <= num_days:
                    self._show_day_events(year, month, day_num, events_by_day.get(day_num, []))
                else:
                    print("❌ Invalid day number")
        
    def _show_day_events(self, year, month, day, events):
        """
        Show events for a specific day
        """
        print(f"\n📅 Events on {month_name[month]} {day}, {year}")
        print(separator())
        
        if not events:
            print("No events on this day")
            return
        
        for i, event in enumerate(events, 1):
            event_info = self._format_event_for_display(event, i)
            print(f"{i:2d}. {event_info['display']}")
        
        print(separator())
        
        # Offer to view event details
        print("\nOptions:")
        print("1. View event details")
        print("2. Back to grid view")
        
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            event_choice = input("Enter event number: ").strip()
            if event_choice.isdigit():
                event_index = int(event_choice) - 1
                if 0 <= event_index < len(events):
                    self.show_event_details({
                        'id': event_index + 1,
                        'object': events[event_index]
                    })
