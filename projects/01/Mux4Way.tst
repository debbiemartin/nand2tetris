// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/01/Mux.tst

load Mux4Way.hdl,
output-file Mux4Way.out,
compare-to Mux4Way.cmp,
output-list a%B3.1.3 b%B3.1.3 c%B3.1.3 d%B3.1.3 sel%B2.2.2 out%B3.1.3;

set a 0,
set b 0,
set c 1,
set d 0,
set sel %B00,
eval,
output;

set a 0,
set b 0,
set c 1,
set d 0,
set sel %B01,
eval,
output;

set a 0,
set b 0,
set c 1,
set d 0,
set sel %B10,
eval,
output;

set a 0,
set b 0,
set c 1,
set d 0,
set sel %B11,
eval,
output;
