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
                if module_path.startswith("rdflib.namespace"):
                    # namespace module page gets too big, so we disable source code display
                    fd.write("    options:\n")
                    fd.write("        show_source: false\n")
                    fd.write("        show_if_no_docstring: false\n\n")
                if module_path.startswith("examples."):
                    # Special handling for examples: show top docstring and rest of source code
                    file_path = module.__file__
                    if file_path:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        docstring = module.__doc__ or ""
                        # Remove the docstring from the code content
                        code = content
                        if docstring:
                            for quote in ['"""', "'''"]:
                                doc_quoted = quote + docstring + quote
                                start = code.find(doc_quoted)
                                if start != -1:
                                    end = start + len(doc_quoted)
                                    code = code[:start] + code[end:]
                                    break
                        # Mkdocstrings options: https://mkdocstrings.github.io/python/reference/api/#mkdocstrings_handlers.python.PythonInputOptions
                        with mkdocs_gen_files.open(doc_path, "w") as fd:
                            fd.write("    options:\n")
                            fd.write("        show_source: false\n")
                            fd.write("        show_docstring_attributes: false\n")
                            fd.write("        show_docstring_functions: false\n")
                            fd.write("        show_docstring_modules: false\n")
                            fd.write("        show_docstring_classes: false\n")
                            fd.write("        show_signature: false\n")
                            fd.write("        show_signature_annotations: false\n")
                            fd.write("        show_signature_type_parameters: false\n")
                            fd.write("        show_docstring_other_parameters: false\n")
                            fd.write("        show_docstring_parameters: false\n")
                            fd.write("        show_docstring_raises: false\n")
                            fd.write("        show_docstring_receives: false\n")
                            fd.write("        show_docstring_returns: false\n")
                            fd.write("        summary: false\n")
                            fd.write("        show_if_no_docstring: false\n\n")
                            fd.write("```python\n")
                            fd.write(code)
                            fd.write("\n```\n")

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
