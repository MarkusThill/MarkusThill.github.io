; Field is stored in a 1-dim. array (indices)
;|-----------------| 
;| 00, 01 | 02, 03 |
;| 04, 05 | 06, 07 |
;|--------+--------|
;| 08, 09 | 10, 11 |
;| 12, 13 | 14, 15 |
;|-----------------|

; --------------------------------------------------------------------
; Zero-page pointer + constants
; --------------------------------------------------------------------
p             = $80            ; ZP pointer to current Sudoku (low/high at p, p+1)

FIELD_SIZE    = 16
CELLS_PER_ROW = 4
CELLS_PER_COL = 4
NUM_DIGITS    = 4

currentSudoku = sudoku17       ; default puzzle source (can be repointed)

;====================================================================
; Macros
;====================================================================
; Save selected registers/flags to stack (order matters!)
SAXY_TO_STACK .MACRO sS, sA, sX, sY
	.IF sS
		PHP                 ; save status flags
	.ENDIF
	.IF sA
		PHA                 ; save A
	.ENDIF
	.IF sX
		TXA                 ; push X via A
		PHA
	.ENDIF
	.IF sY
		TYA                 ; push Y via A
		PHA
	.ENDIF
	.ENDM

; Restore selected registers/flags from stack (reverse order!)
SAXY_FROM_STACK .MACRO sS, sA, sX, sY
	.IF sY
		PLA
		TAY                 ; restore Y
	.ENDIF
	.IF sX
		PLA
		TAX                 ; restore X
	.ENDIF
	.IF sA
		PLA                 ; restore A
	.ENDIF
	.IF sS
		PLP                 ; restore status flags
	.ENDIF
	.ENDM

	.ORG $4000

main:
	; SAXY_TO_STACK 1,1,1,1
	; JSR IS_FULL_TEST
	; JSR IS_LEGAL_COL_TEST
	; JSR IS_LEGAL_HOUSE_TEST
	; JSR IS_LEGAL_BOARD_TEST
	; JSR init

	; Initialize ZP pointer p -> currentSudoku (little endian)
	LDA #<currentSudoku          ; low byte
	STA p
	LDA #>currentSudoku          ; high byte
	STA p+1

	JSR init
	JSR solve
	RTS
;--------------------------------------------------------------------


;====================================================================
; 1. Copy given Sudoku referenced by pointer p to array field
;====================================================================
init:
	SAXY_TO_STACK 1,1,1,1

	; reset field (currently commented out)
	; LDY #FIELD_SIZE-1
	; LDA #0
; init_resetField:
	; STA field, Y
	; DEY
	; BPL init_resetField

	; Copy content of referenced input-field to field
	LDY #FIELD_SIZE-1
init_cpy_field:
	LDA (p), Y                    ; read from *p + Y
	STA field, Y                  ; write into local board
	DEY
	BPL init_cpy_field

	SAXY_FROM_STACK 1,1,1,1
	RTS
;--------------------------------------------------------------------


;====================================================================
; Solve the Sudoku given in the array "field"
; Parameters:
;	None
; Return:
;	AKKU: True(1) if Sudoku could be solved, otherwise False (0)
;		Alternative is the Zero-Flag
; Temporary variables used:
; 	none
;====================================================================
solve:
	SAXY_TO_STACK 0,0,1,1          ; only save X/Y

	; Two bytes of local state are kept on the stack:
	;   $0102,X : current index (cell)
	;   $0101,X : current digit guess
	LDA #0
	PHA                            ; start at index 0
	PHA                            ; digit (initially 0)

	; If board is full => solved (note: is_full returns 1 by INC on stack)
	JSR is_full
	BEQ solve_nextCell

	; We have a solution
	SEC
	BCS solveEnd                   ; unconditional (SEC sets C)

solve_nextCell:                  ; loop over cells
	TSX
	LDA $0102, X                   ; load index (cell pointer) from stack frame
	TAY

	; Skip filled cells
	LDA field, Y
	BNE solve_nextCellEnd          ; continue with next cell if not empty

	; Start trying digits at 1
	LDA #1
	STA $0101, X                   ; store current digit in stack frame

