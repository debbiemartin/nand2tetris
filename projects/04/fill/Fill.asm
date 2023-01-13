// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


@8192
D=A
@screenlen
M=D // 2^13 - 32 cols (512 pixels) x 256 rows

(OUTERLOOP)
    @SCREEN
    D=A

    @screenptr
    M=D

    @KBD 
    D=M

    @WHITE
    D; JEQ 

    @BLACK
    0; JNE

    (BLACK)
        @colour
        M=-1
        @LOOP
        0; JMP

    (WHITE)
        @colour
        M=0
        @LOOP
        0; JMP

    (LOOP)
        @screenptr
        D=M
        @screenlen
        D=D-M // 0 if screenptr == screenlen
        @SCREEN
        D=D-A // D is now position relative to SCREEN start 
        @OUTERLOOP
        D; JGE // if screenptr >= screenlen go to end 

        @colour
        D=M
        @screenptr
        A=M // get the pointer to the next screen register
        M=D // colour the pixel

        @screenptr
        M=M+1 // increment loop 
        @LOOP
        0; JMP
