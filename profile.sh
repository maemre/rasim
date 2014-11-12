#!/usr/bin/env sh

kernprof -v ./sim.py $*
gprof2dot sim.py.prof --format=pstats -o sim.py.dot
dot -Tpdf sim.py.dot -o sim.py.pdf