solve_nextDigit:
	STA field, Y                   ; set current cell to current digit

	; Check legality of this placement (row/col/house + empties allowed)
	JSR isLegalBoard
	BEQ solve_nextDigitEnd         ; not legal => try next digit

	; Recurse
	JSR solve
	SEC                            ; use Carry as "solution found" indicator
	BNE solveEnd                   ; if solution found (A!=0), stop unwinding

solve_nextDigitEnd:
	; Next digit
	INC $0101, X
	LDA $0101, X
	CMP #NUM_DIGITS+1
	BMI solve_nextDigit

	; No digit worked -> reset cell
	LDA #0
	STA field, Y

	; All digits were tried
	CLC                            ; indicate failure via Carry
	BEQ solveEnd                   ; unconditional (Z is set from previous STA? kept as-is)

solve_nextCellEnd:
	INC $0102, X                   ; next cell index
	LDA #FIELD_SIZE
	CMP $0102, X
	BPL solve_nextCell

	CLC                            ; C-Flag needed to decide on return value

solveEnd:
	PLA                            ; pop index-counter
	PLA                            ; pop digit-counter

	SAXY_FROM_STACK 0,0,1,1
	LDA #0                          ; default return: no solution
	BCC solveEndNoSolution          ; if Carry clear => failure

	LDA #1                          ; success
solveEndNoSolution:
	RTS
;--------------------------------------------------------------------


;====================================================================
; Check if the whole board is legal (all houses/cols/rows).
; Empty cells are considered legal.
; Parameters:
;	None
; Return:
;	AKKU: True(1) or False (0), Alternative is the Zero-Flag
; Temporary variables used:
; 	return+1: Return-value (safe temp; not used by callees)
;====================================================================
isLegalBoard:
	SAXY_TO_STACK 0,1,1,1

	LDA #0
	STA return+1                    ; return+1 is not used by called subroutines

	LDX #3                          ; iterate over 0..3
isLegalBoardLoop:
	TXA
	JSR isLegalHouse
	BEQ isLegalBoardEnd

	TXA
	JSR isLegalCol
	BEQ isLegalBoardEnd

	TXA
	JSR isLegalRow
	BEQ isLegalBoardEnd

	DEX
	BPL isLegalBoardLoop

	INC return+1                    ; all checks passed

isLegalBoardEnd:
	SAXY_FROM_STACK 0,1,1,1
	LDA return+1
	RTS
;--------------------------------------------------------------------


;====================================================================
; Check if the given house (0-3) is legal.
; Empty cells are considered as legal.
; Parameters:
;	AKKU: House to be checked
; Return:
;	AKKU: True(1) or False (0), Alternative is the Zero-Flag
; Temporary variables used:
; 	return:  Return-value
;	counter: Offset/temporary
;====================================================================
	;|-----------------|
	;| 00, 01 | 02, 03 |
	;| 04, 05 | 06, 07 |
	;|--------+--------|
	;| 08, 09 | 10, 11 |
	;| 12, 13 | 14, 15 |
	;|-----------------|
isLegalHouse:
	SAXY_TO_STACK 0,1,1,1

	LDA #0
	STA counter                      ; offset for even houses
	STA return

	; Get house index from caller stack frame
	TSX
	LDA $0103, X

	; Compute starting index of the 2x2 house:
	; - LSR splits even/odd house in row (C=1 for odd)
	; - ASL*3 scales to row-block offset
	LSR                               ; C-Flag set for odd house
	BCC isLegalHouse_EvenHouse
	INC counter
	INC counter                       ; Add offset of 2 for odd house
isLegalHouse_EvenHouse:
	ASL
	ASL
	ASL
	ADC counter

	; Starting index now in A
	TAX                               ; X = start of house
	TAY

	; Precompute the other 3 indices of this house into counter..counter+2
	INY
	STY counter                       ; cell #2
	INY
	INY
	INY
	STY counter+1                     ; cell #3
	INY
	STY counter+2                     ; cell #4

	; Compare cell #1 against the other three (skip if empty)
	LDY counter
	LDA field, X
	BEQ isLegalHouse_EvenHouse_Cell2
	CMP field, Y
	BEQ isLegalHouseEnd               ; #1 == #2
	LDY counter+1
	CMP field, Y
	BEQ isLegalHouseEnd               ; #1 == #3
	INY
	CMP field, Y
	BEQ isLegalHouseEnd               ; #1 == #4

