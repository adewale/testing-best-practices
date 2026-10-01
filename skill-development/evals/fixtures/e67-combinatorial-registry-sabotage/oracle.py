#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

FIXTURE_ROOT = Path(__file__).resolve().parent
TRUSTED_SAMPLE_ROOTS = {
    (FIXTURE_ROOT / "samples" / "good").resolve(),
    (FIXTURE_ROOT / "samples" / "bad").resolve(),
}
REQUIRED_IMPORTS = {"REGISTRY", "one_way_cases", "contract_passes"}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_portfolio", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import portfolio.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def is_self_assertion(node: ast.Call, name: str) -> bool:
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == name
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
    )


def assignment(node: ast.AST) -> tuple[str | None, ast.AST | None]:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id, node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id, node.value
    return None, None


def constant_string(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def references_name(node: ast.AST | None, name: str) -> bool:
    return node is not None and any(isinstance(item, ast.Name) and item.id == name for item in ast.walk(node))


def function_return(function: ast.FunctionDef) -> ast.Return | None:
    returns = [node for node in ast.walk(function) if isinstance(node, ast.Return) and node.value is not None]
    return returns[0] if returns else None


def direct_registry_iterator(expression: ast.AST, argument: str) -> bool:
    if isinstance(expression, ast.Name):
        return expression.id == argument
    if isinstance(expression, ast.Call):
        if (
            isinstance(expression.func, ast.Attribute)
            and isinstance(expression.func.value, ast.Name)
            and expression.func.value.id == argument
            and expression.func.attr in {"items", "keys"}
            and not expression.args
            and not expression.keywords
        ):
            return True
        if (
            isinstance(expression.func, ast.Name)
            and expression.func.id in {"iter", "list", "sorted", "tuple"}
            and len(expression.args) == 1
            and not expression.keywords
        ):
            return direct_registry_iterator(expression.args[0], argument)
    return False


def directly_enumerates_registry(function: ast.FunctionDef) -> bool:
    if not function.args.args:
        return False
    argument = function.args.args[0].arg
    returned = function_return(function)
    if returned is None or returned.value is None:
        return False
    expression = returned.value
    if (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Name)
        and expression.func.id in {"list", "set", "tuple"}
        and len(expression.args) == 1
        and not expression.keywords
    ):
        expression = expression.args[0]
    if not isinstance(expression, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
        return False
    if len(expression.generators) != 1:
        return False
    generator = expression.generators[0]
    if generator.is_async or generator.ifs or not direct_registry_iterator(generator.iter, argument):
        return False
    if isinstance(generator.target, ast.Name):
        member_id_name = generator.target.id
    elif (
        isinstance(generator.target, (ast.Tuple, ast.List))
        and generator.target.elts
        and isinstance(generator.target.elts[0], ast.Name)
    ):
        member_id_name = generator.target.elts[0].id
    else:
        return False
    if any(isinstance(node, ast.IfExp) for node in ast.walk(expression.elt)):
        return False
    return references_name(expression.elt, member_id_name)


def attribute_root_name(node: ast.AST) -> str | None:
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def calls_subject_behavior(function: ast.FunctionDef) -> bool:
    if not function.args.args:
        return False
    argument = function.args.args[0].arg
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and attribute_root_name(node.func) == argument
        for node in ast.walk(function)
    )


def portfolio_shape(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError as exc:
        return [f"cannot parse portfolio.py: {exc}"]

    assignments: dict[str, ast.AST | None] = {}
    for node in tree.body:
        name, value = assignment(node)
        if name:
            assignments[name] = value
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    errors: list[str] = []

    registry = assignments.get("REGISTRY")
    auto_enrolled_classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(keyword.arg == "member_id" and constant_string(keyword.value) for keyword in node.keywords)
    ]
    if not isinstance(registry, ast.Dict) or (not registry.keys and not auto_enrolled_classes):
        errors.append("portfolio.py REGISTRY must be populated directly or through member_id class enrollment")

    for name in ("one_way_cases", "contract_passes"):
        function = functions.get(name)
        if function is None:
            errors.append(f"portfolio.py has no {name} function")
            continue
        if not function.args.args:
            errors.append(f"portfolio.py {name} must accept its subject as an argument")
            continue
        argument = function.args.args[0].arg
        returned = function_return(function)
        if returned is None or not references_name(function, argument):
            errors.append(f"portfolio.py {name} must return after using its argument")
        if name == "one_way_cases" and not directly_enumerates_registry(function):
            errors.append(
                "portfolio.py one_way_cases must directly enumerate every supplied registry member without filters"
            )
        if name == "contract_passes" and not calls_subject_behavior(function):
            errors.append("portfolio.py contract_passes must call behavior reached through its case argument")

    return errors


