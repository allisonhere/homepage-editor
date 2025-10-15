
#!/bin/bash

# Get the absolute path to the script's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if virtual environment exists
if [ -d "$DIR/venv" ]; then
    echo "Using virtual environment..."
    PYTHON_CMD="$DIR/venv/bin/python"
else
    echo "Using system Python..."
    PYTHON_CMD="python3"
fi

# Check if requirements are installed
if ! $PYTHON_CMD -c "import yaml, PIL" 2>/dev/null; then
    echo "Installing required dependencies..."
    $PYTHON_CMD -m pip install PyYAML Pillow cairosvg
fi

# Run the simple homepage editor
echo "Starting Simple Homepage Editor..."
$PYTHON_CMD "$DIR/simple_homepage_gui.py"
