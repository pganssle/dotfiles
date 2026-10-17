---
name: pganssle-python-typing
description: >-
  Reviews and designs Python data models, type annotations, abstract collection
  signatures (Sequence vs Set vs Mapping), PEP 695 type aliases, Union of
  Products signatures, enums (StrEnum), dataclasses, Protocols, and path/resource
  types emulating Paul Ganssle (pganssle). Use when reviewing Python diffs for
  typing and data modeling, designing Python class hierarchies or function
  signatures, or refactoring untyped dicts/tuples into structured domain types.
  Don't use for C++ kernel logic, CI/CD workflow YAML, or mock test setup (use
  pganssle-cpp-and-ml, pganssle-build-and-ci, or pganssle-testing-and-mocks).
---

# Paul Ganssle (`pganssle`) — Python Data Modeling, Type Precision & Signatures

Review and author Python data models, type annotations, protocols, and function signatures with the precision and data-model rigor of Paul Ganssle (`pganssle`).

> **Completeness & Line-Anchoring Contract**:
> - **Audit every signature and declaration**: Check **every** newly added or modified function, helper, `@property` getter, dataclass field, module-level constant, CLI script, and test file in the diff.
> - **Emit a separate comment at each offending line**: Never bundle distant functions or constants into a single summary comment, and never skip later functions in a file because an earlier function already had a comment.

---

## 1. Structured Data, Domain Objects & Enums Over Ad-Hoc Dicts, Tuples, and Strings

### Fixed-Key Dictionaries & Dict Subclasses → `@dataclass` or `TypedDict`
- When a function accepts, returns, or accumulates a `dict` with a fixed schema of known keys (e.g., `defaultdict(lambda: {"busy": 0, "idle": 0, "offline": 0, "total": 0})` or a JSON configuration/policy loader), push for `@dataclasses.dataclass(frozen=True)` or `TypedDict` .
- **Never subclass `dict` to attach side-channel attributes**: Subclassing `dict[str, set[int]]` to tack on a mutable `.operations` attribute (and smuggling it via `getattr(..., "operations", None)`) is brittle (`dict(m)` or `m.copy` silently drops attributes, and static type checkers cannot verify them on `Mapping`). Use a `@dataclass(frozen=True)` instead.

### Domain Objects with `@functools.cached_property` Over Raw String Plumbing
- When code passes raw strings around (such as a raw commit message string) and calls procedural parser helpers on them (e.g., calling a tag-parsing helper inside a rule check), suggest encapsulating the entity as a domain object (e.g., a `Commit` class that exposes `.message` and `.tags`, each as a `@functools.cached_property`).
- **Voice framing**: Acknowledge if the current usage is small (*"I see that we're only using ... here, so this is basically fine, but my inclination would probably have been to have a `Commit` object that has `.message` and `.tags`, which each could be cached properties."*).

### `NamedTuple` vs `@dataclass`
- Challenge `typing.NamedTuple` or `collections.namedtuple` when the object represents a domain record rather than an actual tuple (`gh-google-pytorch-torch_tpu-3894`).
- **Why**: `NamedTuple` is a subclass of `tuple`. It unintentionally commits the class to positional indexing (`obj[0]`), unpacking, iteration (`for x in obj:`), and length equality as part of its public contract, making it impossible to add fields later without breaking callers.
- **Fix**: Use `@dataclasses.dataclass(frozen=True)` (or `attrs.define` in repos that already use `attrs`).

### Enums (`StrEnum` / `Enum` / `IntEnum`) Over Fixed Tuples of Strings & Parallel Constants
- **Fixed `Final[tuple[str, ...]]` domain value sets**: Whenever a module defines a tuple of string constants representing a closed set of domain values (such as severities `('ERROR', 'WARNING', 'NOTICE')`, modes, file operations, or VCS types), emit a comment **right on that constant's definition line** asking: *"Should this be an enum? (`StrEnum` maybe?)"*
- **Parallel string constants + lookup dict**: When a module defines string constants (`_ACTIVE = "ACTIVE"`, `_INACTIVE = "INACTIVE"`) alongside a dictionary mapping those strings to numbers or states (`{"ACTIVE": 1.0, "INACTIVE": -1.0}`), recommend consolidating them into an `enum.IntEnum` or `enum.Enum` (or `enum.StrEnum` in Python 3.11+).
- **`(str, enum.Enum)` in Python 3.11+**: Always flag `class Foo(str, enum.Enum):` in Python 3.11+ codebases and suggest `enum.StrEnum`.