def imported_portfolio_names(tree: ast.Module) -> set[str]:
    imported: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "portfolio":
            imported.update(alias.asname or alias.name for alias in node.names if alias.name in REQUIRED_IMPORTS)
    return imported


def is_unittest_case(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if (
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "unittest"
            and base.attr == "TestCase"
        ):
            return True
        if isinstance(base, ast.Name) and base.id == "TestCase":
            return True
    return False


def has_skip_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> bool:
    for decorator in node.decorator_list:
        name = ""
        if isinstance(decorator, ast.Name):
            name = decorator.id
        elif isinstance(decorator, ast.Attribute):
            name = decorator.attr
        elif isinstance(decorator, ast.Call):
            name = call_name(decorator)
        if name.lower() in {"skip", "skipif", "skipunless", "xfail"}:
            return True
    return False


def has_dead_constant_branch(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(function):
        if (
            isinstance(node, (ast.If, ast.While))
            and isinstance(node.test, ast.Constant)
            and node.test.value in {False, None}
        ):
            return True
    return False


def test_shape(test_paths: list[Path]) -> list[str]:
    errors: list[str] = []
    exact_registry = False
    sabotage_bases: set[str] = set()

    for path in test_paths:
        source = path.read_text(errors="ignore")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"cannot parse candidate test {path.name}: {exc}")
            continue

        imported = imported_portfolio_names(tree)
        if imported != REQUIRED_IMPORTS:
            errors.append(
                f"{path.name} must import REGISTRY, one_way_cases, and contract_passes directly from portfolio"
            )
            continue
        if not any(isinstance(node, ast.Import) and any(alias.name == "unittest" for alias in node.names) for node in tree.body):
            errors.append(f"{path.name} must import unittest")
            continue

        shadowed = {
            name
            for node in tree.body
            for name, _ in [assignment(node)]
            if name in REQUIRED_IMPORTS
        }
        shadowed.update(
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name in REQUIRED_IMPORTS
        )
        if shadowed:
            errors.append(f"{path.name} shadows imported portfolio names: {sorted(shadowed)}")
            continue

        classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and is_unittest_case(node)]
        if not classes:
            errors.append(f"{path.name} has no unittest.TestCase class")
            continue

        functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        for class_node in classes:
            if has_skip_decorator(class_node):
                errors.append(f"{path.name} skips its unittest.TestCase class")
            functions.extend(
                node
                for node in class_node.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test")
            )

        for function in functions:
            if has_skip_decorator(function):
                errors.append(f"{path.name}:{function.name} is skipped or expected to fail")
                continue
            if has_dead_constant_branch(function):
                errors.append(f"{path.name}:{function.name} hides obligations in a statically dead branch")
                continue
            if not function.args.args or function.args.args[0].arg != "self":
                errors.append(f"{path.name}:{function.name} is not a bound unittest method")
                continue
            if any(isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) for statement in function.body):
                errors.append(f"{path.name}:{function.name} nests helper functions inside the test")
                continue

            nodes = sorted(
                (node for statement in function.body for node in ast.walk(statement)),
                key=lambda node: (getattr(node, "lineno", 0), getattr(node, "col_offset", 0)),
            )
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
                    if (
                        isinstance(value, ast.Dict)
                        and not value.keys
                    ) or (
                        isinstance(value, ast.Call)
                        and call_name(value) == "dict"
                        and value.args
                        and isinstance(value.args[0], ast.Name)
                        and value.args[0].id == "REGISTRY"
                    ) or (
                        isinstance(value, ast.Call)
                        and isinstance(value.func, ast.Attribute)
                        and value.func.attr == "copy"
                        and isinstance(value.func.value, ast.Name)
                        and value.func.value.id == "REGISTRY"
                    ):
                        isolated.add(name)

            def resolve_string(
                node: ast.AST, constants: dict[str, str] = string_constants
            ) -> str | None:
                literal = constant_string(node)
                if literal is not None:
                    return literal
                return constants.get(node.id) if isinstance(node, ast.Name) else None

            for node in assigns:
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Name)
                        and target.value.id in isolated
                    ):
                        key = resolve_string(target.slice)
                        if key:
                            fake_keys.setdefault(target.value.id, set()).add(key)
            for class_node in [node for node in nodes if isinstance(node, ast.ClassDef)]:
                registry_name = next(
                    (
                        keyword.value.id
                        for keyword in class_node.keywords
                        if keyword.arg == "registry" and isinstance(keyword.value, ast.Name)
                    ),
                    None,
                )
                member_id = next(
                    (
                        constant_string(keyword.value)
                        for keyword in class_node.keywords
                        if keyword.arg == "member_id"
                    ),
                    None,
                )
                if registry_name in isolated and member_id:
                    fake_keys.setdefault(registry_name, set()).add(member_id)

            case_collections: dict[str, str] = {}
            id_collections: dict[str, str] = {}
            case_maps: dict[str, str] = {}
            selected_cases: dict[str, tuple[str, str]] = {}

            def cases_base(
                expression: ast.AST, collections: dict[str, str] = case_collections
            ) -> str | None:
                if isinstance(expression, ast.Name):
                    return collections.get(expression.id)
                if (
                    isinstance(expression, ast.Call)
                    and call_name(expression) == "one_way_cases"
                    and len(expression.args) == 1
                    and isinstance(expression.args[0], ast.Name)
                ):
                    return expression.args[0].id
                return None

            def generated_ids_base(
                expression: ast.AST,
                ids: dict[str, str] = id_collections,
                maps: dict[str, str] = case_maps,
            ) -> str | None:
                if isinstance(expression, ast.Name):
                    return ids.get(expression.id)
                if isinstance(expression, ast.Call) and call_name(expression) in {"set", "list", "tuple", "sorted"} and expression.args:
                    if isinstance(expression.args[0], ast.Name) and expression.args[0].id in maps:
                        return maps[expression.args[0].id]
                    return generated_ids_base(expression.args[0])
                if isinstance(expression, (ast.ListComp, ast.SetComp, ast.GeneratorExp)) and len(expression.generators) == 1:
                    generator = expression.generators[0]
                    base = cases_base(generator.iter)
                    if (
                        base
                        and isinstance(generator.target, ast.Name)
                        and isinstance(expression.elt, ast.Attribute)
                        and expression.elt.attr == "member_id"
                        and isinstance(expression.elt.value, ast.Name)
                        and expression.elt.value.id == generator.target.id
                    ):
                        return base
                return None

            def registry_keys_base(expression: ast.AST) -> str | None:
                if isinstance(expression, ast.Call) and call_name(expression) in {"set", "list", "tuple", "sorted"} and expression.args:
                    argument = expression.args[0]
                    if isinstance(argument, ast.Name):
                        return argument.id
                    if (
                        isinstance(argument, ast.Call)
                        and isinstance(argument.func, ast.Attribute)
                        and argument.func.attr == "keys"
                        and isinstance(argument.func.value, ast.Name)
                    ):
                        return argument.func.value.id
                    return registry_keys_base(argument)
                if (
                    isinstance(expression, ast.Call)
                    and isinstance(expression.func, ast.Attribute)
                    and expression.func.attr == "keys"
                    and isinstance(expression.func.value, ast.Name)
                ):
                    return expression.func.value.id
                return None

            def map_base(expression: ast.AST) -> str | None:
                if not isinstance(expression, ast.DictComp) or len(expression.generators) != 1:
                    return None
                generator = expression.generators[0]
                base = cases_base(generator.iter)
                if not base or not isinstance(generator.target, ast.Name):
                    return None
                key_ok = (
                    isinstance(expression.key, ast.Attribute)
                    and expression.key.attr == "member_id"
                    and isinstance(expression.key.value, ast.Name)
                    and expression.key.value.id == generator.target.id
                )
                value_ok = isinstance(expression.value, ast.Name) and expression.value.id == generator.target.id
                return base if key_ok and value_ok else None

            def selected_case(
                expression: ast.AST,
                selected_values: dict[str, tuple[str, str]] = selected_cases,
                maps: dict[str, str] = case_maps,
            ) -> tuple[str, str] | None:
                if isinstance(expression, ast.Name):
                    return selected_values.get(expression.id)
                if isinstance(expression, ast.Subscript) and isinstance(expression.value, ast.Name) and expression.value.id in maps:
                    key = resolve_string(expression.slice)
                    return (maps[expression.value.id], key) if key else None
                if isinstance(expression, ast.Call) and call_name(expression) == "next" and expression.args and isinstance(expression.args[0], ast.GeneratorExp):
                    generator_expression = expression.args[0]
                    if len(generator_expression.generators) != 1:
                        return None
                    generator = generator_expression.generators[0]
                    base = cases_base(generator.iter)
                    if not base or not isinstance(generator.target, ast.Name):
                        return None
                    for condition in generator.ifs:
                        comparisons = [node for node in ast.walk(condition) if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1]
                        for compare in comparisons:
                            sides = [(compare.left, compare.comparators[0]), (compare.comparators[0], compare.left)]
                            for member, literal in sides:
                                if (
                                    isinstance(member, ast.Attribute)
                                    and member.attr == "member_id"
                                    and isinstance(member.value, ast.Name)
                                    and member.value.id == generator.target.id
                                ):
                                    key = resolve_string(literal)
                                    if key:
                                        return base, key
                return None

            for node in assigns:
                name, value = assignment(node)
                if not name or value is None:
                    continue
                base = cases_base(value)
                if base:
                    case_collections[name] = base
                base = generated_ids_base(value)
                if base:
                    id_collections[name] = base
                base = map_base(value)
                if base:
                    case_maps[name] = base
                selected = selected_case(value)
                if selected:
                    selected_cases[name] = selected
            for node in assigns:
                if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                    continue
                target = node.targets[0]
                if (
                    isinstance(target, (ast.Tuple, ast.List))
                    and len(target.elts) == 1
                    and isinstance(target.elts[0], ast.Name)
                    and isinstance(node.value, ast.Name)
                    and node.value.id in case_collections
                ):
                    base = case_collections[node.value.id]
                    keys = fake_keys.get(base, set())
                    if len(keys) == 1:
                        selected_cases[target.elts[0].id] = (base, next(iter(keys)))

            exact_bases: set[str] = set()
            bite_bases: set[str] = set()
            for call in [node for node in nodes if isinstance(node, ast.Call)]:
                if is_self_assertion(call, "assertEqual") and len(call.args) >= 2:
                    left_generated = generated_ids_base(call.args[0])
                    right_generated = generated_ids_base(call.args[1])
                    left_registry = registry_keys_base(call.args[0])
                    right_registry = registry_keys_base(call.args[1])
                    if left_generated and right_registry == left_generated:
                        exact_bases.add(left_generated)
                    if right_generated and left_registry == right_generated:
                        exact_bases.add(right_generated)
                if (
                    is_self_assertion(call, "assertFalse")
                    and call.args
                    and isinstance(call.args[0], ast.Call)
                    and call_name(call.args[0]) == "contract_passes"
                    and call.args[0].args
                ):
                    selected = selected_case(call.args[0].args[0])
                    if selected and selected[1] in fake_keys.get(selected[0], set()):
                        bite_bases.add(selected[0])

            if "REGISTRY" in exact_bases:
                exact_registry = True
            sabotage_bases.update(
                base for base in isolated if base in exact_bases and base in bite_bases and fake_keys.get(base)
            )

    if not exact_registry:
        errors.append("candidate tests do not compare generated member_id values with exact canonical registry keys")
    if not sabotage_bases:
        errors.append("candidate tests do not select the injected fake from generated cases and assert its contract failure")
    combined = "\n".join(path.read_text(errors="ignore").lower() for path in test_paths)
    if "covered = true" in combined or "covered=true" in combined:
        errors.append("uses a voluntary covered flag")
    return errors


def main() -> int:
    root = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()).resolve()
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

    trusted_self_test = os.environ.get("TBP_TRUSTED_FIXTURE_SELF_TEST") == "1" and root in TRUSTED_SAMPLE_ROOTS
    if trusted_self_test and portfolio.exists():
        try:
            module = load_module(portfolio)
            registry = dict(module.REGISTRY)
            fake_id = "__oracle_broken_member__"
            registry[fake_id] = lambda: "BROKEN"
            cases = list(module.one_way_cases(registry))
            ids = {case.member_id for case in cases}
            if ids != set(registry):
                errors.append("one_way_cases does not exactly follow the supplied registry")
            fake_cases = [case for case in cases if case.member_id == fake_id]
            if not fake_cases:
                errors.append("injected fake member was not auto-enrolled")
            elif module.contract_passes(fake_cases[0]) is not False:
                errors.append("the deliberately broken fake does not fail the generated contract")
        except Exception as exc:
            errors.append(f"dynamic registry sabotage failed: {exc}")
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(root), "-p", "test*.py"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        if proc.returncode != 0:
            errors.append(f"candidate unittest suite failed: {proc.stdout}{proc.stderr}")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
