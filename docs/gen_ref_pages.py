"""Generate the code reference pages."""

import importlib
import pkgutil
from pathlib import Path

import mkdocs_gen_files


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
            with mkdocs_gen_files.open(doc_path, "w") as fd:
                fd.write(f"::: {module_path}\n\n")
                # namespace module page gets too big, so we disable source code display
                if module_path.startswith("rdflib.namespace"):
                    fd.write("    options:\n")
                    fd.write("        show_source: false\n")
                    fd.write("        show_if_no_docstring: false\n\n")

            mkdocs_gen_files.set_edit_path(
                doc_path, Path(f"../{module_path.replace('.', '/')}.py")
            )
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


# Creating navigation structure requires mkdocs-literate-nav
# nav = mkdocs_gen_files.Nav()
nav = None

# Generate all docs
generate_module_docs("rdflib", Path("apidocs/_index.md"), nav)
generate_module_docs("examples", Path("apidocs/examples.md"), nav)

# # Write the navigation file for the literate-nav plugin
# with mkdocs_gen_files.open("SUMMARY.md", "w") as nav_file:
#     nav_file.writelines(nav.build_literate_nav())
