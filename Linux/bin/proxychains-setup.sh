#!/usr/bin/bash
# filepath: /media/thestalrus/OS/Users/manth/Documents/GitHub/PConT/Linux/bin/proxychains-setup.sh

# Function to run commands with sudo
run_with_sudo() {
    if [ "$(id -u)" -ne "0" ]; then
        echo "This script requires root privileges. Attempting to elevate with sudo..."
        sudo "$0" "$@"
        exit
    fi
}

# Function to display help
show_help() {
    echo "Usage: proxychains-setup [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help            Show this help message and exit"
    echo "  -g, --gui             Launch the GUI interface"
    echo "  -c, --cli             Use the CLI interface with prompts"
    echo "  -n, --non-interactive Configure using saved settings without prompts"
    echo "  -u, --update          Update the proxy list before configuring"
    echo "  -v, --validate        Validate proxies before configuring"
    echo "  --chain=TYPE          Chain type (1=strict, 2=random, 3=dynamic, 4=round-robin)"
    echo "  --length=N            Chain length (0-25)"
    echo "  --types=LIST          Comma-separated proxy types (http,socks4,socks5)"
    echo "  --country=CODE        Country code filter (e.g., US, DE, all)"
    echo ""
    echo "Examples:"
    echo "  proxychains-setup -g                  # Launch the GUI"
    echo "  proxychains-setup -u -v               # Update and validate proxies, then configure interactively"
    echo "  proxychains-setup -n                  # Configure using saved settings"
    echo "  proxychains-setup --chain=2 --length=5 --types=socks4,socks5  # Configure with specific settings"
    echo ""
}

# Parse command-line arguments
GUI_MODE=false
CLI_MODE=false
NON_INTERACTIVE=false
UPDATE_PROXIES=false
VALIDATE_PROXIES=false
CHAIN_TYPE=""
CHAIN_LENGTH=""
PROXY_TYPES=""
COUNTRY_FILTER=""

for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            exit 0
            ;;
        -g|--gui)
            GUI_MODE=true
            shift
            ;;
        -c|--cli)
            CLI_MODE=true
            shift
            ;;
        -n|--non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        -u|--update)
            UPDATE_PROXIES=true
            shift
            ;;
        -v|--validate)
            VALIDATE_PROXIES=true
            shift
            ;;
        --chain=*)
            CHAIN_TYPE="${arg#*=}"
            shift
            ;;
        --length=*)
            CHAIN_LENGTH="${arg#*=}"
            shift
            ;;
        --types=*)
            PROXY_TYPES="${arg#*=}"
            shift
            ;;
        --country=*)
            COUNTRY_FILTER="${arg#*=}"
            shift
            ;;
        *)
            # Unknown option
            echo "Unknown option: $arg"
            show_help
            exit 1
            ;;
    esac
done

# Run the function to check and request sudo
run_with_sudo "$@"

# Navigate to the directory where the Python scripts are located
# Assuming that src and bin are in the same parent directory
PARENT_DIR="$(dirname "$(realpath "$0")")"
SRC_DIR="$PARENT_DIR/../src"
cd "$SRC_DIR" || exit

# Display the intro
python3 intro.py

# Update proxies if requested
if [ "$UPDATE_PROXIES" = true ]; then
    echo "Updating the proxylist from the API..."
    
    # Build scraper command with any provided options
    SCRAPER_CMD="python3 scraper.py"
    
    if [ -n "$PROXY_TYPES" ]; then
        SCRAPER_CMD="$SCRAPER_CMD --proxy-types=$PROXY_TYPES"
    fi
    
    if [ -n "$COUNTRY_FILTER" ]; then
        SCRAPER_CMD="$SCRAPER_CMD --country=$COUNTRY_FILTER"
    fi
    
    # Run the scraper
    eval "$SCRAPER_CMD"
else
    # Check if free_proxies.txt exists, if not, run scraper
    if [ ! -f "free_proxies.txt" ]; then
        echo "No proxy list found. Updating the proxylist from the API..."
        python3 scraper.py
    fi
fi

# Validate proxies if requested
if [ "$VALIDATE_PROXIES" = true ]; then
    echo "Validating proxies..."
    python3 validator.py
fi

# Choose which interface to use
if [ "$GUI_MODE" = true ]; then
    # Check if Tkinter is available
    if python3 -c "import tkinter" &>/dev/null; then
        echo "Launching GUI interface..."
        python3 gui.py
        exit 0
    else
        echo "Error: Tkinter not available. GUI mode requires Python with Tkinter."
        echo "Falling back to interactive CLI mode."
        CLI_MODE=true
    fi
fi

if [ "$NON_INTERACTIVE" = true ]; then
    echo "Running in non-interactive mode..."
    
    # Build command with any provided options
    CMD="python3 cli.py configure"
    
    if [ -n "$CHAIN_TYPE" ]; then
        CMD="$CMD --chain-type=$CHAIN_TYPE"
    fi
    
    if [ -n "$CHAIN_LENGTH" ]; then
        CMD="$CMD --chain-length=$CHAIN_LENGTH"
    fi
    
    if [ -n "$PROXY_TYPES" ]; then
        CMD="$CMD --proxy-types=$PROXY_TYPES"
    fi
    
    if [ -n "$COUNTRY_FILTER" ]; then
        CMD="$CMD --country=$COUNTRY_FILTER"
    fi
    
    # Run the command
    eval "$CMD"
    
elif [ "$CLI_MODE" = true ]; then
    echo "Running CLI with interactive prompts..."
    python3 cli.py configure
else
    # Default to config.py for backward compatibility
    echo "Running Configuration Script with admin privileges..."
    python3 config.py
fi

echo "Setup completed."

