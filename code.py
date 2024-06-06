import time
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal

# You can display in 'GBP', 'EUR' or 'USD'
CURRENCY = "USD"
SYMBOLS = {'USD': '$', 'EUR': '€', 'GBP': '£'}
FONT = "/fonts/6x10.bdf"

# Set up where we'll be fetching data from
TOKEN = ""
STOCK = "SPY"
DATA_SOURCE = "https://finnhub.io/api/v1/quote?symbol=" + STOCK + "&token=" + TOKEN

# Parse the Json data
CURRENT_PRICE = ["c"]  # Current price
DAY_HIGH = ["h"]  # High price of the day
DAY_LOW = ["l"]  # Low price of the day
PREVIOUS_CLOSE = ["pc"]  # Previous Close
DAY_CHANGE = ["d"]  # Day change
DAY_CHANGE_PERCENT = ["dp"] # Day change Percentage

# Get the JSON data
matrixportal = MatrixPortal(
    url=DATA_SOURCE,
    json_path=(CURRENT_PRICE, DAY_HIGH, DAY_LOW, PREVIOUS_CLOSE, DAY_CHANGE, DAY_CHANGE_PERCENT),
    status_neopixel=board.NEOPIXEL,
    debug=True,
    width=64,
    height=64
)

positions = [(0, 6), (0, 16), (0, 26), (0, 36), (0, 46), (0, 56)]
default_colors = [0xC0C0C0, 0x9f316c, 0x631f44, 0x31349f, 0x8533FF, 0x8533FF]
labels = [STOCK, "▲H", "▼L", "PC", "CH", "%C"]

def format_currency(value, label, is_change=False):
    symbol = SYMBOLS.get(CURRENCY, '$')
    if is_change:
        formatted_value = f"{value:+.1f}%"
    else:
        formatted_value = f"{symbol}{value:5.1f}"
    return f"{formatted_value} {label}"

# Function to set text color based on change value
def determine_color(change_value):
    if change_value > 0:
        return 0x00FF00  # Green for positive change
    elif change_value < 0:
        return 0xFF0000  # Red for negative change
    else:
        return 0xFFFFFF  # White for no change

# Add text elements with initial color setup
for index, pos in enumerate(positions):
    matrixportal.add_text(
        text_transform=lambda val, idx=index: format_currency(val, labels[idx], is_change=(idx == 5)),
        text_font=FONT,
        text_position=pos,
        text_color=default_colors[index]
    )

last_check = None
matrixportal.preload_font(b"$0123456789")  # preload numbers
matrixportal.preload_font((0x00A3, 0x20AC, 0x25B2, 0x25BC))  # preload GBP/euro symbol and triangles

while True:
    try:
        value = matrixportal.fetch()
        current_price = value[0]
        previous_close = value[3]
        percent_change = round(value[5], 2)
        print("Response is", value)
        print(time.monotonic())

        # Update the color for the change text based on its value
        change_color = determine_color(percent_change)
        matrixportal.set_text_color(change_color, index=0)
        matrixportal.set_text_color(change_color, index=4)
        matrixportal.set_text_color(change_color, index=5)
        matrixportal.set_text(f"{percent_change:+6.1f} % ", 5)

        last_check = time.monotonic()
    except (ValueError, RuntimeError) as e:
        print("Error occurred, retrying! -", e)
        matrixportal.exit_and_reconnect()  # Example function, implement based on your setup
    time.sleep(5)  # Check every 5 seconds
