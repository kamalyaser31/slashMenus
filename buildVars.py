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
        """Makes the slash and at-sign menus of AI apps speak. When you type / or @ in ChatGPT, Claude, OpenCode or WhatsApp, NVDA reads the list that opens and the highlighted command, file or person as you move with the arrows or keep typing. The arrows behave normally everywhere else."""
    ),
    addon_version="2026.1",
    addon_changelog=_(
        """- Version 2026.1: First release. NVDA reads the / and @ suggestion lists in ChatGPT, Claude, OpenCode and WhatsApp."""
    ),
    addon_author="Kamal Yaser <kamalyaser31@gmail.com>",
    addon_url="https://github.com/kamalyaser31/slashMenus",
    addon_sourceURL="https://github.com/kamalyaser31/slashMenus",
    addon_docFileName="readme.html",
    addon_minimumNVDAVersion="2024.1.0",
    addon_lastTestedNVDAVersion="2026.1.0",
    addon_updateChannel=None,
    addon_license="GPL v2",
    addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

pythonSources = ["addon/**/*.py"]
i18nSources: list[str] = pythonSources + ["buildVars.py"]
excludedFiles: list[str] = ["*.pyc"]
baseLanguage: str = "en"
markdownExtensions: list[str] = []
brailleTables: BrailleTables = {}
symbolDictionaries: SymbolDictionaries = {}
speechDictionaries: dict = {}