isLegalHouse_EvenHouse_Cell2:
	; Compare cell #2 against #3/#4
	INX
	LDA field, X
	BEQ isLegalHouse_EvenHouse_Cell3
	LDY counter+2
	CMP field, Y
	BEQ isLegalHouseEnd               ; #2 == #4
	DEY
	CMP field, Y
	BEQ isLegalHouseEnd               ; #2 == #3

isLegalHouse_EvenHouse_Cell3:
	; Compare cell #3 against #4
	LDY counter+1
	LDA field, Y
	BEQ isLegalHouseTrue
	INY
	CMP field, Y
	BEQ isLegalHouseEnd               ; #3 == #4

isLegalHouseTrue:
	INC return

isLegalHouseEnd:
	SAXY_FROM_STACK 0,1,1,1
	LDA return
	RTS
;--------------------------------------------------------------------


;====================================================================
; Check if the given column (0-3) is legal (no duplicates).
; Empty cells are considered as legal.
; Parameters:
;	AKKU: Column to be checked
; Return:
;	AKKU: True(1) or False (0), Alternative is the Zero-Flag
; Temporary variables used:
; 	return:    Return-value
;	counter:   loop-counter outer-loop / starting index
;	counter+1: loop-counter inner-loop
;	index:     second-last index of current column
;	index+1:   last index of current column
;====================================================================
	;|-----------------|
	;| 00, 01 | 02, 03 |
	;| 04, 05 | 06, 07 |
	;|--------+--------|
	;| 08, 09 | 10, 11 |
	;| 12, 13 | 14, 15 |
	;|-----------------|
isLegalCol:
	SAXY_TO_STACK 0,1,1,1

	; Set return value, initially zero
	LDA #0
	STA return

	; Get starting index (column number) from caller stack frame
	TSX
	LDA $0103, X
	STA counter

	; calc second-last index of current column
	CLC
	ADC #CELLS_PER_ROW*2
	STA index                         ; second-last index of current column

	; calc last index of current column
	ADC #CELLS_PER_ROW
	STA index+1                       ; last index of current column

	; <outerLoop>
isLegalCol_checkLoop:
	CLC
	LDA counter
	TAY
	ADC #CELLS_PER_ROW
	STA counter+1

	; <innerLoop> compare field[Y] against all later cells in this column
isLegalCol_countDigits:
	LDX counter+1
	LDA field, Y
	BEQ isLegalCol_checkLoopEnd       ; empty => skip comparisons
	CMP field, X
	BEQ isLegalColEnd                 ; duplicate found => illegal

	CLC
	LDA counter+1
	ADC #CELLS_PER_ROW
	STA counter+1

	LDA index+1
	CMP counter+1
	BCS isLegalCol_countDigits
	; </innerLoop>

isLegalCol_checkLoopEnd:
	CLC
	LDA counter
	ADC #CELLS_PER_ROW
	STA counter

	LDA index
	CMP counter
	BCS isLegalCol_checkLoop
	; </outerLoop>

	INC return                         ; no duplicates
isLegalColEnd:
	SAXY_FROM_STACK 0,1,1,1
	LDA return
	RTS


;====================================================================
; Check if the given row (0-3) is legal (no duplicates).
; Empty cells are considered as legal.
; Parameters:
;	AKKU: Row to be checked
; Return:
;	AKKU: True(1) or False (0), Alternative is the Zero-Flag
; Temporary variables used:
; 	index:    starting index of next row
;	index+1:  last index of current row
;	return:   Return-value
;====================================================================
	;|-----------------|
	;| 00, 01 | 02, 03 |
	;| 04, 05 | 06, 07 |
	;|--------+--------|
	;| 08, 09 | 10, 11 |
	;| 12, 13 | 14, 15 |
	;|-----------------|
