// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

@nloop
M=1

@R2
M=0

(LOOP)
   @nloop
   D=M
   @R0
   D=D-M // 0 if nloop == R0
   @END
   D; JGT // if nloop > R0 go to end 

   @nloop
   M=M+1 // increment loop
   @R1
   D=M
   @R2
   M=M+D // add R1 to R2  
   @LOOP
   0; JMP

(END)
    @END  
    0; JMP