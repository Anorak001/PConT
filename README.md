# PConT - Proxy Configuration Tool

```
██████╗  ██████╗ ██████╗ ███╗   ██╗████████╗
██╔══██╗██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝
██████╔╝██║     ██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██║     ██║   ██║██║╚██╗██║   ██║   
██║     ╚██████╗╚██████╔╝██║ ╚████║   ██║   
╚═╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
```


 
An open-source Linux tool to automatically configure your Proxychains with advanced features for proxy management.

## Features

- **Multiple Chain Types**: Configure proxies with strict, random, dynamic, or round-robin chaining
- **Automatic Proxy Rotation**: Schedule proxy changes at customizable intervals
- **Proxy Filtering**: Filter proxies by speed, country, or type (HTTP, SOCKS4, SOCKS5)
- **GUI and CLI Interfaces**: Use either graphical or command-line interfaces
- **Proxy Scraping**: Automatically fetch fresh proxies from multiple sources
- **Proxy Validation**: Test and validate proxy connections
- **Configuration Management**: Save, load, and reset proxy configurations

## Installation

### Prerequisites

- Python 3.6 or higher
- Proxychains or Proxychains-NG installed
- Required Python packages (see requirements below)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Anorak001/PConT.git
   cd PConT
   ```

2. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 python-socks pysocks geoip2
   ```

3. Make scripts executable:
   ```bash
   chmod +x Linux/bin/*.sh
   ```

## Usage

### Command Line Interface (CLI)

#### Configure Proxychains

```bash
python3 Linux/src/cli.py configure [options]
```

Options:
- `--chain-type`: Chain type (1=strict, 2=random, 3=dynamic, 4=round-robin)
- `--chain-length`: Length of the proxy chain (0-25)
- `--proxy-types`: Comma-separated proxy types (http,socks4,socks5)
- `--auto-rotate`: Enable automatic proxy rotation
- `--rotation-interval`: Proxy rotation interval in minutes
- `--max-ping`: Maximum ping time in milliseconds
- `--country`: Country code to filter proxies (e.g., US, DE)
- `--proxy-file`: File containing list of proxies
- `--no-save`: Do not save configuration to file

#### Update Proxy List

```bash
python3 Linux/src/cli.py update [options]
```

Options:
- `--proxy-types`: Comma-separated proxy types to fetch
- `--country`: Country code to filter proxies
- `--limit`: Maximum number of proxies to fetch
- `--timeout`: Maximum timeout in seconds for proxy requests
- `--output`: Output file name

#### Show Current Configuration

```bash
python3 Linux/src/cli.py status [--json]
```

#### Reset Configuration

```bash
sudo python3 Linux/src/cli.py reset [--defaults]
```

### Graphical User Interface (GUI)

Launch the GUI interface:

```bash
python3 Linux/src/gui.py
```

### Helper Scripts

Several helper scripts are available in the `Linux/bin` directory:

- `proxychains-setup.sh`: Quick setup script
- `proxychains-reset.sh`: Reset all configurations
- `proxychains-help.sh`: Show help information
- `pcont-verify.sh`: Verify if PCONT is working correctly

## Testing Your Setup

To check if your PCONT setup is running and functional:

1. Check the status of your configuration:
   ```bash
   python3 Linux/src/cli.py status
   ```

2. Test with a simple curl request:
   ```bash
   proxychains curl https://api.ipify.org
   ```

3. Verify the configuration files:
   ```bash
   cat /etc/proxychains.conf
   ```

4. Use the built-in verification script:
   ```bash
   ./Linux/bin/pcont-verify.sh
   ```

## Directory Structure

```
PConT/
├── Docs/
│   ├── checks.txt
│   ├── demo.zip
│   ├── README.md
│   └── project-outline/
│       ├── Blueprint.drawio
│       └── Screenshot.png
└── Linux/
    ├── bin/
    │   ├── pcont-verify.sh
    │   ├── proxychains-help.sh
    │   ├── proxychains-reset.sh
    │   └── proxychains-setup.sh
    └── src/
        ├── cli.py
        ├── config.py
        ├── gui.py
        ├── intro.py
        ├── scraper.py
        └── validator.py
```

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4
  - python-socks
  - pysocks
  - geoip2
  - tkinter (for GUI)

## Common Issues and Solutions

- **Permission issues**: Some operations require root permissions. Use `sudo` when running the reset command.
- **No proxies found**: Run the update command to fetch fresh proxies.
- **Slow connection**: Try filtering proxies by speed using the `--max-ping` option.
- **Configuration not applied**: Make sure you have write permissions for the proxychains configuration files.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Special thanks to the Proxychains project
- Logo ASCII art generated with https://patorjk.com/software/taag

---

Created by Anorak001  