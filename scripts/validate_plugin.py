#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("FAIL jsonschema is not installed. Run pip install jsonschema")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
PATH_FIELDS = ("logo", "skills", "rules", "agents", "commands", "hooks", "mcpServers", "source")
SECRET_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "api-key",
    "secret",
    "password",
    "access_token",
    "refresh_token",
    "client_secret",
    "private_key",
}
SECRET_VALUE = re.compile(
    r"(?:sk-[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|xox[baprs]-[A-Za-z0-9-]+|AKIA[0-9A-Z]{16}|Bearer\s+\S+)"
)
NAME_PATTERN = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SHARED_IDENTITY = ("name", "version", "description", "license", "repository", "homepage", "keywords")
failures = []


def fail(message):
    failures.append(message)


def load_json(path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as error:
        fail(f"{path.relative_to(ROOT)} does not parse: {error}")
        return None


def json_files():
    found = []
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        found.append(path)
    return found


def walk(value, visit):
    visit(value)
    if isinstance(value, dict):
        for child in value.values():
            walk(child, visit)
    elif isinstance(value, list):
        for child in value:
            walk(child, visit)


def check_secrets(path, document):
    def visit(value):
        if not isinstance(value, dict):
            return
        for key, child in value.items():
            if key.lower() in SECRET_KEYS and child not in ("", None, [], {}):
                fail(f"{path.relative_to(ROOT)} has secret field {key}")
            if isinstance(child, str) and SECRET_VALUE.search(child):
                fail(f"{path.relative_to(ROOT)} has a secret-shaped value at {key}")

    walk(document, visit)


def validate_declared_schema(path, document):
    schema_id = document.get("$schema") if isinstance(document, dict) else None
    if schema_id == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        schema_path = SCHEMA_DIR / "plugin.schema.json"
    elif schema_id == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        schema_path = SCHEMA_DIR / "mcp.schema.json"
    else:
        return
    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    if not errors:
        print(f"schema ok {path.relative_to(ROOT)}")
        return
    for error in errors:
        location = "/".join(str(part) for part in error.path) or "<root>"
        fail(f"{path.relative_to(ROOT)} {location}: {error.message}")


def path_strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def is_remote(value):
    return value.startswith("http://") or value.startswith("https://")


def check_relative_path(owner, field, raw):
    if is_remote(raw):
        return None
    parts = Path(raw).parts
    if raw.startswith("/") or ".." in parts:
        fail(f"{owner} {field} path {raw} leaves the repository")
        return None
    relative = raw[2:] if raw.startswith("./") else raw
    if relative in ("", "."):
        return ROOT
    return ROOT / relative


def require_exists(owner, field, path):
    if path is None:
        return
    if path.exists():
        print(f"path ok {owner} {field} -> {path.relative_to(ROOT) if path != ROOT else '.'}")
        return
    fail(f"{owner} {field} missing {path.relative_to(ROOT)}")


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} has no frontmatter")
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        fail(f"{path.relative_to(ROOT)} frontmatter does not close")
        return {}
    data = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def check_skills(directory):
    skill_files = sorted(directory.glob("*/SKILL.md"))
    if not skill_files:
        fail(f"{directory.relative_to(ROOT)} has no skills")
        return
    for skill in skill_files:
        meta = frontmatter(skill)
        name = meta.get("name", "")
        description = meta.get("description", "")
        if not NAME_PATTERN.match(name):
            fail(f"{skill.relative_to(ROOT)} name is missing or not kebab-case")
        if not description:
            fail(f"{skill.relative_to(ROOT)} description is empty")
        if name and name != skill.parent.name:
            fail(f"{skill.relative_to(ROOT)} name {name} does not match {skill.parent.name}")
        else:
            print(f"skill ok {skill.parent.name}")


