import importlib
import pkgutil

import donor_reporting_portal


def check_imports(package=donor_reporting_portal):
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        current_module = f"{package.__name__}.{modname}"
        m = importlib.import_module(current_module)
        if hasattr(m, "__path__"):  # pragma: no cover
            for _, sub_mod, __ in pkgutil.iter_modules(m.__path__):
                sub_module = f"{current_module}.{sub_mod}"
                sm = importlib.import_module(sub_module)
                if hasattr(sm, "__path__"):
                    for _, s_sub_mod, __ in pkgutil.iter_modules(sm.__path__):
                        s_sub = f"{current_module}.{sub_mod}.{s_sub_mod}"
                        try:
                            importlib.import_module(s_sub)
                        except Exception as e:  # noqa
                            raise Exception(
                                f"""Error importing '{s_sub}'.
    {e}
    """
                            )
