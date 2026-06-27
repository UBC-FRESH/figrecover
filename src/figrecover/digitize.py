from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np

from figrecover.image import color_mask, load_rgb_array
from figrecover.models import DataPoint, Diagnostic, DigitizeResult, DigitizeSpec, SeriesResult


def digitize_image(path: Path, spec: DigitizeSpec) -> DigitizeResult:
    rgb, width, height = load_rgb_array(path)
    results: list[SeriesResult] = []
    diagnostics = list(spec.diagnostics)

    for series_spec in spec.series:
        mask = color_mask(rgb, series_spec.color, tolerance=series_spec.tolerance)
        left, right, top, bottom = spec.calibration.clipped_bounds(width, height, margin=1)
        inner_left = min(right, left + series_spec.plot_edge_margin_px)
        inner_right = max(inner_left, right - series_spec.plot_edge_margin_px)
        inner_top = min(bottom, top + series_spec.plot_edge_margin_px)
        inner_bottom = max(inner_top, bottom - series_spec.plot_edge_margin_px)
        clipped_mask = np.zeros_like(mask, dtype=bool)
        clipped_mask[inner_top:inner_bottom, inner_left:inner_right] = mask[
            inner_top:inner_bottom, inner_left:inner_right
        ]

        if series_spec.mode == "line":
            series_result = _extract_line(clipped_mask, spec, series_spec)
        elif series_spec.mode == "scatter":
            series_result = _extract_scatter(clipped_mask, spec, series_spec)
        elif series_spec.mode == "bar":
            series_result = _extract_bars(clipped_mask, spec, series_spec)
        else:
            raise ValueError(f"Unsupported extraction mode: {series_spec.mode}")
        results.append(series_result)

    return DigitizeResult(
        spec=spec,
        image_path=path,
        width=width,
        height=height,
        series=results,
        diagnostics=diagnostics,
    )


def _extract_line(mask: np.ndarray, spec: DigitizeSpec, series_spec) -> SeriesResult:
    ys, xs = np.nonzero(mask)
    diagnostics: list[Diagnostic] = []
    points: list[DataPoint] = []
    if xs.size == 0:
        diagnostics.append(
            Diagnostic(
                level="warning",
                code="no_pixels_matched",
                message=(
                    f"No pixels matched colour {series_spec.color} "
                    f"for series {series_spec.name}."
                ),
            )
        )
        return SeriesResult(spec=series_spec, diagnostics=diagnostics)

    for x_pixel in range(int(xs.min()), int(xs.max()) + 1, series_spec.sample_every_px):
        y_values = ys[xs == x_pixel]
        if y_values.size == 0:
            continue
        if series_spec.line_aggregation == "min":
            y_pixel = float(np.min(y_values))
        elif series_spec.line_aggregation == "max":
            y_pixel = float(np.max(y_values))
        else:
            y_pixel = float(np.median(y_values))
        x_value, y_value = spec.calibration.pixel_to_data(float(x_pixel), y_pixel)
        confidence = min(1.0, max(0.2, y_values.size / 8.0))
        points.append(
            DataPoint(
                series=series_spec.name,
                x=x_value,
                y=y_value,
                x_pixel=float(x_pixel),
                y_pixel=y_pixel,
                confidence=confidence,
            )
        )

    diagnostics.append(
        Diagnostic(
            level="info",
            code="line_extracted",
            message=f"Extracted {len(points)} line samples for {series_spec.name}.",
            context={"matched_pixels": int(xs.size)},
        )
    )
    return SeriesResult(spec=series_spec, points=points, diagnostics=diagnostics)


