---
name: consensus-cpp-and-native
description: >-
  Writes and refactors CPython C extensions, Google/Abseil/PyTorch/TorchTPU C++,
  and standalone C++17/20 systems code to satisfy pganssle, wan, and pablogsal.
  Covers Rust-style const-by-default C++, PEP 7, C-API error/refcount/GC
  contracts, Abseil StatusOr/NoDestructor, ABSL_CHECK vs TT_CHECK_THROW, and
  RAII. Use whenever writing or editing .c, .cc, .cpp, or .h files.
---

# Consensus C, C++ & Native Code (`pganssle` + `wan` + `pablogsal`)

Route C and C++ code by its target runtime: **CPython C**, **Standalone C++17/20**, or **Google / Abseil / ML Runtime C++**. Across all three, enforce strict lifetime safety, explicit error propagation, and zero undefined behavior. Write C++ like Rust (`const` by default everywhere unless mutation or moving is required), yielding to local project style in existing repositories.

## 1. Dialect Routing Table

| Ecosystem | Naming & Formatting | Error Mechanism | Key Idioms |
| :--- | :--- | :--- | :--- |
| **CPython C / C Extensions** | PEP 7: 4-space indent, space in `if (`, braces on every `if`/`for`/`while`, C99 designated initializers | Return `NULL` / `-1` with Python exception set (`goto exit`) | Argument Clinic, `Py_DECREF` across all paths, `tp_traverse`/`tp_clear`/`tp_dealloc`, `Py_GIL_DISABLED` safety |
| **Standalone C++17/20** | Repo naming convention; clang-format | Exceptions or `std::expected` / status types; `noexcept` on cleanup | Rust-style `const` on all non-mutated locals/params/methods, `explicit` 1-arg ctors, `override`, RAII wrappers |
| **Google / Abseil / PyTorch / TorchTPU C++** | Google C++ Style: `PascalCase` functions, `snake_case_` fields | `absl::StatusOr<T>` (internal invariants: `ABSL_CHECK`/`TT_CHECK`; user input: `TT_CHECK_THROW`/`TORCH_CHECK`) | `absl::NoDestructor`, `std::string_view`/`absl::Span`, no `T&&` params, `auto*`, `absl_nonnull`, Abseil Tip #109 in `.h` |

---

## 2. Rust-Style `const`-by-Default in C++ (`pganssle` + `pablogsal`)

- **Everything `const` unless mutation or move is required**:
  - Mark every local variable, parameter, and read-only member function `const` by default.
  - Only drop `const` on a local variable when it is mutated in place or moved from (`std::move(var)`).
  - Do **not** mark scalar local variables `const` in pure CPython C (PEP 7 C convention).
  - **Local project override**: When working in a Google C++ / Abseil repository, follow Abseil Tip #109 by omitting top-level `const` on by-value parameters in `.h` function declarations (you may still keep `const` on the parameter in the `.cc` definition).

---

## 3. CPython C & Native Extensions (`PEP 7` + C-API)

- **PEP 7 braces & layout**: Always put braces `{ ... }` around every `if`, `else`, `for`, and `while` body, even single statements. Put a space after control keywords (`if (x < 0) {`).
- **Signed bounds & integer overflow**:
  - Check `< 0` on signed integers (`ssize_t`, `Py_ssize_t`, `int`) *before* casting to `size_t`.
  - On untrusted sizes or offsets, check arithmetic overflow both when decoding the value and when accumulating (`total += delta`).
- **Check every fallible C-API & OS call**:
  - Never assume `PyTuple_GetItem`, `PyList_GetItem`, `PyDict_GetItemWithError`, `PyObject_GetAttrString`, or `PyDateTime_IMPORT` succeeds without checking the return value.
  - After `PyLong_AsLong`, `PyLong_AsSize_t`, or `PyLong_AsLongAndOverflow`, always check `value == -1 && PyErr_Occurred()`.
  - Check OS calls cleanly: compare `mmap` against `MAP_FAILED` (never `!ptr`), and check `fflush`, `write`, and `close` return codes.
- **Single cleanup exit (`goto exit`)**:
  - Initialize owned `PyObject *` locals to `NULL` and route every error branch to a single `exit:` label that calls `Py_XDECREF` on all temporaries.
  - Never expose a `PyListObject` or `PyTupleObject` with uninitialized `NULL` slots to Python or the garbage collector.
- **Heap types & GC lifecycle (`tp_traverse` / `tp_clear` / `tp_dealloc`)**:
  - `tp_clear` must only call `Py_CLEAR` on Python object references. Never free raw C buffers in `tp_clear` if methods can still access the object afterward; free raw C memory in `tp_dealloc`.
  - Heap-type `tp_dealloc` must call `PyObject_GC_UnTrack(self)`, clear references, free the instance via `tp->tp_free(self)`, and call `Py_DECREF(tp)` last.
  - Call `_PyObject_GC_Track(self)` only after every field is initialized, and before any `Py_DECREF` that could trigger a GC collection.
