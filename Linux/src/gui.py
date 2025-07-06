#!/usr/bin/env python3
# filepath: /media/thestalrus/OS/Users/manth/Documents/GitHub/PConT/Linux/src/gui.py
import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import time
from datetime import datetime
import io
import contextlib

# Import our own modules
from config import (
    chains, extract_ip, extract_protocol_port, is_proxy_online,
    check_required_proxies, write_to_proxychains_conf,
    pcont_dir, pcont_db_path, pcont_config_path,
    load_user_config, save_user_config, update_proxy_database,
    get_proxy_speed, get_proxy_details, test_proxy_connection
)

class RedirectText:
    """Redirect stdout to a tkinter Text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")
        
    def flush(self):
        pass

class ProxyChainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PConT - Proxy Configuration Tool")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set theme and styling
        style = ttk.Style()
        style.theme_use('classic')  # or 'alt', 'default', 'classic'
        
        # Define custom colors
        bg_color = "#2E3440"  # Dark blue-grey
        fg_color = "#ECEFF4"  # Light grey
        accent_color = "#88C0D0"  # Light blue
        button_color = "#5E81AC"  # Blue
        
        # Configure styles
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=button_color, foreground=fg_color)
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
        style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        style.configure("TNotebook", background=bg_color)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", accent_color)],
                 foreground=[("selected", "#000000")])
        
        # Configure root background
        self.root.configure(bg=bg_color)
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.advanced_tab = ttk.Frame(self.notebook)
        self.log_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Setup")
        self.notebook.add(self.advanced_tab, text="Advanced")
        self.notebook.add(self.log_tab, text="Log")
        self.notebook.add(self.about_tab, text="About")
        
        # Initialize the tabs
        self.init_setup_tab()
        self.init_advanced_tab()
        self.init_log_tab()
        self.init_about_tab()
        
        # Load configuration
        self.config = load_user_config()
        self.load_config_to_ui()
        
        # Process status
        self.is_processing = False
        
    def init_setup_tab(self):
        """Initialize the Setup tab"""
        # Chain Type Frame
        chain_frame = ttk.LabelFrame(self.setup_tab, text="Chain Type")
        chain_frame.pack(fill="x", padx=10, pady=10)
        
        # Chain Type Radio Buttons
        self.chain_var = tk.IntVar(value=1)
        
        for i, chain_name in enumerate(["Strict Chain", "Random Chain", 
                                      "Dynamic Chain", "Round-Robin Chain"], 1):
            ttk.Radiobutton(chain_frame, text=chain_name, value=i, 
                           variable=self.chain_var).pack(anchor="w", padx=20, pady=5)
        
        # Chain Length Frame
        length_frame = ttk.LabelFrame(self.setup_tab, text="Chain Length")
        length_frame.pack(fill="x", padx=10, pady=10)
        
        # Chain Length Slider
        self.length_var = tk.IntVar(value=10)
        ttk.Label(length_frame, text="Number of proxies to use (0-25):").pack(anchor="w", padx=20, pady=5)
        self.length_slider = ttk.Scale(length_frame, from_=0, to=25, 
                                     variable=self.length_var, orient="horizontal")
        self.length_slider.pack(fill="x", padx=20, pady=5)
        
        # Display the value
        self.length_label = ttk.Label(length_frame, text="10")
        self.length_label.pack(anchor="e", padx=20, pady=5)
        
        # Update label when slider moves
        def update_length_label(event):
            self.length_label.config(text=str(int(self.length_slider.get())))
        
        self.length_slider.bind("<Motion>", update_length_label)
        
        # Proxy Type Frame
        type_frame = ttk.LabelFrame(self.setup_tab, text="Proxy Types")
        type_frame.pack(fill="x", padx=10, pady=10)
        
        # Proxy Type Checkboxes
        self.http_var = tk.BooleanVar(value=True)
        self.socks4_var = tk.BooleanVar(value=True)
        self.socks5_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(type_frame, text="HTTP", variable=self.http_var).pack(anchor="w", padx=20, pady=5)
        ttk.Checkbutton(type_frame, text="SOCKS4", variable=self.socks4_var).pack(anchor="w", padx=20, pady=5)
        ttk.Checkbutton(type_frame, text="SOCKS5", variable=self.socks5_var).pack(anchor="w", padx=20, pady=5)
        
        # Action Buttons
        button_frame = ttk.Frame(self.setup_tab)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Button(button_frame, text="Configure Proxies", command=self.run_configuration).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_to_default).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Save Configuration", command=self.save_configuration).pack(side="left", padx=10)
        
    def init_advanced_tab(self):
        """Initialize the Advanced tab"""
        # Auto-rotation Frame
        rotation_frame = ttk.LabelFrame(self.advanced_tab, text="Proxy Rotation")
        rotation_frame.pack(fill="x", padx=10, pady=10)
        
        # Auto-rotation Checkbox
        self.rotation_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rotation_frame, text="Enable Automatic Proxy Rotation", 
                       variable=self.rotation_var).pack(anchor="w", padx=20, pady=5)
        
        # Rotation Interval
        interval_frame = ttk.Frame(rotation_frame)
        interval_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(interval_frame, text="Rotation Interval (minutes):").pack(side="left", padx=5)
        self.interval_var = tk.StringVar(value="60")
        ttk.Entry(interval_frame, textvariable=self.interval_var, width=10).pack(side="left", padx=5)
        
        # Speed Filtering Frame
        speed_frame = ttk.LabelFrame(self.advanced_tab, text="Speed Filtering")
        speed_frame.pack(fill="x", padx=10, pady=10)
        
        # Speed Filtering Checkbox
        self.speed_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(speed_frame, text="Filter Proxies by Speed", 
                       variable=self.speed_var).pack(anchor="w", padx=20, pady=5)
        
        # Max Ping Time
        ping_frame = ttk.Frame(speed_frame)
        ping_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(ping_frame, text="Maximum Ping Time (ms):").pack(side="left", padx=5)
        self.ping_var = tk.StringVar(value="1000")
        ttk.Entry(ping_frame, textvariable=self.ping_var, width=10).pack(side="left", padx=5)
        
        # Country Filtering Frame
        country_frame = ttk.LabelFrame(self.advanced_tab, text="Country Filtering")
        country_frame.pack(fill="x", padx=10, pady=10)
        
        # Country dropdown
        country_inner_frame = ttk.Frame(country_frame)
        country_inner_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(country_inner_frame, text="Filter by Country:").pack(side="left", padx=5)
        
        # Country codes (common ones)
        countries = [
            ("All Countries", "all"),
            ("United States", "US"),
            ("United Kingdom", "GB"),
            ("Germany", "DE"),
            ("France", "FR"),
            ("Canada", "CA"),
            ("Australia", "AU"),
            ("Japan", "JP"),
            ("India", "IN"),
            ("Brazil", "BR"),
            ("Russia", "RU"),
            ("China", "CN")
        ]
        
        self.country_var = tk.StringVar(value="all")
        country_combo = ttk.Combobox(country_inner_frame, textvariable=self.country_var, 
                                    state="readonly", width=20)
        country_combo['values'] = [f"{name} ({code})" for name, code in countries]
        country_combo.current(0)
        country_combo.pack(side="left", padx=5)
        
        # Apply button
        ttk.Button(self.advanced_tab, text="Apply Advanced Settings", 
                  command=self.apply_advanced_settings).pack(pady=20)
        
    def init_log_tab(self):
        """Initialize the Log tab"""
        # Create a frame for the log
        log_frame = ttk.Frame(self.log_tab)
        log_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create a scrolled text widget for the log
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                               bg="#2E3440", fg="#ECEFF4",
                                               font=("Courier", 10))
        self.log_text.pack(expand=True, fill="both")
        self.log_text.configure(state="disabled")
        
        # Create a frame for log actions
        action_frame = ttk.Frame(self.log_tab)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        # Add buttons for log actions
        ttk.Button(action_frame, text="Clear Log", command=self.clear_log).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Save Log", command=self.save_log).pack(side="left", padx=5)
        
    def init_about_tab(self):
        """Initialize the About tab"""
        # Add a frame for the about content
        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Add the ASCII art
        ttk.Label(about_frame, text="PConT - Proxy Configuration Tool", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # ASCII art
        ascii_art = """
