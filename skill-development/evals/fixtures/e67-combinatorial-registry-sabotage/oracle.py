#!/usr/bin/env python3
from __future__ import annotations
import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_portfolio", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import portfolio.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name): return node.func.id
    if isinstance(node.func, ast.Attribute): return node.func.attr
    return ""


def assignment(node: ast.AST) -> tuple[str | None, ast.AST | None]:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id, node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id, node.value
    return None, None


def constant_string(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def portfolio_shape(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError as exc:
        return [f"cannot parse portfolio.py: {exc}"]
    assigned = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assigned.update(
        node.target.id
        for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    )
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    errors = []
    if "REGISTRY" not in assigned:
        errors.append("portfolio.py has no top-level REGISTRY assignment")
    for name in ("one_way_cases", "contract_passes"):
        if name not in functions:
            errors.append(f"portfolio.py has no {name} function")
    return errors


def test_shape(test_paths: list[Path]) -> list[str]:
    errors: list[str] = []
    exact_registry = False
    sabotage_bases: set[str] = set()

    for path in test_paths:
        source = path.read_text(errors="ignore")
        try: tree = ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"cannot parse candidate test {path.name}: {exc}")
            continue

        functions = [
            node for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test")
        ]
        for fn in functions:
            nodes = sorted(ast.walk(fn), key=lambda node: (getattr(node, "lineno", 0), getattr(node, "col_offset", 0)))
            assigns = [node for node in nodes if isinstance(node, (ast.Assign, ast.AnnAssign))]
            isolated: set[str] = set()
            fake_keys: dict[str, set[str]] = {}
            string_constants: dict[str, str] = {}

            for node in assigns:
                name, value = assignment(node)
                if name and value:
                    literal = constant_string(value)
                    if literal is not None:
                        string_constants[name] = literal
                    if isinstance(value, ast.Call) and call_name(value) == "dict" and value.args and isinstance(value.args[0], ast.Name) and value.args[0].id == "REGISTRY":
                        isolated.add(name)
                    elif isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr == "copy" and isinstance(value.func.value, ast.Name) and value.func.value.id == "REGISTRY":
                        isolated.add(name)

            def resolve_string(node: ast.AST) -> str | None:
                literal = constant_string(node)
                if literal is not None: return literal
                return string_constants.get(node.id) if isinstance(node, ast.Name) else None

            for node in assigns:
                name, value = assignment(node)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id in isolated:
                        key = resolve_string(target.slice)
                        if key: fake_keys.setdefault(target.value.id, set()).add(key)

            case_collections: dict[str, str] = {}
            id_collections: dict[str, str] = {}
            case_maps: dict[str, str] = {}
            selected_cases: dict[str, tuple[str, str]] = {}

            def cases_base(expr: ast.AST) -> str | None:
                if isinstance(expr, ast.Name): return case_collections.get(expr.id)
                if isinstance(expr, ast.Call) and call_name(expr) == "one_way_cases" and len(expr.args) == 1 and isinstance(expr.args[0], ast.Name):
                    return expr.args[0].id
                return None

            def generated_ids_base(expr: ast.AST) -> str | None:
                if isinstance(expr, ast.Name): return id_collections.get(expr.id)
                if isinstance(expr, ast.Call) and call_name(expr) in {"set", "list", "tuple", "sorted"} and expr.args:
                    if isinstance(expr.args[0], ast.Name) and expr.args[0].id in case_maps:
                        return case_maps[expr.args[0].id]
                    return generated_ids_base(expr.args[0])
                if isinstance(expr, (ast.ListComp, ast.SetComp, ast.GeneratorExp)) and len(expr.generators) == 1:
                    gen = expr.generators[0]
                    base = cases_base(gen.iter)
                    if base and isinstance(gen.target, ast.Name) and isinstance(expr.elt, ast.Attribute) and expr.elt.attr == "member_id" and isinstance(expr.elt.value, ast.Name) and expr.elt.value.id == gen.target.id:
                        return base
                return None

            def registry_keys_base(expr: ast.AST) -> str | None:
                if isinstance(expr, ast.Call) and call_name(expr) in {"set", "list", "tuple", "sorted"} and expr.args:
                    arg = expr.args[0]
                    if isinstance(arg, ast.Name): return arg.id
                    if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "keys" and isinstance(arg.func.value, ast.Name):
                        return arg.func.value.id
                    return registry_keys_base(arg)
                if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "keys" and isinstance(expr.func.value, ast.Name):
                    return expr.func.value.id
                return None

            def map_base(expr: ast.AST) -> str | None:
                if not isinstance(expr, ast.DictComp) or len(expr.generators) != 1: return None
                gen = expr.generators[0]; base = cases_base(gen.iter)
                if not base or not isinstance(gen.target, ast.Name): return None
                key_ok = isinstance(expr.key, ast.Attribute) and expr.key.attr == "member_id" and isinstance(expr.key.value, ast.Name) and expr.key.value.id == gen.target.id
                value_ok = isinstance(expr.value, ast.Name) and expr.value.id == gen.target.id
                return base if key_ok and value_ok else None

            def selected_case(expr: ast.AST) -> tuple[str, str] | None:
                if isinstance(expr, ast.Name): return selected_cases.get(expr.id)
                if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name) and expr.value.id in case_maps:
                    key = resolve_string(expr.slice)
                    return (case_maps[expr.value.id], key) if key else None
                if isinstance(expr, ast.Call) and call_name(expr) == "next" and expr.args and isinstance(expr.args[0], ast.GeneratorExp):
                    genexp = expr.args[0]
                    if len(genexp.generators) != 1: return None
                    gen = genexp.generators[0]; base = cases_base(gen.iter)
                    if not base or not isinstance(gen.target, ast.Name): return None
                    for condition in gen.ifs:
                        for compare in [n for n in ast.walk(condition) if isinstance(n, ast.Compare) and len(n.ops) == 1 and len(n.comparators) == 1]:
                            sides = [(compare.left, compare.comparators[0]), (compare.comparators[0], compare.left)]
                            for member, literal in sides:
                                if isinstance(member, ast.Attribute) and member.attr == "member_id" and isinstance(member.value, ast.Name) and member.value.id == gen.target.id:
                                    key = resolve_string(literal)
                                    if key: return base, key
                return None

            for node in assigns:
                name, value = assignment(node)
                if not name or value is None: continue
                base = cases_base(value)
                if base: case_collections[name] = base
                base = generated_ids_base(value)
                if base: id_collections[name] = base
                base = map_base(value)
                if base: case_maps[name] = base
                selected = selected_case(value)
                if selected: selected_cases[name] = selected

            exact_bases: set[str] = set()
            bite_bases: set[str] = set()
            for call in [node for node in nodes if isinstance(node, ast.Call)]:
                name = call_name(call)
                if name == "assertEqual" and len(call.args) >= 2:
                    left_generated = generated_ids_base(call.args[0]); right_generated = generated_ids_base(call.args[1])
                    left_registry = registry_keys_base(call.args[0]); right_registry = registry_keys_base(call.args[1])
                    if left_generated and right_registry == left_generated: exact_bases.add(left_generated)
                    if right_generated and left_registry == right_generated: exact_bases.add(right_generated)
                if name == "assertFalse" and call.args and isinstance(call.args[0], ast.Call) and call_name(call.args[0]) == "contract_passes" and call.args[0].args:
                    selected = selected_case(call.args[0].args[0])
                    if selected and selected[1] in fake_keys.get(selected[0], set()):
                        bite_bases.add(selected[0])

            if "REGISTRY" in exact_bases: exact_registry = True
            sabotage_bases.update(base for base in isolated if base in exact_bases and base in bite_bases and fake_keys.get(base))

    if not exact_registry: errors.append("candidate tests do not compare generated member_id values with exact canonical registry keys")
    if not sabotage_bases: errors.append("candidate tests do not select the injected fake from generated cases and assert its contract failure")
    combined = "\n".join(path.read_text(errors="ignore").lower() for path in test_paths)
    if "covered = true" in combined or "covered=true" in combined:
        errors.append("uses a voluntary covered flag")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors: list[str] = []
    portfolio = root / "portfolio.py"
    test_paths = sorted(root.rglob("test*.py"))
    if not portfolio.exists():
        errors.append("missing portfolio.py")
    else:
        errors.extend(portfolio_shape(portfolio))
    if not test_paths:
        errors.append("missing candidate unittest files")
    else:
        errors.extend(test_shape(test_paths))

    # Model-generated code is untrusted. Dynamic validation is permitted only
    # for the checked-in good/bad samples invoked by run-fixture-oracles.py.
    # Shared and prompt-run grading remain AST-only on the host.
    if os.environ.get("TBP_TRUSTED_FIXTURE_SELF_TEST") == "1" and portfolio.exists():
        try:
            mod = load_module(portfolio)
            registry = dict(mod.REGISTRY)
            fake_id = "__oracle_broken_member__"
            registry[fake_id] = lambda: "BROKEN"
            cases = list(mod.one_way_cases(registry))
            ids = {case.member_id for case in cases}
            if ids != set(registry):
                errors.append("one_way_cases does not exactly follow the supplied registry")
            fake_cases = [case for case in cases if case.member_id == fake_id]
            if not fake_cases:
                errors.append("injected fake member was not auto-enrolled")
            elif mod.contract_passes(fake_cases[0]) is not False:
                errors.append("the deliberately broken fake does not fail the generated contract")
        except Exception as exc:
            errors.append(f"dynamic registry sabotage failed: {exc}")
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(root), "-p", "test*.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            errors.append(f"candidate unittest suite failed: {proc.stdout}{proc.stderr}")
    for error in errors: print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