- **Re-entrancy across callbacks**:
  - Calling `PyObject_Hash`, `PyObject_RichCompareBool`, `PyNumber_Index`, or `Py_DECREF` can execute arbitrary Python code and mutate containers. Hold a strong reference (`Py_NewRef`) to borrowed items and re-read `PyList_GET_SIZE` / data pointers after the call.
- **Struct layout & trailing arrays**:
  - Whenever adding a struct field or variable-length tail, verify `tp_basicsize`, `tp_itemsize`, `offsetof`, and `memcpy` lengths match the new layout.
- **Free-threading (`Py_GIL_DISABLED`)**:
  - Re-read shared state after acquiring `PyMutex_Lock`. Never invoke Python callbacks or `Py_DECREF` while holding a native mutex.

---

## 4. Google, Abseil, PyTorch & TorchTPU C++

- **Function signatures & value semantics**:
  - Pass small read-only views by value (`int64_t`, `std::string_view`, `absl::Span<const T>`).
  - Pass heavier read-only objects by `const T&`. Never add `T&&` forwarding-reference overloads to ordinary APIs.
- **Ownership, moves & `StatusOr`**:
  - Allocate heap objects with `std::make_unique<T>(...)` (never raw `new`); prefer direct value members in test fixtures and classes.
  - Move out of `absl::StatusOr<T>` when returning (`return std::move(result).value();`). Never access a variable after `std::move`.
  - In `ToProto(..., Proto* out)` functions, call `out->Clear()` at entry so stale fields from a reused proto never leak through.
- **Static singletons**:
  - Wrap function-local `static` objects with non-trivial destructors in `absl::NoDestructor<T>` so program shutdown never hits destruction-order crashes.
- **Pointers & headers**:
  - Write `auto* ptr = GetPointer();` (never bare `auto`) so pointer-ness is visible at the declaration.
  - Mark non-null pointer returns and parameters with `absl_nonnull` (or use `T&`).
  - Include `<iosfwd>` in `.h` files instead of `<iostream>` or `<sstream>`. Add `[[nodiscard]]` on pure query/status helpers.
- **Invariants vs. user errors**:
  - Crash immediately with `ABSL_CHECK`, `TT_CHECK`, or `TORCH_INTERNAL_ASSERT` when an internal invariant is broken.
  - Raise user-facing exceptions with `TT_CHECK_THROW` or `TORCH_CHECK` for invalid caller inputs.
  - In operator lowerings (`Aten*`), validate tensor ranks, shapes, dtypes, and scalar bounds eagerly *before* emitting HLO / compiler IR nodes.
- **Runtime & macro hygiene**:
  - Use `c10::ThreadLocalDebugInfo` instead of raw `thread_local` state across PyTorch dispatch boundaries.
  - Route `out=` operators through `DispatchOpOut` so output aliasing and resize checks run consistently.
  - Keep `#ifdef` / `#else` class definitions ABI-compatible (same virtual methods and member layout).
  - Prefix macros with the project namespace (`TORCH_TPU_..._`); never start a macro with a leading underscore (`_MY_MACRO`).

---

## 5. Standalone Modern C++17/20 Hygiene

- **Class hygiene**: Mark every single-argument constructor `explicit`. Write `override` (without `virtual`) on overridden virtual functions, and `~Derived() override = default;`.
- **Safe containers & casts**: Use `std::array` and `.data()` instead of C arrays; check `size_t` -> `ssize_t` / `int64_t` narrowing before casting.
- **Explicit lambda captures**: List captures explicitly (`[this, &buffer]`); avoid default `[=]` or `[&]` on lambdas that outlive the current statement.
- **RAII for OS handles**: Wrap file descriptors, `mmap` regions (`munmap`), `dlopen` handles, and profiler/unwinder resources in RAII types with `noexcept` destructors and move operations.

## Quick Checklist Before Finishing C / C++ Files
- [ ] Every C++ local variable, parameter, and method is `const` unless mutated or moved (or overridden by local repo style like Abseil Tip #109 in `.h` files).
- [ ] Every fallible C-API / OS call is checked; all error branches release owned refs (`goto exit`) or use RAII.
- [ ] Signed `< 0` bounds and integer overflows are checked before `size_t` casts or accumulation.
- [ ] Heap types obey `tp_clear` (only `Py_CLEAR`) vs. `tp_dealloc` (raw memory + `tp_free` + `Py_DECREF(tp)`).
- [ ] C++ code avoids `T&&` on ordinary APIs, uses `absl::NoDestructor` for statics, separates `ABSL_CHECK` from `TT_CHECK_THROW`, and calls `out->Clear()` on output protos.
