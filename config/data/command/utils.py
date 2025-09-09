# utils/context_capture.py
import json
import inspect, os, sys, threading, traceback
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

REDACT_KEYS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "apikey",
    "api_key",
    "authorization",
    "auth",
    "jwt",
    "sessionid",
    "csrftoken",
    "cookie",
}


def _is_primitive(x: Any) -> bool:
    return isinstance(x, (type(None), bool, int, float, str))


def _safe_repr(obj: Any, max_len: int = 200) -> str:
    try:
        s = repr(obj)
    except Exception as e:
        s = f"<unreprable {type(obj).__name__}: {e}>"
    return s if len(s) <= max_len else (s[: max_len - 3] + "...")


def _redact_key(key: str) -> bool:
    k = key.lower()
    return any(part in k for part in REDACT_KEYS)


def _serialize_mapping(
    m: Dict[Any, Any], max_items: int, max_len: int, depth: int
) -> Dict[str, Any]:
    out = {}
    for i, (k, v) in enumerate(m.items()):
        if i >= max_items:
            out["__truncated__"] = f"only first {max_items} items kept"
            break
        key = str(k)
        out[key] = (
            "***"
            if _redact_key(key)
            else _to_jsonable(v, max_items=max_items, max_len=max_len, depth=depth - 1)
        )
    return out


def _serialize_iterable(it: Iterable[Any], max_items: int, max_len: int, depth: int):
    out = []
    for i, v in enumerate(it):
        if i >= max_items:
            out.append(f"...(truncated after {max_items} items)")
            break
        out.append(
            _to_jsonable(v, max_items=max_items, max_len=max_len, depth=depth - 1)
        )
    return out


def _to_jsonable(obj: Any, *, max_items: int, max_len: int, depth: int) -> Any:
    if depth <= 0:
        return _safe_repr(obj, max_len)
    if _is_primitive(obj):
        return obj
    if isinstance(obj, dict):
        return _serialize_mapping(obj, max_items, max_len, depth)
    if isinstance(obj, (list, tuple, set)):
        return _serialize_iterable(obj, max_items, max_len, depth)
    if isinstance(obj, bytes):
        return f"<bytes len={len(obj)}>"
    if hasattr(obj, "__dict__"):
        return f"<{type(obj).__name__} at {hex(id(obj))}>"
    return _safe_repr(obj, max_len)


def _frame_locals_snapshot(
    frame, *, max_items: int, max_len: int, depth: int
) -> Dict[str, Any]:
    try:
        raw = dict(frame.f_locals)
    except Exception:
        return {"__error__": "unavailable"}
    return _to_jsonable(raw, max_items=max_items, max_len=max_len, depth=depth)


def capture_context_deep(
    *,
    include_stack_locals: bool = True,
    stack_max_frames: int = 10,  # how many frames to keep (tail of the stack)
    locals_max_items: int = 50,  # per frame locals limit (keys/items)
    locals_depth: int = 2,  # nesting depth for complex values
    max_str_len: int = 300,  # repr truncation
    order: str = "tail",  # "tail" (nearest first) or "head" (root first)
) -> dict:
    """
    Captures metadata about the *current call site* AND (optionally) locals for *every* frame.
    Returns a JSON-serializable dict.

    You typically call this in the place you want to record context (e.g., right before creating/saving a model).
    """
    now = datetime.now(timezone.utc).isoformat()
    thread = threading.current_thread().name
    pid = os.getpid()
    pyver = sys.version.split()[0]

    current = inspect.currentframe()
    caller = current.f_back if current and current.f_back else None

    try:
        if not caller:
            return {
                "created_at_utc": now,
                "pid": pid,
                "thread_name": thread,
                "python": pyver,
                "note": "no frame available",
            }

        # Current site info
        finfo = inspect.getframeinfo(caller, context=1)
        envelope = {
            "created_at_utc": now,
            "pid": pid,
            "thread_name": thread,
            "python": pyver,
            "file": os.path.abspath(finfo.filename),
            "line": finfo.lineno,
            "func": finfo.function,
            "code_line": (
                finfo.code_context[0].rstrip() if finfo.code_context else None
            ),
        }

        # Build stack summaries
        extracted = traceback.extract_stack(caller)
        # Keep only the last N frames (closest to the call site)
        if order == "tail":
            frames_to_keep = extracted[-stack_max_frames:]
        else:
            frames_to_keep = extracted[:stack_max_frames]

        stack_summary = []
        if include_stack_locals:
            # We need live frames to access f_locals; use walk back from 'caller'
            # and align with the chosen subset.
            # Build a list of live frames from root->caller or caller->root
            live_frames = []
            f = caller
            while f:
                live_frames.append(f)
                f = f.f_back
            live_frames.reverse()  # root -> caller

            # Map (filename, lineno, name) to frame object (best-effort)
            live_index = {}
            for lf in live_frames:
                try:
                    li = inspect.getframeinfo(lf, context=0)
                    live_index[
                        (os.path.abspath(li.filename), li.lineno, li.function)
                    ] = lf
                except Exception:
                    continue

        for fr in frames_to_keep:
            absfile = os.path.abspath(fr.filename)
            item = {
                "file": absfile,
                "line": fr.lineno,
                "func": fr.name,
                "code": (fr.line or "").strip(),
            }
            if include_stack_locals:
                key = (absfile, fr.lineno, fr.name)
                lf = live_index.get(key)
                if lf is not None:
                    item["locals"] = _frame_locals_snapshot(
                        lf,
                        max_items=locals_max_items,
                        max_len=max_str_len,
                        depth=locals_depth,
                    )
                else:
                    item["locals"] = {"__note__": "locals not resolved for this frame"}
            stack_summary.append(item)

        envelope["stack"] = stack_summary
        # Also include caller frame locals at top-level convenience:
        envelope["locals"] = _frame_locals_snapshot(
            caller, max_items=locals_max_items, max_len=max_str_len, depth=locals_depth
        )
        return envelope
    finally:
        # IMPORTANT: break reference cycles so GC can collect frames
        try:
            del current
            del caller
        except Exception:
            pass