def _extract_scatter(mask: np.ndarray, spec: DigitizeSpec, series_spec) -> SeriesResult:
    components = _connected_components(mask)
    diagnostics: list[Diagnostic] = []
    points: list[DataPoint] = []

    for component in components:
        if len(component) < series_spec.min_component_pixels:
            continue
        y_pixels = np.array([p[0] for p in component], dtype=float)
        x_pixels = np.array([p[1] for p in component], dtype=float)
        x_pixel = float(np.mean(x_pixels))
        y_pixel = float(np.mean(y_pixels))
        x_value, y_value = spec.calibration.pixel_to_data(x_pixel, y_pixel)
        points.append(
            DataPoint(
                series=series_spec.name,
                x=x_value,
                y=y_value,
                x_pixel=x_pixel,
                y_pixel=y_pixel,
                confidence=min(1.0, len(component) / 20.0),
            )
        )

    points.sort(key=lambda point: (point.x, point.y))
    diagnostics.append(
        Diagnostic(
            level="info",
            code="scatter_extracted",
            message=f"Extracted {len(points)} scatter components for {series_spec.name}.",
            context={"components": len(components)},
        )
    )
    return SeriesResult(spec=series_spec, points=points, diagnostics=diagnostics)


def _extract_bars(mask: np.ndarray, spec: DigitizeSpec, series_spec) -> SeriesResult:
    ys, xs = np.nonzero(mask)
    diagnostics: list[Diagnostic] = []
    points: list[DataPoint] = []
    if xs.size == 0:
        diagnostics.append(
            Diagnostic(
                level="warning",
                code="no_pixels_matched",
                message=(
                    f"No pixels matched colour {series_spec.color} "
                    f"for series {series_spec.name}."
                ),
            )
        )
        return SeriesResult(spec=series_spec, diagnostics=diagnostics)

    occupied_x = sorted(set(int(x) for x in xs))
    runs = _runs(occupied_x)
    baseline_pixel = (
        spec.calibration.y.data_to_pixel(series_spec.bar_baseline)
        if series_spec.bar_baseline is not None
        else spec.calibration.y.pixel_max
    )

    for start, end in runs:
        run_mask = (xs >= start) & (xs <= end)
        y_values = ys[run_mask]
        if y_values.size < series_spec.min_component_pixels:
            continue
        top_pixel = float(np.min(y_values))
        bottom_pixel = float(np.max(y_values))
        y_pixel = top_pixel if top_pixel < baseline_pixel else bottom_pixel
        x_pixel = (start + end) / 2.0
        x_value, y_value = spec.calibration.pixel_to_data(x_pixel, y_pixel)
        points.append(
            DataPoint(
                series=series_spec.name,
                x=x_value,
                y=y_value,
                x_pixel=x_pixel,
                y_pixel=y_pixel,
                confidence=min(1.0, y_values.size / 80.0),
            )
        )

    diagnostics.append(
        Diagnostic(
            level="info",
            code="bars_extracted",
            message=f"Extracted {len(points)} bars for {series_spec.name}.",
            context={"runs": len(runs), "matched_pixels": int(xs.size)},
        )
    )
    return SeriesResult(spec=series_spec, points=points, diagnostics=diagnostics)


def _runs(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        return []
    runs: list[tuple[int, int]] = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        runs.append((start, previous))
        start = previous = value
    runs.append((start, previous))
    return runs


def _connected_components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    visited = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    components: list[list[tuple[int, int]]] = []
    offsets = [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]

    starts = zip(*np.nonzero(mask), strict=False)
    for row, col in starts:
        if visited[row, col]:
            continue
        component: list[tuple[int, int]] = []
        queue: deque[tuple[int, int]] = deque([(int(row), int(col))])
        visited[row, col] = True
        while queue:
            current_row, current_col = queue.popleft()
            component.append((current_row, current_col))
            for d_row, d_col in offsets:
                next_row = current_row + d_row
                next_col = current_col + d_col
                if (
                    0 <= next_row < height
                    and 0 <= next_col < width
                    and mask[next_row, next_col]
                    and not visited[next_row, next_col]
                ):
                    visited[next_row, next_col] = True
                    queue.append((next_row, next_col))
        components.append(component)
    return components