---

## 2. Type Annotation Precision, `Sequence` vs `Set`, & PEP 695 Aliases

### Complete Function, `@property`, Script & Test Annotations
- Require parameter and return type annotations on all functions, methods, `@property` getters, CLI scripts, and local container variables whose element type is non-obvious (`labels: list[str] = []`) (`gh-google-ml-infra-bap-29`).
- **`Final[...]` on Module & Test Constants**: Annotate module-level constants (both in library code and in test files) with `Final[str]`, `Final[int]`, `Final[bool]`, `Final[Sequence[str]]`, etc. .

### Abstract Collection Types (`Sequence`, `Set`, `Mapping`) & `Set` vs `Sequence` Semantics
1. **Replace concrete `list[T]`, `set[T]`, `dict[K, V]` in signatures and `@property` getters**:
   - Prefer `collections.abc.Sequence[T]` over `list[T]` or `tuple[T, ...]`, `collections.abc.Set[T]` over `set[T]`, and `collections.abc.Mapping[K, V]` over `dict[K, V]` for function parameters, return types (including internal helpers like `def _compute_*(...) -> list[int]:` and `@property` getters like `def line_starts(self) -> list[int]:`), and read-only dataclass fields (`gh-google-pytorch-torch_tpu-3894`, `gh-google-ml-infra-bap-23`).
   - When multiple functions/`@property` methods in a file return `list[int]` or accept `set[int]` / `list[...]`, comment on **each** of them (*"Should return `Sequence`."*, *"`Sequence` again for most things like this."*, *"`Sequence` and `Set` here too."*).
2. **Question `Sequence[T]` when `Set[T]` is the true semantic abstraction**:
   - Whenever a dataclass field, parameter, or return type is typed as `Sequence[str]` (or `tuple[str, ...]`), ask whether ordering and integer indexing are actually meaningful, or whether the collection only cares about membership (`in`) and set intersection (`&`):
     > *"Should this be a `Sequence` or can it be a `Set`? Sequences need to be ordered, they need to be indexable. With `...` I think you don't care about order, you just care about set intersection."*
3. **Inner Fixed-Length Tuples**: When representing a sequence of fixed-width records (e.g., `(step, tensor)` pairs), use `tuple[int, Tensor]` for the inner fixed-schema record and `Sequence[tuple[int, Tensor]]` for the outer collection .

### PEP 695 `type X = ...` Aliases & Representing Only Exact Allowed Combinations
- **Require `type X = ...` for type aliases in Python 3.12+**: Flag bare module-level type alias assignments (`_Item = tuple[...]` or `Foo: TypeAlias = ...`) and recommend PEP 695 syntax (`type _Item = ...`).
- **Union of Products over Product of Unions (Representing Only the Exact Allowed Combinations)**:
  > *"For the 'partial null' thing, the key insight actually isn't that it's partial null, it's the way the types are unioned together. It could be `tuple[int | str, float | str]` — ideally the type system gives you *exactly* the allowed combinations in a union, rather than a set of allowed combinations that includes the actually allowed combinations."*
  >
  > *"This doesn't just apply to tuples, by the way, it also applies to stuff like function signatures. `f(a: str | int) -> str | int` is OK if either can generate either, but if it's a 1-1 mapping you need `f[T: (int, str)](a: T) -> T`, or for more complicated stuff you may need to use `@typing.overload`s."*

  When elements of a compound type or function signatures vary together, do not write a product of unions that permits the full Cartesian product of combinations when only specific correlated combinations are valid:
  1. **Compound Types (Tuples / Containers)**: Use a union of products (`tuple[int, float] | tuple[str, str]` or `tuple[int, str] | None`) rather than a product of unions (`tuple[int | str, float | str]` or `tuple[int | None, str | None]`) when elements vary together:
     > *"`type _Item = `. Also, should this be `tuple[int, str] | None` or `tuple[int, str] | tuple[None, None]` instead? Is there a situation where a `_Item` is a `[1, None]` or something?"*
  2. **1-to-1 Type-Preserving Function Signatures**: A signature like `def f(a: str | int) -> str | int` is only accurate if either input type can yield either output type. If `str` yields `str` and `int` yields `int`, use a constrained type parameter:
     - Python 3.12+: `def f[T: (int, str)](a: T) -> T:`
     - Python 3.11 and earlier: `_T = TypeVar("_T", int, str)` followed by `def f(a: _T) -> _T:`
  3. **General Correlated Function Signatures (Multi-Parameter or Non-Identity Mappings)**: When parameter types or return types correlate in non-identity ways (e.g., `int -> float` and `str -> bytes`, or coupled argument pairs where `a: int` requires `b: float` while `a: str` requires `b: str`), use `@typing.overload` declarations so the type system enforces the exact allowed input/output combinations rather than an overly broad product of unions.

