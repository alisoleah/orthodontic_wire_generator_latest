import numpy as np
from scipy.ndimage import gaussian_filter1d

def catmull_rom_spline(points, num_points=300):
    """
    Computes the Catmull-Rom spline for a given set of control points.
    Updated with Gaussian smoothing for ultra-smooth curves.

    Args:
        points (list of np.ndarray): A list of 3D control points.
        num_points (int): The number of points to generate for the spline (default: 300).

    Returns:
        np.ndarray: A numpy array of 3D points representing the spline.
    """
    if len(points) < 4:
        raise ValueError("Catmull-Rom spline requires at least 4 control points.")

    points = np.array(points)

    # Add dummy points at the start and end to ensure the spline passes through the first and last points
    p0 = 2 * points[0] - points[1]
    p_end = 2 * points[-1] - points[-2]

    control_points = np.vstack([p0, points, p_end])

    t = np.linspace(0, 1, num_points)

    # Calculate the spline
    spline_points = []
    for i in range(1, len(control_points) - 2):
        p0, p1, p2, p3 = control_points[i-1:i+3]

        # Catmull-Rom matrix
        C = 0.5 * np.array([
            [-1,  3, -3,  1],
            [ 2, -5,  4, -1],
            [-1,  0,  1,  0],
            [ 0,  2,  0,  0]
        ])

        T = np.array([t**3, t**2, t, np.ones(num_points)]).T

        segment = T @ C @ np.array([p0, p1, p2, p3])
        spline_points.extend(segment)

    spline_array = np.array(spline_points)

    # Apply Gaussian smoothing for ultra-smooth curves
    if len(spline_array) > 5:
        smoothed = spline_array.copy()
        for dim in range(3):  # X, Y, Z
            temp = spline_array[:, dim].copy()
            # Apply 5 passes of Gaussian smoothing with sigma=12.0
            for _ in range(5):
                temp = gaussian_filter1d(temp, sigma=12.0, mode='nearest')
            smoothed[:, dim] = temp
        return smoothed

    return spline_array