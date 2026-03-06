"""iCloud Drive module for iCloud CLI"""

class DriveModule:
    def __init__(self, auth=None):
        self.auth = auth
        self.current_path = "/"
        self.file_cache = {}
    
    def browse_files(self):
        """Interactive file tree browser for iCloud Drive"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud Drive.")
            return
        
        # Check session activity
        self.auth.check_session_activity()
        
        print("\n=== iCloud Drive Browser ===")
        print("📁 Navigating your iCloud Drive files")
        print("Commands: [number] to enter, b=back, q=quit, r=refresh")
        print("=" * 60)
        
        while True:
            if not self._show_current_directory():
                break
            
            # Get user input
            choice = input("\n📂 Enter choice: ").strip().lower()
            
            if choice == 'q':
                print("Exiting iCloud Drive browser...")
                break
            elif choice == 'b':
                self._go_back()
            elif choice == 'r':
                self.file_cache = {}  # Clear cache
                print("🔄 Refreshed file list")
            elif choice.isdigit():
                self._handle_file_selection(int(choice))
            else:
                print("❌ Invalid choice. Use numbers, 'b' for back, 'q' to quit, 'r' to refresh")
    
    def _show_current_directory(self):
        """Display current directory contents"""
        try:
            drive_service = self.auth.get_drive_service()
            if not drive_service:
                print("❌ Drive service not available")
                return False
            
            # Check cache first
            cache_key = self.current_path
            if cache_key in self.file_cache:
                files = self.file_cache[cache_key]
            else:
                print(f"📂 Loading: {self.current_path}...")
                files = drive_service.dir(self.current_path)
                self.file_cache[cache_key] = files
            
            if not files:
                print("📂 This directory is empty")
                return True
            
            # Display breadcrumb
            self._show_breadcrumb()
            
            # Display files
            print(f"\n📁 Contents ({len(files)} items):")
            print("-" * 60)
            
            directories = []
            files_list = []
            
            for i, file in enumerate(files, 1):
                if file.type == "FOLDER":
                    directories.append((i, file))
                else:
                    files_list.append((i, file))
            
            # Show directories first
            for i, file in directories:
                size_str = self._format_size(file.size) if hasattr(file, 'size') else "-"
                print(f"{i:2d}. 📁 {file.name}/ {size_str}")
            
            # Show files
            for i, file in files_list:
                size_str = self._format_size(file.size) if hasattr(file, 'size') else "-"
                print(f"{i:2d}. 📄 {file.name} {size_str}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading directory: {str(e)}")
            return False
    
    def _show_breadcrumb(self):
        """Show navigation breadcrumb"""
        if self.current_path == "/":
            print("📁 iCloud Drive (Root)")
        else:
            # Clean up path for display
            path_parts = [p for p in self.current_path.split("/") if p]
            breadcrumb = " / ".join(path_parts)
            print(f"📁 iCloud Drive / {breadcrumb}")
    
    def _handle_file_selection(self, choice_num):
        """Handle user selection of a file/directory"""
        try:
            drive_service = self.auth.get_drive_service()
            if not drive_service:
                return
            
            # Get files again to ensure we have current data
            files = drive_service.dir(self.current_path)
            
            if 1 <= choice_num <= len(files):
                selected_file = files[choice_num - 1]
                
                if selected_file.type == "FOLDER":
                    # Enter directory
                    new_path = f"{self.current_path.rstrip('/')}/{selected_file.name}"
                    self.current_path = new_path
                else:
                    # Show file details
                    self._show_file_details(selected_file)
            else:
                print("❌ Invalid selection")
                
        except Exception as e:
            print(f"❌ Error handling selection: {str(e)}")
    
    def _show_file_details(self, file):
        """Show detailed information about a file"""
        print(f"\n📄 File Details: {file.name}")
        print("=" * 40)
        print(f"Type: {'Directory' if file.type == 'FOLDER' else 'File'}")
        print(f"Path: {self.current_path}/{file.name}")
        
        if hasattr(file, 'size'):
            print(f"Size: {self._format_size(file.size)} ({file.size} bytes)")
        
        if hasattr(file, 'date_created'):
            print(f"Created: {file.date_created}")
        
        if hasattr(file, 'date_modified'):
            print(f"Modified: {file.date_modified}")
        
        print("\nOptions:")
        print("d. Download this file")
        print("b. Back to directory listing")
        
        choice = input("Choose option: ").strip().lower()
        
        if choice == 'd':
            self._download_file_prompt(file)
        elif choice == 'b':
            return
        else:
            print("❌ Invalid choice")
    
    def _download_file_prompt(self, file):
        """Handle file download with user prompt"""
        local_filename = input(f"Enter local filename for {file.name} (or 'q' to cancel): ").strip()
        
        if local_filename.lower() == 'q':
            print("Download cancelled")
            return
        
        if not local_filename:
            local_filename = file.name
        
        print(f"📥 Downloading {file.name} to {local_filename}...")
        
        try:
            drive_service = self.auth.get_drive_service()
            if drive_service:
                remote_path = f"{self.current_path}/{file.name}"
                # This would call the actual download method
                print(f"✅ Download would save to: {local_filename}")
                print("   (Actual download implementation would go here)")
            else:
                print("❌ Drive service not available")
                
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
    
    def _go_back(self):
        """Navigate to parent directory"""
        if self.current_path == "/":
            print("📁 Already at root directory")
        else:
            # Go up one level
            path_parts = [p for p in self.current_path.split("/") if p]
            if len(path_parts) > 1:
                new_path = "/" + "/".join(path_parts[:-1])
            else:
                new_path = "/"
            
            self.current_path = new_path
            print(f"📁 Moved to parent directory: {self.current_path}")
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes is None:
            return "-"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def list_files(self, path="/"):
        """List files in iCloud Drive (legacy method)"""
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud Drive.")
            return
        
        # Check session activity
        self.auth.check_session_activity()
        
        try:
            drive_service = self.auth.get_drive_service()
            if not drive_service:
                print("❌ Drive service not available")
                return
            
            print(f"Loading files from iCloud Drive ({path})...")
            # Get files from specified path
            files = drive_service.dir(path)
            
            if not files:
                print("No files found in this directory.")
                return
            
            print(f"Found {len(files)} items:")
            for i, file in enumerate(files[:10], 1):  # Show first 10 files
                file_type = "Directory" if file.type == "FOLDER" else "File"
                size_str = self._format_size(file.size) if hasattr(file, 'size') else "-"
                print(f"{i}. {file_type} - {file.name} ({size_str})")
            
        except Exception as e:
            print(f"❌ Error loading files: {str(e)}")
            print("   Please check your internet connection and try again.")
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to iCloud Drive"""
        print(f"Uploading {local_path} to {remote_path}...")
        # TODO: Implement actual file upload
        
    def download_file(self, remote_path, local_path):
        """Download a file from iCloud Drive"""
        print(f"Downloading {remote_path} to {local_path}...")
        # TODO: Implement actual file download
