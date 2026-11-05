#!/usr/bin/env python3
"""Oracle for E60: inspect untrusted candidates without executing them.

Default grading checks a bounded shared-pytest-fixture shape and undecorated test
functions statically. It does
not claim runtime validation or infer arbitrary helpers, aliases or control flow.
Only the exact checked-in sample roots with the trusted self-test flag run the
legacy dynamic controls below; an ambient flag never authorizes another path.

For those trusted samples, three pytest runs decide:
  1. pristine impls           -> candidate tests must PASS
  2. drifted fake (get() returns None on missing keys) -> must FAIL
  3. drifted real (get() returns None on missing keys) -> must FAIL

Run 2 catches a suite that never checks the fake's contract; run 3 catches a
suite that checks the fake but never runs the same expectations against the
real implementation. Only a shared contract suite executed against BOTH
implementations passes all three — which is the lesson (Google Testing Blog:
Fake Your Way to Better Tests, 2013; Exercise Service Call Contracts, 2018).
"""
from __future__ import annotations

import os
import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
REAL = (FIXTURE / "impl" / "store.py").read_text()
FAKE = (FIXTURE / "impl" / "fake_store.py").read_text()
TRUSTED_SAMPLE_ROOTS = {(FIXTURE / "samples" / name).resolve() for name in ("good", "bad")}


def static_contract(files: list[Path]) -> list[str]:
    """Support the direct shared pytest fixture shape, without executing code."""
    errors = []
    try:
        trees = [ast.parse(path.read_text()) for path in files]
    except (SyntaxError, UnicodeError) as exc:
        return [f"candidate is not parseable Python: {exc}"]
    imports = {(node.module, alias.name) for tree in trees for node in tree.body
               if isinstance(node, ast.ImportFrom) for alias in node.names if alias.asname is None}
    if not {("store", "RealStore"), ("fake_store", "FakeStore")} <= imports:
        errors.append("missing direct real/fake implementation imports")
    functions = [node for tree in trees for node in tree.body if isinstance(node, ast.FunctionDef)]
    fixtures = []
    for fn in functions:
        # Stay within the direct factory shape. In particular name= changes
        # pytest's registered name; another decorator may replace the factory.
        if len(fn.decorator_list) != 1:
            continue
        for decorator in fn.decorator_list:
            if not (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                    and isinstance(decorator.func.value, ast.Name)
                    and decorator.func.value.id == "pytest" and decorator.func.attr == "fixture"):
                continue
            if decorator.args or len(decorator.keywords) != 1 or decorator.keywords[0].arg != "params":
                continue
            params = next((kw.value for kw in decorator.keywords if kw.arg == "params"), None)
            if not (isinstance(params, (ast.List, ast.Tuple)) and
                    len(params.elts) == 2 and
                    [item.value for item in params.elts if isinstance(item, ast.Constant)] == ["fake", "real"]):
                continue
            # Only the direct two-branch factory is supported; mere references
            # to RealStore in dead code do not enroll the real implementation.
            if len(fn.body) != 2 or not isinstance(fn.body[0], ast.If) or fn.body[0].orelse:
                continue
            branch = fn.body[0]
            condition = branch.test
            if not (isinstance(condition, ast.Compare) and len(condition.ops) == 1
                    and isinstance(condition.ops[0], ast.Eq)
                    and ast.unparse(condition.left) == "request.param"
                    and ast.literal_eval(condition.comparators[0]) == "fake"):
                continue
            def returns_constructor(statements, name):
                return (len(statements) == 1 and isinstance(statements[0], ast.Return)
                        and isinstance(statements[0].value, ast.Call)
                        and isinstance(statements[0].value.func, ast.Name)
                        and statements[0].value.func.id == name)
            if returns_constructor(branch.body, "FakeStore") and returns_constructor([fn.body[1]], "RealStore"):
                fixtures.append(fn.name)
    if not fixtures:
        errors.append("no supported shared fixture directly selects FakeStore and RealStore")
    get_checked = missing_checked = False
    for fn in functions:
        # Parametrization can override a same-named fixture, and skip/other
        # decorators can change test reachability. This bounded checker only
        # credits plain tests, rather than pretending to interpret decorators.
        if not fn.name.startswith("test_") or fn.decorator_list:
            continue
        names = {arg.arg for arg in fn.args.args} & set(fixtures)
        for name in names:
            saved = {}
            for statement in fn.body:
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    call = statement.value
                    if (isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name)
                            and call.func.value.id == name and call.func.attr == "set"
                            and len(call.args) == 2 and all(isinstance(arg, ast.Constant) and isinstance(arg.value, str) for arg in call.args)):
                        saved[call.args[0].value] = call.args[1].value
                if isinstance(statement, ast.Assert) and isinstance(statement.test, ast.Compare):
                    comparison = statement.test
                    if len(comparison.ops) == 1 and isinstance(comparison.ops[0], ast.Eq):
                        call, expected = comparison.left, comparison.comparators[0]
                        if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                                and isinstance(call.func.value, ast.Name) and call.func.value.id == name
                                and call.func.attr == "get" and len(call.args) == 1
                                and isinstance(call.args[0], ast.Constant) and isinstance(expected, ast.Constant)):
                            get_checked |= call.args[0].value in saved and saved[call.args[0].value] == expected.value
                if isinstance(statement, ast.With) and len(statement.items) == 1:
                    context = statement.items[0].context_expr
                    if (isinstance(context, ast.Call) and ast.unparse(context.func) == "pytest.raises"
                            and len(context.args) == 1 and isinstance(context.args[0], ast.Name)
                            and context.args[0].id == "KeyError" and len(statement.body) == 1
                            and isinstance(statement.body[0], ast.Expr)):
                        call = statement.body[0].value
                        if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                                and isinstance(call.func.value, ast.Name) and call.func.value.id == name
                                and call.func.attr == "get" and len(call.args) == 1
                                and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str)):
                            missing_checked |= call.args[0].value not in saved
    if not get_checked:
        errors.append("no direct literal set/get equality through the shared fixture")
    if not missing_checked:
        errors.append("no direct missing-key KeyError assertion through the shared fixture")
    return errors