isLegalRow:
	SAXY_TO_STACK 0,1,1,1

	; Set return value, initially zero
	LDA #0
	STA return

	; Multiply row by 4 to get starting index
	TSX
	LDA $0103, X
	ASL
	ASL
	TAX                               ; X = row start (outer loop)

	; Add 4 to get first index of the next row
	CLC
	ADC #CELLS_PER_ROW
	STA index

	; Add 3 to get last index of current row
	STA index+1
	DEC index+1

	; <Outer loop> iterate over cells in this row
isLegalRow_checkLoop:
	TXA
	TAY                               ; Y = current cell (inner loop anchor)
	INY                               ; start comparisons at next cell
	LDA field, X                      ; digit to check
	BEQ isLegalRow_CheckLoopEnd       ; empty => skip comparisons

	; <Inner loop> compare against remaining cells in row
isLegalRow_countDigits:
	CMP field, Y
	BEQ isLegalRow_End                ; duplicate found
	INY
	CPY index
	BNE isLegalRow_countDigits
	; </Inner loop>

isLegalRow_CheckLoopEnd:
	INX
	CPX index+1
	BNE isLegalRow_checkLoop
	; </Outer loop>

	INC return                         ; no duplicates

isLegalRow_End:
	SAXY_FROM_STACK 0,1,1,1
	LDA return
	RTS


;====================================================================
; Tests if the sudoku-field is completely filled.
; Does NOT check consistency: only whether every cell != 0.
; Return is via stack-mutation trick (INC $0103,X) while A stays 0/1.
; Zero flag can be used by caller.
;====================================================================
is_full:
	LDA #0                             ; assume not full (return value 0)
	SAXY_TO_STACK 0,1,1,1

	LDX #FIELD_SIZE-1
is_full_loop:
	; Check if cell is empty and leave loop if so
	LDY field, X
	BEQ is_full_end

	; Cell not empty -> next
	DEX
	BPL is_full_loop                   ; continue while X >= 0

	; All cells filled -> set return-value to true (1)
	TSX
	INC $0103, X                       ; flips caller-visible return byte

is_full_end:
	SAXY_FROM_STACK 0,1,1,1
	RTS
;--------------------------------------------------------------------



;====================================================================
; Data section
;====================================================================
	.ORG $6000

; --------------------------------------------------------------------
; Working field (4x4 Sudoku = 16 cells)
; This is the board that gets modified by the solver
; --------------------------------------------------------------------
field:
	.RS $10                 ; reserve 16 bytes for the current board


; --------------------------------------------------------------------
; Sudoku test boards (4x4)
; Zeros denote empty cells
; Comments show one valid solution (if solvable)
; --------------------------------------------------------------------

sudoku17:
ll171:	.BYTE 2,0,0,3		; 2,4,1,3
ll172:	.BYTE 0,0,0,1		; 1,3,2,4
ll173:	.BYTE 1,0,0,0		; 4,1,3,2
ll174:	.BYTE 3,0,0,2		; 3,2,4,1

sudoku16:
ll161:	.BYTE 0,4,0,3		; 2,4,1,3
ll162:	.BYTE 1,0,0,0		; 1,3,2,4
ll163:	.BYTE 0,0,0,0		; 4,1,3,2
ll164:	.BYTE 0,0,4,1		; 3,2,4,1

sudoku15:
ll151:	.BYTE 0,0,0,1		; 2,4,3,1
ll152:	.BYTE 3,0,2,0		; 3,1,2,4
ll153:	.BYTE 4,0,0,3		; 4,2,1,3
ll154:	.BYTE 0,0,0,0		; 1,3,4,2

sudoku14:
ll141:	.BYTE 0,0,0,1		; 2,3,4,1
ll142:	.BYTE 0,0,2,0		; 4,1,2,3
ll143:	.BYTE 0,4,0,0		; 1,4,3,2
ll144:	.BYTE 3,2,0,0		; 3,2,1,4

