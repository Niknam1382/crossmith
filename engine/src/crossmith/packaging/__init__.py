from crossmith.packaging.base import PackageResult, PackagingBackend
from crossmith.packaging.nuitka_backend import NuitkaBackend
from crossmith.packaging.pyinstaller_backend import PyInstallerBackend

BACKENDS: dict[str, PackagingBackend] = {
    "nuitka": NuitkaBackend(),
    "pyinstaller": PyInstallerBackend(),
}

__all__ = [
    "BACKENDS",
    "NuitkaBackend",
    "PackageResult",
    "PackagingBackend",
    "PyInstallerBackend",
]
