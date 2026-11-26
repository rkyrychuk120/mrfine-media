#!/bin/bash
D=$(python3 -c "import json;print(json.load(open('timeline.json'))['total'])")
P=${1:-6}
pids=()
for i in $(seq 0 $((P-1))); do
  A=$(python3 -c "print(round($D*$i/$P*30)/30)"); B=$(python3 -c "print(round($D*($i+1)/$P*30)/30)")
  python3 render.py video $A $B part$i.mp4 > rlog$i.txt 2>&1 &
  pids+=($!)
done
wait
ls part*.mp4 | sort -V | sed 's/^/file /' > list.txt
ffmpeg -v error -y -f concat -i list.txt -c copy video_only.mp4
ffmpeg -v error -y -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out_1080.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 out_1080.mp4
cat rlog*.txt
