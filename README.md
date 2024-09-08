# ScanTheBox

`ScanTheBox` is a Python-based automated tool designed to streamline the enumeration and reconnaissance process for HackTheBox (HTB) machines. It uses tools like `nmap`, `gobuster`, and `whatweb` to identify open services and perform deep scans.

## Disclaimer
This project is currently under development and may contain bugs or incomplete features. Use at your own risk. Contributions and feedback are welcome to help improve the tool.

## Features (done or in progress)

- Automatic network scanning with `nmap` (common ports and full port scans)
- HTTP service detection with follow-up analysis using `whatweb` and `gobuster`
- DNS service enumeration and zone transfer checks
- Easy-to-use command-line interface with interactive shell for loaded scans
- Organized output into dedicated folders for each scan

## Installation

Make sure you have the required tools installed. You can install the Python dependencies using `pip`.

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/ScanTheBox.git
   cd ScanTheBox
   ```

2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the following external tools are installed:
   - take a look at modules.utils.check_tools()

## Usage

You can start a new scan or load an existing one using the following commands:

### Start a New Scan

```bash
python scanthebox.py new <hostname>
```

Note: hostname must be added in /etc/hosts before (the application will try to resolve it first)
This will create a new directory for the host, run an nmap scan on the target, and perform other checks depending on the services detected.

### Load an Existing Scan

```bash
python scanthebox.py load <hostname>
```

This will enter an interactive shell where you can continue working with the results from a previous scan.

## Configuration

`ScanTheBox` uses a YAML configuration file (`scanthebox.yaml`) to set scan parameters. You can adjust the settings according to your needs.

## Example Workflow

1. Start a new scan:
   ```bash
   python scanthebox.py new target.htb
   ```

2. If HTTP services are detected, `whatweb` and `gobuster` will run automatically in separate windows.

3. For DNS services, the script performs DNS enumeration using `dig`.

4. Load a previous scan:
   ```bash
   python scanthebox.py load target.htb
   ```

## Todo
[] Create the HTTP module
[] Extract HTTP and DNS from `nmap_fingerprint`, that should be independent and should work from the output
[] Save DNS output
[] Add enum4linux command for port 445: `enum4linux -a solarlab.htb`
[] load mode: check if workspace already exists

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.