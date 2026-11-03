#!/bin/bash
cd /tmp/claude-0/work/stylo2/v
export NOIR=1 ACC=18,150,100 MARG=150,205,180 PYTHONPATH=/tmp/claude-0/work/pal
for a in $(seq 0 200 1600); do
  b=$((a+200)); [ $b -gt 1602 ] && b=1602
  f=seg_$(printf %04d $a).mp4
  [ -s $f ] && ffprobe -v error $f 2>/dev/null && continue
  python3 ../../pal/seg_render.py ep.py $f.tmp.mp4 $a $b && mv $f.tmp.mp4 $f
done
echo ALLDONE
