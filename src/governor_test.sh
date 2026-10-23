#!/usr/bin/env bash
# ------- CPU GOVERNOR TEST -----------------------------------------------
# runs holistic_bench.py 3 times with different cpu speed settings, logs
# temps / MHz / throttling the whole time, then pushes everything to github.
# takes ~9 min. run from repo root, plugged in:
#   bash src/governor_test.sh
#
# settings tested:
#   1-now                  powersave governor + balance_performance (default)
#   2-epp-performance      powersave governor + performance energy preference
#   3-governor-performance performance governor (always flat out)
# the cpu goes back to the default when it's done (or if it crashes).

set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

CPU=/sys/devices/system/cpu
OUT=reports/$(date +%Y-%m-%d_%H%M)_governor-test
LOG=$OUT/monitor.csv
mkdir -p "$OUT"

# ------- SUDO ------------------------------------------------------------
sudo -v  # ask for the password once
while true; do sudo -n true; sleep 50; done &  # keep sudo from timing out
KEEPALIVE=$!

set_speed() {  # $1 = governor, $2 = energy preference (governor has to go first)
    echo "$1" | sudo tee $CPU/cpu*/cpufreq/scaling_governor >/dev/null
    echo "$2" | sudo tee $CPU/cpu*/cpufreq/energy_performance_preference >/dev/null
}

# ------- MONITOR ---------------------------------------------------------
# every 2 sec: hottest sensor, average cpu speed, total throttle events
echo "cooldown" > "$OUT/.setting"
echo "time,setting,max_temp_c,avg_mhz,throttle_count,plugged_in,battery" > "$LOG"
monitor() {
    set +e  # a missing sensor shouldn't kill the logging
    while true; do
        temp=$(( $(sort -n /sys/class/thermal/thermal_zone*/temp | tail -1) / 1000 ))
        mhz=$(awk '/MHz/ {s += $4; n++} END {printf "%.0f", s / n}' /proc/cpuinfo)
        throttle=$(cat $CPU/cpu*/thermal_throttle/core_throttle_count 2>/dev/null | awk '{s += $1} END {print s + 0}')
        echo "$(date +%T),$(cat "$OUT/.setting"),$temp,$mhz,$throttle,$(cat /sys/class/power_supply/ACAD/online),$(cat /sys/class/power_supply/BAT1/capacity)" >> "$LOG"
        sleep 2
    done
}
monitor &
MONITOR=$!

cleanup() {
    kill $MONITOR $KEEPALIVE 2>/dev/null || true
    set_speed powersave balance_performance
    rm -f "$OUT/.setting"
    echo "cpu back to default (powersave + balance_performance)"
}
trap cleanup EXIT

# ------- RUN -------------------------------------------------------------
LABELS=(1-now 2-epp-performance 3-governor-performance)
declare -A DIRS

run() {  # $1 = label, $2 = governor, $3 = energy preference
    set_speed "$2" "$3"
    echo "cooldown" > "$OUT/.setting"
    echo -e "\n=== $1 ($2 + $3): cooling down 60s first"
    sleep 60
    echo "$1" > "$OUT/.setting"
    python -u src/holistic_bench.py --secs 10 --no-video | tee "$OUT/$1.txt"
    DIRS[$1]=$(sed -n 's/.*report -> //p' "$OUT/$1.txt")
}

run 1-now powersave balance_performance
run 2-epp-performance powersave performance
run 3-governor-performance performance performance

# ------- SUMMARY ---------------------------------------------------------
{
    echo "# CPU governor test"
    echo
    echo "- **laptop:** $(hostname), $(date '+%Y-%m-%d %H:%M')"
    echo "- **plugged in:** $(cat /sys/class/power_supply/ACAD/online) (1 = yes), battery $(cat /sys/class/power_supply/BAT1/capacity)% at the end"
    echo "- 60 sec cooldown before each setting, 10 sec per benchmark test. Full temps in \`monitor.csv\`."
    echo
    echo "| setting | 1 cam total FPS | 2 cams (threads) total FPS | max temp °C | avg MHz | throttle events |"
    echo "|---|---|---|---|---|---|"
    for label in "${LABELS[@]}"; do
        summary="${DIRS[$label]}/summary.md"
        one=$(grep '^| 1cam_c1_w640 ' "$summary" | cut -d'|' -f9 | xargs)
        two=$(grep '^| 2cam_threads' "$summary" | cut -d'|' -f9 | xargs)
        stats=$(awk -F, -v s="$label" '$2 == s {if ($3 > t) t = $3; m += $4; n++; if (n == 1) f = $5; l = $5}
                END {if (n) printf "%d | %.0f | %d", t, m / n, l - f; else printf "? | ? | ?"}' "$LOG")
        echo "| $label | $one | $two | $stats |"
    done
} > "$OUT/summary.md"
cat "$OUT/summary.md"

# ------- PUSH ------------------------------------------------------------
git add reports
git commit -q -m "Add CPU governor test results"
git pull -q --no-rebase --no-edit
git push -q
echo -e "\npushed to github: $OUT"
