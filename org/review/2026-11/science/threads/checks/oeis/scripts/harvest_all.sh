P=../../../work/pc-venv/bin/python
for q in 'name:"some element plus some"' 'name:"neighbor totalling" Hardin' 'name:"totalling" name:"no more than once"' 'name:"totalling" name:"exactly once" name:"0..3"' 'name:"totalling" name:"exactly once" name:"binary"' 'name:"totalling" name:"horizontally or vertically"' 'name:"totalling" name:"antidiagonally or vertically"' 'name:"totalling" name:"0..2"' 'name:"totalling" name:"0..4"' 'name:"totalling" name:"kXn"' 'name:"totalling" name:"4Xn"' ; do
  $P harvest.py "$q" 60
done
