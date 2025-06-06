import lief

binary = lief.parse("login_checker_patched")
main = binary.get_function_address("main")
#pw: S3cur3P4ssw0rd!
anti_debug_shellcode = [
    0x55, 0x89, 0xe5, 0x53, 0x83, 0xec, 0x04, 0xe8, 0xfc, 0xff, 0xff, 0xff,
    0x81, 0xc3, 0x02, 0x00, 0x00, 0x00, 0x6a, 0x00, 0x6a, 0x00, 0x6a, 0x00,
    0x6a, 0x00, 0xe8, 0xfc, 0xff, 0xff, 0xff, 0x83, 0xc4, 0x10, 0x83, 0xf8,
    0xff, 0x75, 0x1c, 0x83, 0xec, 0x0c, 0x8d, 0x83, 0x00, 0x00, 0x00, 0x00,
    0x50, 0xe8, 0xfc, 0xff, 0xff, 0xff, 0x83, 0xc4, 0x10, 0x83, 0xec, 0x0c,
    0x6a, 0x01, 0xe8, 0xfc, 0xff, 0xff, 0xff, 0x90, 0x8b, 0x5d, 0xfc, 0xc9,
    0xc3
]

segment = binary.segment_from_virtual_address(main)
offset = main - segment.virtual_address + segment.file_offset

with open("login_checker_patched", "rb+") as f:
    f.seek(offset)
    f.write(bytes(anti_debug_shellcode))

print("injected!")