> Current status: Planned, not built.

## Overview
Combines the output of every other protocol into one clean data packet.

## Does
- Takes in all protocol readings + all finger/palm sensor data
- Priority rules on top, confidence weighting underneath

## Priority (top wins)
1. Civil / safety
2. Task context
3. Explicit input
4. Voice words
5. Pressure / touch
6. Gestures / hand position
7. Gaze / attention
8. Face / affect

## Open
- Write down why task context outranks explicit input
