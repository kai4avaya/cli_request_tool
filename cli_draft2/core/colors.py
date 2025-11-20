"""Color scheme constants for the CLI.

Simple and clean color palette used throughout the application.
Rich supports hex colors in format: #RRGGBB
"""
# Header title: Blue (#6b8bd6) - Keywords
COLOR_HEADER = "#6b8bd6"

# Rank column: Gray (#999999) - Punctuation
COLOR_RANK = "#999999"

# Name column: Purple (#8b7bd6) - Functions
COLOR_NAME = "#8b7bd6"

# Speed column: Green (#7bd6a8) - Operators
COLOR_SPEED = "#7bd6a8"

# Accuracy column: Pink (#d67b9f) - Strings/special
COLOR_ACCURACY = "#d67b9f"

# Total column: Orange (#d6a87b)
COLOR_TOTAL = "#d6a87b"

# Additional colors for general use (using Rich markdown format)
COLOR_SUCCESS = COLOR_SPEED  # Green for success messages
COLOR_ERROR = COLOR_ACCURACY  # Pink for errors
COLOR_INFO = COLOR_HEADER  # Blue for info messages
