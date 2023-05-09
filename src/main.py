import itertools
from typing import Any, Callable
from db import load
from jet_engine import Turbojet

from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

plt: Any = plt


# Courtesy of ChatGPT
def hsv_to_rgb(h: float, s: float, v: float):
    """
    Converts a color from HSV color space to RGB color space.
    `h` is the hue value in degrees, ranging from 0 to 360.
    `s` and `v` are the saturation and value values, ranging from 0 to 1.
    Returns a tuple of (r, g, b) values ranging from 0 to 255.
    """
    h /= 60
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


def clamp(mini: float, value: float, maxi: float) -> float:
    """
    Clamps a value between a minimum and maximum.
    """
    return max(mini, min(value, maxi))


def heat_rgb(value: float) -> tuple[int, int, int]:
    """
    Converts a value from 0 to 1 to a color from blue to red.
    """
    return hsv_to_rgb(240 * (1 - value), 1, 1)


def plot_scatter_with_background_color(
    x_label: str,
    y_label: str,
    x_width: int,
    y_width: int,
    data: list[tuple[float, float, str]],
    color_function: Callable[[float, float], tuple[int, int, int]],
):
    # Calculate the size of the image needed to display all data points
    w: tuple[list[float], list[float], list[str]] = zip(*data)  # type: ignore
    x_values, y_values, labels = w
    min_x = int(min(x_values))
    max_x = int(max(x_values))
    min_y = int(min(y_values))
    max_y = int(max(y_values))
    width = int(max_x - min_x + 1000)
    height = int(max_y - min_y + 1000)

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.set_xticks(range(min_x, max_x + 1, x_width))
    ax.set_yticks(range(min_y, max_y + 1, y_width))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Set axis limits
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

    ax.set_title("Scatter Plot")

    # ============= BACKGROUND ================
    # Create the image and draw the background color
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    # draw: Any = ImageDraw.Draw(img)

    def to_display(x: float, y: float) -> tuple[int, int]:
        return ax.transData.transform((x, y))

    def to_plot(x: float, y: float) -> tuple[int, int]:
        return ax.transData.inverted().transform((x, y))

    left, bottom = to_display(min_x, min_y)
    right, top = to_display(max_x, max_y)

    # print(left, bottom, right, top)
    for x in range(int(left), int(right)):
        for y in range(int(bottom), int(top)):
            plot_x, plot_y = to_plot(x, y)
            img.putpixel((x + 1, height - y), color_function(plot_x, plot_y))

    # ============= SCATTER ================
    ax.scatter(x_values, y_values)
    for i, label in enumerate(labels):
        ax.annotate(label, (x_values[i], y_values[i]))

    # fig.canvas.draw()
    fig.savefig("plot.png", transparent=True)
    # Convert the plot to an image and paste it onto the background image
    # buf = fig.canvas.tostring_argb()

    plt.close(fig)
    plot_img = Image.open("plot.png")  # type: ignore
    # plot_img.show()
    img = Image.alpha_composite(img, plot_img)

    return img


if __name__ == "__main__":
    DB = load("./data")

    def show(
        attr_x: str,
        attr_y: str,
        info: str,
        info_range: tuple[float, float],
        x_label: str,
        y_label: str,
        x_width: int,
        y_width: int,
        x_ratio: float,
        y_ratio: float,
    ):
        print("=" * 80)
        print(f"rendering plot of {attr_x} vs {attr_y} with background {info}")
        data: list[tuple[float, float, str]] = []

        for air in DB.aircraft_types.dict.values():
            jetinfo = air.jet_information
            if jetinfo is None:
                continue
            data.append((getattr(jetinfo, attr_x) * x_ratio, getattr(jetinfo, attr_y) * y_ratio, air.name))  # type: ignore

        print("data calculation done, plotting...")

        tj = Turbojet(0.6, 0.4, 50_000, 50_000, 9, 847 + 273, 30_000)

        mini = 100000000
        maxi = -100000000

        def coloring(x: float, y: float) -> tuple[int, int, int]:
            setattr(tj, attr_x, x / x_ratio)
            setattr(tj, attr_y, y / y_ratio)
            v = getattr(tj.calculate(273 - 33, 200), info) - info_range[0]
            nonlocal mini, maxi
            mini = min(mini, v)
            maxi = max(maxi, v)
            return heat_rgb(
                clamp(
                    0,
                    v / (info_range[1] - info_range[0]),
                    1,
                )
            )

        img = plot_scatter_with_background_color(
            x_label
            + " with background heatmap "
            + info
            + " range from "
            + str(info_range[0])
            + " to "
            + str(info_range[1]),
            y_label,
            x_width,
            y_width,
            data,
            coloring,
        )

        print(f"min: {mini}, max: {maxi}")
        print("plotting done, saving...")

        fname = f"plots/plot of {attr_x}-{attr_y} bg-{info}.png"
        img.save(fname)

        print(f"saved to {fname}")
        # img.show()

    attributes = [
        ("inlet_area", "Inlet Area (m^2)", 2, 1),
        # "exit_area",
        # "inlet_pressure",
        # "exit_pressure",
        ("compresser_ratio", "Compresser Ratio", 5, 1),
        # "inlet_temperature",
        # "diffuser_pressure_increase",
        ("weight", "Weight (Ton)", 5, 0.001),
    ]

    info = [
        ("mass_flowrate", (0, 500)),
        ("heat_flowrate", (0, 100_000)),
        ("thrust", (0, 1500_000)),
        ("efficiency", (0, 1)),
        ("power", (0, 1500_000)),
    ]

    for info_attr, info_range in info:
        for (ax, xn, xw, xr), (ay, yn, yw, yr) in itertools.combinations(attributes, 2):
            show(ax, ay, info_attr, info_range, xn, yn, xw, yw, xr, yr)
