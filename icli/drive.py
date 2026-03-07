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
        print("Commands: [number] to enter, 0 for parent (..), b=back, q=quit, r=refresh")
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
            
            # Get the current node based on path
            current_node = self._get_node_for_path(drive_service)
            if not current_node:
                print("❌ Could not find specified directory")
                return False
            
            # Check cache first
            cache_key = self.current_path
            if cache_key in self.file_cache:
                children = self.file_cache[cache_key]
            else:
                print(f"📂 Loading: {self.current_path}...")
                # Get full node objects directly
                children = current_node.get_children()
                self.file_cache[cache_key] = children
            
            if not children:
                print("📂 This directory is empty")
                return True
            
            # Display breadcrumb
            self._show_breadcrumb()
            
            # Add parent directory entry (..) if not at root
            items = []
            if self.current_path != "/":
                items.append(("..", "PARENT", None))
            
            # Add actual children
            for node in children:
                node_type = "FOLDER" if node.type == "folder" else "FILE"
                items.append((node.name, node_type, node))
            
            # Display files
            print(f"\n📁 Contents ({len(items)} items):")
            print("-" * 60)
            
            # Show parent directory first (if present)
            if items and items[0][0] == "..":
                print(" 0. 📁 .. (Parent Directory)")
                
                # Show actual items starting from index 1
                for i, (name, item_type, node) in enumerate(items[1:], 1):
                    if item_type == "FOLDER":
                        size_str = self._format_size(self._get_node_size(node)) if hasattr(node, 'data') else "-"
                        print(f"{i:2d}. 📁 {name}/ {size_str}")
                    else:
                        size_str = self._format_size(self._get_node_size(node)) if hasattr(node, 'data') else "-"
                        print(f"{i:2d}. 📄 {name} {size_str}")
            else:
                # No parent directory (at root), show all items normally
                for i, (name, item_type, node) in enumerate(items, 1):
                    if item_type == "FOLDER":
                        size_str = self._format_size(self._get_node_size(node)) if hasattr(node, 'data') else "-"
                        print(f"{i:2d}. 📁 {name}/ {size_str}")
                    else:
                        size_str = self._format_size(self._get_node_size(node)) if hasattr(node, 'data') else "-"
                        print(f"{i:2d}. 📄 {name} {size_str}")
            
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
            
            # Get current node and its children
            current_node = self._get_node_for_path(drive_service)
            if not current_node:
                print("❌ Could not access current directory")
                return
            
            # Build items list with parent directory
            items = []
            if self.current_path != "/":
                items.append(("..", "PARENT", None))
            
            for node in children:
                node_type = "FOLDER" if node.type == "folder" else "FILE"
                items.append((node.name, node_type, node))
            
            # Handle selection (0 for parent, 1+ for actual items)
            if choice_num == 0 and self.current_path != "/":
                # Navigate to parent directory
                self._go_back()
            elif 1 <= choice_num <= len(items):
                # Adjust index for parent directory
                selected_index = choice_num - 1
                if items[selected_index][1] == "PARENT":
                    # This shouldn't happen since we handle 0 separately, but just in case
                    self._go_back()
                else:
                    name, item_type, selected_node = items[selected_index]
                    
                    if item_type == "FOLDER":
                        # Enter directory - update path and clear cache for new location
                        new_path = f"{self.current_path.rstrip('/')}/{name}"
                        self.current_path = new_path
                        
                        # Clear cache for the new path since we're navigating to it
                        if new_path in self.file_cache:
                            del self.file_cache[new_path]
                        
                        print(f"📁 Entered directory: {self.current_path}")
                    else:
                        # Show file details
                        self._show_file_details(selected_node)
            else:
                print("❌ Invalid selection")
                
        except Exception as e:
            print(f"❌ Error handling selection: {str(e)}")
    
    def _show_file_details(self, node):
        """Show detailed information about a file"""
        print(f"\n📄 File Details: {node.name}")
        print("=" * 40)
        
        # Determine type from node
        node_type = "Directory" if node.type == "folder" else "File"
        print(f"Type: {node_type}")
        print(f"Path: {self.current_path}/{node.name}")
        
        # Get size from node data
        size = self._get_node_size(node)
        if size > 0:
            print(f"Size: {self._format_size(size)} ({size} bytes)")
        else:
            print("Size: -")
        
        # Get dates from node data if available
        if hasattr(node, 'data') and node.data:
            if 'dateCreated' in node.data:
                print(f"Created: {node.data['dateCreated']}")
            if 'dateModified' in node.data:
                print(f"Modified: {node.data['dateModified']}")
        
        print("\nOptions:")
        print("d. Download this file")
        print("b. Back to directory listing")
        
        choice = input("Choose option: ").strip().lower()
        
        if choice == 'd':
            self._download_file_prompt(node)
        elif choice == 'b':
            return
        else:
            print("❌ Invalid choice")
    
    def _download_file_prompt(self, node):
        """Handle file download with user prompt"""
        local_filename = input(f"Enter local filename for {node.name} (or 'q' to cancel): ").strip()
        
        if local_filename.lower() == 'q':
            print("Download cancelled")
            return
        
        if not local_filename:
            local_filename = node.name
        
        print(f"📥 Downloading {node.name} to {local_filename}...")
        
        try:
            drive_service = self.auth.get_drive_service()
            if drive_service:
                # Use the actual download method from pyicloud
                with open(local_filename, 'wb') as f:
                    node.download(f)
                print(f"✅ Download completed: {local_filename}")
                size = self._get_node_size(node)
                if size > 0:
                    print(f"   Downloaded {self._format_size(size)}")
            else:
                print("❌ Drive service not available")
                
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
    
    def _get_node_for_path(self, drive_service):
        """Get the DriveNode for the current path by traversing from root"""
        if self.current_path == "/":
            return drive_service.root  # root is a property, not a method
        
        # Traverse the path from root
        current_node = drive_service.root
        if not current_node:
            return None
        
        # Skip empty path parts and root
        path_parts = [p for p in self.current_path.split("/") if p and p != "/"]
        
        # Traverse each part of the path
        for part in path_parts:
            if not part:
                continue
            
            # Find the child node with this name
            found = False
            children = current_node.get_children()
            for child in children:
                if child.name == part:
                    current_node = child
                    found = True
                    break
            
            if not found:
                print(f"❌ Could not find directory: {part}")
                return None
        
        return current_node
    
    def _find_child_node(self, parent_node, child_name):
        """Find a child node by name using get_children()"""
        try:
            # Get all children as DriveNode objects
            children = parent_node.get_children()
            
            # Find the child with matching name
            for child in children:
                if child.name == child_name:
                    return child
            return None
        except Exception:
            return None
    
    def _get_node_size(self, node):
        """Get the size of a node from its data"""
        try:
            if hasattr(node, 'data') and node.data:
                return node.data.get('size', 0)
            return 0
        except Exception:
            return 0
    
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
    
    def search_files(self, query="", file_type=None, min_size=None, max_size=None):
        """
        Search files in iCloud Drive
        
        Args:
            query: Search text to match in filenames
            file_type: Optional file extension to filter by (e.g., 'pdf', 'docx')
            min_size: Optional minimum file size in bytes
            max_size: Optional maximum file size in bytes
            
        Returns:
            List of matching files with metadata
        """
        if not self.auth or not self.auth.is_authenticated():
            print("❌ Not authenticated. Please log in to access your iCloud Drive.")
            return []
        
        # Check session activity
        self.auth.check_session_activity()
        
        try:
            drive_service = self.auth.get_drive_service()
            if not drive_service:
                print("❌ Drive service not available")
                return []
            
            print(f"🔍 Searching iCloud Drive for '{query}'...")
            
            # Start from root and search recursively
            root_node = drive_service.root
            if not root_node:
                print("❌ Could not access iCloud Drive root")
                return []
            
            # Search through the entire drive
            matching_files = self._search_node_recursive(
                root_node, 
                query, 
                file_type, 
                min_size, 
                max_size
            )
            
            if not matching_files:
                print(f"🔍 No files found matching your search criteria")
                return []
            
            print(f"🔍 Found {len(matching_files)} matching files:")
            print("=" * 80)
            
            for i, file_info in enumerate(matching_files[:20], 1):  # Show first 20
                self._display_search_result(file_info, i)
            
            if len(matching_files) > 20:
                print(f"\n📝 Showing first 20 of {len(matching_files)} results")
            
            print("=" * 80)
            return matching_files
            
        except Exception as e:
            print(f"❌ Error searching files: {str(e)}")
            print("   Please check your internet connection and try again.")
            return []
    
    def _search_node_recursive(self, node, query, file_type, min_size, max_size):
        """
        Recursively search through a directory node
        
        Args:
            node: Current DriveNode to search
            query: Search query string
            file_type: File extension filter
            min_size: Minimum size filter
            max_size: Maximum size filter
            
        Returns:
            List of matching files
        """
        matching_files = []
        
        try:
            # Get children of current node
            children = node.get_children()
            
            for child in children:
                # Skip directories for now (we'll recurse into them)
                if child.type == "folder":
                    # Recursively search subdirectories
                    subdir_matches = self._search_node_recursive(
                        child, query, file_type, min_size, max_size
                    )
                    matching_files.extend(subdir_matches)
                else:
                    # Check if this file matches search criteria
                    if self._file_matches_criteria(child, query, file_type, min_size, max_size):
                        file_info = self._get_file_info(child)
                        matching_files.append(file_info)
            
            return matching_files
            
        except Exception as e:
            print(f"⚠️  Error searching directory {getattr(node, 'name', 'unknown')}: {str(e)}")
            return []
    
    def _file_matches_criteria(self, file_node, query, file_type, min_size, max_size):
        """
        Check if a file matches all search criteria
        """
        try:
            # Check query match (filename contains query text)
            if query and not query.lower() in file_node.name.lower():
                return False
            
            # Check file type match
            if file_type:
                file_ext = self._get_file_extension(file_node.name)
                if file_ext.lower() != file_type.lower():
                    return False
            
            # Check size constraints
            file_size = self._get_node_size(file_node)
            if min_size is not None and file_size < min_size:
                return False
            if max_size is not None and file_size > max_size:
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error checking file criteria: {str(e)}")
            return False
    
    def _get_file_extension(self, filename):
        """Extract file extension from filename"""
        try:
            # Handle filenames with multiple dots
            if '.' in filename:
                return filename.rsplit('.', 1)[1].lower()
            return ''
        except Exception:
            return ''
    
    def _get_file_info(self, file_node):
        """Extract comprehensive file information for display"""
        try:
            path = self._get_node_path(file_node)
            size = self._get_node_size(file_node)
            
            return {
                'name': file_node.name,
                'path': path,
                'size': size,
                'type': file_node.type,
                'node': file_node,
                'extension': self._get_file_extension(file_node.name),
                'formatted_size': self._format_size(size)
            }
        except Exception as e:
            print(f"⚠️  Error getting file info: {str(e)}")
            return None
    
    def _get_node_path(self, node):
        """Get the full path of a node"""
        try:
            # This is a simplified approach
            # In a full implementation, we'd track the path during recursion
            return f"{self.current_path}/{node.name}"
        except Exception:
            return node.name
    
    def _display_search_result(self, file_info, index):
        """Display a search result in a user-friendly format"""
        try:
            size_str = file_info['formatted_size']
            extension = file_info['extension'].upper() if file_info['extension'] else ''
            
            print(f"{index:2d}. 📄 {file_info['name']}")
            print(f"     📍 {file_info['path']}")
            print(f"     💾 {size_str} • {extension}")
            
            # Add additional info if available
            if hasattr(file_info['node'], 'date_created'):
                print(f"     📅 Created: {file_info['node'].date_created}")
        except Exception as e:
            print(f"⚠️  Error displaying search result: {str(e)}")
    
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
            
            # Get root node
            if path == "/":
                root_node = drive_service.root  # root is a property, not a method
            else:
                # For simplicity, use root for now
                # Full path support would require traversal
                root_node = drive_service.root  # root is a property, not a method
            
            if not root_node:
                print("No files found in this directory.")
                return
            
            # Get children
            children_names = root_node.dir()
            if not children_names:
                print("No files found in this directory.")
                return
            
            # Get full node objects
            children = []
            for child_name in children_names[:10]:  # Show first 10 files
                child_node = self._find_child_node(root_node, child_name)
                if child_node:
                    children.append(child_node)
            
            print(f"Found {len(children)} items:")
            for i, node in enumerate(children, 1):
                node_type = "Directory" if node.type == "folder" else "File"
                size_str = self._format_size(self._get_node_size(node))
                print(f"{i}. {node_type} - {node.name} ({size_str})")
            
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