def check_mcp_file(owner, path):
    document = load_json(path)
    if not isinstance(document, dict):
        fail(f"{owner} MCP config is not an object")
        return
    servers = document.get("mcpServers")
    if not isinstance(servers, dict) or "skulayer" not in servers:
        fail(f"{path.relative_to(ROOT)} has no skulayer MCP server")
        return
    server = servers["skulayer"]
    if not isinstance(server, dict):
        fail(f"{path.relative_to(ROOT)} skulayer entry is not an object")
        return
    if server.get("url") != "https://skulayer.com/mcp":
        fail(f"{path.relative_to(ROOT)} skulayer URL is not https://skulayer.com/mcp")
    if "headers" in server or "env" in server:
        fail(f"{path.relative_to(ROOT)} skulayer server carries headers or env")
    print(f"mcp ok {path.relative_to(ROOT)}")


def check_cursor_manifest(document):
    owner = ".cursor-plugin/plugin.json"
    name = document.get("name", "")
    if not isinstance(name, str) or not NAME_PATTERN.match(name):
        fail(f"{owner} name must be kebab-case")
    for field in ("logo", "skills", "mcpServers"):
        value = document.get(field)
        if not isinstance(value, str) or not value:
            fail(f"{owner} {field} must be a path")
            continue
        resolved = check_relative_path(owner, field, value)
        require_exists(owner, field, resolved)
        if field == "skills" and resolved is not None and resolved.is_dir():
            check_skills(resolved)
        if field == "mcpServers" and resolved is not None and resolved.is_file():
            check_mcp_file(owner, resolved)
        if field == "logo" and resolved is not None and resolved.is_file():
            if resolved.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
                fail(f"{owner} logo suffix {resolved.suffix} is not an image")
    for field in PATH_FIELDS:
        for raw in path_strings(document.get(field)):
            check_relative_path(owner, field, raw)


def check_manifest_paths(owner, document):
    def visit(value):
        if not isinstance(value, dict):
            return
        for field in PATH_FIELDS:
            for raw in path_strings(value.get(field)):
                resolved = check_relative_path(owner, field, raw)
                require_exists(owner, field, resolved)

    walk(document, visit)


def check_identity(agent, cursor):
    for field in SHARED_IDENTITY:
        if agent.get(field) != cursor.get(field):
            fail(f"plugin.json and .cursor-plugin/plugin.json disagree on {field}")
    agent_author = agent.get("author") if isinstance(agent.get("author"), dict) else {}
    cursor_author = cursor.get("author") if isinstance(cursor.get("author"), dict) else {}
    if agent_author.get("name") != cursor_author.get("name"):
        fail("plugin manifests disagree on author.name")
    print("identity ok")


def check_readme():
    readme = ROOT / "README.md"
    if not readme.is_file():
        fail("README.md is missing")
        return
    text = readme.read_text()
    for needle in (
        "Install the plugin in Cursor",
        "~/.cursor/plugins/local/skulayer",
        "https://skulayer.com/mcp",
    ):
        if needle not in text:
            fail(f"README.md does not mention {needle}")
    print("readme ok")


def main():
    documents = {}
    for path in json_files():
        document = load_json(path)
        if document is None:
            continue
        documents[path] = document
        check_secrets(path, document)
        validate_declared_schema(path, document)
        print(f"parse ok {path.relative_to(ROOT)}")

    for path, document in documents.items():
        owner = str(path.relative_to(ROOT))
        if owner == ".cursor-plugin/plugin.json":
            continue
        check_manifest_paths(owner, document)

    cursor_path = ROOT / ".cursor-plugin" / "plugin.json"
    cursor = documents.get(cursor_path)
    if cursor is None:
        fail(".cursor-plugin/plugin.json is missing")
    else:
        check_cursor_manifest(cursor)

    agent = documents.get(ROOT / "plugin.json")
    if isinstance(agent, dict) and isinstance(cursor, dict):
        check_identity(agent, cursor)

    mcp = documents.get(ROOT / "mcp.json")
    if isinstance(mcp, dict):
        check_mcp_file("mcp.json", ROOT / "mcp.json")

    check_readme()

    if failures:
        for message in failures:
            print(f"FAIL {message}")
        print(f"{len(failures)} failure(s)")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
