# Asusctl GUI

A simple GUI for controlling ASUS laptop profiles and keyboard RGB
lighting using `asusctl` on Linux.

The project is written with Python and PySide6 and is designed to provide
a small and easy-to-use interface instead of using `asusctl` commands
directly from the terminal.

## Features

- Change ASUS system profiles
- Detect the current system profile
- Change keyboard backlight color
- Support multiple Aura effects
- Simple dark interface
- Uses `QProcess` to communicate with `asusctl`
- Handles command errors and missing `asusctl`
- No database
- No external services

## Supported Effects

```text
static
breathe
rainbow-cycle
rainbow-wave
stars
rain
highlight
laser
ripple
pulse
comet
flash
```

## Supported Profiles

```text
Quiet
Balanced
Performance
```

## Requirements

- Linux
- Python 3.10+
- PySide6
- asusctl
- asusd
- ASUS laptop with supported hardware

Not every ASUS laptop supports every Aura effect.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/asusctl-gui.git
cd asusctl-gui
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the Python dependency:

```bash
pip install PySide6
```

Make sure `asusctl` is installed:

```bash
asusctl --help
```

You can also check the current profile:

```bash
asusctl profile get
```

## Run

Start the application with:

```bash
python main.py
```

## Project Structure

```text
asusctl-gui/
├── main.py
├── README.md
├── LICENSE
├── requirements.txt
└── styles/
    └── dark.qss
```

## How It Works

The application uses `QProcess` to execute `asusctl` commands.

For example, selecting a red static backlight runs:

```bash
asusctl aura effect static -c ff0000
```

Changing the system profile to Performance runs:

```bash
asusctl profile set performance
```

The GUI does not communicate with the ASUS hardware directly.
`asusctl` and `asusd` handle the hardware communication.

## Why QProcess?

`QProcess` allows the application to execute `asusctl` without blocking
the Qt interface.

Each command gets its own `QProcess`, so different commands don't share
stdout, stderr or process state.

## Troubleshooting

### asusctl not found

If the application says:

```text
Could not start asusctl
```

check whether it is available:

```bash
which asusctl
```

Then try:

```bash
asusctl --help
```

### asusd is not running

Check the service:

```bash
systemctl status asusd
```

If needed:

```bash
sudo systemctl enable --now asusd
```

### An Aura effect doesn't work

Your laptop may not support that particular effect.

You can check the Aura options supported by your installation:

```bash
asusctl aura --help
```

Hardware support depends on the ASUS laptop model, firmware and
`asusctl` support.

### Profile detection doesn't work

Run:

```bash
asusctl profile get
```

and check the output.

The application tries to detect one of these profiles:

```text
Quiet
Balanced
Performance
```

## Development

The project intentionally keeps the code simple.

Main technologies:

- Python
- PySide6
- QProcess
- Qt Style Sheets
- asusctl

## Future Ideas

Some possible improvements:

- Second color picker
- Aura speed selector
- Rainbow direction selector
- Keyboard brightness control
- Save favorite effects
- System tray support
- Start with system
- Hardware capability detection
- Custom effect presets

## Contributing

Pull requests are welcome.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the application.
5. Commit your changes.
6. Open a Pull Request.

Example:

```bash
git checkout -b feature/new-effect
```

```bash
git add .
git commit -m "Add new effect"
git push origin feature/new-effect
```

## Disclaimer

This project is not affiliated with or endorsed by ASUS.

It is an independent graphical frontend for `asusctl`.

Hardware compatibility depends on your laptop and the features supported
by `asusctl` and `asusd`.

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for more information.