██████╗  ██████╗ ██████╗ ███╗   ██╗████████╗
██╔══██╗██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝
██████╔╝██║     ██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██║     ██║   ██║██║╚██╗██║   ██║   
██║     ╚██████╗╚██████╔╝██║ ╚████║   ██║   
╚═╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
        """
        
        ttk.Label(about_frame, text=ascii_art, font=("Courier", 10)).pack(pady=10)
        
        ttk.Label(about_frame, text="An Open Source Linux tool to configure your Proxychains",
                 font=("Arial", 10)).pack(pady=5)
        
        ttk.Label(about_frame, text="By Anorak001",
                 font=("Arial", 10, "italic")).pack(pady=5)
        
        ttk.Label(about_frame, text=f"Version: 2.0 - {datetime.now().strftime('%Y-%m-%d')}",
                 font=("Arial", 10)).pack(pady=5)
        
        # Add a separator
        ttk.Separator(about_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Add usage instructions
        ttk.Label(about_frame, text="Usage Instructions:", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        instructions = """
1. Configure your proxy chain settings in the Setup tab
2. Use the Advanced tab for more specific configurations
3. Click 'Configure Proxies' to apply your settings
4. Run commands with proxychains in the terminal:
   proxychains <command>
        """
        
        ttk.Label(about_frame, text=instructions, 
                 justify="left").pack(anchor="w", pady=5)
        
    def load_config_to_ui(self):
        """Load configuration values to UI elements"""
        # Set chain type
        chain_type = self.config.get("chain", "strict_chain")
        for i, chain_value in chains.items():
            if chain_value == chain_type:
                self.chain_var.set(i)
                break
        
        # Set chain length
        self.length_var.set(self.config.get("chain_length", 10))
        self.length_label.config(text=str(self.config.get("chain_length", 10)))
        
        # Set proxy types
        preferred_types = self.config.get("preferred_types", ["http", "socks4", "socks5"])
        self.http_var.set("http" in preferred_types)
        self.socks4_var.set("socks4" in preferred_types)
        self.socks5_var.set("socks5" in preferred_types)
        
        # Set advanced options
        self.rotation_var.set(self.config.get("auto_rotate", False))
        self.interval_var.set(str(self.config.get("rotation_interval_minutes", 60)))
        
        # Set speed filtering
        max_ping = self.config.get("max_ping_time")
        self.speed_var.set(max_ping is not None)
        if max_ping is not None:
            self.ping_var.set(str(max_ping))
            
        # Set country
        self.country_var.set(self.config.get("country_filter", "all"))
        
    def save_configuration(self):
        """Save the current configuration to file"""
        # Get values from UI
        chain_type = chains[self.chain_var.get()]
        chain_length = int(self.length_var.get())
        
        preferred_types = []
        if self.http_var.get():
            preferred_types.append("http")
        if self.socks4_var.get():
            preferred_types.append("socks4")
        if self.socks5_var.get():
            preferred_types.append("socks5")
            
        # Advanced settings
        auto_rotate = self.rotation_var.get()
        try:
            rotation_interval = int(self.interval_var.get())
        except ValueError:
            rotation_interval = 60
            
        use_speed_filter = self.speed_var.get()
        try:
            max_ping_time = int(self.ping_var.get()) if use_speed_filter else None
        except ValueError:
            max_ping_time = 1000 if use_speed_filter else None
            
        country_filter = self.country_var.get()
        # Extract country code if selected from dropdown
        if "(" in country_filter and ")" in country_filter:
            country_filter = country_filter.split("(")[1].split(")")[0]
        
        # Create config dict
        config = {
            "chain": chain_type,
            "chain_length": chain_length,
            "preferred_types": preferred_types,
            "auto_rotate": auto_rotate,
            "rotation_interval_minutes": rotation_interval,
            "max_ping_time": max_ping_time,
            "country_filter": country_filter
        }
        
        # Save to file
        self.config = config
        if save_user_config(config):
            messagebox.showinfo("Success", "Configuration saved successfully")
            self.log("Configuration saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save configuration")
            self.log("Failed to save configuration", error=True)
            
    def reset_to_default(self):
        """Reset configuration to default values"""
        self.chain_var.set(1)  # strict_chain
        self.length_var.set(10)
        self.length_label.config(text="10")
        self.http_var.set(True)
        self.socks4_var.set(True)
        self.socks5_var.set(True)
        self.rotation_var.set(False)
        self.interval_var.set("60")
        self.speed_var.set(False)
        self.ping_var.set("1000")
        self.country_var.set("all")
        
        messagebox.showinfo("Reset", "Settings reset to default values")
        self.log("Settings reset to default values")
        
    def apply_advanced_settings(self):
        """Apply advanced settings"""
        self.save_configuration()
        messagebox.showinfo("Advanced Settings", "Advanced settings applied")
        self.log("Advanced settings applied")
        
    def run_configuration(self):
        """Run the proxy configuration process"""
        if self.is_processing:
            messagebox.showwarning("Processing", "Configuration is already in progress")
            return
            
        # Save current config
        self.save_configuration()
        
        # Start configuration in a separate thread
        self.is_processing = True
        threading.Thread(target=self._run_configuration_thread, daemon=True).start()
        
        # Switch to log tab
        self.notebook.select(2)  # Index of the log tab
        
    def _run_configuration_thread(self):
        """Run configuration in a separate thread"""
        # Redirect stdout to our log widget
        old_stdout = sys.stdout
        sys.stdout = RedirectText(self.log_text)
        
        try:
            # Clear the log
            self.clear_log()
            
            # Log start
            self.log("Starting proxy configuration...")
            self.log(f"Configuration: {json.dumps(self.config, indent=2)}")
            
            # Load proxies
            self.log("Loading proxies from free_proxies.txt...")
            try:
                with open("free_proxies.txt") as f:
                    proxies = f.readlines()
                self.log(f"Loaded {len(proxies)} proxies")
            except FileNotFoundError:
                self.log("Error: File 'free_proxies.txt' not found.", error=True)
                
                # Ask if user wants to run the scraper
                if messagebox.askyesno("File Not Found", 
                                       "free_proxies.txt not found. Run the scraper to download proxies?"):
                    self.log("Running scraper to download proxies...")
                    
                    # Build command based on config
                    cmd = ["python3", "../src/scraper.py"]
                    
                    # Add proxy types
                    proxy_types = []
                    if self.http_var.get():
                        proxy_types.append("http")
                    if self.socks4_var.get():
                        proxy_types.append("socks4")
                    if self.socks5_var.get():
                        proxy_types.append("socks5")
                    
                    if proxy_types:
                        cmd.extend(["--proxy-types", ",".join(proxy_types)])
                        
                    # Add country filter if set
                    country = self.country_var.get()
                    if country != "all":
                        cmd.extend(["--country", country])
                        
                    # Run the scraper
                    self.log(f"Running command: {' '.join(cmd)}")
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        self.log(result.stdout)
                        if result.stderr:
                            self.log(f"Error: {result.stderr}", error=True)
                            
                        # Try to load proxies again
                        if os.path.exists("free_proxies.txt"):
                            with open("free_proxies.txt") as f:
                                proxies = f.readlines()
                            self.log(f"Loaded {len(proxies)} proxies")
                        else:
                            self.log("Error: Failed to create free_proxies.txt", error=True)
                            return
                    except Exception as e:
                        self.log(f"Error running scraper: {e}", error=True)
                        return
                else:
                    return
            
            # Check and select required number of proxies
            self.log(f"Checking and selecting {self.config['chain_length']} proxies...")
            selected_proxies = check_required_proxies(proxies, self.config["chain_length"], self.config)
            
            if not selected_proxies:
                self.log("Error: No suitable proxies found", error=True)
                return
                
            self.log(f"Selected {len(selected_proxies)} proxies")
            
            # Write configuration
            self.log("Writing configuration to proxychains.conf and proxychains4.conf...")
            try:
                write_to_proxychains_conf(self.config["chain"], selected_proxies)
                self.log("Configuration files written successfully")
            except Exception as e:
                self.log(f"Error writing configuration: {e}", error=True)
                return
                
            # Set up rotation if enabled
            if self.config.get("auto_rotate"):
                try:
                    from config import setup_rotation_daemon
                    setup_rotation_daemon(self.config)
                    self.log(f"Automatic proxy rotation set up (every {self.config['rotation_interval_minutes']} minutes)")
                except Exception as e:
                    self.log(f"Error setting up rotation: {e}", error=True)
            
            # Complete
            self.log("\nProxy setup completed successfully!")
            self.log("To use proxychains, run your commands with proxychains like this:")
            self.log("  proxychains <command>")
            self.log("\nFor example, to run curl through proxychains:")
            self.log("  proxychains curl http://example.com")
            
            # Show message box on completion
            self.root.after(0, lambda: messagebox.showinfo("Success", "Proxy configuration completed successfully"))
            
        except Exception as e:
            self.log(f"Unexpected error: {e}", error=True)
            # Show error message
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            self.is_processing = False
    
    def log(self, message, error=False):
        """Add message to the log"""
        self.log_text.configure(state="normal")
        
        # Add timestamp
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        
        # Set color based on error status
        if error:
            self.log_text.insert(tk.END, timestamp, "timestamp")
            self.log_text.insert(tk.END, message + "\n", "error")
        else:
            self.log_text.insert(tk.END, timestamp, "timestamp")
            self.log_text.insert(tk.END, message + "\n", "normal")
            
        # Configure tags
        self.log_text.tag_configure("timestamp", foreground="#88C0D0")
        self.log_text.tag_configure("normal", foreground="#ECEFF4")
        self.log_text.tag_configure("error", foreground="#BF616A")
        
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        
    def clear_log(self):
        """Clear the log text"""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
        
    def save_log(self):
        """Save log content to a file"""
        from tkinter import filedialog
        
        # Get filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log As"
        )
        
        if not filename:
            return
            
        try:
            # Get log content
            self.log_text.configure(state="normal")
            log_content = self.log_text.get(1.0, tk.END)
            self.log_text.configure(state="disabled")
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(log_content)
                
            messagebox.showinfo("Success", f"Log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")

def main():
    # Create root window
    root = tk.Tk()
    
    # Create the app
    app = ProxyChainApp(root)
    
    # Run the main loop
    root.mainloop()
    
if __name__ == "__main__":
    main()
