from site_scons.site_tools.NVDATool.typings import (
    AddonInfo,
    BrailleTables,
    SymbolDictionaries,
)
from site_scons.site_tools.NVDATool.utils import _

addon_info = AddonInfo(
    addon_name="slashMenus",
    addon_summary=_("Slash Menus"),
    addon_description=_(
        """Reads the slash and at-sign suggestion lists of AI apps such as ChatGPT, Claude, OpenCode and WhatsApp, which screen readers otherwise ignore."""
    ),
    addon_version="0.1.0",
    addon_changelog=_("""- Version 0.1.0: First version."""),
    addon_author="Kamal Yaser <kamalyaser31@gmail.com>",
    addon_url="https://github.com/kamalyaser31/slashMenus",
    addon_sourceURL="https://github.com/kamalyaser31/slashMenus",
    addon_docFileName="readme.html",
    addon_minimumNVDAVersion="2024.1.0",
    addon_lastTestedNVDAVersion="2026.1.0",
    addon_updateChannel=None,
    addon_license="GPL v2",
    addon_licenseURL="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
)

pythonSources = ["addon/**/*.py"]
i18nSources: list[str] = pythonSources + ["buildVars.py"]
excludedFiles: list[str] = ["*.pyc"]
baseLanguage: str = "en"
markdownExtensions: list[str] = []
brailleTables: BrailleTables = {}
symbolDictionaries: SymbolDictionaries = {}
speechDictionaries: dict = {}
