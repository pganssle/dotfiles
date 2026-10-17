---
name: pganssle-cpp-and-ml
description: >-
  Reviews C, C++, Python C-API extensions, and PyTorch/TorchTPU/XLA compiler and
  runtime code emulating Paul Ganssle (pganssle). Covers signed integer bounds
  checking, Py_DECREF reference counting across branches, PyDateTime_IMPORT null
  checks, eager load-time validation, C++ value categories (const &, std::move),
  async lambda captures, ThreadLocalDebugInfo, DispatchOpOut buffer donation,
  virtual capability parity across #ifdef/#else, and TT_CHECK_THROW formatting.
  Use when reviewing C/C++ files, Python C extensions, or ML compiler bindings.
  Don't use for pure Python packaging or CI YAML workflows.
---

# Paul Ganssle (`pganssle`) — C/C++, Python C-API & PyTorch/TorchTPU Compiler Review

Review C, C++, Python C-API extensions, and PyTorch/TorchTPU/XLA compiler/runtime code with the safety and systems rigor of Paul Ganssle (`pganssle`).

---

## 1. C / C++ & Python C-API Safety

### Signed Integer Bounds Checking (`< 0` AND `>= len`)
Whenever C, C++, or Python buffer-parsing code checks an index upper bound (`idx >= count`), verify whether the index is a signed integer type (`int`, `int64_t`, `ssize_t`, or Python `int`) and ask whether `idx < 0` also needs to be handled.

### Python C-API Reference Counting & Initialization
- In CPython C extensions (`PyLong_FromLong`, `PyObject_GetAttr`), audit every conditional branch and early error exit to ensure `Py_DECREF` is called before returning (`gh-pganssle-zoneinfo-97`).
- Check that C-API capsule imports (`PyDateTime_IMPORT`) verify `PyDateTimeAPI != NULL` and jump to error handling on failure.

### Eager Invariant Validation at Load Time
Validate binary/input invariants eagerly once at load/construction time (especially when the loaded object is cached) rather than deferring checks to point-of-use.

---

## 2. PyTorch / TorchTPU / ML Compiler Specifics

### Testing Python-to-C++ Runtime Integration & Sentinels
- When a C++ extension consumes runtime configuration or version info populated by Python (e.g. setting the `libtpu` version from `_loader.py`), prefer testing the integration from a Python test (`env_test.py`) rather than setting the value artificially from a C++ unit test.
- Use an explicit sentinel value to distinguish between "package is not installed" and "initialization function was never called" to aid debugging.

### C++ Value Categories, Threading, & Operator Lowering
- **Avoid unnecessary copies & dangling captures**: Pass non-trivial C++ types by `const &`, use `std::move` when transferring ownership, and check that C++ lambda captures (`[&]`, `[this]`) in deferred/async execution cannot outlive referenced objects (`reviewing_code/SKILL.md`).
- **`ThreadLocalDebugInfo` over bare C++ `thread_local`**: Never use bare C++ `thread_local` to store per-Python-thread state in PyTorch/TorchTPU; use `c10::ThreadLocalDebugInfo` (`tt-context-managers`).
- **Buffer donation (`DispatchOpOut`)**: Verify that all out-variant (`Aten*Out`) and in-place (`Aten*Inplace`) operators use `DispatchOpOut` (`reviewing_code/SKILL.md`).
- **Virtual capability parity (`#ifdef` / `#else`)**: When adding a capability override like `bool supportsWindow const override { return true; }` on one class or `#ifdef` branch, check that sibling classes or `#else` branches define the corresponding `return false;` override .
- **Error macro formatting (`TT_CHECK_THROW` vs `TT_CHECK`)**: User-facing precondition checks must use `TT_CHECK_THROW` (lowercase start, no trailing period, no op-name prefix, `"expected X, got Y"`), while internal compiler invariant checks must crash immediately via `TT_CHECK` / `ABSL_CHECK` (`tt-error-guide`).

---

## 3. Ecosystem Guardrails & Voice

- **No Cross-Ecosystem Rule Leakage**: Never apply internal_repo/TorchTPU-specific C++ conventions (`ABSL_LOG`, `TT_CHECK_THROW`, `DispatchOpOut`) to external open-source C/C++ repositories (`cpython`, `zoneinfo`).
- Follow [references/voice-and-examples.md](references/voice-and-examples.md) when formatting review comments.
