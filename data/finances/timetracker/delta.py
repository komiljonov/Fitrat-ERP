from datetime import datetime, timedelta
from typing import List


class Range:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end
        if end < start:
            raise ValueError("End datetime must be after start datetime.")

    def __repr__(self):
        return f"Range({self.start}, {self.end})"

def include_only_ranges(main_ranges: List[Range], includes: List[Range]) -> timedelta:
    """
    Given a list of main_ranges and a list of include ranges,
    returns the effective duration that is inside both any of the main_ranges
    and any of the include ranges.

    The result is returned as a timedelta.
    """
    intervals = []
    for main_range in main_ranges:
        for include in includes:
            # Find the overlapping part between main_range and include
            effective_start = max(main_range.start, include.start)
            effective_end = min(main_range.end, include.end)
            if effective_end > effective_start:
                intervals.append((effective_start, effective_end))

    # Sort intervals by start time
    intervals.sort(key=lambda interval: interval[0])

    # Merge overlapping or adjacent intervals
    merged_intervals = []
    for interval in intervals:
        if not merged_intervals:
            merged_intervals.append(interval)
        else:
            last_start, last_end = merged_intervals[-1]
            current_start, current_end = interval
            if current_start <= last_end:  # Overlap or adjacent
                merged_intervals[-1] = (last_start, max(last_end, current_end))
            else:
                merged_intervals.append(interval)

    # Calculate total included duration
    total_included = timedelta(0)
    for start, end in merged_intervals:
        total_included += end - start

    return total_included
