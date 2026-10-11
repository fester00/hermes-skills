#!/usr/bin/env python3
"""Compare the model surface of two Hermes profile configs.

Usage:
    python3 compare-profile-models.py SOURCE_CONFIG TARGET_CONFIG

Prints model.*, providers.*.models and delegation.* for both files plus the
per-provider set differences. Exits 1 when the target is missing anything the
source offers (so it works as a pre/post parity check).

PyYAML is required; if the system python lacks it, run this with the Hermes
venv interpreter: $HERMES_HOME/hermes-agent/venv/bin/python
"""
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit(
        "PyYAML missing - run with the Hermes venv python:\n"
        "  $HERMES_HOME/hermes-agent/venv/bin/python compare-profile-models.py ..."
    )


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src_path, tgt_path = sys.argv[1], sys.argv[2]
    src, tgt = load(src_path), load(tgt_path)
    missing = False

    print(f"source: {src_path}\ntarget: {tgt_path}\n")

    print("-- model --")
    for key in ("default", "provider", "base_url"):
        s = (src.get("model") or {}).get(key)
        t = (tgt.get("model") or {}).get(key)
        mark = "" if s == t else "   <-- differs"
        missing = missing or s != t
        print(f"  {key}: source={s!r} target={t!r}{mark}")

    print("-- providers --")
    sp, tp = src.get("providers") or {}, tgt.get("providers") or {}
    for name in sorted(set(sp) | set(tp)):
        s, t = sp.get(name), tp.get(name)
        if t is None:
            print(f"  {name}: MISSING in target")
            missing = True
            continue
        if s is None:
            print(f"  {name}: only in target ({len(t.get('models') or [])} models) - left alone")
            continue
        sm, tm = set(s.get("models") or []), set(t.get("models") or [])
        absent = sorted(sm - tm)
        print(
            f"  {name}: source={len(sm)} target={len(tm)} "
            f"missing_in_target={absent or 'none'} extra_in_target={sorted(tm - sm) or 'none'}"
        )
        if absent:
            missing = True
        if s.get("default_model") != t.get("default_model"):
            print(
                f"    default_model differs: source={s.get('default_model')!r} "
                f"target={t.get('default_model')!r}"
            )
            missing = True

    print("-- delegation ('' = inherit the main model) --")
    for key in ("model", "provider", "base_url"):
        s = (src.get("delegation") or {}).get(key)
        t = (tgt.get("delegation") or {}).get(key)
        mark = "   <-- differs" if s != t else ""
        missing = missing or s != t
        print(f"  {key}: source={s!r} target={t!r}{mark}")

    non_empty = {}
    for label, cfg in (("source", src), ("target", tgt)):
        for name, sub in (cfg.get("auxiliary") or {}).items():
            model = (sub or {}).get("model")
            if model:
                non_empty.setdefault(label, []).append(f"{name}={model}")
    print("-- auxiliary overrides (usually empty in both) --")
    for label in ("source", "target"):
        print(f"  {label}: {non_empty.get(label) or 'none'}")

    print("\nRESULT:", "model surface differs" if missing else "model surface matches")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
