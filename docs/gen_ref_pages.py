"""Generate the code reference pages."""

import ast
import importlib
import pkgutil
from pathlib import Path

DOCS_DIR = Path(__file__).parent


def open_generated(path: Path):
    """Open a generated documentation page for writing."""
    destination = DOCS_DIR / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination.open("w", encoding="utf-8")


def generate_module_docs(module_path, output_path, nav, indent=0):
    """Generate documentation for a module and its submodules."""
    try:
        module = importlib.import_module(module_path)
        doc_path = Path(output_path)
        # Collect submodule information for parent modules
        submodules = []
        if hasattr(module, "__path__"):
            for _, submodule_name, is_pkg in pkgutil.iter_modules(module.__path__):
                submodules.append((submodule_name, is_pkg))

        # Create a .md file for the current module
        if not module_path == "rdflib":
            with open_generated(doc_path) as fd:
                fd.write(f"::: {module_path}\n\n")
                if module_path.startswith("rdflib.namespace"):
                    # namespace module page gets too big, so we disable source code display
                    fd.write("    options:\n")
                    fd.write("        show_source: false\n")
                    fd.write("        show_if_no_docstring: false\n\n")

            # Add to navigation - convert path to tuple of parts for nav
            # parts = tuple(doc_path.with_suffix("").parts)
            # nav[parts] = doc_path.as_posix()
        # Process submodules
        if hasattr(module, "__path__"):
            for _, submodule_name, is_pkg in pkgutil.iter_modules(module.__path__):
                full_submodule_path = f"{module_path}.{submodule_name}"
                # Create path for submodule documentation
                generate_module_docs(
                    full_submodule_path,
                    Path(f"apidocs/{full_submodule_path}.md"),
                    nav,
                    indent + 4,
                )
    except (ImportError, AttributeError) as e:
        print(f"Error processing {module_path}: {e}")


def generate_example_docs(examples_dir: Path) -> None:
    """Document examples without importing or executing their code."""
    package = ast.parse((examples_dir / "__init__.py").read_text(encoding="utf-8"))
    with open_generated(Path("apidocs/examples.md")) as index:
        index.write(f"# Examples\n\n{ast.get_docstring(package) or ''}\n\n")
        for source_path in sorted(examples_dir.glob("*.py")):
            if source_path.name == "__init__.py":
                continue
            module_path = f"examples.{source_path.stem}"
            doc_path = Path(f"apidocs/{module_path}.md")
            index.write(f"- [{source_path.stem}]({doc_path.name})\n")
            source = source_path.read_text(encoding="utf-8")
            module = ast.parse(source)
            docstring = ast.get_docstring(module)
            lines = source.splitlines(keepends=True)
            if docstring is not None:
                del lines[module.body[0].lineno - 1 : module.body[0].end_lineno]
            with open_generated(doc_path) as page:
                page.write(f"# {source_path.stem} {{ #{module_path} }}\n\n")
                if docstring:
                    page.write(f"{docstring}\n\n")
                code = "".join(lines).strip("\n")
                page.write(f"```python\n{code}\n```\n")


nav = None

# Generate all docs
generate_module_docs("rdflib", Path("apidocs/_index.md"), nav)
generate_example_docs(DOCS_DIR.parent / "examples")
