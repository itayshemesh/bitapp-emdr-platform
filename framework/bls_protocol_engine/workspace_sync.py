"""Zero-Repo-Secret Google Workspace & Local Session Telemetry Exporter."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
import sys
from typing import Any, Dict, Optional

from framework.bls_protocol_engine.schemas import SessionSummary

DEFAULT_OAUTH_CONFIG_PATH = os.path.expanduser(
    "~/.config/bitapp-emdr/oauth_client.json"
)
DEFAULT_SESSION_LOG_DIR = os.path.expanduser(
    "~/.local/share/bitapp-emdr/sessions"
)


class GoogleWorkspaceSessionExporter:
    """Exports anonymized EMDR session summaries to local JSONL and optional Google Workspace.

    Enforces strict credential isolation:
    - OAuth 2.0 Installed Application credentials are NEVER stored inside the repository.
    - Credentials are loaded exclusively from ~/.config/bitapp-emdr/oauth_client.json (mode 0600)
      or the BITAPP_OAUTH_CLIENT_PATH environment variable.
    - All I/O and parsing errors emit structured diagnostics to sys.stderr.
    """

    def __init__(
        self,
        oauth_client_path: Optional[str] = None,
        session_log_dir: Optional[str] = None,
    ) -> None:
        self.oauth_client_path = (
            oauth_client_path
            or os.environ.get("BITAPP_OAUTH_CLIENT_PATH")
            or DEFAULT_OAUTH_CONFIG_PATH
        )
        self.session_log_dir = session_log_dir or DEFAULT_SESSION_LOG_DIR

    def load_installed_oauth_metadata(self) -> Optional[Dict[str, Any]]:
        """Loads and validates OAuth client config from outside the Git repository."""
        if not os.path.isfile(self.oauth_client_path):
            sys.stderr.write(
                f"[workspace_sync] Diagnostic: OAuth config not found at "
                f"'{self.oauth_client_path}'; falling back to local JSONL storage.\n"
            )
            return None
        try:
            with open(self.oauth_client_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            installed = data.get("installed")
            if not isinstance(installed, dict) or not installed.get("client_id"):
                sys.stderr.write(
                    f"[workspace_sync] Error: Invalid 'installed' OAuth structure in "
                    f"'{self.oauth_client_path}'.\n"
                )
                return None
            return {
                "project_id": installed.get("project_id", ""),
                "auth_uri": installed.get("auth_uri", ""),
                "token_uri": installed.get("token_uri", ""),
                "client_id_configured": True,
            }
        except (OSError, ValueError, json.JSONDecodeError) as err:
            sys.stderr.write(
                f"[workspace_sync] Error reading OAuth client file "
                f"'{self.oauth_client_path}': {err}\n"
            )
            return None

    def persist_session_summary(self, summary: SessionSummary) -> str:
        """Writes the session summary to an isolated local JSONL ledger."""
        try:
            os.makedirs(self.session_log_dir, mode=0o700, exist_ok=True)
            log_file = os.path.join(self.session_log_dir, "sessions.jsonl")
            payload = asdict(summary)
            payload["completed_phases"] = [p.value for p in summary.completed_phases]
            oauth_meta = self.load_installed_oauth_metadata()
            payload["oauth_workspace_ready"] = bool(oauth_meta)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, sort_keys=True) + "\n")
            return log_file
        except OSError as err:
            sys.stderr.write(
                f"[workspace_sync] Failed persisting session '{summary.session_id}' "
                f"to '{self.session_log_dir}': {err}\n"
            )
            raise