### Modern Builtin Generics, Pipe Unions, `tuple[T]` Trap & `or` Type Alias Bug
- Replace legacy `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Set` with built-in `list[...]`, `dict[...]`, `tuple[...]`, `set[...]` (or `Sequence` / `Mapping` / `Set`) in Python 3.9+ codebases (`gh-google-ml-infra-bap-23`).
- Replace `typing.Union[A, B]` and `typing.Optional[A]` with `A | B` and `A | None` in Python 3.10+ codebases, and remove unused `typing` imports.
- **Stub/Backport Version Compatibility**: In `.pyi` stubs or libraries supporting Python 3.6–3.9, do **not** use `X | Y` union syntax without `from __future__ import annotations` (`gh-pganssle-zoneinfo-126`). Never demand Python 3-only syntax on historical Python 2.7/3.x dual-compatible PRs.
- **`tuple[int]` is a 1-tuple**: Flag `tuple[int]` when an arbitrary-length homogeneous tuple `tuple[int, ...]` or `Sequence[int]` is intended .
- **`Value = float or int` is `float`**: Because `float` is truthy at runtime, `float or int` evaluates immediately to `float`! Recommend `type Value = float | int` (Python 3.12+) or `Value: TypeAlias = float | int` .

---

## 3. Polymorphism (`Protocol`), Generics, `@overload`, and Constructors

### Polymorphism (`Protocol` or Base Class Interface) Over Procedural Backend Wrappers
- When standalone functions take a backend selector string (e.g., `vcs: str`) or wrap a backend object just to parse its output into domain results (e.g., procedural `get_modified_lines_from_vcs(...)` and `get_commit_message(...)` functions), recommend **polymorphism** (either inheritance on the base class or a `typing.Protocol`):
  > *"I feel like a lot of these things should be using polymorphism of some sort (doesn't have to be inheritance, can be a Protocol). The base VCS should probably have `.get_modified_lines` and `.get_commit_message` etc."*
- Note that when a class implements `__enter__` and `__exit__`, it already satisfies `contextlib.AbstractContextManager` as a structural `Protocol` without needing explicit runtime inheritance.

### Generics & `@overload` Over `Any` or Boolean-Switched Returns
- When a helper normalizes inputs (e.g., wrapping a single element `T` into `list[T]` while leaving `list[T]` unchanged), use type parameters (`def _ensure_list[T](val: list[T] | T) -> list[T]:`) or `@typing.overload` rather than `Any` (`gh-pganssle-zoneinfo-126`).
- Never vary a function's return type based on a boolean flag (`return_context: bool = False`); split into two functions (`writings: clean-api-design-variants`).

### `@classmethod` Constructors & Liskov Substitution (LSP)
- Replace union-typed `__init__(self, x: str | float)` argument sniffing with `@classmethod` alternate constructors (`from_str`) (`writings: single-dispatch-constructors`).
- Flag subclass methods that incompatibly narrow parameter types or violate base class contracts .

---

## 4. Paths, Package Resources & Metadata

- **Path Types**: Prefer `pathlib.Path`, `gpathlib.GPath`, or `type PathType = os.PathLike | str` over bare `str` . In Python 2/3 dual-compatible code, check whether path setters/getters need `Union[bytes, Text]` (`gh-pypa-build-149`).
- **Path Joining**: Flag string concatenation (`root_dir + '/subdir'`) and recommend `os.path.join` or `pathlib.Path` `/` .
- **`importlib.resources` over `__file__`**: Flag `__file__`-relative path traversal for locating deployed package data or policy/golden files; recommend `importlib.resources` .
- **`importlib.metadata` for Package Versions**: To check an installed package's version without triggering import-time side effects, suggest `importlib.metadata.version(...)`.

---

## 5. Voice & Anti-Bikeshedding Guardrails

Follow [references/voice-and-examples.md](references/voice-and-examples.md) when formatting comments:
- Never tell an author to replace `attrs` with `dataclasses` in a repository where `attrs` is already used.
- Keep local typing, alias, and enum observations crisp (1–2 sentences anchored directly on the offending line).