DRIFT_FAKE = FAKE.replace(
    "        if key not in self._data:\n            raise KeyError(key)\n        return self._data[key]",
    "        return self._data.get(key)",
)
DRIFT_REAL = REAL.replace(
    "        if row is None:\n            raise KeyError(key)\n        return row[0]",
    "        return row[0] if row is not None else None",
)


def run_pytest(store_src: str, fake_src: str, candidate_files: list[Path]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "store.py").write_text(store_src)
        (d / "fake_store.py").write_text(fake_src)
        for f in candidate_files:
            shutil.copy(f, d / f.name)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
            cwd=d, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
        )
        return proc.returncode == 0, proc.stdout[-1500:]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    candidates = sorted(
        p for p in root.rglob("*.py")
        if p.name.startswith("test") or p.name.endswith("_test.py") or p.name == "conftest.py"
    )
    if not candidates:
        print("no test files (test*.py / conftest.py) found in candidate dir", file=sys.stderr)
        return 1
    if not (os.environ.get("TBP_TRUSTED_FIXTURE_SELF_TEST") == "1" and root.resolve() in TRUSTED_SAMPLE_ROOTS):
        try:
            errors = static_contract(candidates)
        except (ValueError, TypeError, OSError) as exc:
            errors = [f"unsupported static shape: {exc}"]
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    for name, drifted, original in [("fake", DRIFT_FAKE, FAKE), ("real", DRIFT_REAL, REAL)]:
        if drifted == original:
            print(f"oracle self-error: {name} drift substitution failed", file=sys.stderr)
            return 2

    errors: list[str] = []
    ok, out = run_pytest(REAL, FAKE, candidates)
    if not ok:
        errors.append(f"candidate tests FAIL against the pristine implementations:\n{out}")
    else:
        ok, _ = run_pytest(REAL, DRIFT_FAKE, candidates)
        if ok:
            errors.append(
                "drifted FAKE survived: tests pass although FakeStore.get now returns "
                "None on missing keys (the shipped-bug scenario repeats)"
            )
        ok, _ = run_pytest(DRIFT_REAL, FAKE, candidates)
        if ok:
            errors.append(
                "drifted REAL survived: the contract expectations never run against "
                "RealStore, so the fake is only honest with itself"
            )

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
