# GreenAI Network MCP Server for Alexa+

Ask Alexa+ about a real AI compute network — and get measured answers.

**GreenAI Network** is a distributed, sustainable AI compute network
coordinated by a swarm of AI agents. This project exposes the network's
**live telemetry** to Alexa+ (and any MCP client) through a self-hosted
**Model Context Protocol** server using the **Streamable HTTP** transport
(MCP spec **2025-11-25**).

Every answer comes from the network's public telemetry endpoint
(`https://www.greenainetwork.com/api/sala`) and reflects the network *right
now*: nodes online, active agents, responses served, and — the point of
GreenAI — **energy measured on the hardware** (real GPU watts per response,
idle draw subtracted). What cannot be measured is never estimated or shown.

## Tools

| Tool | What it answers |
| --- | --- |
| `network_status` | Nodes online, active agents in the swarm, responses served today and success rate. |
| `energy_report` (`period`: `today` \| `week`) | Measured Wh, Wh per response, metered responses, solar node state, measurement policy. |
| `node_details` | Per-node GPU utilization, VRAM and live power draw. |

Example questions an Alexa+ user can ask:

- “How is the GreenAI Network doing right now?”
- “How much energy did the network use today?”
- “What is the solar node drawing at the moment?”

## Run it

```bash
pip install -r requirements.txt
python server.py
# MCP endpoint: http://localhost:8000/mcp  (Streamable HTTP)
```

Verify with the bundled test client (starts from a second terminal while
the server is running):

```bash
python test_client.py
```

It performs the MCP `initialize` handshake (negotiating protocol
2025-11-25), lists the tools and calls each one against the live network.

## Security / privacy

- The server is **read-only** and consumes a **public** telemetry endpoint.
- It holds **no credentials, tokens or secrets** of any kind — there is
  nothing to configure and nothing sensitive in this repository.
- It exposes no internal addresses: the only outbound call is the public
  `https://www.greenainetwork.com/api/sala`.

## What was built for this hackathon

The GreenAI Network itself (nodes, agent swarm, telemetry) predates the
hackathon and is live in production. **Built during the hackathon window:**
this MCP server, its tool layer over the public telemetry API, and the
Alexa+ integration described above.

## License

MIT — see [LICENSE](LICENSE).