sudoku13:
ll131:	.BYTE 0,0,0,0		; 2,4,1,3
ll132:	.BYTE 1,3,0,0		; 1,3,2,4
ll133:	.BYTE 4,0,0,2		; 4,1,3,2
ll134:	.BYTE 0,0,4,0		; 3,2,4,1

sudoku12:
ll121:	.BYTE 2,0,1,0		; not solvable
ll122:	.BYTE 0,0,0,2
ll123:	.BYTE 0,3,0,1
ll124:	.BYTE 4,0,2,0

sudoku11:
ll111:	.BYTE 0,0,1,0		; 3,2,1,4
ll112:	.BYTE 0,0,0,2		; 1,4,3,2
ll113:	.BYTE 0,3,0,1		; 2,3,4,1
ll114:	.BYTE 4,0,2,0		; 4,1,2,3

sudoku10:
ll101:	.BYTE 0,0,4,0		; not solvable
ll102:	.BYTE 0,1,0,3
ll103:	.BYTE 0,0,0,1
ll104:	.BYTE 1,0,0,4

sudoku9:
ll91:	.BYTE 0,0,4,0		; 2,3,4,1
ll92:	.BYTE 0,1,0,3		; 4,1,2,3
ll93:	.BYTE 0,0,0,0		; 3,4,1,2
ll94:	.BYTE 1,0,0,4		; 1,2,3,4

sudoku8:
ll81:	.BYTE 0,0,2,0		; 4,3,2,1
ll82:	.BYTE 2,0,0,3		; 2,1,4,3
ll83:	.BYTE 0,4,0,0		; 3,4,1,2
ll84:	.BYTE 0,0,3,0		; 1,2,3,4

sudoku7:
ll71:	.BYTE 0,0,4,0		; 3,2,4,1
ll72:	.BYTE 1,4,0,0		; 1,4,3,2
ll73:	.BYTE 2,0,0,0		; 2,3,1,4
ll74:	.BYTE 0,0,2,0		; 4,1,2,3

sudoku6:
ll61:	.BYTE 4,0,0,0		; 4,1,2,3
ll62:	.BYTE 3,0,1,4		; 3,2,1,4
ll63:	.BYTE 0,0,3,0		; 2,4,3,1
ll64:	.BYTE 1,0,0,0		; 1,3,4,2

sudoku5:
ll51:	.BYTE 2,0,3,0		; 2,1,3,4
ll52:	.BYTE 0,3,0,0		; 4,3,1,2
ll53:	.BYTE 1,0,0,0		; 1,2,4,3
ll54:	.BYTE 0,0,2,0		; 3,4,2,1

sudoku4:
ll41:	.BYTE 0,0,0,0		; 4,3,2,1
ll42:	.BYTE 1,0,3,0		; 1,2,3,4
ll43:	.BYTE 0,1,4,0		; 3,1,4,2
ll44:	.BYTE 2,0,0,0		; 2,4,1,3

sudoku3:
ll31:	.BYTE 0,0,1,0		; 2,4,1,3
ll32:	.BYTE 0,3,0,0		; 1,3,4,2
ll33:	.BYTE 0,2,0,0		; 4,2,3,1
ll34:	.BYTE 0,0,0,4		; 3,1,2,4

sudoku2:
ll21:	.BYTE 0,0,0,0
ll22:	.BYTE 0,0,0,0
ll23:	.BYTE 0,0,0,0
ll24:	.BYTE 0,0,0,0

sudoku1:
ll11:	.BYTE 4,0,2,0		; 4,3,2,1
ll12:	.BYTE 1,0,0,3		; 1,2,4,3
ll13:	.BYTE 0,0,0,0		; 2,1,3,4
ll14:	.BYTE 0,0,0,2		; 3,4,1,2


; --------------------------------------------------------------------
; Temporary variables
; NOTE:
; - Only valid within ONE subroutine
; - Must not be relied upon across subroutine calls
; - Contents are generally non-zero / undefined on entry
; --------------------------------------------------------------------
index:	.RS $10              ; general-purpose index storage
counter: .RS $10             ; loop counters / offsets
return:	.RS $10              ; boolean return values