"""Start an MCP server with credentials from a local .env, so no secret is ever written in a config file.

    python tools/mcp_env_wrapper.py --env-file .env --need GITHUB_TOKEN -- npx -y @modelcontextprotocol/server-github

Some MCP clients cannot resolve ${env:NAME} in their configuration, which tempts people to
paste the secret as text. Point the client at this wrapper instead: it reads only the names
asked for with --need from the .env file, adds them to the environment, and starts the
server with the command after "--".

Why it is written this way:
- the .env parser is a few lines and needs no package;
- the command is started as a list of arguments, never through a shell, so nothing in it is
  interpreted (on Windows the command interpreter is not involved either);
- values are never printed, and messages go to stderr only, because stdout is the channel
  the MCP protocol uses;
- a missing name stops with an error that names the variable, never its value.
"""

import os
import subprocess
import sys
from pathlib import Path


def parse_env(text: str) -> dict[str, str]:
    """KEY=VALUE lines; comments, blank lines and lines without "=" are ignored, never echoed."""
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip().removeprefix("export ").strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def build_env(env_file: Path, needed: list[str], base: dict[str, str]) -> dict[str, str]:
    found = parse_env(env_file.read_text(encoding="utf-8")) if env_file.is_file() else {}
    env = dict(base)
    missing = []
    for name in needed:
        if name in found:
            env[name] = found[name]
        elif not base.get(name):
            missing.append(name)
    if missing:
        raise SystemExit(f"mcp_env_wrapper: missing {', '.join(missing)} in {env_file} and in the environment")
    return env


def split_args(argv: list[str]) -> tuple[Path, list[str], list[str]]:
    if "--" not in argv:
        raise SystemExit('usage: mcp_env_wrapper.py --env-file .env --need NAME [--need NAME] -- command args...')
    own, command = argv[:argv.index("--")], argv[argv.index("--") + 1:]
    env_file, needed = Path(".env"), []
    for i, arg in enumerate(own):
        if arg == "--env-file":
            env_file = Path(own[i + 1])
        elif arg == "--need":
            needed.append(own[i + 1])
    if not command:
        raise SystemExit("mcp_env_wrapper: no command after --")
    return env_file, needed, command


def main(argv: list[str] | None = None) -> int:
    env_file, needed, command = split_args(sys.argv[1:] if argv is None else argv)
    env = build_env(env_file, needed, dict(os.environ))
    # A list of arguments and shell=False: nothing in the command is interpreted by a shell.
    return subprocess.call(command, env=env, shell=False)


if __name__ == "__main__":
    sys.exit(main())
