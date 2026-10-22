# SKULayer agent plugin

SKULayer connects an AI assistant to a product feed. The assistant can audit the feed, turn issues into rules, and show a preview before anything is enabled. This repository is that package for Cursor and for Claude Code.

## Install the plugin in Cursor

1. Clone https://github.com/SKULayer/skulayer-agent-plugin.
2. Copy the clone into `~/.cursor/plugins/local/skulayer`.
3. Open the command palette and run `Developer: Reload Window`.
4. Open Customize and confirm `feed-audit`, `feed-fix`, `feed-health`, and the `skulayer` MCP server.

The MCP entry points at `https://skulayer.com/mcp`. Cursor signs you in with OAuth. The committed config is that URL.

To share the plugin with a team, import https://github.com/SKULayer/skulayer-agent-plugin from Dashboard under Plugins and MCPs. SKULayer submits this repository to the Cursor Marketplace as its own step.

## Install the plugin in Claude Code

1. Run `/plugin marketplace add SKULayer/skulayer-agent-plugin`.
2. Run `/plugin install skulayer@skulayer`.

Claude Code reads the root `plugin.json`, `.mcp.json`, and `.claude-plugin/marketplace.json`. Those files stay the Claude package.

## License

MIT. Copyright 2026 SKULayer Ltd.
