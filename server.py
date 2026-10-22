"""GreenAI Network MCP server for Alexa+.

Exposes the live GreenAI Network (a distributed, sustainable AI compute
network coordinated by a swarm of AI agents) to Alexa+ and any MCP client
through the Model Context Protocol Streamable HTTP transport
(spec 2025-11-25).

All data is real and live: every tool reads the network's public telemetry
endpoint (https://www.greenainetwork.com/api/sala), which reports measured
GPU energy per response - never estimates.

Run:
    pip install -r requirements.txt
    python server.py            # serves MCP at http://0.0.0.0:8000/mcp
"""

import asyncio
import json
import os
import urllib.request

from mcp.server.mcpserver import MCPServer

API_URL = "https://www.greenainetwork.com/api/sala"

mcp = MCPServer("greenai-network")


def _fetch_sync() -> dict:
    """Fetch the telemetry snapshot with the stdlib only.

    Uses HTTPS_PROXY/https_proxy when the host defines one and connects
    directly otherwise. (No credentials are involved: the endpoint is
    public.)
    """
    proxies = {}
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        proxies["https"] = proxy
    opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    req = urllib.request.Request(
        API_URL, headers={"User-Agent": "greenai-network-mcp/1.0"}
    )
    with opener.open(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def _sala() -> dict:
    """Fetch the live network telemetry snapshot."""
    return await asyncio.to_thread(_fetch_sync)


@mcp.tool()
async def network_status() -> str:
    """Current status of the GreenAI Network: which compute nodes are
    online, how many AI agents are active, and how many responses the
    network has served today, with its success rate."""
    d = await _sala()
    nodes = d.get("nodos", [])
    online = [n for n in nodes if n.get("online")]
    lines = [
        f"GreenAI Network status at {d.get('ts', 'now')}:",
        f"- Nodes online: {len(online)} of {len(nodes)}",
    ]
    for n in nodes:
        state = "online" if n.get("online") else "offline"
        lines.append(f"  * {n.get('nombre')} ({n.get('tipo')}): {state}")
    lines.append(f"- Active AI agents in the swarm: {d.get('agentes_activos')}")
    hoy = d.get("metricas", {}).get("hoy", {})
    if hoy:
        lines.append(
            f"- Today: {hoy.get('respuestas')} responses served, "
            f"{hoy.get('exito_pct')}% success rate."
        )
    return "\n".join(lines)


@mcp.tool()
async def energy_report(period: str = "today") -> str:
    """Measured energy report of the GreenAI Network.

    Energy is measured on the hardware (real GPU watts drawn during each
    response, minus idle draw) - never estimated.

    Args:
        period: "today" or "week".
    """
    d = await _sala()
    key = "hoy" if period != "week" else "semana"
    label = "Today" if key == "hoy" else "This week"
    m = d.get("metricas", {}).get(key, {})
    if not m:
        return f"No energy data available for period '{period}'."
    lines = [
        f"GreenAI Network energy report ({label.lower()}):",
        f"- Responses served: {m.get('respuestas')}",
        f"- Success rate: {m.get('exito_pct')}%",
        f"- Measured energy: {m.get('wh_medidos')} Wh across "
        f"{m.get('respuestas_medidas')} metered responses",
        f"- Average: {m.get('wh_por_respuesta')} Wh per response",
    ]
    solar = d.get("solar") or {}
    if solar:
        parts = [f"{k}={v}" for k, v in solar.items()]
        lines.append(f"- Solar node: {', '.join(parts)}")
    if d.get("honestidad"):
        lines.append(f"- Measurement policy: {d['honestidad']}")
    return "\n".join(lines)


@mcp.tool()
async def node_details() -> str:
    """Per-node detail of the GreenAI Network: GPU utilization, VRAM and
    live power draw for each compute node."""
    d = await _sala()
    lines = ["GreenAI Network nodes:"]
    for n in d.get("nodos", []):
        state = "online" if n.get("online") else "offline"
        lines.append(f"- {n.get('nombre')} ({n.get('tipo')}): {state}")
        if "power_w_total" in n:
            lines.append(f"  Power draw now: {n['power_w_total']} W total")
        if "vram_total_gib" in n:
            lines.append(f"  VRAM: {n['vram_total_gib']} GiB")
        for i, g in enumerate(n.get("gpus", [])):
            lines.append(
                f"  GPU {i}: {g.get('util_pct')}% utilization, "
                f"{g.get('vram_pct')}% VRAM, {g.get('power_w')} W"
            )
        models = n.get("modelos_cargados")
        if models:
            lines.append(f"  Models loaded: {', '.join(models)}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
