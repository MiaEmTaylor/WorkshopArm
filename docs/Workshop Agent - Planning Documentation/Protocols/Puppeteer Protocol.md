> Current status: Planned, not built.

## Overview
The boss. Decides what the arm should do and gives Marionette general direction (e.g. "touch user's hand").

## Does
- Picks the next action from Signal Fusion's data packet
- Uses [[Handshake Protocol|Handshake]]'s info about who it's working with
- Sends general goals to [[Marionette Protocol|Marionette]]

## Talks to
Signal Fusion, Handshake, Marionette, Service, Personality, GPT. [[Civil Protocol|Civil]] can override it.

## Open
- How it picks between competing goals
