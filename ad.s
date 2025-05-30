	.file	"ptrace_checker.c"
	.text
	.section	.rodata
.LC0:
	.string	"DEBUG DETECTED!"
	.text
	.globl	anti_debug
	.type	anti_debug, @function
anti_debug:
.LFB6:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	pushl	%ebx
	subl	$4, %esp
	.cfi_offset 3, -12
	call	__x86.get_pc_thunk.bx
	addl	$_GLOBAL_OFFSET_TABLE_, %ebx
	pushl	$0
	pushl	$0
	pushl	$0
	pushl	$0
	call	ptrace@PLT
	addl	$16, %esp
	cmpl	$-1, %eax
	jne	.L3
	subl	$12, %esp
	leal	.LC0@GOTOFF(%ebx), %eax
	pushl	%eax
	call	printf@PLT
	addl	$16, %esp
	subl	$12, %esp
	pushl	$1
	call	exit@PLT
.L3:
	nop
	movl	-4(%ebp), %ebx
	leave
	.cfi_restore 5
	.cfi_restore 3
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
.LFE6:
	.size	anti_debug, .-anti_debug
	.section	.text.__x86.get_pc_thunk.bx,"axG",@progbits,__x86.get_pc_thunk.bx,comdat
	.globl	__x86.get_pc_thunk.bx
	.hidden	__x86.get_pc_thunk.bx
	.type	__x86.get_pc_thunk.bx, @function
__x86.get_pc_thunk.bx:
.LFB7:
	.cfi_startproc
	movl	(%esp), %ebx
	ret
	.cfi_endproc
.LFE7:
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
