# CPU governor test

- **laptop:** the-cake-is-a-lie, 2026-10-22 23:35
- **plugged in:** 1 (1 = yes), battery 46% at the end
- 60 sec cooldown before each setting, 10 sec per benchmark test. Full temps in `monitor.csv`.

| setting | 1 cam total FPS | 2 cams (threads) total FPS | max temp °C | avg MHz | throttle events |
|---|---|---|---|---|---|
| 1-now | 15.0 | 28.3 | 49 | 2100 | 0 |
| 2-epp-performance | 15.3 | 28.4 | 49 | 2100 | 0 |
| 3-governor-performance | 15.4 | 28.7 | 49 | 2100 | 0 |
