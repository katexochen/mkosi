# SPDX-License-Identifier: LGPL-2.1+

from pathlib import Path
from typing import Optional

from mkosi.config import MkosiArgs, MkosiConfig
from mkosi.log import die
from mkosi.tree import make_tree
from mkosi.util import umask


class MkosiState:
    """State related properties."""
    source_date_epoch: Optional[int] = None

    def __init__(self, args: MkosiArgs, config: MkosiConfig, workspace: Path) -> None:
        self.args = args
        self.config = config
        self.workspace = workspace

        with umask(~0o755):
            make_tree(self.config, self.root)
        self.staging.mkdir()
        self.pkgmngr.mkdir()
        self.install_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        source_date_epoch = self.config.environment.get("SOURCE_DATE_EPOCH")
        if source_date_epoch is not None:
            try:
                mtime_epoch = int(source_date_epoch)
            except ValueError:
                die(f"SOURCE_DATE_EPOCH={source_date_epoch} is not a valid integer")
            if mtime_epoch < 0:
                die(f"SOURCE_DATE_EPOCH={source_date_epoch} is negative")
            self.source_date_epoch = mtime_epoch

    @property
    def root(self) -> Path:
        return self.workspace / "root"

    @property
    def staging(self) -> Path:
        return self.workspace / "staging"

    @property
    def pkgmngr(self) -> Path:
        return self.workspace / "pkgmngr"

    @property
    def cache_dir(self) -> Path:
        return self.config.cache_dir or self.workspace / f"cache/{self.config.distribution}~{self.config.release}"

    @property
    def install_dir(self) -> Path:
        return self.workspace / "dest"
